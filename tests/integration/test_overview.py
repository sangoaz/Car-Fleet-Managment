from app.enums import UserRole


def test_overview_without_entretien(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    res = client.get(f"/vehicules/{vehicule_db.id}/overview")

    assert res.status_code == 200
    data = res.json()

    assert "vehicule" in data
    assert data["vehicule"]["id"] == vehicule_db.id
    assert data["last_entretiens"] == []
    assert data["last_controle_technique"] is None


def test_overview_with_entretiens_limit_5(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    for i in range(6):
        client.post(
            f"/vehicules/{vehicule_db.id}/entretiens",
            json={
                "date": f"2025-01-0{i+1}",
                "km": vehicule_db.km + 1000 + i * 100,
                "type": "VIDANGE",
            },
        )

    res = client.get(f"/vehicules/{vehicule_db.id}/overview")

    assert res.status_code == 200
    data = res.json()

    entretiens = data["last_entretiens"]

    assert len(entretiens) == 5
    assert entretiens[0]["date"] == "2025-01-06"

    dates = [e["date"] for e in entretiens]
    assert "2025-01-01" not in dates


def test_overview_last_controle_technique_only(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    client.post(
        f"/vehicules/{vehicule_db.id}/entretiens",
        json={
            "date": "2023-01-01",
            "km": vehicule_db.km + 10000,
            "type": "CONTROLE_TECHNIQUE",
        },
    )

    client.post(
        f"/vehicules/{vehicule_db.id}/entretiens",
        json={
            "date": "2024-01-01",
            "km": vehicule_db.km + 12000,
            "type": "CONTROLE_TECHNIQUE",
        },
    )

    client.post(
        f"/vehicules/{vehicule_db.id}/entretiens",
        json={
            "date": "2024-06-01",
            "km": vehicule_db.km + 13000,
            "type": "VIDANGE",
        },
    )

    res = client.get(f"/vehicules/{vehicule_db.id}/overview")

    assert res.status_code == 200
    data = res.json()

    ct = data["last_controle_technique"]

    assert ct is not None
    assert ct["type"] == "CONTROLE_TECHNIQUE"
    assert ct["date"] == "2024-01-01"
