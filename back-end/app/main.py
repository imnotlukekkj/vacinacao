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

            where_clauses = []
            params = {}
            if ano_int is not None:
                where_clauses.append('"ano" = :ano')
                params['ano'] = ano_int
            if mes_int is not None:
                where_clauses.append('"mes" = :mes')
                params['mes'] = mes_int

            base_sql = 'SELECT COALESCE(SUM(CAST("QTDE" AS numeric)),0) AS total FROM distribuicao_raw'
            if where_clauses:
                base_sql = f"{base_sql} WHERE {' AND '.join(where_clauses)}"

            # Tentar executar com e sem schema qualificator se necessário
            sql_variants = [
                base_sql,
                base_sql.replace('distribuicao_raw', 'public.distribuicao_raw'),
            ]

            r = None
            for sql in sql_variants:
                try:
                    r = db.execute(text(sql), params).first()
                    if r is not None:
                        break
                except Exception:
                    continue

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
    db: Session = Depends(get_db)
):
    try:
        ano_val = parse_int(ano)
        # Não aplicar filtro de ano/uf/mes automaticamente — somente se fornecidos
        query = db.query(TimePoint)

        if ano_val is not None:
            query = query.filter(TimePoint.ano == ano_val)

        if not is_unset(uf):
            query = query.filter(TimePoint.uf == uf)

        if not is_unset(mes):
            m = parse_int(mes)
            if m is not None:
                query = query.filter(TimePoint.mês == m)
        
        records = query.all()
        
        if not records:
            # Se não existirem registros na tabela timeseries, tentar agregar por
            # mês a partir da tabela `distribuicao` como fallback.
            try:
                sql_variants = [
                    "SELECT ano, mes AS mês, SUM(CAST(qtde AS numeric)) AS distribuídas FROM distribuicao_raw GROUP BY ano, mes ORDER BY ano, mes",
                    'SELECT ano, mes AS mês, SUM(CAST("QTDE" AS numeric)) AS distribuídas FROM distribuicao_raw GROUP BY ano, mes ORDER BY ano, mes',
                    'SELECT ano, mes AS mês, SUM(CAST("TX_QTDE" AS numeric)) AS distribuídas FROM distribuicao_raw GROUP BY ano, mes ORDER BY ano, mes',
                    'SELECT ano, mes AS mês, SUM(CAST("QTDE" AS numeric)) AS distribuídas FROM public.distribuicao_raw GROUP BY ano, mes ORDER BY ano, mes',
                ]
                agg = try_query_all(db, sql_variants) or []
                series = [
                    {
                        "ano": int(r.ano) if getattr(r, 'ano', None) is not None else 2021,
                        "mês": int(r.mês),
                        "uf": "BR",
                        "distribuídas": int(r.distribuídas),
                        "aplicadas": 0,
                        "eficiência": 0.0,
                        "esavi": 0,
                    }
                    for r in agg
                ]
                if not is_unset(mes):
                    m = parse_int(mes)
                    if m:
                        series = [p for p in series if p["mês"] == m]
            except Exception:
                series = []
        else:
            # Converter objetos do banco para dicts
            series = [
                {
                    "ano": r.ano,
                    "mês": r.mês,
                    "uf": r.uf,
                    "distribuídas": r.distribuídas,
                    "aplicadas": r.aplicadas,
                    "eficiência": round(r.eficiência, 1),
                    "esavi": r.esavi,
                }
                for r in records
            ]
        
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
                sql_variants = [
                    "SELECT sigla AS uf, SUM(CAST(qtde AS numeric)) AS distribuídas FROM distribuicao_raw GROUP BY sigla ORDER BY SUM(CAST(qtde AS numeric)) DESC",
                    'SELECT "TX_SIGLA" AS uf, SUM(CAST("QTDE" AS numeric)) AS distribuídas FROM distribuicao_raw GROUP BY "TX_SIGLA" ORDER BY SUM(CAST("QTDE" AS numeric)) DESC',
                    'SELECT sigla AS uf, SUM(CAST("QTDE" AS numeric)) AS distribuídas FROM public.distribuicao_raw GROUP BY sigla ORDER BY SUM(CAST("QTDE" AS numeric)) DESC'
                ]
                agg = try_query_all(db, sql_variants) or []
                items = [
                    {
                        "uf": (r.uf.strip() if getattr(r, 'uf', None) else r.uf) if getattr(r, 'uf', None) is not None else None,
                        "nome": None,
                        "distribuídas": int(r.distribuídas),
                        "aplicadas": 0,
                        "eficiência": 0.0,
                    }
                    for r in agg
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


