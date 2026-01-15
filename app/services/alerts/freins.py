from sqlmodel import select, Session
from app.models import Entretien
from app.enums import EntretienType
from app.services.alerts.base import Alert

FREINS_INTERVAL_KM = 60000


def check_freins_alert(
    session: Session,
    vehicule_id: int,
    vehicule_km: int,
) -> Alert:
    stmt = (
        select(Entretien)
        .where(
            Entretien.vehicule_id == vehicule_id,
            Entretien.type == EntretienType.FREINS,
        )
        .order_by(Entretien.date.desc())
        .limit(1)
    )

    last = session.scalars(stmt).first()

    if not last:
        return Alert(
            type="FREINS",
            status="warning",
            message="Aucun entretien des freins enregistré",
        )

    if vehicule_km - last.km >= FREINS_INTERVAL_KM:
        return Alert(
            type="FREINS",
            status="alert",
            message="Contrôle des freins recommandé",
        )

    return Alert(type="FREINS", status="ok")
