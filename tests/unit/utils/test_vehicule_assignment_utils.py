import pytest
from fastapi import HTTPException

from app.utils.vehicule_assignment import (
    check_vehicle_access,
    check_same_company,
    ensure_driver,
)
from app.enums import UserRole
from app.models import User, Vehicule


def create_user(role, company_id):
    return User(id=1, role=role, company_id=company_id, is_active=True)


def create_vehicle(company_id):
    return Vehicule(id=1, company_id=company_id)


# ===========================
# TESTS check_vehicle_access
# ===========================


def test_check_vehicle_access_same_company():
    user = create_user(UserRole.MANAGER, 1)
    vehicule = create_vehicle(1)

    check_vehicle_access(user, vehicule)  # no exception


def test_check_vehicle_access_different_company():
    user = create_user(UserRole.MANAGER, 1)
    vehicule = create_vehicle(2)

    with pytest.raises(HTTPException):
        check_vehicle_access(user, vehicule)


def test_check_vehicle_access_super_admin():
    user = create_user(UserRole.SUPER_ADMIN, None)
    vehicule = create_vehicle(2)

    check_vehicle_access(user, vehicule)


# =====================
# TESTS ensure_driver
# =====================


def test_ensure_driver_ok():
    user = create_user(UserRole.DRIVER, 1)

    ensure_driver(user)


def test_ensure_driver_fail():
    user = create_user(UserRole.MANAGER, 1)

    with pytest.raises(HTTPException):
        ensure_driver(user)


# =========================
# TESTS check_same_company
# =========================


def test_check_same_company_ok():
    user = create_user(UserRole.DRIVER, 1)
    vehicule = create_vehicle(1)

    check_same_company(user, vehicule)


def test_check_same_company_fail():
    user = create_user(UserRole.DRIVER, 1)
    vehicule = create_vehicle(2)

    with pytest.raises(HTTPException):
        check_same_company(user, vehicule)
