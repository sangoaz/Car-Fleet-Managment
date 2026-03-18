"""Routes relatives aux alertes métier des véhicules"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.deps.auth import get_current_user
from app.models import Vehicule, User
from app.permissions.vehicules import can_read_vehicle
from app.schemas import VehiculeAlertsResponse
from app.services.alerts.vidange import check_vidange_alert
from app.services.alerts.pneus import check_pneus_alert
from app.services.alerts.freins import check_freins_alert
from app.services.alerts.revision import check_revision_alert
from app.services.alerts.controle_technique import check_controle_technique_alert
from app.services.alerts.fuel import compute_fuel_alerts
from app.utils.vehicules import get_vehicule_or_404

router = APIRouter(
    prefix="/vehicules",
    tags=["alerts"],
)


@router.get("/{vehicule_id}/alerts", response_model=VehiculeAlertsResponse)
def get_vehicule_alerts(
    vehicule_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    vehicule = get_vehicule_or_404(session, vehicule_id)

    if not can_read_vehicle(current_user, vehicule):
        raise HTTPException(status_code=403, detail="Not allowed")

    alerts = []

    alerts.extend(
        filter(
            None,
            [
                check_vidange_alert(session, vehicule.id, vehicule.km),
                check_pneus_alert(session, vehicule.id, vehicule.km),
                check_freins_alert(session, vehicule.id, vehicule.km),
                check_revision_alert(session, vehicule.id, vehicule.km),
                check_controle_technique_alert(session, vehicule.id),
            ],
        )
    )

    alerts.extend(compute_fuel_alerts(session, vehicule_id))

    return {
        "vehicule_id": vehicule.id,
        "alerts": alerts,
    }
