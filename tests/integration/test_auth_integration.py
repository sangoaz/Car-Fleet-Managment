import uuid

from app.security import decode_access_token, hash_password
from app.models import User
from app.enums import UserRole


# =========================
# TESTS LOGIN
# =========================


def test_login_success(client, session):
    password = "test123"

    user = User(
        email=f"{uuid.uuid4()}@test.com",
        password_hash=hash_password(password),
        role=UserRole.DRIVER,
        is_active=True,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    response = client.post(
        "/auth/login",
        data={
            "username": user.email,
            "password": password,
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client, session):
    user = User(
        email=f"{uuid.uuid4()}@test.com",
        password_hash=hash_password("correct_password"),
        role=UserRole.DRIVER,
        is_active=True,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    response = client.post(
        "/auth/login",
        data={
            "username": user.email,
            "password": "wrong_password",
        },
    )

    assert response.status_code == 401


def test_login_user_not_found(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "unknown@mail.com",
            "password": "test123",
        },
    )

    assert response.status_code == 401


def test_login_inactive_user(client, session):
    password = "test123"

    user = User(
        email="inactive@mail.com",
        password_hash=hash_password(password),
        role=UserRole.DRIVER,
        is_active=False,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    response = client.post(
        "/auth/login",
        data={
            "username": user.email,
            "password": password,
        },
    )

    assert response.status_code == 403


def test_login_returns_valid_token(client, session):
    password = "test123"

    user = User(
        email="token@mail.com",
        password_hash=hash_password(password),
        role=UserRole.DRIVER,
        is_active=True,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    response = client.post(
        "/auth/login",
        data={
            "username": user.email,
            "password": password,
        },
    )

    token = response.json()["access_token"]

    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == str(user.id)


# ============================
# TESTS D'AFFICHAGE DE COMPTE
# ============================


def test_get_me(client, session):
    password = "test123"

    user = User(
        email=f"{uuid.uuid4()}@test.com",
        password_hash=hash_password(password),
        role=UserRole.DRIVER,
        is_active=True,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # login
    res = client.post(
        "/auth/login",
        data={"username": user.email, "password": password},
    )
    token = res.json()["access_token"]

    # call /me
    res = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 200
    assert res.json()["id"] == user.id
