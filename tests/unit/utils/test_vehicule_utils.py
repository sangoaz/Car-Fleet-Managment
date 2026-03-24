import pytest
from fastapi import HTTPException

from app.enums import UserRole
from app.models import VehiculeAssignment
from app.utils.vehicules import get_vehicule_or_404, get_driver_assignment_flag

# =========================
# TESTS VEHICULE 404
# =========================


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


# =========================
# TESTS IS_ASSIGNED
# =========================


def test_get_driver_assignment_flag_driver_assigned(session, create_user, vehicule_db):
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)

    # assignation
    session.add(
        VehiculeAssignment(
            vehicule_id=vehicule_db.id,
            user_id=driver.id,
        )
    )
    session.commit()

    result = get_driver_assignment_flag(session, driver, vehicule_db.id)

    assert result is True


def test_get_driver_assignment_flag_driver_not_assigned(
    session, create_user, vehicule_db
):
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)

    result = get_driver_assignment_flag(session, driver, vehicule_db.id)

    assert result is False


def test_get_driver_assignment_flag_non_driver(session, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)

    result = get_driver_assignment_flag(session, owner, vehicule_db.id)

    assert result is False
