from fastapi import HTTPException
from sqlmodel import select, Session
from datetime import date
from app.models import Entretien
from app.enums import EntretienType


def validate_entretien_coherence(
    session: Session,
    vehicule_id: int,
    entretien_type: EntretienType,
    date_: date,
    km: int,
    exclude_entretien_id: int | None = None,
):
    stmt = select(Entretien).where(
        Entretien.vehicule_id == vehicule_id,
        Entretien.type == entretien_type,
    )

    if exclude_entretien_id:
        stmt = stmt.where(Entretien.id != exclude_entretien_id)

    for e in session.scalars(stmt):
        if e.date > date_ and e.km < km:
            raise HTTPException(
                status_code=422,
                detail="Incohérence : kilométrage plus élevé dans le passé",
            )

        if e.date < date_ and e.km > km:
            raise HTTPException(
                status_code=422,
                detail="Incohérence : kilométrage plus faible dans le futur",
            )

        if e.date == date_ and e.km != km:
            raise HTTPException(
                status_code=422,
                detail="Incohérence : deux entretiens le même jour avec des kilométrages différents",
            )
