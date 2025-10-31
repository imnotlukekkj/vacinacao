FROM python:3.12-slim

WORKDIR /app

# Instalar cliente do Postgres para usar pg_isready (espera o DB ficar pronto)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends postgresql-client \
	&& rm -rf /var/lib/apt/lists/*

# Instalar dependências do projeto
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Tornar entrypoint executável
RUN chmod +x ./entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
