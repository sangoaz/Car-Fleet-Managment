def test_overview_without_entretien(client):
    # Création du véhicule
    res = client.post(
        "/vehicules", json={"plate": "OV-001", "model": "Overview Test", "km": 5000}
    )
    vehicule_id = res.json()["id"]

    res = client.get(f"/vehicules/{vehicule_id}/overview")

    assert res.status_code == 200
    data = res.json()

    assert "vehicule" in data
    assert data["vehicule"]["id"] == vehicule_id
    assert data["last_entretiens"] == []
    assert data["last_controle_technique"] is None


def test_overview_with_entretiens_limit_5(client):
    # Création du véhicule
    res = client.post(
        "/vehicules",
        json={"plate": "OV-002", "model": "Overview Many", "km": 10000},
    )
    vehicule_id = res.json()["id"]

    # Création de 6 entretiens (dates croissantes)
    for i in range(6):
        client.post(
            f"/vehicules/{vehicule_id}/entretiens",
            json={
                "date": f"2025-01-0{i+1}",
                "km": 10000 + i * 100,
                "type": "VIDANGE",
            },
        )

    # Appel de l’overview
    res = client.get(f"/vehicules/{vehicule_id}/overview")

    assert res.status_code == 200
    data = res.json()

    entretiens = data["last_entretiens"]

    # Limité à 5
    assert len(entretiens) == 5

    # Le plus récent en premier
    assert entretiens[0]["date"] == "2025-01-06"

    # Le plus ancien exclu
    dates = [e["date"] for e in entretiens]
    assert "2025-01-01" not in dates


def test_overview_last_controle_technique_only(client):
    # Création du véhicule
    res = client.post(
        "/vehicules",
        json={"plate": "OV-003", "model": "Overview CT", "km": 20000},
    )
    vehicule_id = res.json()["id"]

    # Création de plusieurs contrôles techniques
    client.post(
        f"/vehicules/{vehicule_id}/entretiens",
        json={
            "date": "2023-01-01",
            "km": 15000,
            "type": "CONTROLE_TECHNIQUE",
        },
    )

    client.post(
        f"/vehicules/{vehicule_id}/entretiens",
        json={
            "date": "2024-01-01",
            "km": 18000,
            "type": "CONTROLE_TECHNIQUE",
        },
    )

    # Création d’un autre type d’entretien (ne doit pas interférer)
    client.post(
        f"/vehicules/{vehicule_id}/entretiens",
        json={
            "date": "2024-06-01",
            "km": 19000,
            "type": "VIDANGE",
        },
    )

    # Appel de l’overview
    res = client.get(f"/vehicules/{vehicule_id}/overview")

    assert res.status_code == 200
    data = res.json()

    ct = data["last_controle_technique"]

    assert ct is not None
    assert ct["type"] == "CONTROLE_TECHNIQUE"
    assert ct["date"] == "2024-01-01"
