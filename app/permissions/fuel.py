"""Gestion des permissions du CRUD des pleins de carburant"""

from app.enums import UserRole
from app.models import User, FuelFill


def can_create_fuelfill(current_user: User, vehicule, is_assigned=False) -> bool:
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    if current_user.company_id != vehicule.company_id:
        return False

    if current_user.role in [UserRole.OWNER, UserRole.MANAGER]:
        return True

    if current_user.role == UserRole.DRIVER:
        return is_assigned

    return False


def can_read_fuelfill(current_user: User, vehicule, is_assigned=False) -> bool:
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    if current_user.company_id != vehicule.company_id:
        return False

    if current_user.role in [UserRole.OWNER, UserRole.MANAGER]:
        return True

    if current_user.role == UserRole.DRIVER:
        return is_assigned

    return False


def can_modify_fuelfill(current_user: User, fuelfill: FuelFill) -> bool:
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    vehicule = fuelfill.vehicule

    if current_user.company_id != vehicule.company_id:
        return False

    if current_user.role in [UserRole.OWNER, UserRole.MANAGER]:
        return True

    return False


def can_delete_fuelfill(current_user: User, fuelfill: FuelFill) -> bool:
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    vehicule = fuelfill.vehicule

    if current_user.company_id != vehicule.company_id:
        return False

    if current_user.role in [UserRole.OWNER, UserRole.MANAGER]:
        return True

    return False
