"""Gestion des permissions du CRUD des entretiens"""

from app.enums import UserRole
from app.models import User, Entretien


def can_create_entretien(current_user: User, vehicule) -> bool:
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    if current_user.company_id != vehicule.company_id:
        return False

    if current_user.role in [UserRole.OWNER, UserRole.MANAGER]:
        return True

    return False


def can_read_entretien(
    current_user: User, entretien: Entretien, is_assigned=False
) -> bool:
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    vehicule = entretien.vehicule

    if current_user.company_id != vehicule.company_id:
        return False

    if current_user.role in [UserRole.OWNER, UserRole.MANAGER]:
        return True

    if current_user.role == UserRole.DRIVER:
        return is_assigned

    return False


def can_modify_entretien(current_user: User, entretien: Entretien) -> bool:
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    vehicule = entretien.vehicule

    if current_user.company_id != vehicule.company_id:
        return False

    if current_user.role in [UserRole.OWNER, UserRole.MANAGER]:
        return True

    return False


def can_delete_entretien(current_user: User, entretien: Entretien) -> bool:

    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    vehicule = entretien.vehicule

    if current_user.company_id != vehicule.company_id:
        return False

    if current_user.role == UserRole.OWNER:
        return True

    return False
