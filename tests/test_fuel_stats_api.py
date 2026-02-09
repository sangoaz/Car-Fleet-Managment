# Vérifier l'accessibilité de la route
def test_get_fuel_stats_ok(client, create_vehicule):
    # Création du véhicule
    vehicule = create_vehicule(
        plate="STATS-API",
        model="Stats API",
        km=10000,
    )

    response = client.get(f"/vehicules/{vehicule["id"]}/fuel-stats")

    assert response.status_code == 200

    data = response.json()
    assert "total_km" in data
    assert "average_consumption" in data
    assert "rolling_consumption" in data
    assert "cost_per_km" in data


# Test stats cohérentes avec des pleins
def test_get_fuel_stats_with_fuels(client, create_vehicule):
    # Création du véhicule
    vehicule = create_vehicule(
        plate="STAT-API-2",
        model="Stats API 2",
        km=10000,
    )

    client.post(
        f"/vehicules/{vehicule["id"]}/fuel-fills",
        json={
            "date": "2026-01-01",
            "km": 10100,  # 👈 strictement supérieur
            "liters": 40,
            "cost": 60,
        },
    )
    client.post(
        f"/vehicules/{vehicule["id"]}/fuel-fills",
        json={
            "date": "2026-01-10",
            "km": 10600,
            "liters": 30,
            "cost": 50,
        },
    )

    response = client.get(f"/vehicules/{vehicule["id"]}/fuel-stats")

    data = response.json()
    assert data["total_km"] == 500
    assert data["average_consumption"] == 6.0
