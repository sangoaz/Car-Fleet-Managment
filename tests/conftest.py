import sys
from pathlib import Path

# Ajouter la racine du projet au PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_session
from app import models  # ⚠️ CRUCIAL : charge Vehicule / Entretien

# Engine SQLite de test (isolé)
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # 🔥 CRITIQUE
    echo=False,
)


@pytest.fixture(scope="session")
def client():
    # ✅ créer les tables sur SQLite
    SQLModel.metadata.create_all(test_engine)

    def get_test_session():
        with Session(test_engine) as session:
            yield session

    # 🔁 override de la dépendance FastAPI
    app.dependency_overrides[get_session] = get_test_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    # DB SQLite isolée PAR TEST
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
