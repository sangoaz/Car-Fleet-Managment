import pytest
from app.enums import UserRole
from app.permissions.vehicules import (
    can_create_vehicle,
    can_read_vehicle,
    can_modify_vehicle,
    can_delete_vehicle,
)
from app.models import User, Vehicule

# =========================
# HELPERS
# =========================


def make_user(role, company_id=1, user_id=1):
    return User(
        id=user_id,
        email="test@test.com",
        password_hash="fake",
        role=role,
        company_id=company_id,
        is_active=True,
    )


def make_vehicle(company_id=1):
    return Vehicule(
        id=1,
        plate="TEST",
        model="Model",
        km=1000,
        company_id=company_id,
    )


# =========================
# CREATE
# =========================


def test_super_admin_can_create_any_vehicle():
    admin = make_user(UserRole.SUPER_ADMIN, company_id=None)
    assert can_create_vehicle(admin, company_id=99) is True


def test_owner_can_create_vehicle_same_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    assert can_create_vehicle(owner, company_id=1) is True


def test_owner_cannot_create_vehicle_other_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    assert can_create_vehicle(owner, company_id=2) is False


def test_manager_can_create_vehicle():
    manager = make_user(UserRole.MANAGER, company_id=1)
    assert can_create_vehicle(manager, company_id=1) is True


def test_manager_cannot_create_vehicle_other_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    assert can_create_vehicle(manager, company_id=2) is False


def test_driver_cannot_create_vehicle():
    driver = make_user(UserRole.DRIVER, company_id=1)
    assert can_create_vehicle(driver, company_id=1) is False


# =========================
# READ
# =========================


def test_super_admin_can_read_vehicle():
    admin = make_user(UserRole.SUPER_ADMIN, company_id=None)
    vehicle = make_vehicle(company_id=1)
    assert can_read_vehicle(admin, vehicle) is True


def test_owner_can_read_vehicle_same_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicle = make_vehicle(company_id=1)
    assert can_read_vehicle(owner, vehicle) is True


def test_owner_cannot_read_vehicle_other_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicle = make_vehicle(company_id=2)
    assert can_read_vehicle(owner, vehicle) is False


def test_manager_can_read_vehicle_same_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicle = make_vehicle(company_id=1)
    assert can_read_vehicle(manager, vehicle) is True


def test_manager_can_read_vehicle_other_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicle = make_vehicle(company_id=2)
    assert can_read_vehicle(manager, vehicle) is False


def test_driver_can_read_vehicle_if_assigned():
    driver = make_user(UserRole.DRIVER, company_id=1)
    vehicle = make_vehicle(company_id=1)
    assert can_read_vehicle(driver, vehicle, is_assigned=True) is True


def test_driver_cannot_read_vehicle_if_not_assigned():
    driver = make_user(UserRole.DRIVER, company_id=1)
    vehicle = make_vehicle(company_id=1)
    assert can_read_vehicle(driver, vehicle, is_assigned=False) is False


# =========================
# MODIFY
# =========================


def admin_can_modify_vehicle():
    admin = make_user(UserRole.SUPER_ADMIN, company_id=None)
    vehicle = make_vehicle(company_id=1)
    assert can_modify_vehicle(admin, vehicle) is True


def test_owner_can_modify_vehicle_same_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicle = make_vehicle(company_id=1)
    assert can_modify_vehicle(owner, vehicle) is True


def test_owner_cannot_modify_vehicle_other_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicle = make_vehicle(company_id=2)
    assert can_modify_vehicle(owner, vehicle) is False


def test_manager_can_modify_vehicle_same_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicle = make_vehicle(company_id=1)
    assert can_modify_vehicle(manager, vehicle) is True


def test_manager_cannot_modify_vehicle_other_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicle = make_vehicle(company_id=2)
    assert can_modify_vehicle(manager, vehicle) is False


def test_driver_cannot_modify_vehicle():
    driver = make_user(UserRole.DRIVER, company_id=1)
    vehicle = make_vehicle(company_id=1)
    assert can_modify_vehicle(driver, vehicle) is False


# =========================
# DELETE
# =========================


def test_admin_can_delete_vehicle():
    admin = make_user(UserRole.SUPER_ADMIN, company_id=None)
    vehicle = make_vehicle(company_id=1)
    assert can_delete_vehicle(admin, vehicle) is True


def test_owner_can_delete_same_company_vehicle():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicle = make_vehicle(company_id=1)
    assert can_delete_vehicle(owner, vehicle) is True


def test_owner_cannot_delete_vehicle_other_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicle = make_vehicle(company_id=2)
    assert can_delete_vehicle(owner, vehicle) is False


def test_manager_cannot_delete_vehicle():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicle = make_vehicle(company_id=1)
    assert can_delete_vehicle(manager, vehicle) is False


def test_drier_cannot_delete_vehicle():
    driver = make_user(UserRole.DRIVER, company_id=1)
    vehicle = make_vehicle(company_id=1)
    assert can_delete_vehicle(driver, vehicle) is False
