# Bem-vindo ao projeto de Vacinação

## Project info

# Vacinação — app de visualização

Este repositório contém o frontend (React + Vite + TypeScript) e o backend (FastAPI) usados para visualizar dados de vacinação.

Objetivo deste README
- Consolidar as instruções para rodar localmente e para deploy simples.
- Explicar como importar um dump `.sql` para o banco (caso você receba um arquivo de dados).

Estrutura do repositório
- `src/` — frontend (Vite + React + TypeScript)
- `backend/` — aplicação FastAPI (Python)
- `docker-compose.yml` — define serviços para desenvolvimento (Postgres + backend)

Pré-requisitos
- Docker Desktop (Windows/Mac) ou Docker Engine + docker-compose
- Node.js (LTS) se você quiser rodar o frontend localmente com `npm run dev`

Rodando localmente (modo recomendado: Docker Compose)

1) Subir os serviços:

```powershell
# na raiz do projeto
docker compose up --build -d
```

Isso cria um container Postgres e o backend. O backend expõe a porta `8001` por padrão no `docker-compose.yml`.

2) Verificar health do backend:

```powershell
curl http://localhost:8001/health
# ou no browser: http://localhost:8001/health
```

Importar um arquivo `.sql` (dump) para o Postgres em container

Faça backup antes de importar (recomendado):

```powershell
docker exec -i pg-temp pg_dump -U postgres -d vacinacao > .\vacinacao_backup_before_import.sql
```

Importar um SQL textual (ex.: `dados.sql`):

```powershell
# copiar para o container
docker cp .\dados.sql pg-temp:/tmp/dados.sql
docker exec -i pg-temp psql -U postgres -d vacinacao -f /tmp/dados.sql

# ou stream via stdin
Get-Content .\dados.sql -Raw | docker exec -i pg-temp psql -U postgres -d vacinacao -f -
```
# Bem-vindo ao projeto de Vacinação

Este repositório contém o frontend (React + Vite + TypeScript) e o backend (FastAPI) usados para visualizar dados de vacinação.

Resumo rápido
- Frontend: Vite + React + TypeScript em `src/`
- Backend: FastAPI em `backend/`
- Banco de dados: usar Supabase (Postgres) — o projeto está preparado para se conectar via `DATABASE_URL` em `backend/.env`

Pré-requisitos para desenvolvimento
- Node.js (LTS) — para rodar o frontend
- Python 3.10+ — para rodar o backend localmente
- Cliente PostgreSQL (`psql`/`pg_restore`) opcional para importar dumps

Configuração local (usar Supabase para o banco)
1) Criar um projeto no Supabase e obter a `DATABASE_URL` (idealmente a string do Pooler se disponível).
2) Colocar a string em `backend/.env`:

```
DATABASE_URL=postgresql://<user>:<pass>@<host>:5432/<db>?sslmode=require
```

3) Backend — criar e ativar venv e instalar dependências:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

4) Iniciar o backend:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

5) Frontend — instalar e rodar (em outro terminal):

```powershell
# na raiz do projeto
npm install
npm run dev
```

Observações sobre variáveis do frontend
- O frontend lê a URL da API por `import.meta.env.VITE_API_URL`. Para desenvolvimento, crie um arquivo `.env.local` com a variável:

```
VITE_API_URL=http://localhost:8002
```

Importar um dump para o Supabase
- Para arquivos grandes, prefira o painel do Supabase (SQL Editor / Backups).
- Há um script pronto para ajudar a importar localmente via `psql`/`pg_restore`:

```powershell
# da raiz do projeto
.\scripts\import_to_supabase.ps1 -FilePath .\dados.sql
```

Ou manualmente com `psql`:

```powershell
psql "postgresql://<user>:<pass>@<host>:5432/<db>?sslmode=require" -f .\dados.sql
```

Verificações pós-import (exemplo):

```powershell
psql "postgresql://<user>:<pass>@<host>:5432/<db>?sslmode=require" -c "SELECT COUNT(*) FROM public.distribuicao;"
psql "postgresql://<user>:<pass>@<host>:5432/<db>?sslmode=require" -c "SELECT SUM(qtde) FROM public.distribuicao;"
```

Produção
- Não commit `DATABASE_URL` ou segredos. Use variáveis de ambiente/secret manager no host.
- Ajuste `DB_POOL_SIZE` e `DB_MAX_OVERFLOW` em `backend/.env` se necessário.
- Para deploy do backend, publique um serviço que execute Uvicorn/Gunicorn apontando `DATABASE_URL` para seu Supabase.

Ajuda
Se quiser, eu posso:
- criar `backend/.env.example`,
- adicionar um endpoint de diagnóstico que tenta as variantes de consulta e retorna qual funcionou,
- preparar scripts de deploy/CI que leiam a `DATABASE_URL` de um secret manager.

---
Feito por você — instruções curtas e práticas para rodar e publicar.
