"""Routes relatives aux entretiens des véhicules"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import select, func, Session
from sqlalchemy import desc
from typing import Optional

from app.database import get_session
from app.models import Entretien, Vehicule, User
from app.schemas import Create_entretien, PaginatedEntretiens, Update_entretien
from app.enums import EntretienType, UserRole
from app.services.entretien_validation import validate_entretien_coherence
from app.permissions.vehicules import can_read_vehicle
from app.permissions.entretiens import (
    can_create_entretien,
    can_delete_entretien,
    can_modify_entretien,
    can_read_entretien,
)
from app.deps.auth import get_current_user

router = APIRouter(prefix="/vehicules", tags=["entretiens"])


# Enregistrer un entretien de véhicule
@router.post("/{vehicule_id}/entretiens", status_code=201)
def create_entretien(
    vehicule_id: int,
    entretien: Create_entretien,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Vérifier que le véhicule existe
    vehicule = session.get(Vehicule, vehicule_id)
    if not vehicule:
        raise HTTPException(status_code=404, detail="Véhicule introuvable")

    # Vérification permissions
    if not can_create_entretien(current_user, vehicule):
        raise HTTPException(status_code=403, detail="Not allowed")

    # Validation métier date ↔ km (même type)
    validate_entretien_coherence(
        session,
        vehicule_id,
        entretien.type,
        entretien.date,
        entretien.km,
    )

    # Creer l'entretien
    new_entretien = Entretien(**entretien.model_dump(), vehicule_id=vehicule_id)

    # Mise à jour des km du véhicule si nécessaire
    if entretien.km > vehicule.km:
        vehicule.km = entretien.km

    # Sauvegarder
    session.add(new_entretien)
    session.commit()
    session.refresh(new_entretien)

    return new_entretien


@router.get("/{vehicule_id}/entretiens", response_model=PaginatedEntretiens)
def get_entretiens(
    vehicule_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    entretien_type: Optional[EntretienType] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order: str = Query("date_desc"),
):
    # Vérifier que le véhicule existe
    vehicule = session.get(Vehicule, vehicule_id)
    if not vehicule:
        raise HTTPException(status_code=404, detail="Véhicule introuvable")

    # 🔐 Vérification permissions
    if not can_read_vehicle(current_user, vehicule):
        raise HTTPException(status_code=403, detail="Not allowed")

    # total count
    total_stmt = select(func.count()).where(Entretien.vehicule_id == vehicule_id)

    if entretien_type:
        total_stmt = total_stmt.where(Entretien.type == entretien_type)

    total_count = session.exec(total_stmt).one()

    # Requête paginée
    stmt = select(Entretien).where(Entretien.vehicule_id == vehicule_id)

    if entretien_type:
        stmt = stmt.where(Entretien.type == entretien_type)

    if order == "date_asc":
        stmt = stmt.order_by(Entretien.date)
    else:
        stmt = stmt.order_by(desc(Entretien.date))

    stmt = stmt.offset(offset).limit(limit)

    items = session.scalars(stmt).all()

    return {"total_count": total_count, "items": items}


@router.patch("/{vehicule_id}/entretiens/{entretien_id}")
def patch_entretien(
    vehicule_id: int,
    entretien_id: int,
    entretien: Update_entretien,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Vérifier véhicule
    vehicule = session.get(Vehicule, vehicule_id)
    if not vehicule:
        raise HTTPException(404)

    # Vérifier entretien
    existing_entretien = session.get(Entretien, entretien_id)
    if not existing_entretien:
        raise HTTPException(404)

    if existing_entretien.vehicule_id != vehicule_id:
        raise HTTPException(404)

    # 🔐 Permission
    if not can_modify_entretien(current_user, existing_entretien):
        raise HTTPException(403)

    # 🔑 Valeurs finales
    final_date = (
        entretien.date if entretien.date is not None else existing_entretien.date
    )
    final_km = entretien.km if entretien.km is not None else existing_entretien.km
    final_type = (
        entretien.type if entretien.type is not None else existing_entretien.type
    )

    if final_km <= 0:
        raise HTTPException(status_code=400, detail="Kilométrage invalide")

    # 🔍 Validation métier
    validate_entretien_coherence(
        session,
        vehicule_id,
        final_type,
        final_date,
        final_km,
        exclude_entretien_id=entretien_id,
    )

    # ✅ Appliquer modifications
    existing_entretien.date = final_date
    existing_entretien.km = final_km
    existing_entretien.type = final_type

    if entretien.cost is not None:
        existing_entretien.cost = entretien.cost
    if entretien.comment is not None:
        existing_entretien.comment = entretien.comment

    # 🔁 Mise à jour km véhicule
    if final_km > vehicule.km:
        vehicule.km = final_km

    session.commit()
    session.refresh(existing_entretien)
    session.refresh(vehicule)

    return existing_entretien


@router.delete("/{vehicule_id}/entretiens/{entretien_id}", status_code=204)
def delete_entretien(
    vehicule_id: int,
    entretien_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),  # 🔐 AJOUT
):
    # Vérifier véhicule
    vehicule = session.get(Vehicule, vehicule_id)
    if not vehicule:
        raise HTTPException(status_code=404, detail="Véhicule introuvable")

    # Vérifier entretien
    entretien = session.get(Entretien, entretien_id)
    if not entretien:
        raise HTTPException(status_code=404, detail="Entretien introuvable")

    if entretien.vehicule_id != vehicule_id:
        raise HTTPException(
            status_code=404,
            detail="Cet entretien n'appartient pas à ce véhicule",
        )

    # 🔐 Vérification permissions
    if not can_delete_entretien(current_user, entretien):
        raise HTTPException(status_code=403, detail="Not allowed")

    session.delete(entretien)
    session.commit()

    return None
