"Gestion des permissions des assignements de véhicules"

from app.enums import UserRole
from app.models import User


# Fonction déterminant quel user peut assigner un véhicule
def can_assign_vehicle(current_user: User) -> bool:
    if current_user.role in [UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.MANAGER]:
        return True
    return False
