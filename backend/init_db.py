"""Cria as tabelas do banco e insere alguns dados de exemplo se estiver vazio.

Este script é executado pelo entrypoint do container para garantir que o backend
tenha tabelas mínimas para responder com dados reais (não apenas mock).
"""
from app.database import engine, Base, SessionLocal, EstadoSnapshot, TimePoint
from sqlalchemy.orm import Session
import random


def create_tables():
    Base.metadata.create_all(bind=engine)


def seed_estado_snapshot(db: Session):
    # Inserir alguns estados de exemplo
    samples = [
        ("SP", "São Paulo", 40000000, 35000000, 87.5),
        ("RJ", "Rio de Janeiro", 18000000, 15000000, 83.3),
        ("MG", "Minas Gerais", 20000000, 17000000, 85.0),
    ]
    objs = []
    for uf, nome, dist, aplic, ef in samples:
        objs.append(EstadoSnapshot(uf=uf, nome=nome, distribuídas=dist, aplicadas=aplic, eficiência=ef))
    db.add_all(objs)


def seed_timeseries(db: Session):
    # Inserir série mensal de exemplo para BR e SP
    objs = []
    for mes in range(1, 13):
        dist = int(15_000_000 + random.random() * 5_000_000)
        aplic = int(dist * (0.78 + random.random() * 0.12))
        ef = round((aplic / max(1, dist)) * 100, 1)
        esavi = int(1000 + random.random() * 500)
        objs.append(TimePoint(ano=2021, mês=mes, uf="BR", distribuídas=dist, aplicadas=aplic, eficiência=ef, esavi=esavi))

    # Também adicionar alguns pontos para SP
    for mes in range(1, 13):
        dist = int(4_000_000 + random.random() * 1_000_000)
        aplic = int(dist * (0.80 + random.random() * 0.10))
        ef = round((aplic / max(1, dist)) * 100, 1)
        esavi = int(200 + random.random() * 100)
        objs.append(TimePoint(ano=2021, mês=mes, uf="SP", distribuídas=dist, aplicadas=aplic, eficiência=ef, esavi=esavi))

    db.add_all(objs)


def main():
    print("Creating tables (if not exists)...")
    create_tables()

    db = SessionLocal()
    try:
        has_snapshot = db.query(EstadoSnapshot).first() is not None
        has_timeseries = db.query(TimePoint).first() is not None

        if not has_snapshot:
            print("Seeding estado_snapshot...")
            seed_estado_snapshot(db)
        else:
            print("estado_snapshot already has data, skipping seeding.")

        if not has_timeseries:
            print("Seeding timeseries (sample)...")
            seed_timeseries(db)
        else:
            print("timeseries already has data, skipping seeding.")

        db.commit()
        print("Tabelas verificadas/criadas com sucesso!")
    except Exception as e:
        print("Erro durante inicialização do DB:", e)
    finally:
        db.close()


if __name__ == '__main__':
    main()
