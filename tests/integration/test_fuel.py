from app.enums import UserRole
from app.models import Vehicule


# =========================
# TESTS DE CREATION
# =========================


def test_create_fuel_fill_ok(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    payload = {
        "date": "2026-01-10",
        "km": vehicule_db.km + 100,
        "liters": 45.5,
        "cost": 82.3,
    }

    response = client.post(
        f"/vehicules/{vehicule_db.id}/fuel-fills",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["vehicule_id"] == vehicule_db.id
    assert data["km"] == payload["km"]


def test_create_fuel_fill_invalid_km(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    client.post(
        f"/vehicules/{vehicule_db.id}/fuel-fills",
        json={
            "date": "2026-01-01",
            "km": vehicule_db.km + 100,
            "liters": 40,
            "cost": 70,
        },
    )

    response = client.post(
        f"/vehicules/{vehicule_db.id}/fuel-fills",
        json={
            "date": "2026-01-02",
            "km": vehicule_db.km,  # inférieur
            "liters": 30,
            "cost": 55,
        },
    )

    assert response.status_code == 400


# =========================
# TESTS D'AFFICHAGE
# =========================


def test_get_fuel_fill_without_auth_returns_401(client, vehicule_db):
    response = client.get(f"/vehicules/{vehicule_db.id}/fuel-fills")
    assert response.status_code == 401


def test_get_fuel_fills_list(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    client.post(
        f"/vehicules/{vehicule_db.id}/fuel-fills",
        json={
            "date": "2026-01-01",
            "km": vehicule_db.km + 200,
            "liters": 40,
            "cost": 70,
        },
    )

    client.post(
        f"/vehicules/{vehicule_db.id}/fuel-fills",
        json={
            "date": "2026-01-10",
            "km": vehicule_db.km + 600,
            "liters": 45,
            "cost": 80,
        },
    )

    response = client.get(f"/vehicules/{vehicule_db.id}/fuel-fills")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["km"] > data[1]["km"]


def test_get_fuel_fill_ok(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    fuel_res = client.post(
        f"/vehicules/{vehicule_db.id}/fuel-fills",
        json={
            "date": "2026-01-05",
            "km": vehicule_db.km + 300,
            "liters": 42,
            "cost": 75,
        },
    )

    fuel_id = fuel_res.json()["id"]

    response = client.get(f"/vehicules/{vehicule_db.id}/fuel-fills/{fuel_id}")

    assert response.status_code == 200
    assert response.json()["id"] == fuel_id


def test_get_fuel_fill_wrong_vehicle(auth_client, create_user, vehicule_db, session):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    v2 = Vehicule(
        plate="OTHER-001",
        model="Other Vehicle",
        km=5000,
        company_id=vehicule_db.company_id,
    )
    session.add(v2)
    session.commit()
    session.refresh(v2)

    # créer un fuel fill sur le premier véhicule
    fuel_id = client.post(
        f"/vehicules/{vehicule_db.id}/fuel-fills",
        json={
            "date": "2026-01-10",
            "km": vehicule_db.km + 200,
            "liters": 40,
            "cost": 70,
        },
    ).json()["id"]

    # essayer de lire avec le mauvais véhicule
    response = client.get(f"/vehicules/{v2.id}/fuel-fills/{fuel_id}")

    assert response.status_code == 404


def test_driver_can_read_fuel_same_company(auth_client, create_user, vehicule_db):
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)
    client = auth_client(driver)

    response = client.get(f"/vehicules/{vehicule_db.id}/fuel-fills")

    assert response.status_code == 200


def test_owner_cannot_read_fuel_other_company(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=999)
    client = auth_client(owner)

    response = client.get(f"/vehicules/{vehicule_db.id}/fuel-fills")

    assert response.status_code == 403


# =========================
# TESTS D'UPDATE
# =========================


def test_patch_last_fuel_fill_ok(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    fuel = client.post(
        f"/vehicules/{vehicule_db.id}/fuel-fills",
        json={
            "date": "2026-01-10",
            "km": vehicule_db.km + 200,
            "liters": 50,
            "cost": 90,
        },
    ).json()

    response = client.patch(
        f"/vehicules/{vehicule_db.id}/fuel-fills/{fuel['id']}",
        json={"cost": 95},
    )

    assert response.status_code == 200
    assert response.json()["cost"] == 95


def test_patch_non_last_fuel_fill_forbidden(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    fuel1 = client.post(
        f"/vehicules/{vehicule_db.id}/fuel-fills",
        json={
            "date": "2026-01-01",
            "km": vehicule_db.km + 100,
            "liters": 40,
            "cost": 70,
        },
    ).json()

    client.post(
        f"/vehicules/{vehicule_db.id}/fuel-fills",
        json={
            "date": "2026-01-10",
            "km": vehicule_db.km + 500,
            "liters": 50,
            "cost": 85,
        },
    )

    response = client.patch(
        f"/vehicules/{vehicule_db.id}/fuel-fills/{fuel1['id']}",
        json={"cost": 75},
    )

    assert response.status_code == 400


# ==========================
# TESTS DELETE
# ==========================


def test_delete_last_fuel_fill_ok(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    fuel = client.post(
        f"/vehicules/{vehicule_db.id}/fuel-fills",
        json={
            "date": "2026-01-10",
            "km": vehicule_db.km + 200,
            "liters": 45,
            "cost": 80,
        },
    ).json()

    response = client.delete(f"/vehicules/{vehicule_db.id}/fuel-fills/{fuel['id']}")

    assert response.status_code == 204


def test_delete_non_last_fuel_fill_forbidden(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    fuel1 = client.post(
        f"/vehicules/{vehicule_db.id}/fuel-fills",
        json={
            "date": "2026-01-01",
            "km": vehicule_db.km + 100,
            "liters": 40,
            "cost": 70,
        },
    ).json()

    client.post(
        f"/vehicules/{vehicule_db.id}/fuel-fills",
        json={
            "date": "2026-01-10",
            "km": vehicule_db.km + 500,
            "liters": 50,
            "cost": 85,
        },
    )

    response = client.delete(f"/vehicules/{vehicule_db.id}/fuel-fills/{fuel1['id']}")

    assert response.status_code == 400
