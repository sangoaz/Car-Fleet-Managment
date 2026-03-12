"""Gestion des permissions du CRUD des vehicules"""

from app.enums import UserRole
from app.models import User, Vehicule


def can_create_vehicle(current_user: User, company_id: int) -> bool:
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    if current_user.role in [UserRole.OWNER, UserRole.MANAGER]:
        return current_user.company_id == company_id

    return False


def can_read_vehicle(
    current_user: User, vehicle: Vehicule, is_assigned: bool = False
) -> bool:
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    if current_user.company_id != vehicle.company_id:
        return False

    if current_user.role in [UserRole.OWNER, UserRole.MANAGER]:
        return True

    if current_user.role == UserRole.DRIVER:
        return is_assigned

    return False


def can_modify_vehicle(current_user: User, vehicle: Vehicule) -> bool:
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    if current_user.company_id != vehicle.company_id:
        return False

    if current_user.role in [UserRole.OWNER, UserRole.MANAGER]:
        return True

    return False


def can_delete_vehicle(current_user: User, vehicle: Vehicule) -> bool:
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    if current_user.company_id != vehicle.company_id:
        return False

    if current_user.role == UserRole.OWNER:
        return True

    return False
