"""Routes relatives aux entretiens des véhicules"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import select, func, Session
from sqlalchemy import desc
from typing import Optional

from app.database import get_session
from app.models import Entretien, Vehicule
from app.schemas import Create_entretien, PaginatedEntretiens, Update_entretien
from app.enums import EntretienType

router = APIRouter(prefix="/vehicules", tags=["entretiens"])


# Enregistrer un entretien de véhicule
@router.post("/{vehicule_id}/entretiens", status_code=201)
def create_entretien(
    vehicule_id: int,
    entretien: Create_entretien,
    session: Session = Depends(get_session),
):
    # Vérifier que le véhicule existe
    vehicule = session.get(Vehicule, vehicule_id)
    if not vehicule:
        raise HTTPException(status_code=404, detail="Véhicule introuvable")

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


# Afficher les entretiens d'un véhicule
@router.get("/{vehicule_id}/entretiens", response_model=PaginatedEntretiens)
def get_entretiens(
    vehicule_id: int,
    session: Session = Depends(get_session),
    entretien_type: Optional[EntretienType] = Query(
        None, description="Type d'entretien"
    ),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order: str = Query("date_desc"),
):
    # Vérifier que le véhicule existe
    vehicule = session.get(Vehicule, vehicule_id)
    if not vehicule:
        raise HTTPException(status_code=404, detail="Véhicule introuvable")

    # total count (sans pagination)
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


# Modifier l'entretien d'un véhicule
@router.patch("/{vehicule_id}/entretiens/{entretien_id}")
def patch_entretien(
    vehicule_id: int,
    entretien_id: int,
    entretien: Update_entretien,
    session: Session = Depends(get_session),
):
    # Vérifier si le véhicule existe
    existing_vehicule = session.get(Vehicule, vehicule_id)
    if not existing_vehicule:
        raise HTTPException(status_code=404, detail="Véhicule introuvable")

    # Vérifier si l'entretien existe
    existing_entretien = session.get(Entretien, entretien_id)
    if not existing_entretien:
        raise HTTPException(status_code=404, detail="Entretien introuvable")

    # Vérifier si l'entretien appartient au véhicule
    if existing_entretien.vehicule_id != vehicule_id:
        raise HTTPException(
            status_code=404,
            detail="Cet entretien n'appartient pas à ce véhicule",
        )

    # Modification des infos
    if entretien.date is not None:
        existing_entretien.date = entretien.date
    if entretien.km is not None:
        if entretien.km <= 0:
            raise HTTPException(status_code=400, detail="kilométrage invalide")
        existing_entretien.km = entretien.km
        # Si le kmage de l'entretien est plus élevé que le kmage du véhicule, le met à jour dans la table véhicule
        if entretien.km > existing_vehicule.km:
            existing_vehicule.km = entretien.km
    if entretien.type is not None:
        existing_entretien.type = entretien.type
    if entretien.cost is not None:
        existing_entretien.cost = entretien.cost
    if entretien.comment is not None:
        existing_entretien.comment = entretien.comment

    session.commit()
    session.refresh(existing_entretien)
    session.refresh(existing_vehicule)
    return existing_entretien
