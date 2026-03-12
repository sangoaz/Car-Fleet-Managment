import pytest
from app.enums import UserRole
from app.permissions.fuel import (
    can_create_fuelfill,
    can_delete_fuelfill,
    can_modify_fuelfill,
    can_read_fuelfill,
)
from app.models import User, Vehicule, FuelFill

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


def make_vehicule(company_id=1):
    return Vehicule(
        id=1,
        plate="TEST",
        model="Model",
        km=1000,
        company_id=company_id,
    )


def make_fuelfill(vehicule):
    return FuelFill(
        id=1,
        vehicule_id=vehicule.id,
        vehicule=vehicule,
        km=50,
        liters=50,
        cost=50,
    )


# =========================
# CREATE
# =========================


def test_admin_can_create_fuelfill():
    admin = make_user(UserRole.SUPER_ADMIN, company_id=None)
    vehicule = make_vehicule(company_id=1)
    assert can_create_fuelfill(admin, vehicule) is True


def test_owner_can_create_fuelfill_same_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    assert can_create_fuelfill(owner, vehicule) is True


def test_owner_cannot_create_fuelfill_other_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicule = make_vehicule(company_id=2)
    assert can_create_fuelfill(owner, vehicule) is False


def test_manager_can_create_fuelfill_same_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    assert can_create_fuelfill(manager, vehicule) is True


def test_manager_cannot_create_fuelfill_other_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicule = make_vehicule(company_id=2)
    assert can_create_fuelfill(manager, vehicule) is False


def test_driver_can_create_fuelfill_if_assigned():
    driver = make_user(UserRole.DRIVER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    assert can_create_fuelfill(driver, vehicule, is_assigned=True) is True


def test_driver_cannot_create_fuelfill_if_not_assigned():
    driver = make_user(UserRole.DRIVER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    assert can_create_fuelfill(driver, vehicule, is_assigned=False) is False


# =========================
# READ
# =========================


def test_admin_can_read_fuelfill():
    admin = make_user(UserRole.SUPER_ADMIN, company_id=None)
    vehicule = make_vehicule(company_id=1)
    assert can_read_fuelfill(admin, vehicule) is True


def test_owner_can_read_fuelfill_same_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    assert can_read_fuelfill(owner, vehicule) is True


def test_owner_cannot_read_fuelfill_other_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicule = make_vehicule(company_id=2)
    assert can_read_fuelfill(owner, vehicule) is False


def test_manager_can_read_fuelfill_same_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    assert can_read_fuelfill(manager, vehicule) is True


def test_manager_cannot_read_fuelfill_other_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicule = make_vehicule(company_id=2)
    assert can_read_fuelfill(manager, vehicule) is False


def test_driver_can_read_fuelfill_if_assigned():
    driver = make_user(UserRole.DRIVER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    assert can_read_fuelfill(driver, vehicule, is_assigned=True) is True


def test_driver_cannot_read_fuelfill_if_not_assigned():
    driver = make_user(UserRole.DRIVER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    assert can_read_fuelfill(driver, vehicule, is_assigned=False) is False


# =========================
# MODIFY
# =========================


def test_admin_can_modify_fuelfill():
    admin = make_user(UserRole.SUPER_ADMIN, company_id=None)
    vehicule = make_vehicule(company_id=1)
    fuelfill = make_fuelfill(vehicule)
    assert can_modify_fuelfill(admin, fuelfill) is True


def test_owner_can_modify_fuelfill_same_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    fuelfill = make_fuelfill(vehicule)
    assert can_modify_fuelfill(owner, fuelfill) is True


def test_owner_cannot_modify_fuelfill_other_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicule = make_vehicule(company_id=2)
    fuelfill = make_fuelfill(vehicule)
    assert can_modify_fuelfill(owner, fuelfill) is False


def test_manager_can_modify_fuelfill_same_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    fuelfill = make_fuelfill(vehicule)
    assert can_modify_fuelfill(manager, fuelfill) is True


def test_manager_cannot_modify_fuelfill_other_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicule = make_vehicule(company_id=2)
    fuelfill = make_fuelfill(vehicule)
    assert can_modify_fuelfill(manager, fuelfill) is False


def test_driver_cannot_modify_fuelfill():
    driver = make_user(UserRole.DRIVER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    fuelfill = make_fuelfill(vehicule)
    assert can_modify_fuelfill(driver, fuelfill) is False


# =========================
# DELETE
# =========================


def test_admin_can_delete_fuelfill():
    admin = make_user(UserRole.SUPER_ADMIN, company_id=None)
    vehicule = make_vehicule(company_id=1)
    fuelfill = make_fuelfill(vehicule)
    assert can_delete_fuelfill(admin, fuelfill) is True


def test_owner_can_delete_fuelfill_same_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    fuelfill = make_fuelfill(vehicule)
    assert can_delete_fuelfill(owner, fuelfill) is True


def test_owner_cannot_delete_fuelfill_other_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicule = make_vehicule(company_id=2)
    fuelfill = make_fuelfill(vehicule)
    assert can_delete_fuelfill(owner, fuelfill) is False


def test_manager_can_delete_fuelfill_same_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    fuelfill = make_fuelfill(vehicule)
    assert can_delete_fuelfill(manager, fuelfill) is True


def test_manager_cannot_delete_fuelfill_other_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicule = make_vehicule(company_id=2)
    fuelfill = make_fuelfill(vehicule)
    assert can_delete_fuelfill(manager, fuelfill) is False


def test_driver_cannot_delete_fuelfill():
    driver = make_user(UserRole.DRIVER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    fuelfill = make_fuelfill(vehicule)
    assert can_delete_fuelfill(driver, fuelfill) is False
