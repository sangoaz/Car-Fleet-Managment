import sys
import uuid
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from datetime import date

from app.main import app
from app.database import get_session
from app.models import User, Company, Vehicule, Entretien
from app.deps.auth import get_current_user
from app.enums import UserRole, EntretienType
from app.security import hash_password
from app import models


TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    SQLModel.metadata.create_all(test_engine)


@pytest.fixture(scope="session")
def client():

    def get_test_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def company_db(session):
    company = Company(name="Test Company")
    session.add(company)
    session.commit()
    session.refresh(company)
    return company


@pytest.fixture
def vehicule_db(session, company_db):
    vehicule = Vehicule(
        plate="TEST-001",
        model="Test Model",
        km=1000,
        company_id=company_db.id,
    )
    session.add(vehicule)
    session.commit()
    session.refresh(vehicule)
    return vehicule


@pytest.fixture
def create_user(session):
    def _create_user(role, company_id=None):
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


@pytest.fixture
def auth_client(client):
    def _auth_client(user):

        def override_get_current_user():
            return user

        app.dependency_overrides[get_current_user] = override_get_current_user
        return client

    yield _auth_client

    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def admin_client(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    return auth_client(admin)


@pytest.fixture
def entretien_db(session, vehicule_db):
    entretien = Entretien(
        vehicule_id=vehicule_db.id,
        type=EntretienType.VIDANGE,
        date=date.today(),
        km=vehicule_db.km + 100,
        cost=100,
    )
    session.add(entretien)
    session.commit()
    session.refresh(entretien)
    return entretien
