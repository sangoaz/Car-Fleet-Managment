import sys
import uuid
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
from app.models import User
from app.deps.auth import get_current_user
from app.enums import UserRole
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
    with Session(test_engine) as session:
        yield session


# Creation d'une entreprise fictive
@pytest.fixture
def company(client):
    response = client.post(
        "/companies",
        json={"name": "Test Company"},
    )
    assert response.status_code == 201
    return response.json()


# Creation d'un véhicule fictif dans une company
@pytest.fixture
def create_vehicule(client, company):
    def _create_vehicule(**overrides):
        data = {
            "plate": "TEST-001",
            "model": "Test Model",
            "km": 1000,
            "company_id": company["id"],  # 🔴 LA LIGNE CRITIQUE
        }
        data.update(overrides)

        response = client.post("/vehicules", json=data)
        assert response.status_code == 201
        return response.json()

    return _create_vehicule


# Création d'un user fictif
@pytest.fixture
def create_user(session):
    def _create_user(role, company_id=1):
        user = User(
            email=f"{role.value}_{uuid.uuid4()}@test.com",
            password_hash="fakehashed",
            role=role,
            company_id=company_id,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    return _create_user


# Authentification fictive d'un utilisateur
@pytest.fixture
def auth_client(client):
    def _auth_client(user):

        def override_get_current_user():
            return user

        app.dependency_overrides[get_current_user] = override_get_current_user
        return client

    yield _auth_client

    app.dependency_overrides.pop(get_current_user, None)
