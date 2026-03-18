import pytest
from fastapi import HTTPException

from app.deps.auth import get_current_user
from app.security import create_access_token
from app.enums import UserRole


# Token invalide
def test_get_current_user_invalid_token(session):
    with pytest.raises(HTTPException) as exc:
        get_current_user(token="invalid", session=session)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid or expired token"


# User introuvable
def test_get_current_user_user_not_found(session):
    token = create_access_token({"sub": "9999"})

    with pytest.raises(HTTPException) as exc:
        get_current_user(token=token, session=session)

    assert exc.value.status_code == 401
    assert exc.value.detail == "User not found"


# User inactif
def test_get_current_user_inactive_user(session, create_user):
    user = create_user(UserRole.SUPER_ADMIN)
    user.is_active = False
    session.commit()

    token = create_access_token({"sub": str(user.id)})

    with pytest.raises(HTTPException) as exc:
        get_current_user(token=token, session=session)

    assert exc.value.status_code == 403
    assert exc.value.detail == "Inactive account"


# User valide:
def test_get_current_user_success(session, create_user):
    user = create_user(UserRole.SUPER_ADMIN)

    token = create_access_token({"sub": str(user.id)})

    result = get_current_user(token=token, session=session)

    assert result.id == user.id
    assert result.email == user.email


def test_get_current_user_company_inactive(session, create_user, company_db):
    # company inactive
    company_db.is_active = False
    session.commit()

    user = create_user(UserRole.SUPER_ADMIN, company_id=company_db.id)

    token = create_access_token({"sub": str(user.id)})

    with pytest.raises(HTTPException) as exc:
        get_current_user(token=token, session=session)

    assert exc.value.status_code == 403
    assert exc.value.detail == "Company inactive"


def test_get_current_user_company_not_found(session, create_user):
    user = create_user(UserRole.SUPER_ADMIN, company_id=9999)

    token = create_access_token({"sub": str(user.id)})

    with pytest.raises(HTTPException) as exc:
        get_current_user(token=token, session=session)

    assert exc.value.status_code == 403
