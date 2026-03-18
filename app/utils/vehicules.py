from fastapi import HTTPException
from sqlmodel import Session
from app.models import Vehicule


def get_vehicule_or_404(session: Session, vehicule_id: int) -> Vehicule:
    vehicule = session.get(Vehicule, vehicule_id)
    if not vehicule:
        raise HTTPException(status_code=404, detail="Véhicule introuvable")
    return vehicule
