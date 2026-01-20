from datetime import date

from app.models import Vehicule, FuelFill
from app.services.fuel_stats import compute_fuel_stats


# Creer un véhicule fictif
def create_vehicle(session, km=10000):
    vehicule = Vehicule(
        plate="STAT-001",
        model="Stats Car",
        km=km,
    )
    session.add(vehicule)
    session.commit()
    session.refresh(vehicule)
    return vehicule


# Creer un plein fictif
def create_fuel(session, vehicule_id, km, liters, cost):
    fuel = FuelFill(
        vehicule_id=vehicule_id,
        date=date.today(),
        km=km,
        liters=liters,
        cost=cost,
    )
    session.add(fuel)
    session.commit()


# Aucun plein enregistré
def test_fuel_stats_no_fuel(session):
    vehicule = create_vehicle(session)

    stats = compute_fuel_stats(session, vehicule.id)

    assert stats["total_km"] == 0
    assert stats["total_liters"] == 0
    assert stats["total_cost"] == 0
    assert stats["average_consumption"] is None
    assert stats["last_consumption"] is None


# Seulement 1 plein enregistré
def test_fuel_stats_one_fuel(session):
    vehicule = create_vehicle(session)

    create_fuel(session, vehicule.id, km=10100, liters=40, cost=70)

    stats = compute_fuel_stats(session, vehicule.id)

    assert stats["total_km"] == 0
    assert stats["total_liters"] == 40
    assert stats["total_cost"] == 70
    assert stats["average_consumption"] is None
    assert stats["last_consumption"] is None


# Deux pleins cohérents
def test_fuel_stats_two_fuels(session):
    vehicule = create_vehicle(session)

    create_fuel(session, vehicule.id, km=10000, liters=40, cost=60)
    create_fuel(session, vehicule.id, km=10500, liters=30, cost=50)

    stats = compute_fuel_stats(session, vehicule.id)

    # Dans le modèle, le premier plein est ignoré afin de calculer au mieux les prochaines moyennes de conso
    assert stats["total_km"] == 500
    assert stats["total_liters"] == 30
    assert stats["total_cost"] == 50
    assert stats["average_consumption"] == 6.0
    assert stats["last_consumption"] == 6.0


# Plusieurs pleins
def test_fuel_stats_multiple_fuels(session):
    vehicule = create_vehicle(session)

    create_fuel(session, vehicule.id, km=10000, liters=40, cost=60)
    create_fuel(session, vehicule.id, km=10500, liters=30, cost=50)
    create_fuel(session, vehicule.id, km=11000, liters=35, cost=55)

    stats = compute_fuel_stats(session, vehicule.id)

    assert stats["total_km"] == 1000
    assert stats["total_liters"] == 65
    assert stats["total_cost"] == 105
    assert stats["average_consumption"] == round((6.0 + 7.0) / 2, 2)
    assert stats["last_consumption"] == 7.0


# Pleins partiels
def test_fuel_stats_partial_fuels(session):
    vehicule = create_vehicle(session)

    create_fuel(session, vehicule.id, km=10000, liters=20, cost=30)
    create_fuel(session, vehicule.id, km=10300, liters=15, cost=25)
    create_fuel(session, vehicule.id, km=10600, liters=25, cost=40)

    stats = compute_fuel_stats(session, vehicule.id)

    assert stats["total_km"] == 600
    assert stats["average_consumption"] is not None


# Km identiques ou décroissants
def test_fuel_stats_ignore_invalid_km(session):
    vehicule = create_vehicle(session)

    create_fuel(session, vehicule.id, 10000, 40, 60)
    create_fuel(session, vehicule.id, 10000, 30, 50)  # km identique
    create_fuel(session, vehicule.id, 10500, 35, 55)

    stats = compute_fuel_stats(session, vehicule.id)

    assert stats["total_km"] == 500
    assert stats["average_consumption"] == 7.0


# Intervalle invalide au milieu

# Vérification total_km

# Vérification total_liters et total_cost

#
