import pytest
from app.enums import UserRole
from app.models import User
from app.permissions.vehicule_assignement import can_assign_vehicle


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
