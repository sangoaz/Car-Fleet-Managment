from app.enums import UserRole


def is_super_admin(user):
    return user.role == UserRole.SUPER_ADMIN


def same_company(user1, user2):
    return user1.company_id == user2.company_id
