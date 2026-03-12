import pytest
from app.enums import UserRole
from app.permissions.entretiens import (
    can_create_entretien,
    can_delete_entretien,
    can_modify_entretien,
    can_read_entretien,
)
from app.models import User, Vehicule, Entretien

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


def make_entretien(vehicule):
    return Entretien(
        id=1,
        vehicule_id=vehicule.id,
        vehicule=vehicule,
        type="VIDANGE",
    )


# =========================
# CREATE
# =========================


def test_admin_can_create_entretien():
    admin = make_user(UserRole.SUPER_ADMIN, company_id=None)
    vehicule = make_vehicule(company_id=1)
    assert can_create_entretien(admin, vehicule) is True


def test_owner_can_create_entretien_same_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    assert can_create_entretien(owner, vehicule) is True


def test_owner_cannot_create_entretien_other_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicule = make_vehicule(company_id=2)
    assert can_create_entretien(owner, vehicule) is False


def test_manager_can_create_entretien_same_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    assert can_create_entretien(manager, vehicule) is True


def test_manager_cannot_create_entretien_other_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicule = make_vehicule(company_id=2)
    assert can_create_entretien(manager, vehicule) is False


def test_driver_cannot_create_entretien():
    driver = make_user(UserRole.DRIVER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    assert can_create_entretien(driver, vehicule) is False


# =========================
# READ
# =========================


def test_admin_can_read_entretien():
    admin = make_user(UserRole.SUPER_ADMIN, company_id=None)
    vehicule = make_vehicule(company_id=1)
    entretien = make_entretien(vehicule)
    assert can_read_entretien(admin, entretien) is True


def test_owner_can_read_entretien_same_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    entretien = make_entretien(vehicule)
    assert can_read_entretien(owner, entretien) is True


def test_owner_cannot_read_entretien_other_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicule = make_vehicule(company_id=2)
    entretien = make_entretien(vehicule)
    assert can_read_entretien(owner, entretien) is False


def test_manager_can_read_entretien_same_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    entretien = make_entretien(vehicule)
    assert can_read_entretien(manager, entretien) is True


def test_manager_cannot_read_entretien_other_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicule = make_vehicule(company_id=2)
    entretien = make_entretien(vehicule)
    assert can_read_entretien(manager, entretien) is False


def test_driver_can_read_entretien_if_assigned():
    driver = make_user(UserRole.DRIVER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    entretien = make_entretien(vehicule)
    assert can_read_entretien(driver, entretien, is_assigned=True) is True


def test_driver_cannot_read_entretien_if_not_assigned():
    driver = make_user(UserRole.DRIVER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    entretien = make_entretien(vehicule)
    assert can_read_entretien(driver, entretien, is_assigned=False) is False


# =========================
# MODIFY
# =========================


def test_admin_can_modify_entretien():
    admin = make_user(UserRole.SUPER_ADMIN, company_id=None)
    vehicule = make_vehicule(company_id=1)
    entretien = make_entretien(vehicule)
    assert can_modify_entretien(admin, entretien) is True


def test_owner_can_modify_entretien_same_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    entretien = make_entretien(vehicule)
    assert can_modify_entretien(owner, entretien) is True


def test_owner_cannot_modify_entretien_other_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicule = make_vehicule(company_id=2)
    entretien = make_entretien(vehicule)
    assert can_modify_entretien(owner, entretien) is False


def test_manager_can_modify_entretien_same_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    entretien = make_entretien(vehicule)
    assert can_modify_entretien(manager, entretien) is True


def test_manager_cannot_modify_entretien_other_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    vehicule = make_vehicule(company_id=2)
    entretien = make_entretien(vehicule)
    assert can_modify_entretien(manager, entretien) is False


def test_driver_cannot_modify_entretien():
    driver = make_user(UserRole.DRIVER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    entretien = make_entretien(vehicule)
    assert can_modify_entretien(driver, entretien) is False


# =========================
# DELETE
# =========================


def test_admin_can_delete_entretien():
    admin = make_user(UserRole.SUPER_ADMIN, company_id=None)
    vehicule = make_vehicule(company_id=1)
    entretien = make_entretien(vehicule)
    assert can_delete_entretien(admin, entretien) is True


def test_owner_can_delete_entretien_same_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicule = make_vehicule(company_id=1)
    entretien = make_entretien(vehicule)
    assert can_delete_entretien(owner, entretien) is True


def test_owner_cannot_delete_entretien_other_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    vehicule = make_vehicule(company_id=2)
    entretien = make_entretien(vehicule)
    assert can_delete_entretien(owner, entretien) is False


@pytest.mark.parametrize(
    "role",
    [
        UserRole.MANAGER,
        UserRole.DRIVER,
    ],
)
def test_manager_driver_cannot_delete_entretien(role):
    user = make_user(role, company_id=1)
    vehicule = make_vehicule(company_id=1)
    entretien = make_entretien(vehicule)
    assert can_delete_entretien(user, entretien) is False
