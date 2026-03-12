from app.enums import UserRole


# Vérifier l'accessibilité de la route
def test_get_fuel_stats_ok(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    response = client.get(f"/vehicules/{vehicule_db.id}/fuel-stats")

    assert response.status_code == 200

    data = response.json()

    assert "total_km" in data
    assert "average_consumption" in data
    assert "rolling_consumption" in data
    assert "cost_per_km" in data


# Test stats cohérentes avec des pleins
def test_get_fuel_stats_with_fuels(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    client.post(
        f"/vehicules/{vehicule_db.id}/fuel-fills",
        json={
            "date": "2026-01-01",
            "km": vehicule_db.km + 100,
            "liters": 40,
            "cost": 60,
        },
    )

    client.post(
        f"/vehicules/{vehicule_db.id}/fuel-fills",
        json={
            "date": "2026-01-10",
            "km": vehicule_db.km + 600,
            "liters": 30,
            "cost": 50,
        },
    )

    response = client.get(f"/vehicules/{vehicule_db.id}/fuel-stats")

    assert response.status_code == 200

    data = response.json()

    assert data["total_km"] == 500
    assert data["average_consumption"] == 6.0
