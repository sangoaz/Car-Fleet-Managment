from app.enums import UserRole


def test_get_vehicule_alerts(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    res = client.get(f"/vehicules/{vehicule_db.id}/alerts")

    assert res.status_code == 200

    data = res.json()

    assert data["vehicule_id"] == vehicule_db.id
    assert len(data["alerts"]) == 5

    types = {alert["type"] for alert in data["alerts"]}

    assert types == {
        "VIDANGE",
        "PNEUS",
        "FREINS",
        "REVISION",
        "CONTROLE_TECHNIQUE",
    }


def test_admin_can_get_vehicule_alerts(auth_client, create_user, vehicule_db):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    res = client.get(f"/vehicules/{vehicule_db.id}/alerts")

    assert res.status_code == 200


def test_manager_can_get_vehicule_alerts(auth_client, create_user, vehicule_db):
    manager = create_user(UserRole.MANAGER, company_id=vehicule_db.company_id)
    client = auth_client(manager)

    res = client.get(f"/vehicules/{vehicule_db.id}/alerts")

    assert res.status_code == 200


def test_driver_cannot_get_vehicule_alerts(auth_client, create_user, vehicule_db):
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)
    client = auth_client(driver)

    res = client.get(f"/vehicules/{vehicule_db.id}/alerts")

    assert res.status_code == 403


# test_driver_can_get_assigned_vehicule_alerts


def test_get_alerts_vehicule_not_found(auth_client, create_user):
    owner = create_user(UserRole.OWNER, company_id=1)
    client = auth_client(owner)

    res = client.get("/vehicules/9999/alerts")

    assert res.status_code == 404
    assert res.json()["detail"] == "Véhicule introuvable"


def test_owner_cannot_get_other_company_alerts(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=999)
    client = auth_client(owner)

    res = client.get(f"/vehicules/{vehicule_db.id}/alerts")

    assert res.status_code == 403


def test_alert_structure(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    client = auth_client(owner)

    res = client.get(f"/vehicules/{vehicule_db.id}/alerts")

    alert = res.json()["alerts"][0]

    assert "type" in alert
    assert "message" in alert
