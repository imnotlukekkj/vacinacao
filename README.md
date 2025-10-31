# Projeto Vacinação

Breve: frontend (Vite + React + TypeScript) e backend (FastAPI) para visualização de dados de vacinação.

Importante — estado atual do código
- O backend está em `back-end/` (FastAPI, Python).
- A aplicação exige explicitamente a variável de ambiente `DATABASE_URL` — não há valores padrão embutidos.
- Há um script Windows PowerShell para auxiliar a importação de dumps: `scripts/import_to_supabase.ps1`.

Requisitos
- Node.js (LTS) — para o frontend
- Python 3.10+ — para o backend
- Cliente PostgreSQL (`psql`/`pg_restore`) opcional (útil para import manual)

Como rodar localmente

1) Backend

- Crie um arquivo `back-end/.env` contendo apenas a chave `DATABASE_URL` (não comite esse arquivo):

```
DATABASE_URL=postgresql://<user>:<pass>@<host>:5432/<db>?sslmode=require
```

- No PowerShell (a partir da raiz do projeto):

```powershell
cd .\back-end
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# iniciar o backend (ajuste porta se precisar)
uvicorn app.main:app --reload --port 8002
```

Observações:
- Se `DATABASE_URL` não estiver definida, a aplicação aborta com uma mensagem clara — garanta que a variável esteja presente antes de iniciar.
- Variáveis opcionais: `DB_POOL_SIZE` e `DB_MAX_OVERFLOW` (ajustam pool do SQLAlchemy).

2) Frontend

- Na raiz do projeto:

```powershell
npm install
# definir a URL da API para desenvolvimento
$env:VITE_API_URL = 'http://localhost:8002'
npm run dev
```

Ou crie um arquivo `.env.local` no root com:

```
VITE_API_URL=http://localhost:8002
```

Importar um dump (opções)

- Para Supabase/Postgres gerenciado, há um script que tenta conectar com `psql` e importar:

```powershell
.\scripts\import_to_supabase.ps1 -FilePath .\dados.sql
```

- Alternativamente, use o painel do Supabase (Backups / SQL Editor) para uploads grandes.

Checks rápidos pós-import

```powershell
psql "${DATABASE_URL}" -c "SELECT COUNT(*) FROM public.distribuicao;"
psql "${DATABASE_URL}" -c "SELECT SUM(qtde) FROM public.distribuicao;"
```

Segurança / Git

- Nunca comite `back-end/.env` ou `DATABASE_URL` nas ferramentas de versionamento. `.gitignore` já contém entradas para `.env`.
- Verifique `git status` antes de `git add`/`git commit` para evitar subir segredos.

Notas de compatibilidade

- O backend foi adaptado para tolerar variações no esquema das colunas (ex.: nomes diferentes em dumps), mas depende da `DATABASE_URL` correta.
- Pydantic foi fixado para a versão compatível (1.10.x) no `back-end/requirements.txt`.

Problemas comuns

- Erro ao iniciar relacionado a `DATABASE_URL` ausente: verifique `back-end/.env` ou defina no ambiente.
- Erro de import/psql: confirme que `psql` está disponível no PATH e que a string de conexão usa `sslmode=require` quando necessário.

Precisa que eu:
- gere um `back-end/.env.example` sem segredos,
- atualize instruções adicionais (CI/deploy), ou
- faça o commit das mudanças feitas no código (README, back-end/app/database.py, scripts)?

Feito por você — README curto e compatível com o estado atual do repositório.
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
