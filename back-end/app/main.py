from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from .database import get_db, TimePoint, EstadoSnapshot


app = FastAPI(title="Vacina Brasil API", version="1.0.0")

# CORS para desenvolvimento (Vite normalmente roda em 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vacinacao-delta.vercel.app",
        "https://vacinacao-5lan.onrender.com",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ====== Modelos de resposta ======

class ApiResponse(BaseModel):
    data: Optional[Dict[str, Any]]
    success: bool
    message: Optional[str] = None


class ApiListResponse(BaseModel):
    data: List[Dict[str, Any]]
    success: bool
    message: Optional[str] = None


def parse_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except Exception:
        return None

def try_scalar_query(db: Session, sql_variants: List[str]):
    """Tenta executar cada string SQL em sql_variants em ordem e retorna
    a first row if uma execução funcionar. Caso todas falhem, retorna None.

    Isso torna o código tolerante a variações no schema (por exemplo colunas
    em maiúsculas ou com prefixos como TX_QTDE)."""
    for sql in sql_variants:
        try:
            r = db.execute(text(sql)).first()
            if r is not None:
                return r
        except Exception:
            # ignora e tenta próxima variante
            continue
    return None


def try_query_all(db: Session, sql_variants: List[str]):
    """Executa cada SQL em sql_variants até uma execução bem sucedida e
    retorna .all() do resultado. Se todas falharem, retorna None."""
    for sql in sql_variants:
        try:
            rows = db.execute(text(sql)).all()
            return rows
        except Exception:
            continue
    return None


def is_unset(filter_value: Optional[str]) -> bool:
    if filter_value is None:
        return True
    v = filter_value.strip().lower()
    return v in ("", "todos", "all", "none", "null")


# ====== Endpoints ======

