import pytest
from fastapi import HTTPException

from app.utils.company import get_company_or_404

# =========================
# TESTS COMPANY 404
# =========================


def test_get_company_or_404_success(session, company_db):
    result = get_company_or_404(session, company_db.id)

    assert result is not None
    assert result.id == company_db.id
    assert result.name == company_db.name


def test_get_company_or_404_not_found(session):
    with pytest.raises(HTTPException) as exc:
        get_company_or_404(session, 9999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Entreprise introuvable"
