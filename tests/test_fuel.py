def test_create_fuel_fill_ok(client, create_vehicule):
    # Création du véhicule
    vehicule = create_vehicule(
        plate="FUEL-001",
        model="Fuel Test",
        km=10000,
    )

    payload = {
        "date": "2026-01-10",
        "km": 10100,
        "liters": 45.5,
        "cost": 82.3,
    }

    response = client.post(
        f"/vehicules/{vehicule["id"]}/fuel-fills",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["vehicule_id"] == vehicule["id"]
    assert data["km"] == payload["km"]
    assert data["liters"] == payload["liters"]
    assert data["cost"] == payload["cost"]


def test_create_fuel_fill_invalid_km(client, create_vehicule):
    vehicule = create_vehicule(
        plate="FUEL-002",
        model="Fuel KM",
        km=10000,
    )

    # Premier plein OK
    client.post(
        f"/vehicules/{vehicule["id"]}/fuel-fills",
        json={
            "date": "2026-01-01",
            "km": 10100,
            "liters": 40,
            "cost": 70,
        },
    )

    # Second plein avec km invalide
    response = client.post(
        f"/vehicules/{vehicule["id"]}/fuel-fills",
        json={
            "date": "2026-01-02",
            "km": 10000,  # ⛔ inférieur
            "liters": 30,
            "cost": 55,
        },
    )

    assert response.status_code == 400


def test_get_fuel_fills_list(client, create_vehicule):
    vehicule = create_vehicule(
        plate="FUEL-003",
        model="Fuel List",
        km=5000,
    )

    client.post(
        f"/vehicules/{vehicule["id"]}/fuel-fills",
        json={
            "date": "2026-01-01",
            "km": 5200,
            "liters": 40,
            "cost": 70,
        },
    )

    client.post(
        f"/vehicules/{vehicule["id"]}/fuel-fills",
        json={
            "date": "2026-01-10",
            "km": 5600,
            "liters": 45,
            "cost": 80,
        },
    )

    response = client.get(f"/vehicules/{vehicule["id"]}/fuel-fills")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["km"] > data[1]["km"]  # tri descendant


def test_get_fuel_fill_ok(client, create_vehicule):
    vehicule = create_vehicule(
        plate="FUEL-004",
        model="Fuel Get",
        km=7000,
    )

    fuel_res = client.post(
        f"/vehicules/{vehicule["id"]}/fuel-fills",
        json={
            "date": "2026-01-05",
            "km": 7300,
            "liters": 42,
            "cost": 75,
        },
    )
    fuel_id = fuel_res.json()["id"]

    response = client.get(f"/vehicules/{vehicule["id"]}/fuel-fills/{fuel_id}")

    assert response.status_code == 200
    assert response.json()["id"] == fuel_id


def test_get_fuel_fill_wrong_vehicle(client, create_vehicule):
    v1 = create_vehicule(
        plate="FUEL-005",
        model="Fuel V1",
        km=8000,
    )

    v2 = create_vehicule(
        plate="FUEL-006",
        model="Fuel V2t",
        km=9000,
    )

    fuel_id = client.post(
        f"/vehicules/{v1["id"]}/fuel-fills",
        json={
            "date": "2026-01-10",
            "km": 8200,
            "liters": 40,
            "cost": 70,
        },
    ).json()["id"]

    response = client.get(f"/vehicules/{v2["id"]}/fuel-fills/{fuel_id}")

    assert response.status_code == 404


def test_patch_last_fuel_fill_ok(client, create_vehicule):
    vehicule = create_vehicule(
        plate="FUEL-007",
        model="Fuel Patch",
        km=10000,
    )

    fuel = client.post(
        f"/vehicules/{vehicule["id"]}/fuel-fills",
        json={
            "date": "2026-01-10",
            "km": 10200,
            "liters": 50,
            "cost": 90,
        },
    ).json()

    response = client.patch(
        f"/vehicules/{vehicule["id"]}/fuel-fills/{fuel['id']}",
        json={"cost": 95},
    )

    assert response.status_code == 200
    assert response.json()["cost"] == 95


def test_patch_non_last_fuel_fill_forbidden(client, create_vehicule):
    vehicule = create_vehicule(
        plate="FUEL-008",
        model="Fuel Patch KO",
        km=0000,
    )

    fuel1 = client.post(
        f"/vehicules/{vehicule["id"]}/fuel-fills",
        json={
            "date": "2026-01-01",
            "km": 9100,
            "liters": 40,
            "cost": 70,
        },
    ).json()

    client.post(
        f"/vehicules/{vehicule["id"]}/fuel-fills",
        json={
            "date": "2026-01-10",
            "km": 9500,
            "liters": 50,
            "cost": 85,
        },
    )

    response = client.patch(
        f"/vehicules/{vehicule["id"]}/fuel-fills/{fuel1['id']}",
        json={"cost": 75},
    )

    assert response.status_code == 400


def test_delete_last_fuel_fill_ok(client, create_vehicule):
    vehicule = create_vehicule(
        plate="FUEL-009",
        model="Fuel Delete",
        km=11000,
    )

    fuel = client.post(
        f"/vehicules/{vehicule["id"]}/fuel-fills",
        json={
            "date": "2026-01-10",
            "km": 11200,
            "liters": 45,
            "cost": 80,
        },
    ).json()

    response = client.delete(f"/vehicules/{vehicule["id"]}/fuel-fills/{fuel['id']}")

    assert response.status_code == 204


def test_delete_non_last_fuel_fill_forbidden(client, create_vehicule):
    vehicule = create_vehicule(
        plate="FUEL-010",
        model="Fuel Delete KO",
        km=10000,
    )

    fuel1 = client.post(
        f"/vehicules/{vehicule["id"]}/fuel-fills",
        json={
            "date": "2026-01-01",
            "km": 10100,
            "liters": 40,
            "cost": 70,
        },
    ).json()

    client.post(
        f"/vehicules/{vehicule["id"]}/fuel-fills",
        json={
            "date": "2026-01-10",
            "km": 10500,
            "liters": 50,
            "cost": 85,
        },
    )

    response = client.delete(f"/vehicules/{vehicule["id"]}/fuel-fills/{fuel1['id']}")

    assert response.status_code == 400
