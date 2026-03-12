from app.enums import UserRole


# Test de dérive de consommation
def test_fuel_consumption_drift_alert(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    vid = vehicule_db.id

    client.post(
        f"/vehicules/{vid}/fuel-fills",
        json={
            "date": "2026-01-01",
            "km": vehicule_db.km + 100,
            "liters": 30,
            "cost": 50,
        },
    )
    client.post(
        f"/vehicules/{vid}/fuel-fills",
        json={
            "date": "2026-01-10",
            "km": vehicule_db.km + 600,
            "liters": 30,
            "cost": 50,
        },
    )
    client.post(
        f"/vehicules/{vid}/fuel-fills",
        json={
            "date": "2026-01-20",
            "km": vehicule_db.km + 1100,
            "liters": 60,
            "cost": 80,
        },
    )
    client.post(
        f"/vehicules/{vid}/fuel-fills",
        json={
            "date": "2026-01-30",
            "km": vehicule_db.km + 1600,
            "liters": 65,
            "cost": 85,
        },
    )
    client.post(
        f"/vehicules/{vid}/fuel-fills",
        json={
            "date": "2026-02-10",
            "km": vehicule_db.km + 2100,
            "liters": 70,
            "cost": 90,
        },
    )

    res = client.get(f"/vehicules/{vid}/alerts")

    assert res.status_code == 200

    alerts = res.json()["alerts"]

    assert any(a["type"] == "FUEL" and "Dérive" in a["message"] for a in alerts)


# Test: Aucune alerte de carburant
def test_no_fuel_alert_when_normal(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    vid = vehicule_db.id

    client.post(
        f"/vehicules/{vid}/fuel-fills",
        json={
            "date": "2026-01-01",
            "km": vehicule_db.km + 100,
            "liters": 30,
            "cost": 50,
        },
    )

    client.post(
        f"/vehicules/{vid}/fuel-fills",
        json={
            "date": "2026-01-10",
            "km": vehicule_db.km + 600,
            "liters": 30,
            "cost": 50,
        },
    )

    res = client.get(f"/vehicules/{vid}/alerts")

    assert res.status_code == 200

    alerts = res.json()["alerts"]

    assert not any(a["type"] == "FUEL" for a in alerts)
