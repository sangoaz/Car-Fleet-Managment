from datetime import date
from sqlmodel import select, Session

from app.models import Entretien
from app.enums import EntretienType
from app.services.alerts.base import Alert


CT_INTERVAL_DAYS = 730


def check_controle_technique_alert(
    session: Session,
    vehicule_id: int,
) -> Alert:
    stmt = (
        select(Entretien)
        .where(
            Entretien.vehicule_id == vehicule_id,
            Entretien.type == EntretienType.CONTROLE_TECHNIQUE,
        )
        .order_by(Entretien.date.desc())
        .limit(1)
    )

    last = session.scalars(stmt).first()

    if not last:
        return Alert(
            type="CONTROLE_TECHNIQUE",
            status="warning",
            message="Aucun contrôle technique enregistré",
        )

    days_since = (date.today() - last.date).days

    if days_since >= CT_INTERVAL_DAYS:
        return Alert(
            type="CONTROLE_TECHNIQUE",
            status="alert",
            message="Contrôle technique expiré",
        )

    return Alert(type="CONTROLE_TECHNIQUE", status="ok")
