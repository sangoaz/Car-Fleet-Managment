def test_create_vehicule(client, create_vehicule):
    vehicule = create_vehicule(plate="CREATE-001", model="Create Test", km=5000)

    response = client.post("/vehicules", json=vehicule)

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["plate"] == vehicule["plate"]
    assert data["model"] == vehicule["model"]
    assert data["km"] == vehicule["km"]


def test_get_vehicule_ok(client, create_vehicule):
    vehicule = create_vehicule(
        plate="GET-001",
        model="Get Test",
        km=5000,
    )

    response = client.get(f"/vehicules/{vehicule['id']}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == vehicule["id"]
    assert data["plate"] == "GET-001"
    assert data["model"] == "Get Test"
    assert data["km"] == 5000


def test_get_vehicule_not_found(client):
    response = client.get("/vehicules/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Véhicule introuvable"


def test_patch_vehicule_partial_update(client, create_vehicule):
    # Création du véhicule
    vehicule = create_vehicule(
        plate="PATCH-001",
        model="Patch Test",
        km=5000,
    )

    # Patch partiel (km uniquement)
    response = client.patch(
        f"/vehicules/{vehicule["id"]}",
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


def test_delete_vehicule_ok(client, create_vehicule):
    # Création du véhicule
    vehicule = create_vehicule(
        plate="DELETE-001",
        model="Delete Test",
        km=5000,
    )

    # Suppression
    response = client.delete(f"/vehicules/{vehicule["id"]}")

    assert response.status_code == 200
    assert "supprimé" in response.json()["message"]

    # Vérifier qu'il n'existe plus
    get_res = client.get(f"/vehicules/{vehicule["id"]}")
    assert get_res.status_code == 404


def test_delete_vehicule_with_entretiens_forbidden(client, create_vehicule):
    # Création du véhicule
    vehicule = create_vehicule(
        plate="DELETE-002",
        model="Delete With Ent Test",
        km=5000,
    )

    # Création d’un entretien
    client.post(
        f"/vehicules/{vehicule["id"]}/entretiens",
        json={
            "date": "2025-01-01",
            "km": 4000,
            "type": "VIDANGE",
            "cost": 100,
        },
    )

    # Tentative de suppression
    response = client.delete(f"/vehicules/{vehicule["id"]}")

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Impossible de supprimer un véhicule avec des entretiens"
    )


def test_delete_vehicule_not_found(client):
    response = client.delete("/vehicules/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Véhicule introuvable"
