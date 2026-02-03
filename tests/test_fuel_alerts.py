# Test de dérive de consommation
def test_fuel_consumption_drift_alert(client):
    vehicule = client.post(
        "/vehicules",
        json={"plate": "ALERT-001", "model": "Fuel Alert", "km": 10000},
    ).json()

    vid = vehicule["id"]

    client.post(
        f"/vehicules/{vid}/fuel-fills",
        json={"date": "2026-01-01", "km": 10100, "liters": 30, "cost": 50},  # 6.0
    )
    client.post(
        f"/vehicules/{vid}/fuel-fills",
        json={"date": "2026-01-10", "km": 10600, "liters": 30, "cost": 50},  # 6.0
    )
    client.post(
        f"/vehicules/{vid}/fuel-fills",
        json={"date": "2026-01-20", "km": 11100, "liters": 60, "cost": 80},  # 12.0
    )
    client.post(
        f"/vehicules/{vid}/fuel-fills",
        json={"date": "2026-01-30", "km": 11600, "liters": 65, "cost": 85},  # 13.0
    )
    client.post(
        f"/vehicules/{vid}/fuel-fills",
        json={"date": "2026-02-10", "km": 12100, "liters": 70, "cost": 90},  # 14.0
    )

    res = client.get(f"/vehicules/{vid}/alerts")
    alerts = res.json()["alerts"]

    assert any(a["type"] == "FUEL" and "Dérive" in a["message"] for a in alerts)


# Test: Aucune alerte de carburant
def test_no_fuel_alert_when_normal(client):
    vehicule = client.post(
        "/vehicules",
        json={"plate": "ALERT-002", "model": "Fuel OK", "km": 10000},
    ).json()

    vid = vehicule["id"]

    client.post(
        f"/vehicules/{vid}/fuel-fills",
        json={"date": "2026-01-01", "km": 10100, "liters": 30, "cost": 50},
    )
    client.post(
        f"/vehicules/{vid}/fuel-fills",
        json={"date": "2026-01-10", "km": 10600, "liters": 30, "cost": 50},
    )

    res = client.get(f"/vehicules/{vid}/alerts")
    data = res.json()
    alerts = data["alerts"]

    assert not any(a["type"] == "FUEL" for a in alerts)
