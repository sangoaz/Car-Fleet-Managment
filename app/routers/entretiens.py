""" Routes relatives aux entretiens des véhicules """

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import select, func, Session, desc
from typing import Optional

from app.database import get_session
from app.models import Entretien, Vehicule
from app.schemas import Create_entretien
from app.enums import EntretienType

router = APIRouter(
    prefix="/vehicules",
    tags=["entretiens"]
)

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
    new_entretien = Entretien(
        **entretien.dict(),
        vehicule_id=vehicule_id
    )

    # Sauvegarder
    session.add(new_entretien)
    session.commit()
    session.refresh(new_entretien)

    return new_entretien

# Afficher les entretiens d'un véhicule
@router.get("/{vehicule_id}/entretiens")
def get_entretiens(
    vehicule_id: int,
    session: Session = Depends(get_session), 

    entretien_type: Optional[EntretienType] = Query(
        None,
        description="Type d'entretien"
    ),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order: str = Query("date_desc")
):
    vehicule = session.get(Vehicule, vehicule_id)
    if not vehicule:
        raise HTTPException(
            status_code=404,
            detail="Véhicule introuvable"
        )
    
    stmt = select(Entretien).where(Entretien.vehicule_id == vehicule_id)

    # Filtre par Enum
    if entretien_type:
        stmt = stmt.where(Entretien.type == entretien_type)

    # Tri
    if order == "date_asc":
        stmt = stmt.order_by(Entretien.date)
    else:
        stmt = stmt.order_by(desc(Entretien.date))

    # Pagination
    stmt = stmt.offset(offset).limit(limit)

    entretiens = session.scalars(stmt).all()
    
    return entretiens  # Ex d'url: vehicules/2/entretiens?entretien_type=CONTROLE_TECHNIQUE
