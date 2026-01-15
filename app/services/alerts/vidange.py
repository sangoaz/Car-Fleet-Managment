from datetime import date
from sqlmodel import select, Session

from app.models import Entretien
from app.enums import EntretienType
from app.services.alerts.base import Alert


VIDANGE_INTERVAL_KM = 15000
VIDANGE_INTERVAL_DAYS = 365


def check_vidange_alert(
    session: Session,
    vehicule_id: int,
    vehicule_km: int,
) -> Alert:
    stmt = (
        select(Entretien)
        .where(
            Entretien.vehicule_id == vehicule_id,
            Entretien.type == EntretienType.VIDANGE,
        )
        .order_by(Entretien.date.desc())
        .limit(1)
    )

    last = session.scalars(stmt).first()

    if not last:
        return Alert(
            type="VIDANGE",
            status="warning",
            message="Aucune vidange enregistrée",
        )

    km_since = vehicule_km - last.km
    days_since = (date.today() - last.date).days

    if km_since >= VIDANGE_INTERVAL_KM or days_since >= VIDANGE_INTERVAL_DAYS:
        return Alert(
            type="VIDANGE",
            status="alert",
            message="Vidange à prévoir",
        )

    return Alert(type="VIDANGE", status="ok")
