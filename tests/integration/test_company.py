import pytest
from app.enums import UserRole


def test_create_company(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    payload = {"name": "TEST_COMPANY"}

    response = client.post("/companies", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["name"] == payload["name"]
    assert data["is_active"] == True
    assert data["created_at"] is not None


@pytest.mark.parametrize(
    "role",
    [
        UserRole.OWNER,
        UserRole.MANAGER,
        UserRole.DRIVER,
    ],
)
def test_non_admin_cannot_create_company(auth_client, create_user, role):
    user = create_user(role, company_id=1)
    client = auth_client(user)

    payload = {"name": "TEST_COMPANY"}

    response = client.post("/companies", json=payload)

    assert response.status_code == 403


def test_admin_get_company(auth_client, create_user, company_db):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.get(f"/companies/{company_db.id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == company_db.id
    assert data["name"] == "Test Company"
    assert data["is_active"] == True
    assert data["created_at"] is not None


@pytest.mark.parametrize(
    "role",
    [
        UserRole.OWNER,
        UserRole.MANAGER,
    ],
)
def test_owner_manager_get_same_company(auth_client, create_user, company_db, role):
    user = create_user(role, company_id=company_db.id)
    client = auth_client(user)

    response = client.get(f"/companies/{company_db.id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == company_db.id
    assert data["name"] == "Test Company"
    assert data["is_active"] == True
    assert data["created_at"] is not None


@pytest.mark.parametrize(
    "role",
    [
        UserRole.OWNER,
        UserRole.MANAGER,
    ],
)
def test_owner_manager_cannot_get_other_company(
    auth_client, create_user, company_db, role
):
    other_company_id = company_db.id + 1  # simulate different company

    user = create_user(role, company_id=other_company_id)
    client = auth_client(user)

    response = client.get(f"/companies/{company_db.id}")

    assert response.status_code == 403


def test_driver_cannot_get_company(auth_client, create_user, company_db):
    driver = create_user(UserRole.DRIVER, company_id=company_db.id)
    client = auth_client(driver)

    response = client.get(f"/companies/{company_db.id}")

    assert response.status_code == 403


def test_get_company_not_found(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.get("/companies/9999")

    assert response.status_code == 404
