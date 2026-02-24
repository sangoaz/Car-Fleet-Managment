def test_create_company(client):
    payload = {"name": "TEST_COMPANY"}

    response = client.post("/companies", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["name"] == payload["name"]
    assert data["is_active"] == True
    assert data["created_at"] is not None


def test_get_company_ok(client, company):
    response = client.get(f"/companies/{company["id"]}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == company["id"]
    assert data["name"] == "Test Company"
    assert data["is_active"] == True
    assert data["created_at"] is not None
