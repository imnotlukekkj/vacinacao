#!/bin/sh
set -e

: "${DB_HOST:=db}"
: "${DB_PORT:=5432}"

echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."
# Loop until pg_isready reports the DB is accepting connections
until pg_isready -h "$DB_HOST" -p "$DB_PORT" >/dev/null 2>&1; do
  printf '.'
  sleep 1
done

echo "Postgres is ready, starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
