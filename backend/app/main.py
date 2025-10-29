from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from .database import get_db, TimePoint, EstadoSnapshot
import random


app = FastAPI(title="Vacina Brasil API", version="1.0.0")

# CORS para desenvolvimento (Vite normalmente roda em 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
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


# ====== Utilitários de geração de dados mock ======

STATES = [
    {"uf": "SP", "nome": "São Paulo", "populacao": 46649132},
    {"uf": "RJ", "nome": "Rio de Janeiro", "populacao": 17463349},
    {"uf": "MG", "nome": "Minas Gerais", "populacao": 21411923},
    {"uf": "BA", "nome": "Bahia", "populacao": 14985284},
    {"uf": "PR", "nome": "Paraná", "populacao": 11597484},
    {"uf": "RS", "nome": "Rio Grande do Sul", "populacao": 11466630},
    {"uf": "PE", "nome": "Pernambuco", "populacao": 9674793},
    {"uf": "CE", "nome": "Ceará", "populacao": 9240580},
    {"uf": "PA", "nome": "Pará", "populacao": 8777124},
    {"uf": "SC", "nome": "Santa Catarina", "populacao": 7338473},
]


FABRICANTES = [
    {"nome": "Pfizer/BioNTech", "id": "pfizer"},
    {"nome": "AstraZeneca", "id": "astrazeneca"},
    {"nome": "CoronaVac", "id": "coronavac"},
    {"nome": "Janssen", "id": "janssen"},
]


def parse_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except Exception:
        return None


def is_unset(filter_value: Optional[str]) -> bool:
    if filter_value is None:
        return True
    v = filter_value.strip().lower()
    return v in ("", "todos", "all", "none", "null")


def generate_state_snapshot() -> List[Dict[str, Any]]:
    items = []
    for s in STATES:
        distribuidas = int(s["populacao"] * (0.8 + random.random() * 0.4))
        aplicadas = int(distribuidas * (0.75 + random.random() * 0.15))
        eficiencia = round((aplicadas / max(1, distribuidas)) * 100, 1)
        items.append(
            {
                "uf": s["uf"],
                "nome": s["nome"],
                "distribuídas": distribuidas,
                "aplicadas": aplicadas,
                "eficiência": eficiencia,
            }
        )
    items.sort(key=lambda x: x["eficiência"], reverse=True)
    return items


def generate_monthly_timeseries(ano: int, uf: str) -> List[Dict[str, Any]]:
    series = []
    for mes in range(1, 13):
        distribuidas = int(15_000_000 + random.random() * 5_000_000)
        aplicadas = int(12_000_000 + random.random() * 4_000_000)
        eficiencia = round((aplicadas / max(1, distribuidas)) * 100, 1)
        esavi = int(1_000 + random.random() * 500)
        series.append(
            {
                "ano": ano,
                "mês": mes,
                "uf": uf,
                "distribuídas": distribuidas,
                "aplicadas": aplicadas,
                "eficiência": eficiencia,
                "esavi": esavi,
            }
        )
    return series


def apply_filters_generic(items: List[Dict[str, Any]], uf: Optional[str]) -> List[Dict[str, Any]]:
    if not is_unset(uf):
        return [x for x in items if x.get("uf") == uf]
    return items


# ====== Endpoints ======

@app.get("/api/overview", response_model=ApiResponse)
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
        
        # Preferir agregar diretamente da tabela `distribuicao` se ela existir e
        # tiver dados — isso garante que o frontend mostre números reais.
        try:
            r = db.execute(text("SELECT COALESCE(SUM(qtde),0) AS total FROM distribuicao")).first()
            distrib_sum = int(r.total) if r and getattr(r, 'total', None) is not None else 0
        except Exception:
            distrib_sum = 0

        if distrib_sum > 0:
            total_distribuidas = distrib_sum
            total_aplicadas = 0
            eficiencia = 0.0
            esavi = 0
        elif not state_items:
            # Sem dados no banco -> retornar valores vazios/zeros conforme solicitado
            total_distribuidas = 0
            total_aplicadas = 0
            eficiencia = 0.0
            esavi = 0
        else:
            # Calcular totais a partir dos dados do banco (estado snapshot)
            total_distribuidas = sum(s.distribuídas for s in state_items) or 1
            total_aplicadas = sum(s.aplicadas for s in state_items)
            eficiencia = round((total_aplicadas / total_distribuidas) * 100, 1)
            # Buscar ESAVI total do banco se disponível
            esavi_query = db.query(func.sum(TimePoint.esavi)).scalar()
            esavi = int(esavi_query) if esavi_query else 0
        
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


@app.get("/api/timeseries", response_model=ApiListResponse)
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
                agg = db.execute(text(
                    "SELECT ano, mes AS mês, SUM(qtde) AS distribuídas FROM distribuicao GROUP BY ano, mes ORDER BY ano, mes"
                )).all()
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


@app.get("/api/ranking/ufs", response_model=ApiListResponse)
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
                agg = db.execute(text(
                    "SELECT sigla AS uf, SUM(qtde) AS distribuídas FROM distribuicao GROUP BY sigla ORDER BY SUM(qtde) DESC"
                )).all()
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
        # Fallback em caso de erro
        items = generate_state_snapshot()
        if not is_unset(uf):
            items = [x for x in items if x["uf"] == uf]
        return {"data": items, "success": True}


# Healthcheck simples
@app.get("/health")
def health():
    return {"ok": True}


