import pytest
import uuid


from sqlmodel import select
from app.security import hash_password
from app.enums import UserRole
from app.models import User


# =========================
# TESTS DE CREATION
# =========================


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


# =========================
# TESTS D'AFFICHAGE
# =========================


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


# =========================
# TESTS DELETE
# =========================


def test_admin_can_deactivate_company(auth_client, session, create_user, company_db):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.delete(
        f"/companies/{company_db.id}/deactivate",
    )

    assert response.status_code == 200

    session.refresh(company_db)
    assert company_db.is_active is False


@pytest.mark.parametrize(
    "role",
    [
        UserRole.OWNER,
        UserRole.MANAGER,
        UserRole.DRIVER,
    ],
)
def test_not_admin_cannot_deactivate_company(
    auth_client, create_user, company_db, role
):
    user = create_user(role, company_id=company_db.id)
    client = auth_client(user)

    response = client.delete(
        f"/companies/{company_db.id}/deactivate",
    )

    assert response.status_code == 403


def test_delete_company_not_found(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.delete(
        f"/companies/{9999}/deactivate",
    )

    assert response.status_code == 404


def test_delete_company_already_desactivated(
    auth_client, create_user, company_db, session
):

    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.delete(
        f"/companies/{company_db.id}/deactivate",
    )

    session.refresh(company_db)

    assert response.status_code == 200

    response = client.delete(
        f"/companies/{company_db.id}/deactivate",
    )

    session.refresh(company_db)

    assert response.status_code == 400


def test_login_blocked_if_company_inactive(client, session, company_db):
    password = "test123"

    # company inactive
    company_db.is_active = False
    session.commit()

    user = User(
        email=f"{uuid.uuid4()}@test.com",
        password_hash=hash_password(password),
        role=UserRole.DRIVER,
        company_id=company_db.id,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    res = client.post(
        "/auth/login",
        data={"username": user.email, "password": password},
    )

    assert res.status_code == 403


# =========================
# TESTS REACTIVATE
# =========================


def test_admin_can_reactivate_company(auth_client, session, create_user, company_db):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.delete(
        f"/companies/{company_db.id}/deactivate",
    )

    assert response.status_code == 200

    session.refresh(company_db)

    response = client.patch(
        f"/companies/{company_db.id}/reactivate",
    )

    session.refresh(company_db)

    assert company_db.is_active is True


@pytest.mark.parametrize(
    "role",
    [
        UserRole.OWNER,
        UserRole.MANAGER,
        UserRole.DRIVER,
    ],
)
def test_not_admin_cannot_reactivate_company(
    auth_client, create_user, company_db, role
):
    user = create_user(role, company_id=company_db.id)
    client = auth_client(user)

    response = client.patch(
        f"/companies/{company_db.id}/reactivate",
    )

    assert response.status_code == 403


def test_reactivate_company_not_found(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.patch(
        f"/companies/{9999}/reactivate",
    )

    assert response.status_code == 404


def test_reactivate_company_already_activated(
    auth_client, create_user, company_db, session
):

    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.patch(
        f"/companies/{company_db.id}/reactivate",
    )

    session.refresh(company_db)

    assert response.status_code == 400
