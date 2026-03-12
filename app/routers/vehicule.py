"""Routes relatives aux véhicules"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import select, func, Session
from sqlalchemy import desc

from app.database import get_session
from app.enums import EntretienType, UserRole
from app.models import Vehicule, Entretien, User
from app.permissions.vehicules import (
    can_create_vehicle,
    can_delete_vehicle,
    can_modify_vehicle,
    can_read_vehicle,
)
from app.schemas import Create_vehicule, Update_vehicule, VehiculeOverviewResponse
from app.services.alerts import get_vehicle_alerts
from app.deps.auth import require_roles, require_admin, get_current_user

router = APIRouter(prefix="/vehicules", tags=["Vehicules"])


# Enregistrer un nouveau véhicule
@router.post("/", status_code=201)
def create_vehicule(
    vehicule: Create_vehicule,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # SUPER_ADMIN peut choisir la company
    if current_user.role == UserRole.SUPER_ADMIN:
        target_company_id = vehicule.company_id
    else:
        # OWNER / MANAGER / DRIVER → forcé à sa company
        target_company_id = current_user.company_id

    if not can_create_vehicle(current_user, target_company_id):
        raise HTTPException(status_code=403, detail="Not allowed")

    new_vehicule = Vehicule(
        plate=vehicule.plate,
        model=vehicule.model,
        km=vehicule.km,
        buy_date=vehicule.buy_date,
        first_registration_date=vehicule.first_registration_date,
        company_id=target_company_id,
    )

    session.add(new_vehicule)
    session.commit()
    session.refresh(new_vehicule)

    return new_vehicule


# Afficher un véhicule
@router.get("/{vehicule_id}")
def get_vehicule(
    vehicule_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    vehicule = session.get(Vehicule, vehicule_id)
    if not vehicule:
        raise HTTPException(status_code=404, detail="Véhicule introuvable")

    if not can_read_vehicle(current_user, vehicule):
        raise HTTPException(status_code=403, detail="Not allowed")

    return vehicule


# Afficher la liste des véhicules
@router.get("/")
def get_vehicules_list(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.role == UserRole.SUPER_ADMIN:
        statement = select(Vehicule)
    else:
        statement = select(Vehicule).where(
            Vehicule.company_id == current_user.company_id
        )
    # Ajouter plus tard les users DRIVER afin qu'ils puissent voir uniquement leurs véhicules

    vehicules = session.exec(statement).all()
    return vehicules


# Mettre à jour un véhicule
@router.patch("/{vehicule_id}")
def patch_vehicule(
    vehicule_id: int,
    vehicule: Update_vehicule,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    existing_vehicule = session.get(Vehicule, vehicule_id)
    if not existing_vehicule:
        raise HTTPException(status_code=404, detail="Véhicule introuvable")
    if not can_modify_vehicle(current_user, existing_vehicule):
        raise HTTPException(status_code=403, detail="Not allowed")

    if vehicule.plate is not None:
        existing_vehicule.plate = vehicule.plate
    if vehicule.model is not None:
        existing_vehicule.model = vehicule.model
    if vehicule.km is not None:
        existing_vehicule.km = vehicule.km
    if vehicule.buy_date is not None:
        existing_vehicule.buy_date = vehicule.buy_date
    if vehicule.first_registration_date is not None:
        existing_vehicule.first_registration_date = vehicule.first_registration_date

    session.commit()
    session.refresh(existing_vehicule)
    return existing_vehicule


# Supprimer un véhicule
@router.delete("/{vehicule_id}")
def delete_vehicule(
    vehicule_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    existing_vehicule = session.get(Vehicule, vehicule_id)

    if not existing_vehicule:
        raise HTTPException(status_code=404, detail="Véhicule introuvable")

    if not can_delete_vehicle(current_user, existing_vehicule):
        raise HTTPException(status_code=403, detail="Not allowed")

    if existing_vehicule.entretiens:
        raise HTTPException(
            status_code=400,
            detail="Impossible de supprimer un véhicule avec des entretiens",
        )

    session.delete(existing_vehicule)
    session.commit()
    return {"message": f"Vehicule {vehicule_id} supprimé"}


# Overview d'un véhicule
@router.get("/{vehicule_id}/overview", response_model=VehiculeOverviewResponse)
def vehicule_overview(
    vehicule_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    # Vérifier si le véhicule existe
    vehicule = session.get(Vehicule, vehicule_id)
    if not vehicule:
        raise HTTPException(status_code=404, detail="Vehicule introuvable")

    # Derniers entretiens (tous types)
    stmt_entretiens = (
        select(Entretien)
        .where(Entretien.vehicule_id == vehicule_id)
        .order_by(desc(Entretien.date))
        .limit(5)
    )
    last_entretien = session.scalars(stmt_entretiens).all()

    # Dernier contrôle technique
    stmt_ct = (
        select(Entretien)
        .where(
            Entretien.vehicule_id == vehicule_id,
            Entretien.type == EntretienType.CONTROLE_TECHNIQUE,
        )
        .order_by(desc(Entretien.date))
        .limit(1)
    )
    last_ct = session.scalars(stmt_ct).first()

    return {
        "vehicule": vehicule,
        "last_entretiens": last_entretien,
        "last_controle_technique": last_ct,
    }
