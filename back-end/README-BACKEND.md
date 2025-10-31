# Backend — Especificação e instruções rápidas (FastAPI)

Este README descreve a API esperada pelo frontend deste projeto (Vacinação Brasil Visualizer) e inclui exemplos e boas práticas para implementar o backend em Python (recomendado: FastAPI + Pydantic).

IMPORTANTE: o frontend foi desenvolvido para consumir http://localhost:8000 como `API_BASE_URL` (ver `src/lib/api.ts`). Ao instalar/rodar o backend, use essa porta ou ajuste `API_BASE_URL`.

---

## Contrato geral

- Formato de resposta padrão: ApiResponse<T>
  - { data: T, success: boolean, message?: string }
- Endpoints principais (GET):
  - GET /api/overview
  - GET /api/timeseries
  - GET /api/ranking/ufs
- Query params aceitos por todos os endpoints: `ano`, `mes`, `uf`, `fabricante` (todos opcionais).
- Campos JSON importantes (usar exatamente estes nomes):
  - `distribuídas` (number)
  - `aplicadas` (number)
  - `eficiência` (number) — percentual
  - `esavi` (number)
  - `mês` (number)
  - `ano`, `uf`, `nome` (strings/number conforme contexto)

---

## Observações importantes para integração

- Nomes com acentos: o frontend espera chaves JSON com acentos (ex.: "distribuídas"). Use Pydantic com `Field(alias=...)` ou construa o dicionário com as chaves exatas.
- Filtros como strings: o frontend pode enviar `mes=todos` ou `uf=todos`; trate isso como ausência de filtro.
- CORS: habilite CORS para `http://localhost:8080` durante o desenvolvimento.
- Respostas e status codes: devolva 200 com `{ success: true }` em respostas válidas; use 4xx/5xx para erros e inclua `message` explicando o problema.
- Tipos: envie números (int/float) para métricas — o frontend espera number (não string).

---

## Exemplos rápidos (FastAPI)

Arquivo exemplo `backend/app/main.py`:

```py
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:8080"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

class OverviewModel(BaseModel):
  distribuídas: int = Field(..., alias="distribuídas")
  aplicadas: int = Field(..., alias="aplicadas")
  eficiência: float = Field(..., alias="eficiência")
  esavi: int = Field(..., alias="esavi")

class ApiResponse(BaseModel):
  data: Optional[dict]
  success: bool
  message: Optional[str] = None

@app.get("/api/overview", response_model=ApiResponse)
def get_overview(
  ano: Optional[str] = Query(None),
  mes: Optional[str] = Query(None),
  uf: Optional[str] = Query(None),
  fabricante: Optional[str] = Query(None),
):
  # parse/validate filters
  # fetch data from DB or generate mock
  overview = {
    "distribuídas": 1000000,
    "aplicadas": 900000,
    "eficiência": 90.0,
    "esavi": 123,
  }
  return {"data": overview, "success": True}

# timeseries example
class TimePoint(BaseModel):
  ano: int
  mês: int = Field(..., alias="mês")
  uf: str
  distribuídas: int = Field(..., alias="distribuídas")
  aplicadas: int = Field(..., alias="aplicadas")
  eficiência: float = Field(..., alias="eficiência")
  esavi: int = Field(..., alias="esavi")

class ApiListResponse(BaseModel):
  data: List[TimePoint]
  success: bool
  message: Optional[str] = None

@app.get("/api/timeseries", response_model=ApiListResponse)
def get_timeseries(...):
  sample = [
    {"ano": 2021, "mês": 1, "uf": "BR", "distribuídas": 1000, "aplicadas": 900, "eficiência": 90.0, "esavi": 1},
  ]
  return {"data": sample, "success": True}
```

### Como rodar localmente (exemplo)

1. Crie um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
pip install fastapi uvicorn pydantic
```

2. Rodar o servidor:

```powershell
uvicorn app.main:app --reload --port 8000
```

3. Teste com o curl:

```powershell
curl "http://localhost:8000/api/overview?ano=2024&mes=01&uf=SP"
```

---

## Checklist final antes de integrar

- [ ] Endpoints funcionando e retornando JSON no formato ApiResponse
- [ ] CORS habilitado para o domínio do frontend
- [ ] Nomes de campos com acento corretos
- [ ] Filtragem aceita `todos` e valores ausentes
- [ ] Teste com curl/Postman e validação com o frontend