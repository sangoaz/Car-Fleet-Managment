import pytest
from app.enums import UserRole
from app.models import User
from app.permissions.users import (
    can_create_user,
    can_modify_user,
    can_delete_user,
    can_reactivate_user,
    can_deactivate_user,
)


def make_user(role, company_id=1):
    return User(role=role, company_id=company_id)


# Tests de création d'utilisateurs
@pytest.mark.parametrize(
    "creator_role, role_to_create, expected",
    [
        # SUPER_ADMIN
        (UserRole.SUPER_ADMIN, UserRole.SUPER_ADMIN, True),
        (UserRole.SUPER_ADMIN, UserRole.OWNER, True),
        (UserRole.SUPER_ADMIN, UserRole.MANAGER, True),
        (UserRole.SUPER_ADMIN, UserRole.DRIVER, True),
        # OWNER
        (UserRole.OWNER, UserRole.MANAGER, True),
        (UserRole.OWNER, UserRole.DRIVER, True),
        (UserRole.OWNER, UserRole.OWNER, False),
        (UserRole.OWNER, UserRole.SUPER_ADMIN, False),
        # MANAGER
        (UserRole.MANAGER, UserRole.DRIVER, True),
        (UserRole.MANAGER, UserRole.MANAGER, False),
        (UserRole.MANAGER, UserRole.OWNER, False),
        # DRIVER
        (UserRole.DRIVER, UserRole.DRIVER, False),
    ],
)
def test_can_create_user(creator_role, role_to_create, expected):
    current_user = make_user(creator_role)
    assert can_create_user(current_user, role_to_create) is expected


# Tests de modification d'utilisateurs
@pytest.mark.parametrize(
    "current_role, target_role, same_company, expected",
    [
        # SUPER_ADMIN peut tout
        (UserRole.SUPER_ADMIN, UserRole.OWNER, True, True),
        (UserRole.SUPER_ADMIN, UserRole.OWNER, False, True),
        # OWNER même société
        (UserRole.OWNER, UserRole.MANAGER, True, True),
        (UserRole.OWNER, UserRole.SUPER_ADMIN, True, False),
        # OWNER autre société
        (UserRole.OWNER, UserRole.MANAGER, False, False),
        # MANAGER même société
        (UserRole.MANAGER, UserRole.DRIVER, True, True),
        (UserRole.MANAGER, UserRole.OWNER, True, False),
        # MANAGER autre société
        (UserRole.MANAGER, UserRole.DRIVER, False, False),
        # DRIVER
        (UserRole.DRIVER, UserRole.DRIVER, True, False),
    ],
)
def test_can_modify_user(current_role, target_role, same_company, expected):
    company_current = 1
    company_target = 1 if same_company else 2

    current_user = make_user(current_role, company_current)
    target_user = make_user(target_role, company_target)

    assert can_modify_user(current_user, target_user) is expected


# Tests de suppression d'utilisateurs
import pytest


@pytest.mark.parametrize(
    "current_role, target_role, same_company, same_user, expected",
    [
        # ---------------- SUPER_ADMIN ----------------
        (UserRole.SUPER_ADMIN, UserRole.DRIVER, True, False, True),
        (UserRole.SUPER_ADMIN, UserRole.OWNER, False, False, True),
        (UserRole.SUPER_ADMIN, UserRole.SUPER_ADMIN, False, False, True),
        # auto suppression
        (UserRole.SUPER_ADMIN, UserRole.SUPER_ADMIN, True, True, False),
        # ---------------- OWNER ----------------
        # même company
        (UserRole.OWNER, UserRole.DRIVER, True, False, True),
        (UserRole.OWNER, UserRole.MANAGER, True, False, True),
        # autre company
        (UserRole.OWNER, UserRole.DRIVER, False, False, False),
        # ne peut pas supprimer SUPER_ADMIN
        (UserRole.OWNER, UserRole.SUPER_ADMIN, True, False, False),
        # auto suppression
        (UserRole.OWNER, UserRole.OWNER, True, True, False),
        # ---------------- MANAGER ----------------
        (UserRole.MANAGER, UserRole.DRIVER, True, False, False),
        # ---------------- DRIVER ----------------
        (UserRole.DRIVER, UserRole.DRIVER, True, False, False),
    ],
)
def test_can_delete_user(current_role, target_role, same_company, same_user, expected):
    company_current = 1
    company_target = 1 if same_company else 2

    current_user = make_user(current_role, company_current)
    target_user = make_user(target_role, company_target)

    # Simulation IDs réalistes
    current_user.id = 1
    target_user.id = 1 if same_user else 2

    assert can_delete_user(current_user, target_user) is expected


