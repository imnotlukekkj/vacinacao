#!/bin/sh
set -e

# Entrypoint simplificado: não espera pela disponibilidade do banco.
# A responsabilidade de garantir que o banco esteja pronto fica com o
# ambiente/infra (e.g. orquestrador, provisionamento ou administrador).

echo "Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
