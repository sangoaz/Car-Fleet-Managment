from app.services.fuel_stats import compute_fuel_stats
from app.schemas import Alert

COST_PER_KM_THRESHOLD = 0.15
CONSUMPTION_DRIFT_RATIO = 1.15


def compute_fuel_alerts(session, vehicule_id: int) -> list[dict]:
    stats = compute_fuel_stats(session, vehicule_id)
    alerts = []

    avg = stats["average_consumption"]
    rolling = stats["rolling_consumption"]
    cost_per_km = stats["cost_per_km"]

    # Dérive de consommation
    if avg and rolling and rolling > avg * CONSUMPTION_DRIFT_RATIO:
        alerts.append(
            Alert(
                type="FUEL",
                status="warning",
                message="Dérive de consommation détectée",
                details={
                    "average": avg,
                    "rolling": rolling,
                },
            )
        )

    # Cout de consommation élevé
    if cost_per_km and cost_per_km > COST_PER_KM_THRESHOLD:
        alerts.append(
            Alert(
                type="FUEL",
                status="alert",
                message="Coût carburant élevé",
                details={
                    "cost_per_km": cost_per_km,
                },
            )
        )

    return alerts
