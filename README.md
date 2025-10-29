# Welcome to your Lovable project

## Project info

**URL**: https://lovable.dev/projects/569bbfc9-db8f-4928-9796-eb92067bf8c8

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

Verificações pós-import:

```powershell
docker exec -i pg-temp psql -U postgres -d vacinacao -c "SELECT COUNT(*) FILTER (WHERE trim(sigla) <> '') AS preenchidas, COUNT(*) AS total FROM distribuicao;"
docker exec -i pg-temp psql -U postgres -d vacinacao -c "SELECT SUM(qtde) FROM distribuicao;"
```

Frontend — executar em dev

1) Instalar dependências:

```powershell
npm install
```

2) Rodar em desenvolvimento (Vite):

```powershell
npm run dev
```

Observação sobre variáveis do frontend
- O frontend lê a URL da API por `import.meta.env.VITE_API_URL`. Para desenvolvimento, crie um arquivo `.env.local` com a variável:

```
VITE_API_URL=http://localhost:8001
```

Backend — executar localmente (sem Docker)

Se preferir rodar o backend localmente (Python):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

Observações importantes antes do deploy

- Migrations: atualmente não há Alembic configurado. Para produção, adicione migrations ou um script idempotente para criar as tabelas.
- Dados: garanta que as colunas importantes (ex.: `sigla` em `distribuicao`) estejam corretas antes do deploy.
- Secrets: não commit `DB_PASSWORD` ou segredos. Use variáveis de ambiente/secret manager no serviço de hosting.
- Frontend: gere build (`npm run build`) e hospede o output estático (Netlify, Vercel ou Nginx). Configure `VITE_API_URL` no ambiente do host.
- Backend: pode ser deployado como container (Render, Fly, Railway) ou como serviço Uvicorn/Gunicorn em VM.

Checklist rápido para publicar uma versão web

1. Adicionar migrations / criar script `init_db` para criar tabelas.
2. Importar dados (ou garantir DB de produção com os dados corretos).
3. Configurar variáveis de ambiente no host (DB_URL, VITE_API_URL).
4. Gerar build do frontend e publicar (Vercel/Netlify).  
5. Publicar backend (container) e apontar frontend para a URL pública.

Se quiser, eu posso:
- adicionar um script de inicialização idempotente para criar tabelas básicas;
- preparar um `frontend/.env.example` e `backend/.env.example` com variáveis necessárias;
- ajudar a gerar o `docker-compose.prod.yml` ou um Dockerfile para o frontend.

Contato / ajuda
- Se quiser que eu atualize o `README` com instruções específicas do seu host (Vercel/Render/etc.) me diga qual serviço pretende usar.

---
Feito por você — instruções curtas e práticas para rodar e publicar.
