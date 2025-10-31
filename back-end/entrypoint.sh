#!/bin/sh
set -e

# Este entrypoint evita usar um fallback rígido para 'db:5432'.
# Força o uso de DATABASE_URL quando possível. Se DATABASE_URL estiver
# definida, não tentamos verificar um host local. Caso contrário, é
# necessário definir DB_HOST e DB_PORT explicitamente.

if [ -n "$DATABASE_URL" ]; then
  echo "DATABASE_URL detectada — pulando checagem de disponibilidade do Postgres."
else
  if [ -z "$DB_HOST" ] || [ -z "$DB_PORT" ]; then
    echo "ERRO: Nem DATABASE_URL nem DB_HOST/DB_PORT foram definidas. Defina DATABASE_URL ou DB_HOST e DB_PORT." >&2
    exit 1
  fi

  echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."
  # Loop until pg_isready reports the DB is accepting connections
  until pg_isready -h "$DB_HOST" -p "$DB_PORT" >/dev/null 2>&1; do
    printf '.'
    sleep 1
  done
fi

echo "Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
