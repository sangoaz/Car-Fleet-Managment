import pytest
from datetime import date

from app.enums import UserRole, EntretienType
from app.models import Entretien, Vehicule, VehiculeAssignment
from datetime import date, UTC, datetime


# =========================
# TESTS DE CREATION
# =========================


def test_admin_can_create_entretien(auth_client, create_user, vehicule_db):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    payload = {
        "type": "VIDANGE",
        "date": "2026-01-01",
        "km": 10000,
        "cost": 100,
    }

    response = client.post(f"/vehicules/{vehicule_db.id}/entretiens", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["vehicule_id"] == vehicule_db.id
    assert data["type"] == "VIDANGE"
    assert data["km"] == 10000
    assert data["cost"] == 100


def test_owner_can_create_entretien_same_company(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    payload = {
        "type": "VIDANGE",
        "date": "2026-01-01",
        "km": 10000,
        "cost": 100,
    }

    response = client.post(f"/vehicules/{vehicule_db.id}/entretiens", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["vehicule_id"] == vehicule_db.id
    assert data["type"] == "VIDANGE"
    assert data["km"] == 10000
    assert data["cost"] == 100


def test_manager_can_create_entretien_same_company(
    auth_client, create_user, vehicule_db
):
    manager = create_user(UserRole.MANAGER, company_id=vehicule_db.company_id)
    client = auth_client(manager)

    payload = {
        "type": "VIDANGE",
        "date": "2026-01-01",
        "km": 10000,
        "cost": 100,
    }

    response = client.post(f"/vehicules/{vehicule_db.id}/entretiens", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["vehicule_id"] == vehicule_db.id
    assert data["type"] == "VIDANGE"
    assert data["km"] == 10000
    assert data["cost"] == 100


def test_owner_cannot_create_entretien_other_company(
    auth_client, create_user, vehicule_db
):
    # OWNER dans une autre company
    owner = create_user(UserRole.OWNER, company_id=999)
    client = auth_client(owner)

    payload = {
        "type": "VIDANGE",
        "date": "2026-01-01",
        "km": 10000,
        "cost": 100,
    }

    response = client.post(
        f"/vehicules/{vehicule_db.id}/entretiens",
        json=payload,
    )

    assert response.status_code == 403


def test_manager_cannot_create_entretien_other_company(
    auth_client, create_user, vehicule_db
):
    # MANAGER dans une autre company
    manager = create_user(UserRole.MANAGER, company_id=999)
    client = auth_client(manager)

    payload = {
        "type": "VIDANGE",
        "date": "2026-01-01",
        "km": 10000,
        "cost": 100,
    }

    response = client.post(
        f"/vehicules/{vehicule_db.id}/entretiens",
        json=payload,
    )

    assert response.status_code == 403


def test_driver_cannot_create_entretien(auth_client, create_user, vehicule_db):
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)
    client = auth_client(driver)

    payload = {
        "type": "VIDANGE",
        "date": "2026-01-01",
        "km": 10000,
        "cost": 100,
    }

    response = client.post(
        f"/vehicules/{vehicule_db.id}/entretiens",
        json=payload,
    )

    assert response.status_code == 403


def test_create_entretien_vehicule_not_found(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.post(
        "/vehicules/999999/entretiens",
        json={
            "date": "2025-01-01",
            "km": 10000,
            "type": "VIDANGE",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Véhicule introuvable"


def test_create_entretien_updates_vehicule_km(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    # Création d’un entretien avec km supérieur
    response = client.post(
        f"/vehicules/{vehicule_db.id}/entretiens",
        json={
            "date": "2025-01-01",
            "km": vehicule_db.km + 5000,
            "type": "VIDANGE",
            "cost": 100,
        },
    )

    assert response.status_code == 201

    # Vérifier que le km du véhicule a été mis à jour
    res = client.get(f"/vehicules/{vehicule_db.id}")
    assert res.status_code == 200
    assert res.json()["km"] == vehicule_db.km + 5000


def test_create_entretien_does_not_lower_vehicule_km(
    auth_client, create_user, vehicule_db
):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    original_km = vehicule_db.km

    # Entretien historique avec km inférieur
    response = client.post(
        f"/vehicules/{vehicule_db.id}/entretiens",
        json={
            "date": "2024-01-01",
            "km": original_km - 1000,
            "type": "VIDANGE",
            "cost": 100,
        },
    )

    assert response.status_code == 201

    # Vérifier que le km n’a pas diminué
    res = client.get(f"/vehicules/{vehicule_db.id}")
    assert res.status_code == 200
    assert res.json()["km"] == original_km


def test_cannot_create_entretien_with_lower_km_in_future(
    auth_client, create_user, vehicule_db
):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    # Vidange valide
    res1 = client.post(
        f"/vehicules/{vehicule_db.id}/entretiens",
        json={
            "date": "2025-01-01",
            "km": 50000,
            "type": "VIDANGE",
            "cost": 100,
        },
    )
    assert res1.status_code == 201

    # Vidange incohérente (future mais km plus bas)
    res2 = client.post(
        f"/vehicules/{vehicule_db.id}/entretiens",
        json={
            "date": "2026-01-01",
            "km": 40000,
            "type": "VIDANGE",
            "cost": 100,
        },
    )

    assert res2.status_code == 422


def test_cannot_create_entretien_with_higher_km_in_past(
    auth_client, create_user, vehicule_db
):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    res1 = client.post(
        f"/vehicules/{vehicule_db.id}/entretiens",
        json={
            "date": "2025-01-01",
            "km": 50000,
            "type": "VIDANGE",
            "cost": 100,
        },
    )
    assert res1.status_code == 201

    res2 = client.post(
        f"/vehicules/{vehicule_db.id}/entretiens",
        json={
            "date": "2024-01-01",
            "km": 60000,
            "type": "VIDANGE",
            "cost": 100,
        },
    )

    assert res2.status_code == 422


def test_can_create_entretien_history(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    res = client.post(
        f"/vehicules/{vehicule_db.id}/entretiens",
        json={
            "date": "2024-01-01",
            "km": 40000,
            "type": "VIDANGE",
            "cost": 100,
        },
    )

    assert res.status_code == 201


# =========================
# TESTS D'AFFICHAGE
# =========================


def test_get_entretiens_without_auth_returns_401(client, vehicule_db):
    response = client.get(f"/vehicules/{vehicule_db.id}/entretiens")
    assert response.status_code == 401


def test_admin_can_get_entretiens(auth_client, create_user, vehicule_db, entretien_db):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.get(f"/vehicules/{vehicule_db.id}/entretiens")

    assert response.status_code == 200
    data = response.json()

    assert data["total_count"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.parametrize("role", [UserRole.OWNER, UserRole.MANAGER])
def test_owner_manager_can_get_entretiens_same_company(
    auth_client, create_user, vehicule_db, entretien_db, role
):
    user = create_user(role, company_id=vehicule_db.company_id)
    client = auth_client(user)

    response = client.get(f"/vehicules/{vehicule_db.id}/entretiens")

    assert response.status_code == 200


@pytest.mark.parametrize("role", [UserRole.OWNER, UserRole.MANAGER])
def test_owner_manager_cannot_get_entretiens_other_company(
    auth_client, create_user, vehicule_db, entretien_db, role
):
    user = create_user(role, company_id=999)
    client = auth_client(user)

    response = client.get(f"/vehicules/{vehicule_db.id}/entretiens")

    assert response.status_code == 403


def test_driver_can_read_assigned_vehicle_entretiens(
    auth_client, create_user, vehicule_db, session
):
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)

    # Assignation
    assignment = VehiculeAssignment(
        vehicule_id=vehicule_db.id,
        user_id=driver.id,
    )
    session.add(assignment)

    # Entretien
    entretien = Entretien(
        vehicule_id=vehicule_db.id,
        type=EntretienType.VIDANGE,
        date=date.today(),
        km=vehicule_db.km + 100,
    )
    session.add(entretien)

    session.commit()

    client = auth_client(driver)

    res = client.get(f"/vehicules/{vehicule_db.id}/entretiens")

    assert res.status_code == 200

    data = res.json()

    assert data["total_count"] == 1
    assert len(data["items"]) == 1


def test_driver_cannot_read_unassigned_vehicle_entretiens(
    auth_client, create_user, vehicule_db, session
):
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)

    # Entretien existant mais PAS d'assignation
    entretien = Entretien(
        vehicule_id=vehicule_db.id,
        type=EntretienType.VIDANGE,
        date=date.today(),
        km=vehicule_db.km + 100,
    )
    session.add(entretien)
    session.commit()

    client = auth_client(driver)

    res = client.get(f"/vehicules/{vehicule_db.id}/entretiens")

    assert res.status_code == 403


def test_driver_cannot_read_after_unassignment(
    auth_client, create_user, vehicule_db, session
):
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)

    assignment = VehiculeAssignment(
        vehicule_id=vehicule_db.id,
        user_id=driver.id,
        end_date=datetime.now(UTC),
    )
    session.add(assignment)

    entretien = Entretien(
        vehicule_id=vehicule_db.id,
        type=EntretienType.VIDANGE,
        date=date.today(),
        km=vehicule_db.km + 100,
    )
    session.add(entretien)

    session.commit()

    client = auth_client(driver)

    res = client.get(f"/vehicules/{vehicule_db.id}/entretiens")

    assert res.status_code == 403


def test_driver_cannot_get_entretien_without_assignment(
    auth_client, create_user, vehicule_db, entretien_db
):
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)
    client = auth_client(driver)

    response = client.get(f"/vehicules/{vehicule_db.id}/entretiens")

    assert response.status_code == 403


def test_driver_cannot_get_entretien_other_company(
    auth_client, create_user, vehicule_db, entretien_db
):
    driver = create_user(UserRole.DRIVER, company_id=999)
    client = auth_client(driver)

    response = client.get(f"/vehicules/{vehicule_db.id}/entretiens")

    assert response.status_code == 403


def test_get_entretiens_vehicle_not_found(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.get("/vehicules/99999/entretiens")

    assert response.status_code == 404


def test_get_entretiens_pagination(auth_client, create_user, vehicule_db, session):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    # créer plusieurs entretiens
    for i in range(5):
        session.add(
            Entretien(
                vehicule_id=vehicule_db.id,
                type=EntretienType.VIDANGE,
                date=date(2025, 1, i + 1),
                km=vehicule_db.km + i + 1,
                cost=100,
            )
        )
    session.commit()

    response = client.get(f"/vehicules/{vehicule_db.id}/entretiens?limit=2&offset=0")

    assert response.status_code == 200
    data = response.json()

    assert data["total_count"] >= 5
    assert len(data["items"]) == 2


def test_get_entretiens_filter_by_type(auth_client, create_user, vehicule_db, session):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    session.add(
        Entretien(
            vehicule_id=vehicule_db.id,
            type=EntretienType.FREINS,
            date=date(2025, 1, 1),
            km=vehicule_db.km + 100,
            cost=100,
        )
    )
    session.commit()

    response = client.get(
        f"/vehicules/{vehicule_db.id}/entretiens?entretien_type=FREINS"
    )

    assert response.status_code == 200
    data = response.json()

    assert all(item["type"] == "FREINS" for item in data["items"])


def test_get_entretiens_empty(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    res = client.get(f"/vehicules/{vehicule_db.id}/entretiens")

    assert res.status_code == 200
    data = res.json()

    assert data["total_count"] == 0
    assert data["items"] == []


# =========================
# TESTS D'UPDATE
# =========================


def test_patch_entretien_without_auth_returns_401(client, vehicule_db, entretien_db):
    response = client.patch(
        f"/vehicules/{vehicule_db.id}/entretiens/{entretien_db.id}",
        json={"km": 99999},
    )
    assert response.status_code == 401


def test_admin_can_patch_entretien(auth_client, create_user, vehicule_db, entretien_db):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.patch(
        f"/vehicules/{vehicule_db.id}/entretiens/{entretien_db.id}",
        json={"km": entretien_db.km + 1000},
    )

    assert response.status_code == 200
    assert response.json()["km"] == entretien_db.km + 1000


@pytest.mark.parametrize("role", [UserRole.OWNER, UserRole.MANAGER])
def test_owner_manager_can_patch_same_company(
    auth_client, create_user, vehicule_db, entretien_db, role
):
    user = create_user(role, company_id=vehicule_db.company_id)
    client = auth_client(user)

    response = client.patch(
        f"/vehicules/{vehicule_db.id}/entretiens/{entretien_db.id}",
        json={"cost": 999},
    )

    assert response.status_code == 200
    assert response.json()["cost"] == 999


@pytest.mark.parametrize("role", [UserRole.OWNER, UserRole.MANAGER])
def test_owner_manager_cannot_patch_other_company(
    auth_client, create_user, vehicule_db, entretien_db, role
):
    user = create_user(role, company_id=999)
    client = auth_client(user)

    response = client.patch(
        f"/vehicules/{vehicule_db.id}/entretiens/{entretien_db.id}",
        json={"km": 99999},
    )

    assert response.status_code == 403


def test_driver_cannot_patch_entretien(
    auth_client, create_user, vehicule_db, entretien_db
):
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)
    client = auth_client(driver)

    response = client.patch(
        f"/vehicules/{vehicule_db.id}/entretiens/{entretien_db.id}",
        json={"km": 99999},
    )

    assert response.status_code == 403


def test_patch_entretien_vehicle_not_found(auth_client, create_user, entretien_db):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.patch(
        f"/vehicules/99999/entretiens/{entretien_db.id}",
        json={"km": 99999},
    )

    assert response.status_code == 404


def test_patch_entretien_not_found(auth_client, create_user, vehicule_db):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.patch(
        f"/vehicules/{vehicule_db.id}/entretiens/99999",
        json={"km": 99999},
    )

    assert response.status_code == 404


def test_patch_entretien_wrong_vehicle(
    auth_client, create_user, vehicule_db, entretien_db, session
):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    # créer un autre véhicule
    other_vehicle = Vehicule(
        plate="OTHER",
        model="Other",
        km=1000,
        company_id=vehicule_db.company_id,
    )
    session.add(other_vehicle)
    session.commit()
    session.refresh(other_vehicle)

    response = client.patch(
        f"/vehicules/{other_vehicle.id}/entretiens/{entretien_db.id}",
        json={"km": 99999},
    )

    assert response.status_code == 404


def test_patch_entretien_invalid_km(
    auth_client, create_user, vehicule_db, entretien_db
):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    response = client.patch(
        f"/vehicules/{vehicule_db.id}/entretiens/{entretien_db.id}",
        json={"km": -10},
    )

    assert response.status_code == 400


def test_patch_entretien_coherence_violation(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    # Entretien 1
    res1 = client.post(
        f"/vehicules/{vehicule_db.id}/entretiens",
        json={
            "date": "2025-01-01",
            "km": 50000,
            "type": "VIDANGE",
            "cost": 100,
        },
    )
    assert res1.status_code == 201
    entretien1_id = res1.json()["id"]

    # Entretien 2
    res2 = client.post(
        f"/vehicules/{vehicule_db.id}/entretiens",
        json={
            "date": "2026-01-01",
            "km": 60000,
            "type": "VIDANGE",
            "cost": 100,
        },
    )
    assert res2.status_code == 201

    # PATCH incohérent : date future mais km plus bas
    res_patch = client.patch(
        f"/vehicules/{vehicule_db.id}/entretiens/{entretien1_id}",
        json={
            "date": "2030-01-01",
            "km": 40000,
        },
    )

    assert res_patch.status_code == 422


def test_patch_entretien_updates_vehicule_km(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    # Création entretien initial
    res = client.post(
        f"/vehicules/{vehicule_db.id}/entretiens",
        json={
            "date": "2025-01-01",
            "km": vehicule_db.km + 1000,
            "type": "VIDANGE",
            "cost": 100,
        },
    )
    assert res.status_code == 201
    entretien_id = res.json()["id"]

    # PATCH avec km supérieur
    res_patch = client.patch(
        f"/vehicules/{vehicule_db.id}/entretiens/{entretien_id}",
        json={"km": vehicule_db.km + 5000},
    )
    assert res_patch.status_code == 200

    # Le km du véhicule DOIT être mis à jour
    res_vehicle = client.get(f"/vehicules/{vehicule_db.id}")
    assert res_vehicle.status_code == 200
    assert res_vehicle.json()["km"] == vehicule_db.km + 5000


def test_patch_entretien_does_not_decrease_vehicule_km(
    auth_client, create_user, vehicule_db
):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    # Création entretien initial avec km supérieur
    res = client.post(
        f"/vehicules/{vehicule_db.id}/entretiens",
        json={
            "date": "2025-01-01",
            "km": 60000,
            "type": "VIDANGE",
            "cost": 100,
        },
    )
    assert res.status_code == 201
    entretien_id = res.json()["id"]

    # PATCH avec km valide mais inférieur au max historique
    res_patch = client.patch(
        f"/vehicules/{vehicule_db.id}/entretiens/{entretien_id}",
        json={"km": 55000},
    )

    assert res_patch.status_code == 200

    # Vérifier que le km véhicule reste le plus haut
    res_vehicle = client.get(f"/vehicules/{vehicule_db.id}")
    assert res_vehicle.status_code == 200
    assert res_vehicle.json()["km"] == 60000


# ==========================
# TESTS DELETE
# ==========================


def test_delete_entretien_without_auth_returns_401(client, vehicule_db, entretien_db):
    response = client.delete(
        f"/vehicules/{vehicule_db.id}/entretiens/{entretien_db.id}"
    )
    assert response.status_code == 401


def test_admin_can_delete_entretien(
    auth_client, create_user, vehicule_db, entretien_db
):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.delete(
        f"/vehicules/{vehicule_db.id}/entretiens/{entretien_db.id}"
    )

    assert response.status_code == 204


def test_owner_can_delete_same_company(
    auth_client, create_user, vehicule_db, entretien_db
):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    response = client.delete(
        f"/vehicules/{vehicule_db.id}/entretiens/{entretien_db.id}"
    )

    assert response.status_code == 204


def test_manager_cannot_delete_entretien(
    auth_client, create_user, vehicule_db, entretien_db
):
    manager = create_user(UserRole.MANAGER, company_id=vehicule_db.company_id)
    client = auth_client(manager)

    response = client.delete(
        f"/vehicules/{vehicule_db.id}/entretiens/{entretien_db.id}"
    )

    assert response.status_code == 403


def test_driver_cannot_delete_entretien(
    auth_client, create_user, vehicule_db, entretien_db
):
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)
    client = auth_client(driver)

    response = client.delete(
        f"/vehicules/{vehicule_db.id}/entretiens/{entretien_db.id}"
    )

    assert response.status_code == 403


def test_owner_cannot_delete_other_company(
    auth_client, create_user, vehicule_db, entretien_db
):
    owner = create_user(UserRole.OWNER, company_id=999)
    client = auth_client(owner)

    response = client.delete(
        f"/vehicules/{vehicule_db.id}/entretiens/{entretien_db.id}"
    )

    assert response.status_code == 403


def test_delete_entretien_vehicle_not_found(auth_client, create_user, entretien_db):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.delete(f"/vehicules/99999/entretiens/{entretien_db.id}")

    assert response.status_code == 404


def test_delete_entretien_not_found(auth_client, create_user, vehicule_db):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.delete(f"/vehicules/{vehicule_db.id}/entretiens/99999")

    assert response.status_code == 404


def test_delete_entretien_wrong_vehicle(
    auth_client, create_user, vehicule_db, entretien_db, session
):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    other_vehicle = Vehicule(
        plate="OTHER",
        model="Other",
        km=1000,
        company_id=vehicule_db.company_id,
    )
    session.add(other_vehicle)
    session.commit()
    session.refresh(other_vehicle)

    response = client.delete(
        f"/vehicules/{other_vehicle.id}/entretiens/{entretien_db.id}"
    )

    assert response.status_code == 404
