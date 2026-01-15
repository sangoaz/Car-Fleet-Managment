def test_get_vehicule_alerts(client):
    # Création du véhicule
    res = client.post(
        "/vehicules",
        json={"plate": "AL-001", "model": "Alert Test", "km": 60000},
    )
    vehicule_id = res.json()["id"]

    # Appel endpoint alerts
    res = client.get(f"/vehicules/{vehicule_id}/alerts")

    assert res.status_code == 200
    data = res.json()

    assert data["vehicule_id"] == vehicule_id
    assert len(data["alerts"]) == 5

    types = {alert["type"] for alert in data["alerts"]}
    assert types == {
        "VIDANGE",
        "PNEUS",
        "FREINS",
        "REVISION",
        "CONTROLE_TECHNIQUE",
    }
