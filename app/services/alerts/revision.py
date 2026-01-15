from datetime import date
from sqlmodel import select, Session
from app.models import Entretien
from app.enums import EntretienType
from app.services.alerts.base import Alert

REVISION_INTERVAL_KM = 30000
REVISION_INTERVAL_DAYS = 730


def check_revision_alert(
    session: Session,
    vehicule_id: int,
    vehicule_km: int,
) -> Alert:
    stmt = (
        select(Entretien)
        .where(
            Entretien.vehicule_id == vehicule_id,
            Entretien.type == EntretienType.REVISION,
        )
        .order_by(Entretien.date.desc())
        .limit(1)
    )

    last = session.scalars(stmt).first()

    if not last:
        return Alert(
            type="REVISION",
            status="warning",
            message="Aucune révision enregistrée",
        )

    km_since = vehicule_km - last.km
    days_since = (date.today() - last.date).days

    if km_since >= REVISION_INTERVAL_KM or days_since >= REVISION_INTERVAL_DAYS:
        return Alert(
            type="REVISION",
            status="alert",
            message="Révision à prévoir",
        )

    return Alert(type="REVISION", status="ok")
