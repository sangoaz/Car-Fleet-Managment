from sqlmodel import Session, select

from app.models import FuelFill


def compute_fuel_stats(
    session: Session,  # Connexion à la base de donnée
    vehicule_id: int,  # Véhicule pour lequel on calcule les stats
):

    # Faire un statement pour interroger la db
    stmt = (
        select(FuelFill)
        .where(FuelFill.vehicule_id == vehicule_id)
        .order_by(FuelFill.km.asc())
    )

    fuels = session.exec(stmt).all()

    # fuels est une liste d'objet FuelFill
    # Ex:
    #   fuels = [
    #   FuelFill(km=10000, liters=40),
    #   FuelFill(km=10500, liters=42),
    #   FuelFill(km=11000, liters=45),
    #   ]

    # Cas particulier, si il n'y a pas assez de données:
    if len(fuels) < 2:
        return {
            "total_km": 0,
            "total_liters": sum(f.liters for f in fuels),
            "total_cost": sum(f.cost for f in fuels),
            "average_consumption": None,
            "last_consumption": None,
        }

    # Initialisation des accumulateurs
    total_km = 0
    total_liters = 0
    total_cost = 0
    consumptions = []

    # Mettre en pair les pleins précédents et suivant
    for prev, curr in zip(fuels, fuels[1:]):
        km_diff = curr.km - prev.km
        if km_diff <= 0:
            continue

        # Calcul de la consommation
        conso = (curr.liters / km_diff) * 100
        consumptions.append(conso)

        # Mise en place des valeurs
        total_km += km_diff
        total_liters += curr.liters
        total_cost += curr.cost

    return {
        "total_km": total_km,
        "total_liters": round(total_liters, 2),
        "total_cost": round(total_cost, 2),
        "average_consumption": (
            round(sum(consumptions) / len(consumptions), 2) if consumptions else None
        ),
        "last_consumption": round(consumptions[-1], 2) if consumptions else None,
    }


# Attention, le modèle ne fonctionne pas si un plein est oublié, cela va fausser les moyennes de consommation.
