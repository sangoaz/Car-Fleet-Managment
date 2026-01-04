""" Routes relatives aux entretiens des véhicules """

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import select, func, Session
from typing import Optional

from app.database import get_session
from app.models import Entretien, Vehicule
from app.schemas import Create_entretien

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
):
    vehicule = session.get(Vehicule, vehicule_id)
    if not vehicule:
        raise HTTPException(
            status_code=404,
            detail="Véhicule introuvable"
        )
    
    return vehicule.entretiens