@pytest.mark.parametrize(
    "current_role, target_role, same_company, same_user, expected",
    [
        # ---------------- SUPER_ADMIN ----------------
        (UserRole.SUPER_ADMIN, UserRole.DRIVER, True, False, True),
        (UserRole.SUPER_ADMIN, UserRole.OWNER, False, False, True),
        (UserRole.SUPER_ADMIN, UserRole.SUPER_ADMIN, False, False, True),
        # auto suppression
        (UserRole.SUPER_ADMIN, UserRole.SUPER_ADMIN, True, True, False),
        # ---------------- OWNER ----------------
        # même company
        (UserRole.OWNER, UserRole.DRIVER, True, False, True),
        (UserRole.OWNER, UserRole.MANAGER, True, False, True),
        # autre company
        (UserRole.OWNER, UserRole.DRIVER, False, False, False),
        # ne peut pas supprimer SUPER_ADMIN
        (UserRole.OWNER, UserRole.SUPER_ADMIN, True, False, False),
        # auto suppression
        (UserRole.OWNER, UserRole.OWNER, True, True, False),
        # ---------------- MANAGER ----------------
        (UserRole.MANAGER, UserRole.DRIVER, True, False, False),
        # ---------------- DRIVER ----------------
        (UserRole.DRIVER, UserRole.DRIVER, True, False, False),
    ],
)
def test_can_deactivate_user(
    current_role, target_role, same_company, same_user, expected
):
    company_current = 1
    company_target = 1 if same_company else 2

    current_user = make_user(current_role, company_current)
    target_user = make_user(target_role, company_target)

    # Simulation IDs réalistes
    current_user.id = 1
    target_user.id = 1 if same_user else 2

    assert can_deactivate_user(current_user, target_user) is expected


@pytest.mark.parametrize(
    "current_role, target_role, same_company, same_user, expected",
    [
        # ---------------- SUPER_ADMIN ----------------
        (UserRole.SUPER_ADMIN, UserRole.DRIVER, True, False, True),
        (UserRole.SUPER_ADMIN, UserRole.OWNER, False, False, True),
        (UserRole.SUPER_ADMIN, UserRole.SUPER_ADMIN, False, False, True),
        # auto suppression
        (UserRole.SUPER_ADMIN, UserRole.SUPER_ADMIN, True, True, False),
        # ---------------- OWNER ----------------
        # même company
        (UserRole.OWNER, UserRole.DRIVER, True, False, True),
        (UserRole.OWNER, UserRole.MANAGER, True, False, True),
        # autre company
        (UserRole.OWNER, UserRole.DRIVER, False, False, False),
        # ne peut pas supprimer SUPER_ADMIN
        (UserRole.OWNER, UserRole.SUPER_ADMIN, True, False, False),
        # auto suppression
        (UserRole.OWNER, UserRole.OWNER, True, True, False),
        # ---------------- MANAGER ----------------
        (UserRole.MANAGER, UserRole.DRIVER, True, False, False),
        # ---------------- DRIVER ----------------
        (UserRole.DRIVER, UserRole.DRIVER, True, False, False),
    ],
)
def test_can_reactivate_user(
    current_role, target_role, same_company, same_user, expected
):
    company_current = 1
    company_target = 1 if same_company else 2

    current_user = make_user(current_role, company_current)
    target_user = make_user(target_role, company_target)

    # Simulation IDs réalistes
    current_user.id = 1
    target_user.id = 1 if same_user else 2

    assert can_reactivate_user(current_user, target_user) is expected
