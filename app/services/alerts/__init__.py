from sqlmodel import Session
from app.models import Vehicule

from app.services.alerts.vidange import check_vidange_alert
from app.services.alerts.controle_technique import check_controle_technique_alert
from app.services.alerts.pneus import check_pneus_alert
from app.services.alerts.freins import check_freins_alert
from app.services.alerts.revision import check_revision_alert


def get_vehicle_alerts(session: Session, vehicule: Vehicule):
    alerts = []

    alerts.append(
        check_vidange_alert(
            session=session,
            vehicule_id=vehicule.id,
            vehicule_km=vehicule.km,
        )
    )

    alerts.append(
        check_controle_technique_alert(
            session=session,
            vehicule_id=vehicule.id,
        )
    )

    alerts.append(
        check_pneus_alert(
            session=session,
            vehicule_id=vehicule.id,
            vehicule_km=vehicule.km,
        )
    )

    alerts.append(
        check_freins_alert(
            session=session,
            vehicule_id=vehicule.id,
            vehicule_km=vehicule.km,
        )
    )

    alerts.append(
        check_revision_alert(
            session=session,
            vehicule_id=vehicule.id,
            vehicule_km=vehicule.km,
        )
    )

    return alerts
