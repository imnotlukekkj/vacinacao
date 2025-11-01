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
        # DEBUG MODE: ignorar filtros de ano/mes/uf/fabricante e agregar
        # diretamente da tabela `distribuicao` para confirmar que a
        # conexão e agregação de dados funcionam.
        try:
            sql_distrib = [
                "SELECT COALESCE(SUM(qtde),0) AS total FROM distribuicao",
                'SELECT COALESCE(SUM("QTDE"),0) AS total FROM distribuicao',
                'SELECT COALESCE(SUM("TX_QTDE"),0) AS total FROM distribuicao',
                'SELECT COALESCE(SUM("QTDE"),0) AS total FROM public.distribuicao',
            ]
            r = try_scalar_query(db, sql_distrib)
            total_distribuidas = int(r.total) if r and getattr(r, 'total', None) is not None else 0
        except Exception:
            total_distribuidas = 0

        try:
            sql_aplic = [
                "SELECT COALESCE(SUM(aplicadas),0) AS total FROM distribuicao",
                'SELECT COALESCE(SUM("APLICADAS"),0) AS total FROM distribuicao',
                'SELECT COALESCE(SUM("TX_APLICADAS"),0) AS total FROM distribuicao',
                'SELECT COALESCE(SUM("APLICADAS"),0) AS total FROM public.distribuicao',
            ]
            r2 = try_scalar_query(db, sql_aplic)
            total_aplicadas = int(r2.total) if r2 and getattr(r2, 'total', None) is not None else 0
        except Exception:
            total_aplicadas = 0

        # Calcular eficiência (protegendo divisão por zero)
        eficiencia = round((total_aplicadas / total_distribuidas) * 100, 1) if total_distribuidas > 0 else 0.0

        # ESAVI: tentar agregar da tabela distribuicao (se existir) ou fallback para 0
        try:
            sql_esavi = [
                "SELECT COALESCE(SUM(esavi),0) AS total FROM distribuicao",
                'SELECT COALESCE(SUM("ESAVI"),0) AS total FROM distribuicao',
                'SELECT COALESCE(SUM("TX_ESAVI"),0) AS total FROM distribuicao',
                'SELECT COALESCE(SUM("ESAVI"),0) AS total FROM public.distribuicao',
            ]
            r3 = try_scalar_query(db, sql_esavi)
            esavi = int(r3.total) if r3 and getattr(r3, 'total', None) is not None else 0
        except Exception:
            esavi = 0

        overview = {
            "distribuídas": total_distribuidas,
            "aplicadas": total_aplicadas,
            "eficiência": eficiencia,
            "esavi": esavi,
        }

        return {"data": overview, "success": True}
    except Exception:
        # Em caso de erro de consulta, retornar zeros para não expor detalhes
        overview = {"distribuídas": 0, "aplicadas": 0, "eficiência": 0.0, "esavi": 0}
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
        ano_val = parse_int(ano) or 2021
        uf_val = uf if not is_unset(uf) else "BR"
        
        # Consultar timeseries do banco
        query = db.query(TimePoint).filter(
            TimePoint.ano == ano_val,
            TimePoint.uf == uf_val
        )
        
        if not is_unset(mes):
            m = parse_int(mes)
            if m:
                query = query.filter(TimePoint.mês == m)
        
        records = query.all()
        
        if not records:
            # Se não existirem registros na tabela timeseries, tentar agregar por
            # mês a partir da tabela `distribuicao` como fallback.
            try:
                sql_variants = [
                    "SELECT ano, mes AS mês, SUM(qtde) AS distribuídas FROM distribuicao GROUP BY ano, mes ORDER BY ano, mes",
                    'SELECT ano, mes AS mês, SUM("QTDE") AS distribuídas FROM distribuicao GROUP BY ano, mes ORDER BY ano, mes',
                    'SELECT ano, mes AS mês, SUM("TX_QTDE") AS distribuídas FROM distribuicao GROUP BY ano, mes ORDER BY ano, mes',
                    'SELECT ano, mes AS mês, SUM("QTDE") AS distribuídas FROM public.distribuicao GROUP BY ano, mes ORDER BY ano, mes',
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
                    "SELECT sigla AS uf, SUM(qtde) AS distribuídas FROM distribuicao GROUP BY sigla ORDER BY SUM(qtde) DESC",
                    'SELECT "TX_SIGLA" AS uf, SUM("QTDE") AS distribuídas FROM distribuicao GROUP BY "TX_SIGLA" ORDER BY SUM("QTDE") DESC',
                    'SELECT sigla AS uf, SUM("QTDE") AS distribuídas FROM public.distribuicao GROUP BY sigla ORDER BY SUM("QTDE") DESC'
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


