from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import FuelFill, Entretien, Vehicule
from app.schemas import FuelFillUpdate


# Récuperer le dernier plein
def get_last_known_km(session: Session, vehicule_id: int) -> int | None:
    """
    Source de vérité du kilométrage :
    1. Dernier plein
    2. Dernier entretien
    3. Km du véhicule
    """

    last_fuel = session.exec(
        select(FuelFill)
        .where(FuelFill.vehicule_id == vehicule_id)
        .order_by(FuelFill.km.desc())
    ).first()

    if last_fuel:
        return last_fuel.km

    last_entretien = session.exec(
        select(Entretien)
        .where(Entretien.vehicule_id == vehicule_id)
        .order_by(Entretien.km.desc())
    ).first()

    if last_entretien:
        return last_entretien.km

    vehicule = session.get(Vehicule, vehicule_id)
    return vehicule.km if vehicule else None


# Valider uniquement les saisies de km croissants + données carburant cohérentes
def validate_km(
    session: Session, vehicule_id: int, km: int, liters: float, cost: float
):
    last_km = get_last_known_km(session, vehicule_id)

    # Validation kilométrage
    if last_km is not None and km <= last_km:
        raise HTTPException(
            status_code=400, detail=f"Kilométrage invalide (dernier connu: {last_km})"
        )

    # Validation litres
    if liters <= 0:
        raise HTTPException(
            status_code=400, detail="Le volume de carburant doit être suppérieur à 0"
        )

    # Validation coût
    if cost < 0:
        raise HTTPException(status_code=400, detail="Le coût ne peut pas être négatif")


# =========================
# UPDATES DES PLEINS
# =========================


# Récuperer le précédent plein
def get_previous_fuel_fill(session: Session, fuel_fill: FuelFill) -> FuelFill | None:
    stmt = (
        select(FuelFill)
        .where(FuelFill.vehicule_id == fuel_fill.vehicule_id)
        .where(FuelFill.km < fuel_fill.km)
        .order_by(FuelFill.km.desc())
    )
    return session.exec(stmt).first()


# Vérifier si c'est le dernier plein
def is_last_fuel_fill(session: Session, fuel_fill: FuelFill) -> bool:
    stmt = (
        select(FuelFill)
        .where(FuelFill.vehicule_id == fuel_fill.vehicule_id)
        .where(FuelFill.km > fuel_fill.km)
    )
    return session.exec(stmt).first() is None


# Validation de l'update du plein
def validate_fuel_fill_update(
    session: Session, fuel_fill: FuelFill, update: FuelFillUpdate
):
    if not is_last_fuel_fill(session, fuel_fill):
        raise HTTPException(
            status_code=400, detail="Seul le dernier plein peut être modifié"
        )

    if update.km is not None:
        previous = get_previous_fuel_fill(session, fuel_fill)
        if previous and update.km <= previous.km:
            raise HTTPException(
                400, "Le kilométrage doit être supérieur au plein précédent"
            )

    if update.liters is not None and update.liters <= 0:
        raise HTTPException(400, "Litres invalides")

    if update.cost is not None and update.cost <= 0:
        raise HTTPException(400, "Coût invalide")
