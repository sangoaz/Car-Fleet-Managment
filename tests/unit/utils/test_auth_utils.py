import pytest
from fastapi import HTTPException, status

from app import security
from app.enums import UserRole
from app.models import User, Company
from app.utils.auth import invalid_credentials, authenticate_user


def test_invalid_credentials_raises_http_exception():
    with pytest.raises(HTTPException) as exc:
        invalid_credentials()

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Invalid credentials"


def test_authenticate_user_success(session, create_user, company_db, monkeypatch):
    user = create_user(UserRole.MANAGER, company_id=company_db.id)

    monkeypatch.setattr("app.utils.auth.verify_password", lambda p, h: True)

    result = authenticate_user(session, user.email, "password")

    assert result is not None
    assert result.id == user.id


def test_authenticate_user_user_not_found(session):
    result = authenticate_user(session, "unknown@test.com", "password")

    assert result is None


def test_authenticate_user_wrong_password(
    session, create_user, company_db, monkeypatch
):
    user = create_user(UserRole.MANAGER, company_id=company_db.id)

    monkeypatch.setattr("app.utils.auth.verify_password", lambda p, h: False)

    result = authenticate_user(session, user.email, "wrong")

    assert result is None


def test_authenticate_user_inactive_user(session, monkeypatch):
    user = User(
        email="test1@test.com",
        password_hash="fakehash",
        is_active=False,
        company_id=None,
    )
    session.add(user)
    session.commit()

    monkeypatch.setattr("app.utils.auth.verify_password", lambda p, h: True)

    result = authenticate_user(session, "test1@test.com", "password")

    assert result is None


def test_authenticate_user_inactive_company(session, monkeypatch):
    company = Company(name="Test", is_active=False)
    session.add(company)
    session.commit()

    user = User(
        email="test2@test.com",
        password_hash="fakehash",
        is_active=True,
        company_id=company.id,
    )
    session.add(user)
    session.commit()

    monkeypatch.setattr("app.utils.auth.verify_password", lambda p, h: True)

    result = authenticate_user(session, "test2@test.com", "password")

    assert result is None


def test_authenticate_user_company_not_found(session, monkeypatch):
    user = User(
        email="test3@test.com",
        password_hash="fakehash",
        is_active=True,
        company_id=999,  # inexistante
    )
    session.add(user)
    session.commit()

    monkeypatch.setattr("app.utils.auth.verify_password", lambda p, h: True)

    result = authenticate_user(session, "test3@test.com", "password")

    assert result is None


def test_authenticate_user_without_company(session, monkeypatch):
    user = User(
        email="test4@test.com",
        password_hash="fakehash",
        is_active=True,
        company_id=None,
    )
    session.add(user)
    session.commit()

    monkeypatch.setattr("app.utils.auth.verify_password", lambda p, h: True)

    result = authenticate_user(session, "test4@test.com", "password")

    assert result is not None
