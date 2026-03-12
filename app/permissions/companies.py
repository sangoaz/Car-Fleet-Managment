"""Gestion des permissions du CRUD des companies"""

from app.enums import UserRole
from app.models import User, Company


def can_create_company(current_user: User) -> bool:
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    return False


def can_read_company(current_user: User, company: Company) -> bool:
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    if current_user.role in [UserRole.OWNER, UserRole.MANAGER]:
        return current_user.company_id == company.id

    return False


def can_modify_company(current_user: User) -> bool:
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    return False


def can_delete_company(current_user: User) -> bool:
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    return False
