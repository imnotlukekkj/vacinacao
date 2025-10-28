# Backend - Vacina Brasil Visualizer API

API FastAPI para o sistema de visualização de dados de vacinação contra COVID-19 no Brasil.

## 📋 Pré-requisitos

- Python 3.9+
- PostgreSQL 12+

## 🚀 Instalação e Configuração

### 1. Criar e ativar ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

### 2. Instalar dependências

```powershell
pip install -r requirements.txt
```

### 3. Configurar banco de dados PostgreSQL

Crie um arquivo `.env` na pasta `backend`:

```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/vacina_brasil
```

**Exemplo:**
```env
DATABASE_URL=postgresql://postgres:minhasenha@localhost:5432/vacina_brasil
```

### 4. Criar banco de dados no PostgreSQL

Execute no PostgreSQL:

```sql
CREATE DATABASE vacina_brasil;
```

### 5. Criar as tabelas no banco

Execute o script SQL abaixo no seu banco de dados:

```sql
-- Tabela para dados de séries temporais
CREATE TABLE timeseries (
    id SERIAL PRIMARY KEY,
    ano INTEGER NOT NULL,
    mês INTEGER NOT NULL,
    uf VARCHAR(2) NOT NULL,
    distribuídas INTEGER DEFAULT 0,
    aplicadas INTEGER DEFAULT 0,
    eficiência DECIMAL(10,2) DEFAULT 0.0,
    esavi INTEGER DEFAULT 0,
    CONSTRAINT unique_timeseries UNIQUE (ano, mês, uf)
);

-- Tabela para snapshot dos estados
CREATE TABLE estado_snapshot (
    uf VARCHAR(2) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    distribuídas INTEGER DEFAULT 0,
    aplicadas INTEGER DEFAULT 0,
    eficiência DECIMAL(10,2) DEFAULT 0.0
);

-- Índices para melhor performance
CREATE INDEX idx_timeseries_ano_mes ON timeseries(ano, mês);
CREATE INDEX idx_timeseries_uf ON timeseries(uf);
CREATE INDEX idx_estado_snapshot_eficiencia ON estado_snapshot(eficiência DESC);
```

### 6. Inserir dados de exemplo (opcional)

```sql
-- Dados de exemplo para séries temporais
INSERT INTO timeseries (ano, mês, uf, distribuídas, aplicadas, eficiência, esavi) VALUES
(2021, 1, 'BR', 15000000, 12000000, 80.0, 1200),
(2021, 2, 'BR', 18000000, 15000000, 83.3, 1500),
(2021, 3, 'BR', 20000000, 17000000, 85.0, 1700);

-- Dados de exemplo para estados
INSERT INTO estado_snapshot (uf, nome, distribuídas, aplicadas, eficiência θηVALUES
('SP', 'São Paulo', 40000000, 35000000, 87.5),
('RJ', 'Rio de Janeiro', 18000000, 15000000, 83.3),
('MG', 'Minas Gerais', 20000000, 17000000, 85.0);
```

## ▶️ Executando o Servidor

```powershell
uvicorn app.main:app --reload --port 8000
```

O servidor estará disponível em: `http://localhost:8000`

## 📚 Documentação da API

Acesse a documentação interativa em:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔌 Endpoints

### GET /api/overview
Retorna dados de overview (KPIs gerais).

**Query Parameters:**
- `ano` (opcional): Ano para filtrar
- `mes` (opcional): Mês para filtrar
- `uf` (opcional): UF para filtrar (use "todos" ou deixe vazio para todos)
- `fabricante` (opcional): Fabricante para filtrar

**Exemplo:**
```powershell
curl "http://localhost:8000/api/overview?uf=todos"
```

### GET /api/timeseries
Retorna série temporal de dados mensais.

**Query Parameters:**
- `ano` (opcional): Ano (default: 2021)
- `mes` (opcional): Mês para filtrar
- `uf` (opcional): UF (default: BR)
- `fabricante` (opcional): Fabricante

**Exemplo:**
```powershell
curl "http://localhost:8000/api/timeseries?ano=2021&uf=SP"
```

### GET /api/ranking/ufs
Retorna ranking de estados por eficiência.

**Query Parameters:**
- `ano` (opcional)
- `mes` (opcional)
- `uf` (opcional): Filtrar por UF específica
- `fabricante` (opcional)

**Exemplo:**
```powershell
curl "http://localhost:8000/api/ranking/ufs"
```

### GET /health
Healthcheck do servidor.

## 🔄 Fallback para Mock Data

Se o banco de dados não estiver disponível ou vazio, a API automaticamente retorna dados mock para garantir que o frontend continue funcionando.

## 🛠️ Estrutura do Projeto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # Aplicação FastAPI principal
│   └── database.py      # Configuração e models do banco
├── requirements.txt
└── README.md
```

## 📝 Notas

- A API usa SQLAlchemy para ORM
- Todas as rotas aceitam filtros opcionais
- Os dados são retornados no formato `ApiResponse<T>` esperado pelo frontend
- Campos JSON mantêm acentos conforme esperado pelo frontend (`distribuídas`, `aplicadas`, `eficiência`, `mês`)
