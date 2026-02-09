from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.models import Vehicule, User
from app.deps.auth import get_current_user


def get_vehicule_or_404(
    vehicule_id: int,
    session: Session,
    current_user: User,
) -> Vehicule:
    vehicule = session.get(Vehicule, vehicule_id)

    if not vehicule:
        raise HTTPException(status_code=404, detail="Véhicule introuvable")

    if current_user.role == "SUPER_ADMIN":
        return vehicule

    if vehicule.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Accès interdit pour ce véhicule")


def vehicule_dep(
    vehicule_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Vehicule:
    return get_vehicule_or_404(vehicule_id, session, current_user)
