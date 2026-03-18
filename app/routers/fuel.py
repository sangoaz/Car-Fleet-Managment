from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.deps.auth import get_current_user
from app.enums import UserRole
from app.models import FuelFill, Vehicule, User
from app.permissions.fuel import (
    can_create_fuelfill,
    can_delete_fuelfill,
    can_modify_fuelfill,
    can_read_fuelfill,
)
from app.schemas import FuelFillCreate, FuelFillRead, FuelFillUpdate, FuelStatsRead
from app.services.fuel_services import (
    validate_km,
    validate_fuel_fill_update,
    is_last_fuel_fill,
)
from app.services.fuel_stats import compute_fuel_stats
from app.services.vehicule_assignment_service import is_driver_assigned
from app.utils.vehicules import get_vehicule_or_404


router = APIRouter(prefix="/vehicules", tags=["Fuel"])


# Enregistrer un nouveau plein de carburant
@router.post("/{vehicule_id}/fuel-fills", response_model=FuelFillRead, status_code=201)
def create_fuel_fill(
    vehicule_id: int,
    fuel: FuelFillCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Vérifier que le véhicule existe
    vehicule = get_vehicule_or_404(session, vehicule_id)

    # Vérification permissions
    is_assigned = False

    if current_user.role == UserRole.DRIVER:
        is_assigned = is_driver_assigned(session, current_user.id, vehicule_id)

    if not can_create_fuelfill(current_user, vehicule, is_assigned):
        raise HTTPException(status_code=403, detail="Not allowed")

    validate_km(session, vehicule_id, fuel.km)

    new_fuel_fill = FuelFill(
        vehicule_id=vehicule_id,
        date=fuel.date,
        km=fuel.km,
        liters=fuel.liters,
        cost=fuel.cost,
    )

    # Mise à jour des km du véhicule si nécessaire
    if fuel.km > vehicule.km:
        vehicule.km = fuel.km

    session.add(new_fuel_fill)
    session.commit()
    session.refresh(new_fuel_fill)

    return new_fuel_fill


# Voir l'historique des pleins de carburant
@router.get("/{vehicule_id}/fuel-fills", response_model=list[FuelFillRead])
def list_fuel_fills(
    vehicule_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Vérifier que le véhicule existe
    vehicule = get_vehicule_or_404(session, vehicule_id)

    # Vérification permissions
    is_assigned = False

    if current_user.role == UserRole.DRIVER:
        is_assigned = is_driver_assigned(session, current_user.id, vehicule_id)

    if not can_read_fuelfill(current_user, vehicule, is_assigned):
        raise HTTPException(status_code=403, detail="Not allowed")

    stmt = (
        select(FuelFill)
        .where(FuelFill.vehicule_id == vehicule_id)
        .order_by(FuelFill.km.desc())
    )

    return session.exec(stmt).all()


# Consulter un plein de carburant
@router.get("/{vehicule_id}/fuel-fills/{fuel_id}", response_model=FuelFillRead)
def get_fuel_fill(
    vehicule_id: int,
    fuel_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Vérifier si le véhicule existe
    vehicule = get_vehicule_or_404(session, vehicule_id)

    fuel = session.get(FuelFill, fuel_id)

    if not fuel or fuel.vehicule_id != vehicule_id:
        raise HTTPException(
            status_code=404, detail="Plein introuvable pour ce véhicule"
        )

    # Vérification permissions
    is_assigned = False

    if current_user.role == UserRole.DRIVER:
        is_assigned = is_driver_assigned(session, current_user.id, vehicule_id)

    if not can_read_fuelfill(current_user, vehicule, is_assigned):
        raise HTTPException(status_code=403, detail="Not allowed")

    return fuel


# Modifier le dernier plein
@router.patch("/{vehicule_id}/fuel-fills/{fuel_id}", response_model=FuelFillRead)
def update_fuel_fill(
    vehicule_id: int,
    fuel_id: int,
    update: FuelFillUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Vérifier si le véhicule existe
    vehicule = get_vehicule_or_404(session, vehicule_id)

    fuel = session.get(FuelFill, fuel_id)

    if not fuel or fuel.vehicule_id != vehicule_id:
        raise HTTPException(
            status_code=404, detail="Plein introuvable pour ce véhicule"
        )

    if not can_modify_fuelfill(current_user, fuel):
        raise HTTPException(status_code=403)

    validate_fuel_fill_update(session, fuel, update)

    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(fuel, field, value)

    session.commit()
    session.refresh(fuel)

    return fuel


# Supprimer le dernier plein
@router.delete("/{vehicule_id}/fuel-fills/{fuel_id}", status_code=204)
def delete_fuel_fill(
    vehicule_id: int,
    fuel_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    vehicule = get_vehicule_or_404(session, vehicule_id)

    fuel = session.get(FuelFill, fuel_id)

    if not fuel or fuel.vehicule_id != vehicule_id:
        raise HTTPException(
            status_code=404, detail="Plein introuvable pour ce véhicule"
        )

    if not can_delete_fuelfill(current_user, fuel):
        raise HTTPException(status_code=403)

    if not is_last_fuel_fill(session, fuel):
        raise HTTPException(
            status_code=400, detail="Seul le dernier plein peut être supprimé"
        )

    session.delete(fuel)
    session.commit()


# Route pour afficher les statistiques de carburant
@router.get("/{vehicule_id}/fuel-stats", response_model=FuelStatsRead)
def get_fuel_stats(
    vehicule_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    vehicule = get_vehicule_or_404(session, vehicule_id)

    is_assigned = False

    if current_user.role == UserRole.DRIVER:
        is_assigned = is_driver_assigned(session, current_user.id, vehicule_id)

    if not can_read_fuelfill(current_user, vehicule, is_assigned):
        raise HTTPException(status_code=403)

    return compute_fuel_stats(session, vehicule_id)
