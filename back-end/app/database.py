from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from dotenv import load_dotenv
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

# Use exclusivamente a variável de ambiente DATABASE_URL.
# Não aceitar valores padrão embutidos nem construir a URL a partir de
# DB_HOST/DB_USER/etc. Isso evita vazamento de defaults e garante que o
# deploy/ambiente defina explicitamente a string de conexão.
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL não encontrada. Configure a variável de ambiente DATABASE_URL "
        "apontando para seu Postgres (ex.: postgresql://user:pass@host:5432/db?sslmode=require) "
        "ou crie um arquivo .env em 'back-end/.env' com a chave DATABASE_URL."
    )

# Ler ajustes de pool (opcionais) — mantém defaults razoáveis quando ausentes
DB_POOL_SIZE = os.getenv("DB_POOL_SIZE")
DB_MAX_OVERFLOW = os.getenv("DB_MAX_OVERFLOW")

# Pool sizing: usar variáveis de ambiente quando fornecidas, senão defaults
try:
    pool_size = int(DB_POOL_SIZE) if DB_POOL_SIZE is not None else 5
except ValueError:
    pool_size = 5

try:
    max_overflow = int(DB_MAX_OVERFLOW) if DB_MAX_OVERFLOW is not None else 10
except ValueError:
    max_overflow = 10

# Habilitar pool_pre_ping para evitar erros com conexões ociosas em servidores gerenciados
engine = create_engine(
    DATABASE_URL,
    pool_size=pool_size,
    max_overflow=max_overflow,
    pool_pre_ping=True,
)
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
def get_db() -> Generator[Session, None, None]:
    """Dependency generator for FastAPI endpoints.

    Creates a new SQLAlchemy Session for each request and ensures it is
    closed after use. The Engine and SessionLocal factory live at module
    level (they do not open a connection until a Session is created).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
