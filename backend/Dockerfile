FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do projeto
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
