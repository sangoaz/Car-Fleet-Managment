def test_create_entretien_ok(client, create_vehicule):
    # Création du véhicule
    vehicule = create_vehicule(
        plate="CREATE-ENT-001",
        model="Create Ent Test",
        km=5000,
    )

    # Création de l’entretien
    res = client.post(
        f"/vehicules/{vehicule["id"]}/entretiens",
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

    assert data["vehicule_id"] == vehicule["id"]
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


def test_get_entretiens_empty(client, create_vehicule):
    # Créer un véhicule
    vehicule = create_vehicule(
        plate="GET-ENTEMPT-001",
        model="Get Ent Empty Test",
        km=5000,
    )

    # Récupérer les entretiens
    res = client.get(f"/vehicules/{vehicule["id"]}/entretiens")

    assert res.status_code == 200
    data = res.json()

    assert data["total_count"] == 0
    assert data["items"] == []


def test_get_entretiens_pagination(client, create_vehicule):
    # Création du véhicule
    vehicule = create_vehicule(
        plate="GET-ENTPAG-001",
        model="Get Ent Pag Test",
        km=5000,
    )

    # Création de 3 entretiens
    for i in range(3):
        client.post(
            f"/vehicules/{vehicule["id"]}/entretiens",
            json={
                "date": f"2025-01-0{i+1}",
                "km": 10000 + i * 100,
                "type": "VIDANGE",
            },
        )

    # limit = 2
    res = client.get(f"/vehicules/{vehicule["id"]}/entretiens?limit=2")

    assert res.status_code == 200
    data = res.json()

    assert data["total_count"] == 3
    assert len(data["items"]) == 2


def test_get_entretiens_filter_by_type(client, create_vehicule):
    # Création du véhicule
    vehicule = create_vehicule(
        plate="GET-ENTFIL-001",
        model="Get Ent Filt Test",
        km=5000,
    )

    # Création d'entretiens variés
    client.post(
        f"/vehicules/{vehicule["id"]}/entretiens",
        json={"date": "2025-01-01", "km": 15000, "type": "VIDANGE"},
    )
    client.post(
        f"/vehicules/{vehicule["id"]}/entretiens",
        json={"date": "2025-02-01", "km": 15500, "type": "PNEUS"},
    )
    client.post(
        f"/vehicules/{vehicule["id"]}/entretiens",
        json={"date": "2025-03-01", "km": 16000, "type": "VIDANGE"},
    )

    # Filtrer par VIDANGE
    res = client.get(f"/vehicules/{vehicule["id"]}/entretiens?entretien_type=VIDANGE")

    assert res.status_code == 200
    data = res.json()

    assert data["total_count"] == 2
    assert len(data["items"]) == 2
    assert all(item["type"] == "VIDANGE" for item in data["items"])


def test_get_entretiens_vehicule_not_found(client):
    res = client.get("/vehicules/999999/entretiens")

    assert res.status_code == 404
    assert res.json()["detail"] == "Véhicule introuvable"


def test_create_entretien_updates_vehicule_km(client, create_vehicule):
    # Création du véhicule
    vehicule = create_vehicule(
        plate="CREATE-ENTUPD-001",
        model="Create Ent Update Km Test",
        km=5000,
    )

    # Création d’un entretien avec un km supérieur
    client.post(
        f"/vehicules/{vehicule["id"]}/entretiens",
        json={
            "date": "2025-01-01",
            "km": 55000,
            "type": "VIDANGE",
        },
    )

    # Vérifier que le km du véhicule a été mis à jour
    res = client.get(f"/vehicules/{vehicule["id"]}")
    assert res.status_code == 200
    assert res.json()["km"] == 55000


def test_create_entretien_does_not_lower_vehicule_km(client, create_vehicule):
    vehicule = create_vehicule(
        plate="CREATE-ENTNOTLOw-001",
        model="Create Ent Not Lower Test",
        km=50000,
    )

    # Entretien historique
    client.post(
        f"/vehicules/{vehicule["id"]}/entretiens",
        json={
            "date": "2024-01-01",
            "km": 40000,
            "type": "VIDANGE",
        },
    )

    res = client.get(f"/vehicules/{vehicule["id"]}")
    assert res.json()["km"] == 50000


def test_patch_entretien_updates_vehicule_km(client, create_vehicule):
    # Création du véhicule
    vehicule = create_vehicule(
        plate="PATCH-ENT-001",
        model="Patch Ent km Test",
        km=5000,
    )

    # Création entretien initial
    res = client.post(
        f"/vehicules/{vehicule["id"]}/entretiens",
        json={
            "date": "2025-01-01",
            "km": 45000,
            "type": "VIDANGE",
        },
    )
    entretien_id = res.json()["id"]

    # PATCH avec km supérieur
    client.patch(
        f"/vehicules/{vehicule["id"]}/entretiens/{entretien_id}",
        json={"km": 60000},
    )

    # Le km du véhicule DOIT être mis à jour
    res = client.get(f"/vehicules/{vehicule["id"]}")
    assert res.json()["km"] == 60000


def test_patch_entretien_does_not_decrease_vehicule_km(client, create_vehicule):
    vehicule = create_vehicule(
        plate="PATCH-ENTNOTDECREASE-001",
        model="Patch Ent Not Decrease Test",
        km=50000,
    )

    res = client.post(
        f"/vehicules/{vehicule["id"]}/entretiens",
        json={
            "date": "2025-01-01",
            "km": 60000,
            "type": "VIDANGE",
        },
    )
    entretien_id = res.json()["id"]

    client.patch(
        f"/vehicules/{vehicule["id"]}/entretiens/{entretien_id}",
        json={"km": 40000},
    )

    res = client.get(f"/vehicules/{vehicule["id"]}")
    assert res.json()["km"] == 60000


def test_patch_entretien_basic_fields(client, create_vehicule):
    # Création véhicule
    vehicule = create_vehicule(
        plate="PATCH-BASIC-001",
        model="Patch Ent Basic Test",
        km=50000,
    )

    # Création entretien
    res = client.post(
        f"/vehicules/{vehicule["id"]}/entretiens",
        json={
            "date": "2025-01-01",
            "km": 45000,
            "type": "VIDANGE",
            "cost": 100,
        },
    )
    entretien_id = res.json()["id"]

    # PATCH sans km
    res = client.patch(
        f"/vehicules/{vehicule["id"]}/entretiens/{entretien_id}",
        json={
            "comment": "Entretien modifié",
            "cost": 120,
        },
    )

    assert res.status_code == 200
    data = res.json()
    assert data["comment"] == "Entretien modifié"
    assert data["cost"] == 120

    # Le km du véhicule ne change PAS
    res = client.get(f"/vehicules/{vehicule["id"]}")
    assert res.json()["km"] == 50000


def test_cannot_create_entretien_with_lower_km_in_future(client, create_vehicule):
    vehicule = create_vehicule(
        plate="RULE-001",
        model="Rules",
        km=60000,
    )

    # Vidange valide
    client.post(
        f"/vehicules/{vehicule["id"]}/entretiens",
        json={
            "date": "2025-01-01",
            "km": 50000,
            "type": "VIDANGE",
        },
    )

    # Vidange incohérente (future mais km plus bas)
    res = client.post(
        f"/vehicules/{vehicule["id"]}/entretiens",
        json={
            "date": "2026-01-01",
            "km": 40000,
            "type": "VIDANGE",
        },
    )

    assert res.status_code == 422


def test_cannot_create_entretien_with_higher_km_in_past(client, create_vehicule):
    vehicule = create_vehicule(
        plate="RULE-002",
        model="Rules",
        km=60000,
    )

    client.post(
        f"/vehicules/{vehicule["id"]}/entretiens",
        json={
            "date": "2025-01-01",
            "km": 50000,
            "type": "VIDANGE",
        },
    )

    res = client.post(
        f"/vehicules/{vehicule["id"]}/entretiens",
        json={
            "date": "2024-01-01",
            "km": 60000,
            "type": "VIDANGE",
        },
    )

    assert res.status_code == 422


def test_can_create_entretien_history(client, create_vehicule):
    vehicule = create_vehicule(
        plate="RULE-003",
        model="Rules",
        km=60000,
    )

    res = client.post(
        f"/vehicules/{vehicule["id"]}/entretiens",
        json={
            "date": "2024-01-01",
            "km": 40000,
            "type": "VIDANGE",
        },
    )

    assert res.status_code == 201


def test_delete_entretien_ok(client, create_vehicule):
    vehicule = create_vehicule(
        plate="DEL-E-001",
        model="Delete Entretien",
        km=50000,
    )

    res = client.post(
        f"/vehicules/{vehicule["id"]}/entretiens",
        json={
            "date": "2025-01-01",
            "km": 40000,
            "type": "VIDANGE",
        },
    )
    entretien_id = res.json()["id"]

    res = client.delete(f"/vehicules/{vehicule["id"]}/entretiens/{entretien_id}")

    assert res.status_code == 204


def test_delete_entretien_not_found(client):
    res = client.delete("/vehicules/1/entretiens/999")
    assert res.status_code == 404


def test_delete_entretien_wrong_vehicle(client, create_vehicule):
    v1 = create_vehicule(
        plate="DEL-A",
        model="A",
        km=10000,
    )

    v2 = create_vehicule(
        plate="DEL-B",
        model="B",
        km=10000,
    )

    entretien_id = client.post(
        f"/vehicules/{v1["id"]}/entretiens",
        json={
            "date": "2025-01-01",
            "km": 9000,
            "type": "VIDANGE",
        },
    ).json()["id"]

    res = client.delete(f"/vehicules/{v2["id"]}/entretiens/{entretien_id}")

    assert res.status_code == 404
