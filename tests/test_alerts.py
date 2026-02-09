def test_get_vehicule_alerts(client, create_vehicule):
    # Création du véhicule
    vehicule = create_vehicule(
        plate="AL-001",
        model="Alert Test",
        km=60000,
    )

    # Appel endpoint alerts
    res = client.get(f"/vehicules/{vehicule["id"]}/alerts")

    assert res.status_code == 200
    data = res.json()

    assert data["vehicule_id"] == vehicule["id"]
    assert len(data["alerts"]) == 5

    types = {alert["type"] for alert in data["alerts"]}
    assert types == {
        "VIDANGE",
        "PNEUS",
        "FREINS",
        "REVISION",
        "CONTROLE_TECHNIQUE",
    }
