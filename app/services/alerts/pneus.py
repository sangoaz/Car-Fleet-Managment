from sqlmodel import select, Session
from app.models import Entretien
from app.enums import EntretienType
from app.services.alerts.base import Alert

PNEUS_INTERVAL_KM = 40000


def check_pneus_alert(
    session: Session,
    vehicule_id: int,
    vehicule_km: int,
) -> Alert:
    stmt = (
        select(Entretien)
        .where(
            Entretien.vehicule_id == vehicule_id,
            Entretien.type == EntretienType.PNEUS,
        )
        .order_by(Entretien.date.desc())
        .limit(1)
    )

    last = session.scalars(stmt).first()

    if not last:
        return Alert(
            type="PNEUS",
            status="warning",
            message="Aucun changement de pneus enregistré",
        )

    if vehicule_km - last.km >= PNEUS_INTERVAL_KM:
        return Alert(
            type="PNEUS",
            status="alert",
            message="Changement de pneus à prévoir",
        )

    return Alert(type="PNEUS", status="ok")
