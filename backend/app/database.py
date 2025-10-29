from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
from pathlib import Path

# Tentar carregar um .env localizado na pasta `backend/` relativa a este arquivo.
# Isso evita um problema conhecido em que `find_dotenv()` falha quando o código
# é executado via `python -c` ou here-doc (stack frame inesperado).
try:
    base_dir = Path(__file__).resolve().parents[1]
    dotenv_path = base_dir / '.env'
    if dotenv_path.exists():
        load_dotenv(dotenv_path=str(dotenv_path))
    else:
        # Fallback para comportamento padrão (procura em parents)
        load_dotenv()
except AssertionError:
    # Proteção extra: se find_dotenv levantar AssertionError em contextos
    # interativos, chamar load_dotenv() sem find_dotenv.
    load_dotenv()

# Construir DATABASE_URL a partir de variáveis DB_* (se fornecidas) ou usar
# a variável DATABASE_URL diretamente. Isso permite manter seu .env atual
# com DB_HOST/DB_USER/... sem precisar duplicar DATABASE_URL.
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if DB_USER and DB_PASSWORD and DB_HOST and DB_NAME:
    # Escapar a senha (caso contenha caracteres especiais)
    password_esc = quote_plus(DB_PASSWORD)
    DATABASE_URL = f"postgresql://{DB_USER}:{password_esc}@{DB_HOST}:{DB_PORT or '5432'}/{DB_NAME}"
else:
    # Fallback para a variável única DATABASE_URL (opção compatível)
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/vacina_brasil"
    )

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Models SQLAlchemy baseados nos tipos esperados

class Estado(Base):
    __tablename__ = "estados"

    uf = Column(String(2), primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    populacao = Column(Integer)


class TimePoint(Base):
    __tablename__ = "timeseries"

    id = Column(Integer, primary_key=True, index=True)
    ano = Column(Integer, nullable=False)
    mês = Column(Integer, nullable=False)
    uf = Column(String(2), nullable=False)
    distribuídas = Column(Integer, default=0)
    aplicadas = Column(Integer, default=0)
    eficiência = Column(Float, default=0.0)
    esavi = Column(Integer, default=0)


class EstadoSnapshot(Base):
    __tablename__ = "estado_snapshot"

    uf = Column(String(2), primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    distribuídas = Column(Integer, default=0)
    aplicadas = Column(Integer, default=0)
    eficiência = Column(Float, default=0.0)


# Helper para pegar a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
