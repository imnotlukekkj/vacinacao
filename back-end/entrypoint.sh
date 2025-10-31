#!/bin/sh
set -e

# Entrypoint simplificado: não espera pela disponibilidade do banco.
# A responsabilidade de garantir que o banco esteja pronto fica com o
# ambiente/infra (e.g. orquestrador, provisionamento ou administrador).

echo "Starting Gunicorn via python -m gunicorn..."
# Chamada final deve delegar ao Gunicorn usando o module runner do Python —
# formato recomendado para plataformas como Render. A variável ${PORT}
# é usada para binding no ambiente de execução.
exec python -m gunicorn app.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT}
