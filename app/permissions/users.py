from app.enums import UserRole
from app.models import User


# Fonction déterminant quel user peut creer quel user
def can_create_user(current_user: User, role_to_create: UserRole) -> bool:
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    if current_user.role == UserRole.OWNER:
        return role_to_create in [UserRole.MANAGER, UserRole.DRIVER]

    if current_user.role == UserRole.MANAGER:
        return role_to_create == UserRole.DRIVER

    return False


# Fonction déterminant quel user peut modifier quel user
def can_modify_user(current_user: User, target_user: User) -> bool:
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    if current_user.company_id != target_user.company_id:
        return False

    if current_user.role == UserRole.OWNER:
        return target_user.role != UserRole.SUPER_ADMIN

    if current_user.role == UserRole.MANAGER:
        return target_user.role == UserRole.DRIVER

    return False


# Fonction derterminant quel user peut supprimer quel users
def can_delete_user(current_user: User, target_user: User) -> bool:

    # Un user ne peut pas se supprimer lui-même (bonne pratique)
    if current_user.id == target_user.id:
        return False

    # SUPER_ADMIN peut tout supprimer
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    # OWNER
    if current_user.role == UserRole.OWNER:

        # Ne peut pas supprimer un SUPER_ADMIN
        if target_user.role == UserRole.SUPER_ADMIN:
            return False

        # Doit être dans la même company
        return current_user.company_id == target_user.company_id

    return False


# Fonction determinant quel user peut reactiver quel users
def can_reactivate_user(current_user: User, target_user: User) -> bool:

    # Un user ne peut pas se reactiver lui-même
    if current_user.id == target_user.id:
        return False

    # SUPER_ADMIN peut tout reactiver
    if current_user.role == UserRole.SUPER_ADMIN:
        return True

    # OWNER
    if current_user.role == UserRole.OWNER:

        # Ne peut pas désactiver un SUPER_ADMIN
        if target_user.role == UserRole.SUPER_ADMIN:
            return False

        # Doit être dans la même company
        return current_user.company_id == target_user.company_id

    return False
