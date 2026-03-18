import pytest
from fastapi import HTTPException
from app.utils.vehicules import get_vehicule_or_404


def test_get_vehicule_or_404_success(session, vehicule_db):
    result = get_vehicule_or_404(session, vehicule_db.id)

    assert result is not None
    assert result.id == vehicule_db.id
    assert result.plate == vehicule_db.plate


def test_get_vehicule_or_404_not_found(session):
    with pytest.raises(HTTPException) as exc:
        get_vehicule_or_404(session, 9999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Véhicule introuvable"
