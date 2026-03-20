from fastapi import HTTPException
from sqlmodel import Session

from app.enums import UserRole
from app.models import Vehicule
from app.services.vehicule_assignment_service import is_driver_assigned


def get_vehicule_or_404(session: Session, vehicule_id: int) -> Vehicule:
    vehicule = session.get(Vehicule, vehicule_id)
    if not vehicule:
        raise HTTPException(status_code=404, detail="Véhicule introuvable")
    return vehicule


def get_driver_assignment_flag(session, user, vehicule_id):
    if user.role == UserRole.DRIVER:
        return is_driver_assigned(session, user.id, vehicule_id)
    return False
