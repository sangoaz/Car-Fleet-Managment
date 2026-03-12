import pytest
from app.enums import UserRole

# =========================
# TESTS DE CREATION
# =========================


def test_admin_can_create_vehicule(auth_client, create_user, company_db):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    payload = {
        "plate": "CREATE-001",
        "model": "Create Test",
        "km": 5000,
        "company_id": company_db.id,
    }

    response = client.post("/vehicules", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["plate"] == payload["plate"]
    assert data["model"] == payload["model"]
    assert data["km"] == payload["km"]


@pytest.mark.parametrize(
    "role",
    [
        UserRole.OWNER,
        UserRole.MANAGER,
    ],
)
def test_owner_manager_can_create_vehicule(auth_client, create_user, role):
    user = create_user(role, company_id=1)
    client = auth_client(user)

    payload = {
        "plate": "CREATE-001",
        "model": "Create Test",
        "km": 5000,
        "company_id": user.company_id,
    }

    response = client.post("/vehicules", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["plate"] == payload["plate"]
    assert data["model"] == payload["model"]
    assert data["km"] == payload["km"]


@pytest.mark.parametrize(
    "role",
    [
        UserRole.OWNER,
        UserRole.MANAGER,
    ],
)
def test_owner_manager_company_id_is_forced(auth_client, create_user, role):
    user = create_user(role, company_id=1)
    client = auth_client(user)

    payload = {
        "plate": "CREATE-001",
        "model": "Create Test",
        "km": 5000,
        "company_id": 999,  # tentative d'injection
    }

    response = client.post("/vehicules", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["company_id"] == 1
    # Ce test vérifie que l'injection d'un véhicule dans une autre entreprise n'est pas possible
    # et créée le véhicule dans l'entreprise de l'user


def test_driver_cannot_create_vehicule(auth_client, create_user):
    driver = create_user(UserRole.DRIVER, company_id=1)
    client = auth_client(driver)

    payload = {
        "plate": "CREATE-001",
        "model": "Create Test",
        "km": 5000,
        "company_id": driver.company_id,
    }

    response = client.post("/vehicules", json=payload)

    assert response.status_code == 403


# =========================
# TESTS D'AFFICHAGE
# =========================


def test_admin_get_vehicule(auth_client, create_user, vehicule_db):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.get(f"/vehicules/{vehicule_db.id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == vehicule_db.id
    assert data["plate"] == vehicule_db.plate
    assert data["model"] == vehicule_db.model
    assert data["km"] == vehicule_db.km


@pytest.mark.parametrize(
    "role",
    [
        UserRole.OWNER,
        UserRole.MANAGER,
    ],
)
def test_owner_manager_get_vehicule(auth_client, create_user, vehicule_db, role):
    user = create_user(role, company_id=vehicule_db.company_id)
    client = auth_client(user)

    response = client.get(f"/vehicules/{vehicule_db.id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == vehicule_db.id
    assert data["plate"] == vehicule_db.plate
    assert data["model"] == vehicule_db.model
    assert data["km"] == vehicule_db.km


def test_get_vehicule_not_found(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.get("/vehicules/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Véhicule introuvable"


# =========================
# TESTS D'UPDATE
# =========================


def test_admin_can_update_vehicule(auth_client, create_user, vehicule_db):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.patch(
        f"/vehicules/{vehicule_db.id}",
        json={
            "plate": "UPDATED-PLATE",
            "km": 9999,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["plate"] == "UPDATED-PLATE"
    assert data["km"] == 9999

    # Vérifie que les autres champs n'ont pas changé
    assert data["model"] == vehicule_db.model
    assert data["company_id"] == vehicule_db.company_id


def test_owner_can_update_same_company(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    response = client.patch(
        f"/vehicules/{vehicule_db.id}",
        json={"km": 8000},
    )

    assert response.status_code == 200
    assert response.json()["km"] == 8000


def test_manager_can_update_same_company(auth_client, create_user, vehicule_db):
    manager = create_user(UserRole.MANAGER, company_id=vehicule_db.company_id)
    client = auth_client(manager)

    response = client.patch(
        f"/vehicules/{vehicule_db.id}",
        json={"km": 7000},
    )

    assert response.status_code == 200


def test_owner_cannot_update_other_company(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=999)
    client = auth_client(owner)

    response = client.patch(
        f"/vehicules/{vehicule_db.id}",
        json={"km": 5000},
    )

    assert response.status_code == 403


def test_manager_cannot_update_other_company(auth_client, create_user, vehicule_db):
    manager = create_user(UserRole.MANAGER, company_id=999)
    client = auth_client(manager)

    response = client.patch(
        f"/vehicules/{vehicule_db.id}",
        json={"km": 5000},
    )

    assert response.status_code == 403


def test_driver_cannot_update_vehicule(auth_client, create_user, vehicule_db):
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)
    client = auth_client(driver)

    response = client.patch(
        f"/vehicules/{vehicule_db.id}",
        json={"km": 5000},
    )

    assert response.status_code == 403


def test_update_vehicule_not_found(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.patch(
        "/vehicules/99999",
        json={"km": 1000},
    )

    assert response.status_code == 404


def test_update_vehicule_without_auth_returns_401(client, vehicule_db):
    response = client.patch(
        f"/vehicules/{vehicule_db.id}",
        json={"km": 5000},
    )

    assert response.status_code == 401


# =========================
# TEST DELETE
# =========================


def test_admin_can_delete_vehicule(auth_client, create_user, vehicule_db):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.delete(f"/vehicules/{vehicule_db.id}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Vehicule {vehicule_db.id} supprimé"


def test_owner_can_delete_same_company(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    response = client.delete(f"/vehicules/{vehicule_db.id}")

    assert response.status_code == 200


def test_owner_cannot_delete_other_company(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=999)
    client = auth_client(owner)

    response = client.delete(f"/vehicules/{vehicule_db.id}")

    assert response.status_code == 403


def test_manager_cannot_delete_vehicule(auth_client, create_user, vehicule_db):
    manager = create_user(UserRole.MANAGER, company_id=vehicule_db.company_id)
    client = auth_client(manager)

    response = client.delete(f"/vehicules/{vehicule_db.id}")

    assert response.status_code == 403


def test_driver_cannot_delete_vehicule(auth_client, create_user, vehicule_db):
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)
    client = auth_client(driver)

    response = client.delete(f"/vehicules/{vehicule_db.id}")

    assert response.status_code == 403


def test_delete_vehicule_not_found(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.delete("/vehicules/99999")

    assert response.status_code == 404


def test_delete_vehicule_without_auth_returns_401(client, vehicule_db):
    response = client.delete(f"/vehicules/{vehicule_db.id}")

    assert response.status_code == 401


def test_delete_vehicule_with_entretiens_returns_400(
    auth_client, create_user, vehicule_db, entretien_db
):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    response = client.delete(f"/vehicules/{vehicule_db.id}")

    assert response.status_code == 400
    assert "Impossible de supprimer" in response.json()["detail"]
