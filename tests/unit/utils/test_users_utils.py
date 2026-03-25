import pytest
from fastapi import HTTPException

from app.enums import UserRole
from app.utils.users import get_user_or_404

# =========================
# TESTS USERS 404
# =========================


def test_get_user_or_404_success(session, create_user):
    user = create_user(UserRole.MANAGER, 1)

    result = get_user_or_404(session, user.id)

    assert result is not None
    assert result.id == user.id
    assert result.email == user.email


def test_get_user_or_404_not_found(session):
    with pytest.raises(HTTPException) as exc:
        get_user_or_404(session, 9999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Utilisateur introuvable"