@app.get("/overview", response_model=ApiResponse)
def get_overview(
    ano: Optional[str] = Query(None),
    mes: Optional[str] = Query(None),
    uf: Optional[str] = Query(None),
    fabricante: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        # Consultar snapshot dos estados
        query = db.query(EstadoSnapshot)
        
        if not is_unset(uf):
            query = query.filter(EstadoSnapshot.uf == uf)
        
        state_items = query.all()
        
        # Agregação direta da tabela `distribuicao_raw` — somar apenas a coluna QTDE
        # Aplicar filtros ANO/MES apenas se fornecidos e válidos (números)
        try:
            ano_int = parse_int(ano)
            mes_int = parse_int(mes)

            where = []
            params = {}
            if ano_int is not None:
                where.append('"ANO" = :ano')
                params['ano'] = ano_int
            if mes_int is not None:
                where.append('"MES" = :mes')
                params['mes'] = mes_int

            base_sql = 'SELECT COALESCE(SUM(CAST("QTDE" AS numeric)),0) AS total FROM public.distribuicao_raw'
            if where:
                base_sql = f"{base_sql} WHERE {' AND '.join(where)}"

            r = db.execute(text(base_sql), params).first()
            total_distribuidas = int(r.total) if r and getattr(r, 'total', None) is not None else 0
        except Exception:
            # Se a tabela não existir ou houver erro, retornar zeros para não quebrar o frontend
            total_distribuidas = 0

        # Para esse diagnóstico/ajuste, manter os demais campos como zero para evitar quebra no frontend
        total_aplicadas = 0
        eficiencia = 0.0
        esavi = 0
        
        overview = {
            "distribuídas": total_distribuidas,
            "aplicadas": total_aplicadas,
            "eficiência": eficiencia,
            "esavi": esavi,
        }
        return {"data": overview, "success": True}
    except Exception:
        # Em caso de erro de consulta, retornar valores vazios/zeros para não expor mocks
        overview = {
            "distribuídas": 0,
            "aplicadas": 0,
            "eficiência": 0.0,
            "esavi": 0,
        }
        return {"data": overview, "success": True}


@app.get("/timeseries", response_model=ApiListResponse)
def get_timeseries(
    ano: Optional[str] = Query(None),
    mes: Optional[str] = Query(None),
    uf: Optional[str] = Query(None),
    fabricante: Optional[str] = Query(None),
    debug: Optional[int] = Query(0),
    db: Session = Depends(get_db)
):
    try:
        # Para evitar depender do snapshot `timeseries` (vazia no deploy),
        # consultar diretamente a tabela `distribuicao_raw` usando a mesma
        # SQL testada no endpoint de debug. Isso garante que o frontend
        # receba dados consistentes filtrados por ano/mes/uf quando
        # disponíveis no dump.
        ano_int = parse_int(ano)
        mes_int = parse_int(mes)
        params = {}
        where = []
        if ano_int is not None:
            where.append('"ANO" = :ano')
            params['ano'] = ano_int
        if mes_int is not None:
            where.append('"MES" = :mes')
            params['mes'] = mes_int
        if not is_unset(uf):
            where.append('"SIGLA" = :uf')
            params['uf'] = uf

        sql = 'SELECT "ANO" AS ano, "MES" AS mes, SUM(CAST("QTDE" AS numeric)) AS distribuidas FROM public.distribuicao_raw'
        if where:
            sql = f"{sql} WHERE {' AND '.join(where)}"
        sql = f"{sql} GROUP BY \"ANO\", \"MES\" ORDER BY \"ANO\", \"MES\""

        agg_rows = db.execute(text(sql), params).all() or []

        series = [
            {
                "ano": int(r.ano) if getattr(r, 'ano', None) is not None else 2021,
                "mês": int(r.mes) if getattr(r, 'mes', None) is not None else 0,
                "uf": (params.get('uf') if params.get('uf') is not None else 'BR'),
                "distribuídas": int(r.distribuidas) if getattr(r, 'distribuidas', None) is not None else 0,
                "aplicadas": 0,
                "eficiência": 0.0,
                "esavi": 0,
            }
            for r in agg_rows
        ]

        if debug:
            return {"data": series, "success": True, "debug": {"sql": sql, "rows": len(agg_rows)}}
        
        return {"data": series, "success": True}
    except Exception:
        # Em caso de erro -> retornar lista vazia
        return {"data": [], "success": True}


@app.get("/ranking/ufs", response_model=ApiListResponse)
def get_ranking_ufs(
    ano: Optional[str] = Query(None),
    mes: Optional[str] = Query(None),
    uf: Optional[str] = Query(None),
    fabricante: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        # Consultar snapshot dos estados no banco
        query = db.query(EstadoSnapshot)
        
        if not is_unset(uf):
            query = query.filter(EstadoSnapshot.uf == uf)
        
        records = query.order_by(EstadoSnapshot.eficiência.desc()).all()
        
        if not records:
            # Se não houver snapshot, tentar agrupar por sigla a partir da tabela
            # `distribuicao` e retornar ranking por distribuídas.
            try:
                # Construir SQL parametrizado para agrupar por UF na tabela distribucao_raw
                ano_int = parse_int(ano)
                mes_int = parse_int(mes)
                where_clauses = []
                params = {}
                if ano_int is not None:
                    where_clauses.append('"ANO" = :ano')
                    params['ano'] = ano_int
                if mes_int is not None:
                    where_clauses.append('"MES" = :mes')
                    params['mes'] = mes_int
                if not is_unset(uf):
                    where_clauses.append('"SIGLA" = :uf')
                    params['uf'] = uf

                # Usar alias sem acento para garantir que o driver exponha a coluna
                base_sql = 'SELECT "SIGLA" AS uf, SUM(CAST("QTDE" AS numeric)) AS distribuidas FROM public.distribuicao_raw'
                if where_clauses:
                    base_sql = f"{base_sql} WHERE {' AND '.join(where_clauses)}"
                base_sql = f"{base_sql} GROUP BY \"SIGLA\" ORDER BY SUM(CAST(\"QTDE\" AS numeric)) DESC"

                # Variantes alternativas caso a coluna tenha nome diferente no dump
                alt_variants = [
                    "SELECT sigla AS uf, SUM(CAST(qtde AS numeric)) AS distribuidas FROM distribuicao_raw",
                    'SELECT "TX_SIGLA" AS uf, SUM(CAST("QTDE" AS numeric)) AS distribuidas FROM distribuicao_raw',
                    'SELECT sigla AS uf, SUM(CAST("QTDE" AS numeric)) AS distribuidas FROM public.distribuicao_raw',
                ]

                agg_rows = []
                # Tentar variante padrão
                try:
                    agg_rows = db.execute(text(base_sql), params).all()
                except Exception:
                    agg_rows = []

                # Se não trouxe resultados, tentar variantes alternativas (sem depender de exceção)
                if not agg_rows:
                    for v in alt_variants:
                        try:
                            sql = v
                            if where_clauses:
                                sql = f"{sql} WHERE {' AND '.join(where_clauses)}"
                            sql = f"{sql} GROUP BY sigla ORDER BY SUM(CAST(\"QTDE\" AS numeric)) DESC"
                            agg_rows = db.execute(text(sql), params).all()
                            if agg_rows:
                                break
                        except Exception:
                            continue

                items = [
                    {
                        "uf": (r.uf.strip() if getattr(r, 'uf', None) else r.uf) if getattr(r, 'uf', None) is not None else None,
                        "nome": None,
                        "distribuídas": int(r.distribuidas) if getattr(r, 'distribuidas', None) is not None else 0,
                        "aplicadas": 0,
                        "eficiência": 0.0,
                    }
                    for r in (agg_rows or [])
                ]
            except Exception:
                items = []
        else:
            # Converter objetos do banco para dicts
            items = [
                {
                    "uf": r.uf,
                    "nome": r.nome,
                    "distribuídas": r.distribuídas,
                    "aplicadas": r.aplicadas,
                    "eficiência": round(r.eficiência, 1),
                }
                for r in records
            ]
        
        return {"data": items, "success": True}
    except Exception:
        # Em caso de erro, não retornar mocks — retornar lista vazia
        items = []
        return {"data": items, "success": True}


# Healthcheck simples
@app.get("/health")
def health():
    return {"ok": True}


# Endpoint de diagnóstico temporário: retorna soma direta da tabela distribuicao_raw
@app.get("/debug/distrib_total")
def debug_distrib_total(ano: Optional[str] = Query(None), mes: Optional[str] = Query(None), db: Session = Depends(get_db)):
    try:
        ano_int = parse_int(ano)
        mes_int = parse_int(mes)
        where = []
        params = {}
        if ano_int is not None:
            where.append('"ANO" = :ano')
            params['ano'] = ano_int
        if mes_int is not None:
            where.append('"MES" = :mes')
            params['mes'] = mes_int

        sql = 'SELECT COALESCE(SUM("QTDE"),0) AS total FROM public.distribuicao_raw'
        if where:
            sql = f"{sql} WHERE {' AND '.join(where)}"

        r = db.execute(text(sql), params).first()
        total = int(r.total) if r and getattr(r, 'total', None) is not None else 0
        return {"data": {"total": total}, "success": True}
    except Exception as e:
        return {"data": {"total": 0}, "success": True, "message": str(e)}


@app.get("/debug/distrib_series")
def debug_distrib_series(ano: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Retorna série agregada por ano/mes diretamente do banco (debug)."""
    try:
        ano_int = parse_int(ano)
        params = {}
        where = []
        if ano_int is not None:
            where.append('"ANO" = :ano')
            params['ano'] = ano_int

        sql = 'SELECT "ANO" AS ano, "MES" AS mes, SUM(CAST("QTDE" AS numeric)) AS total FROM public.distribuicao_raw'
        if where:
            sql = f"{sql} WHERE {' AND '.join(where)}"
        sql = f"{sql} GROUP BY \"ANO\", \"MES\" ORDER BY \"ANO\", \"MES\""

        rows = db.execute(text(sql), params).all()
        data = [ { 'ano': int(r.ano), 'mês': int(r.mes), 'total': int(r.total) } for r in rows ]
        return { 'data': data, 'success': True }
    except Exception as e:
        return { 'data': [], 'success': True, 'message': str(e) }


