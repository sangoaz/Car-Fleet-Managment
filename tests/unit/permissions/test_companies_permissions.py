import pytest
from app.enums import UserRole
from app.permissions.companies import (
    can_create_company,
    can_delete_company,
    can_modify_company,
    can_read_company,
)
from app.models import User, Company

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


def make_company(company_id=1):
    return Company(
        id=company_id,
        name="Test Company",
        is_active=True,
    )


# =========================
# CREATE
# =========================


def test_admin_can_create_company():
    admin = make_user(UserRole.SUPER_ADMIN, company_id=None)
    assert can_create_company(admin) is True


@pytest.mark.parametrize(
    "role",
    [
        UserRole.OWNER,
        UserRole.MANAGER,
        UserRole.DRIVER,
    ],
)
def test_non_admin_cannot_create_company(role):
    user = make_user(role, company_id=1)
    assert can_create_company(user) is False


# =========================
# READ
# =========================


def test_admin_can_read_company():
    admin = make_user(UserRole.SUPER_ADMIN, company_id=None)
    company = make_company(company_id=1)
    assert can_read_company(admin, company) is True


def test_owner_can_read_same_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    company = make_company(company_id=1)
    assert can_read_company(owner, company) is True


def test_owner_cannot_read_other_company():
    owner = make_user(UserRole.OWNER, company_id=1)
    company = make_company(company_id=2)
    assert can_read_company(owner, company) is False


def test_manager_can_read_same_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    company = make_company(company_id=1)
    assert can_read_company(manager, company) is True


def test_manager_cannot_read_other_company():
    manager = make_user(UserRole.MANAGER, company_id=1)
    company = make_company(company_id=2)
    assert can_read_company(manager, company) is False


def test_driver_cannot_read_company():
    driver = make_user(UserRole.DRIVER, company_id=1)
    company = make_company(company_id=1)
    assert can_read_company(driver, company) is False


# =========================
# MODIFY
# =========================


def test_admin_can_modify_company():
    admin = make_user(UserRole.SUPER_ADMIN, company_id=None)
    assert can_modify_company(admin) is True


@pytest.mark.parametrize(
    "role",
    [
        UserRole.OWNER,
        UserRole.MANAGER,
        UserRole.DRIVER,
    ],
)
def test_non_admin_cannot_modify_company(role):
    user = make_user(role, company_id=1)
    assert can_modify_company(user) is False


# =========================
# DELETE
# =========================


def test_admin_can_delete_company():
    admin = make_user(UserRole.SUPER_ADMIN, company_id=None)
    assert can_delete_company(admin) is True


@pytest.mark.parametrize(
    "role",
    [
        UserRole.OWNER,
        UserRole.MANAGER,
        UserRole.DRIVER,
    ],
)
def test_non_admin_cannot_delete_company(role):
    user = make_user(role, company_id=1)
    assert can_delete_company(user) is False
