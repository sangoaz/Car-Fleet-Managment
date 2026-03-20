import pytest
from fastapi import HTTPException
from datetime import date

from app.models import FuelFill
from app.schemas import FuelFillUpdate
from app.services.fuel_services import (
    get_last_known_km,
    validate_km,
    get_previous_fuel_fill,
    is_last_fuel_fill,
    validate_fuel_fill_update,
)


# =========================
# GET LAST KM
# =========================


def test_get_last_known_km_from_fuel(session, vehicule_db):
    fuel = FuelFill(
        vehicule_id=vehicule_db.id,
        date=date.today(),
        km=1500,
        liters=40,
        cost=60,
    )
    session.add(fuel)
    session.commit()

    result = get_last_known_km(session, vehicule_db.id)

    assert result == 1500


def test_get_last_known_km_from_entretien(session, vehicule_db, entretien_db):
    result = get_last_known_km(session, vehicule_db.id)

    assert result == entretien_db.km


def test_get_last_known_km_from_vehicule(session, vehicule_db):
    result = get_last_known_km(session, vehicule_db.id)

    assert result == vehicule_db.km


# =========================
# VALIDATE KM
# =========================


def test_validate_km_ok(session, vehicule_db):
    validate_km(session, vehicule_db.id, 1200, liters=40, cost=50)


def test_validate_km_lower_than_last(session, vehicule_db):
    with pytest.raises(HTTPException):
        validate_km(session, vehicule_db.id, 900, liters=40, cost=50)


def test_validate_km_equal_to_last(session, vehicule_db):
    with pytest.raises(HTTPException):
        validate_km(session, vehicule_db.id, vehicule_db.km, liters=40, cost=50)


def test_validate_km_invalid_liters(session, vehicule_db):
    with pytest.raises(HTTPException):
        validate_km(session, vehicule_db.id, 1200, liters=0, cost=50)


def test_validate_km_invalid_cost(session, vehicule_db):
    with pytest.raises(HTTPException):
        validate_km(session, vehicule_db.id, 1200, liters=40, cost=-10)


# =========================
# PREVIOUS FUEL
# =========================


def test_get_previous_fuel_fill(session, vehicule_db):
    fuel1 = FuelFill(
        vehicule_id=vehicule_db.id,
        date=date.today(),
        km=1200,
        liters=40,
        cost=60,
    )
    fuel2 = FuelFill(
        vehicule_id=vehicule_db.id,
        date=date.today(),
        km=1500,
        liters=45,
        cost=70,
    )

    session.add(fuel1)
    session.add(fuel2)
    session.commit()

    previous = get_previous_fuel_fill(session, fuel2)

    assert previous.id == fuel1.id


def test_get_previous_fuel_fill_none(session, vehicule_db):
    fuel = FuelFill(
        vehicule_id=vehicule_db.id,
        date=date.today(),
        km=1200,
        liters=40,
        cost=60,
    )
    session.add(fuel)
    session.commit()

    previous = get_previous_fuel_fill(session, fuel)

    assert previous is None


# =========================
# IS LAST FUEL
# =========================


def test_is_last_fuel_fill_true(session, vehicule_db):
    fuel = FuelFill(
        vehicule_id=vehicule_db.id,
        date=date.today(),
        km=1500,
        liters=40,
        cost=60,
    )
    session.add(fuel)
    session.commit()

    assert is_last_fuel_fill(session, fuel) is True


def test_is_last_fuel_fill_false(session, vehicule_db):
    fuel1 = FuelFill(
        vehicule_id=vehicule_db.id,
        date=date.today(),
        km=1200,
        liters=40,
        cost=60,
    )
    fuel2 = FuelFill(
        vehicule_id=vehicule_db.id,
        date=date.today(),
        km=1500,
        liters=40,
        cost=60,
    )

    session.add(fuel1)
    session.add(fuel2)
    session.commit()

    assert is_last_fuel_fill(session, fuel1) is False


# =========================
# VALIDATE UPDATE
# =========================


def test_validate_update_ok(session, vehicule_db):
    fuel = FuelFill(
        vehicule_id=vehicule_db.id,
        date=date.today(),
        km=1500,
        liters=40,
        cost=60,
    )
    session.add(fuel)
    session.commit()

    update = FuelFillUpdate(km=1600, liters=45, cost=70)

    validate_fuel_fill_update(session, fuel, update)


def test_validate_update_not_last(session, vehicule_db):
    fuel1 = FuelFill(
        vehicule_id=vehicule_db.id,
        date=date.today(),
        km=1200,
        liters=40,
        cost=60,
    )
    fuel2 = FuelFill(
        vehicule_id=vehicule_db.id,
        date=date.today(),
        km=1500,
        liters=40,
        cost=60,
    )

    session.add(fuel1)
    session.add(fuel2)
    session.commit()

    update = FuelFillUpdate(km=1300)

    with pytest.raises(HTTPException):
        validate_fuel_fill_update(session, fuel1, update)


def test_validate_update_km_too_low(session, vehicule_db):
    fuel1 = FuelFill(
        vehicule_id=vehicule_db.id,
        date=date.today(),
        km=1200,
        liters=40,
        cost=60,
    )
    fuel2 = FuelFill(
        vehicule_id=vehicule_db.id,
        date=date.today(),
        km=1500,
        liters=40,
        cost=60,
    )

    session.add(fuel1)
    session.add(fuel2)
    session.commit()

    update = FuelFillUpdate(km=1100)

    with pytest.raises(HTTPException):
        validate_fuel_fill_update(session, fuel2, update)


def test_validate_update_invalid_liters(session, vehicule_db):
    fuel = FuelFill(
        vehicule_id=vehicule_db.id,
        date=date.today(),
        km=1500,
        liters=40,
        cost=60,
    )
    session.add(fuel)
    session.commit()

    update = FuelFillUpdate(liters=0)

    with pytest.raises(HTTPException):
        validate_fuel_fill_update(session, fuel, update)


def test_validate_update_invalid_cost(session, vehicule_db):
    fuel = FuelFill(
        vehicule_id=vehicule_db.id,
        date=date.today(),
        km=1500,
        liters=40,
        cost=60,
    )
    session.add(fuel)
    session.commit()

    update = FuelFillUpdate(cost=0)

    with pytest.raises(HTTPException):
        validate_fuel_fill_update(session, fuel, update)
