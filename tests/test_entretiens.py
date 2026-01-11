def test_create_entretien_ok(client):
    # Création du véhicule
    res = client.post(
        "/vehicules",
        json={"plate": "ENT-001", "model": "Entretien Test", "km": 10000},
    )
    vehicule_id = res.json()["id"]

    # Création de l’entretien
    res = client.post(
        f"/vehicules/{vehicule_id}/entretiens",
        json={
            "date": "2025-01-01",
            "km": 10000,
            "type": "VIDANGE",
            "cost": 120,
            "comment": "Vidange annuelle",
        },
    )

    assert res.status_code == 201
    data = res.json()

    assert data["vehicule_id"] == vehicule_id
    assert data["type"] == "VIDANGE"
    assert data["km"] == 10000


def test_create_entretien_vehicule_not_found(client):
    res = client.post(
        "/vehicules/999999/entretiens",
        json={
            "date": "2025-01-01",
            "km": 10000,
            "type": "VIDANGE",
        },
    )

    assert res.status_code == 404
    assert res.json()["detail"] == "Véhicule introuvable"


def test_get_entretiens_empty(client):
    # Créer un véhicule
    res = client.post(
        "/vehicules", json={"plate": "TEST-123", "model": "Test Car", "km": 10000}
    )
    vehicule_id = res.json()["id"]

    # Récupérer les entretiens
    res = client.get(f"/vehicules/{vehicule_id}/entretiens")

    assert res.status_code == 200
    data = res.json()

    assert data["total_count"] == 0
    assert data["items"] == []


def test_get_entretiens_pagination(client):
    # Création du véhicule
    res = client.post(
        "/vehicules",
        json={"plate": "ENT-GET-002", "model": "Pagination Test", "km": 10000},
    )
    vehicule_id = res.json()["id"]

    # Création de 3 entretiens
    for i in range(3):
        client.post(
            f"/vehicules/{vehicule_id}/entretiens",
            json={
                "date": f"2025-01-0{i+1}",
                "km": 10000 + i * 100,
                "type": "VIDANGE",
            },
        )

    # limit = 2
    res = client.get(f"/vehicules/{vehicule_id}/entretiens?limit=2")

    assert res.status_code == 200
    data = res.json()

    assert data["total_count"] == 3
    assert len(data["items"]) == 2


def test_get_entretiens_filter_by_type(client):
    # Création du véhicule
    res = client.post(
        "/vehicules",
        json={"plate": "ENT-GET-003", "model": "Filter Test", "km": 15000},
    )
    vehicule_id = res.json()["id"]

    # Création d'entretiens variés
    client.post(
        f"/vehicules/{vehicule_id}/entretiens",
        json={"date": "2025-01-01", "km": 15000, "type": "VIDANGE"},
    )
    client.post(
        f"/vehicules/{vehicule_id}/entretiens",
        json={"date": "2025-02-01", "km": 15500, "type": "PNEUS"},
    )
    client.post(
        f"/vehicules/{vehicule_id}/entretiens",
        json={"date": "2025-03-01", "km": 16000, "type": "VIDANGE"},
    )

    # Filtrer par VIDANGE
    res = client.get(f"/vehicules/{vehicule_id}/entretiens?entretien_type=VIDANGE")

    assert res.status_code == 200
    data = res.json()

    assert data["total_count"] == 2
    assert len(data["items"]) == 2
    assert all(item["type"] == "VIDANGE" for item in data["items"])


def test_get_entretiens_vehicule_not_found(client):
    res = client.get("/vehicules/999999/entretiens")

    assert res.status_code == 404
    assert res.json()["detail"] == "Véhicule introuvable"
