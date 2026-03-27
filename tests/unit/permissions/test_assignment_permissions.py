import pytest
from app.enums import UserRole
from app.models import User
from app.permissions.vehicule_assignement import (
    can_assign_vehicle,
    can_view_assignments,
    can_unassign_vehicle,
)


@pytest.mark.parametrize(
    "role, expected",
    [
        (UserRole.SUPER_ADMIN, True),
        (UserRole.OWNER, True),
        (UserRole.MANAGER, True),
        (UserRole.DRIVER, False),
    ],
)
def test_can_assign_vehicle(role, expected):
    user = User(role=role)

    assert can_assign_vehicle(user) is expected


@pytest.mark.parametrize(
    "role, expected",
    [
        (UserRole.SUPER_ADMIN, True),
        (UserRole.OWNER, True),
        (UserRole.MANAGER, True),
        (UserRole.DRIVER, True),
    ],
)
def test_can_view_assigments(role, expected):
    user = User(role=role)

    assert can_view_assignments(user) is expected


@pytest.mark.parametrize(
    "role, expected",
    [
        (UserRole.SUPER_ADMIN, True),
        (UserRole.OWNER, True),
        (UserRole.MANAGER, True),
        (UserRole.DRIVER, False),
    ],
)
def test_can_unassign_vehicle(role, expected):
    user = User(role=role)

    assert can_assign_vehicle(user) is expected
