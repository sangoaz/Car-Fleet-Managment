def test_create_vehicule(client):
    payload = {"plate": "TEST-001", "model": "Test Car", "km": 10000}

    response = client.post("/vehicules", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["plate"] == payload["plate"]
    assert data["model"] == payload["model"]
    assert data["km"] == payload["km"]


def test_get_vehicule_ok(client):
    # Création du véhicule
    create_res = client.post(
        "/vehicules",
        json={"plate": "GET-001", "model": "Get Test", "km": 5000},
    )
    vehicule_id = create_res.json()["id"]

    # Récupération du véhicule
    response = client.get(f"/vehicules/{vehicule_id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == vehicule_id
    assert data["plate"] == "GET-001"
    assert data["model"] == "Get Test"
    assert data["km"] == 5000


def test_get_vehicule_not_found(client):
    response = client.get("/vehicules/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Véhicule introuvable"


def test_patch_vehicule_partial_update(client):
    # Création du véhicule
    create_res = client.post(
        "/vehicules",
        json={"plate": "PATCH-001", "model": "Patch Test", "km": 8000},
    )
    vehicule = create_res.json()
    vehicule_id = vehicule["id"]

    # Patch partiel (km uniquement)
    response = client.patch(
        f"/vehicules/{vehicule_id}",
        json={"km": 12000},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["km"] == 12000
    assert data["plate"] == "PATCH-001"
    assert data["model"] == "Patch Test"


def test_patch_vehicule_not_found(client):
    response = client.patch("/vehicules/999999", json={"km": 15000})

    assert response.status_code == 404
    assert response.json()["detail"] == "Véhicule introuvable"


def test_delete_vehicule_ok(client):
    # Création du véhicule
    create_res = client.post(
        "/vehicules",
        json={"plate": "DEL-001", "model": "Delete Test", "km": 3000},
    )
    vehicule_id = create_res.json()["id"]

    # Suppression
    response = client.delete(f"/vehicules/{vehicule_id}")

    assert response.status_code == 200
    assert "supprimé" in response.json()["message"]

    # Vérifier qu'il n'existe plus
    get_res = client.get(f"/vehicules/{vehicule_id}")
    assert get_res.status_code == 404


def test_delete_vehicule_with_entretiens_forbidden(client):
    # Création du véhicule
    vehicule_res = client.post(
        "/vehicules",
        json={"plate": "DEL-002", "model": "Delete Blocked", "km": 4000},
    )
    vehicule_id = vehicule_res.json()["id"]

    # Création d’un entretien
    client.post(
        f"/vehicules/{vehicule_id}/entretiens",
        json={
            "date": "2025-01-01",
            "km": 4000,
            "type": "VIDANGE",
            "cost": 100,
        },
    )

    # Tentative de suppression
    response = client.delete(f"/vehicules/{vehicule_id}")

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Impossible de supprimer un véhicule avec des entretiens"
    )


def test_delete_vehicule_not_found(client):
    response = client.delete("/vehicules/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Véhicule introuvable"
