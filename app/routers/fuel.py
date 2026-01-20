from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import FuelFill
from app.schemas import FuelFillCreate, FuelFillRead, FuelFillUpdate
from app.services.fuel_services import (
    validate_km,
    validate_fuel_fill_update,
    is_last_fuel_fill,
)

router = APIRouter(prefix="/vehicules", tags=["Fuel"])


# Enregistrer un nouveau plein de carburant
@router.post("/{vehicule_id}/fuel-fills", response_model=FuelFillRead, status_code=201)
def create_fuel_fill(
    vehicule_id: int,
    fuel: FuelFillCreate,
    session: Session = Depends(get_session),
):
    validate_km(session, vehicule_id, fuel.km)

    new_fuel_fill = FuelFill(
        vehicule_id=vehicule_id,
        date=fuel.date,
        km=fuel.km,
        liters=fuel.liters,
        cost=fuel.cost,
    )

    session.add(new_fuel_fill)
    session.commit()
    session.refresh(new_fuel_fill)

    return new_fuel_fill


# Voir l'historique des pleins de carburant
@router.get("/{vehicule_id}/fuel-fills", response_model=list[FuelFillRead])
def list_fuel_fills(
    vehicule_id: int,
    session: Session = Depends(get_session),
):
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
):
    fuel = session.get(FuelFill, fuel_id)

    if not fuel or fuel.vehicule_id != vehicule_id:
        raise HTTPException(
            status_code=404, detail="Plein introuvable pour ce véhicule"
        )

    return fuel


# Modifier le dernier plein
@router.patch("/{vehicule_id}/fuel-fills/{fuel_id}", response_model=FuelFillRead)
def update_fuel_fill(
    vehicule_id: int,
    fuel_id: int,
    update: FuelFillUpdate,
    session: Session = Depends(get_session),
):
    fuel = session.get(FuelFill, fuel_id)

    if not fuel or fuel.vehicule_id != vehicule_id:
        raise HTTPException(
            status_code=404, detail="Plein introuvable pour ce véhicule"
        )

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
):
    fuel = session.get(FuelFill, fuel_id)

    if not fuel or fuel.vehicule_id != vehicule_id:
        raise HTTPException(
            status_code=404, detail="Plein introuvable pour ce véhicule"
        )

    if not is_last_fuel_fill(session, fuel):
        raise HTTPException(
            status_code=400, detail="Seul le dernier plein peut être supprimé"
        )

    session.delete(fuel)
    session.commit()
