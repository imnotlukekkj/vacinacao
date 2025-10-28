from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# String de conexão PostgreSQL
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
