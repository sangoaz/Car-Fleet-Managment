"""Routes relatives aux véhicules"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import select, func, Session
from typing import Optional
from sqlalchemy import desc

from app.database import get_session
from app.enums import EntretienType, UserRole
from app.models import Vehicule, Entretien, User
from app.schemas import Create_vehicule, Update_vehicule, VehiculeOverviewResponse
from app.services.alerts import get_vehicle_alerts
from app.deps.auth import require_roles, require_admin

router = APIRouter(prefix="/vehicules", tags=["Vehicules"])


# Enregistrer un nouveau véhicule
@router.post("/", status_code=201)
def create_vehicule(
    vehicule: Create_vehicule,
    session: Session = Depends(get_session),
):
    new_vehicule = Vehicule(
        plate=vehicule.plate,
        model=vehicule.model,
        km=vehicule.km,
        buy_date=vehicule.buy_date,
        first_registration_date=vehicule.first_registration_date,
        company_id=vehicule.company_id,
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
):
    vehicule = session.get(Vehicule, vehicule_id)
    if not vehicule:
        raise HTTPException(status_code=404, detail="Véhicule introuvable")
    return vehicule


# Afficher la liste des véhicules
@router.get("/")
def get_vehicules_list(
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.OWNER,
            UserRole.MANAGER,
            UserRole.DRIVER,
        )
    ),
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
):
    existing_vehicule = session.get(Vehicule, vehicule_id)
    if not existing_vehicule:
        raise HTTPException(status_code=404, detail="Véhicule introuvable")

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
):
    existing_vehicule = session.get(Vehicule, vehicule_id)
    if not existing_vehicule:
        raise HTTPException(status_code=404, detail="Véhicule introuvable")

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
def vehicule_overview(vehicule_id: int, session: Session = Depends(get_session)):

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


# Assigner un véhicule
@router.post("/{vehicule_id}/assign")
def assign_vehicule(vehicule_id: int, session: Session = Depends(get_session)):

    return None


# Désassigner un véhicule
@router.post("/{vehicule_id}/unassign")
def unassign_vehicule(vehicule_id: int, session: Session = Depends(get_session)):
    return None


# Voir l'assignation active
@router.get("/{vehicule_id}/assignment")
def assignment_vehicule(vehicule_id: int, session: Session = Depends(get_session)):
    return None
