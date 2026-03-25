from app.enums import UserRole
from app.models import User


# Helpers
# Creation d'un email unique
def unique_email(prefix):
    import uuid

    return f"{prefix}_{uuid.uuid4()}@test.com"


# =========================
# TESTS DE CREATION
# =========================


def test_admin_can_create_owner(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.post(
        "/users",
        json={
            "email": "owner@test.com",
            "password": "password",
            "role": "OWNER",
            "company_id": 1,
        },
    )

    assert response.status_code == 201


def test_owner_can_create_manager(auth_client, create_user):
    owner = create_user(UserRole.OWNER, company_id=1)
    client = auth_client(owner)

    response = client.post(
        "/users",
        json={
            "email": "manager@test.com",
            "password": "password",
            "role": "MANAGER",
            "company_id": 1,
        },
    )

    assert response.status_code == 201


def test_manager_can_create_driver(auth_client, create_user):
    manager = create_user(UserRole.MANAGER, company_id=1)
    client = auth_client(manager)

    response = client.post(
        "/users",
        json={
            "email": "driver@test.com",
            "password": "password",
            "role": "DRIVER",
            "company_id": 1,
        },
    )

    assert response.status_code == 201


def test_driver_can_not_create(auth_client, create_user):
    driver = create_user(UserRole.MANAGER, company_id=1)
    client = auth_client(driver)

    response = client.post(
        "/users",
        json={
            "email": "manager@test.com",
            "password": "password",
            "role": "MANAGER",
            "company_id": 1,
        },
    )

    assert response.status_code == 403


def test_cannot_create_user_with_existing_email(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN)
    client = auth_client(admin)

    email = unique_email("user")

    # Création 1
    res1 = client.post(
        "/users",
        json={
            "email": email,
            "password": "password",
            "role": "DRIVER",
            "company_id": 1,
        },
    )
    assert res1.status_code == 201

    # Création 2 avec même email
    res2 = client.post(
        "/users",
        json={
            "email": email,
            "password": "password",
            "role": "DRIVER",
            "company_id": 1,
        },
    )

    assert res2.status_code == 400
    assert res2.json()["detail"] == "Email already used"


# =========================
# TEST D'UPDATE
# =========================


def test_admin_can_modify_owner(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    # Création owner
    response_owner = client.post(
        "/users",
        json={
            "email": unique_email("owner"),
            "password": "password",
            "role": "OWNER",
            "company_id": 1,
        },
    )

    assert response_owner.status_code == 201

    owner_id = response_owner.json()["id"]

    # Update
    response = client.patch(
        f"/users/{owner_id}",
        json={"email": "owner@testmodify.com"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "owner@testmodify.com"


def test_owner_can_modify_driver(auth_client, create_user):
    owner = create_user(UserRole.OWNER, company_id=1)
    client = auth_client(owner)

    # Création driver
    response_driver = client.post(
        "/users",
        json={
            "email": unique_email("driver"),
            "password": "password",
            "role": "DRIVER",
            "company_id": 1,
        },
    )

    assert response_driver.status_code == 201

    driver_id = response_driver.json()["id"]

    # Update
    response = client.patch(
        f"/users/{driver_id}",
        json={"email": "driver@testmodify.com"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "driver@testmodify.com"


def test_owner_can_not_modify_driver_other_company(auth_client, create_user):
    # SUPER_ADMIN crée un driver company 2
    super_admin = create_user(UserRole.SUPER_ADMIN)
    admin_client = auth_client(super_admin)

    response_driver = admin_client.post(
        "/users",
        json={
            "email": unique_email("driver"),
            "password": "password",
            "role": "DRIVER",
            "company_id": 2,
        },
    )

    assert response_driver.status_code == 201
    driver_id = response_driver.json()["id"]

    # OWNER company 1 tente modification
    owner = create_user(UserRole.OWNER, company_id=1)
    owner_client = auth_client(owner)

    response = owner_client.patch(
        f"/users/{driver_id}",
        json={"email": "driver@testmodify.com"},
    )

    assert response.status_code == 403


def test_manager_can_modify_driver(auth_client, create_user):
    manager = create_user(UserRole.MANAGER, company_id=1)
    client = auth_client(manager)

    # Création driver
    response_driver = client.post(
        "/users",
        json={
            "email": unique_email("driver"),
            "password": "password",
            "role": "DRIVER",
            "company_id": 1,
        },
    )

    assert response_driver.status_code == 201

    driver_id = response_driver.json()["id"]

    # Update
    new_email = unique_email("driver_modified")

    response = client.patch(
        f"/users/{driver_id}",
        json={"email": new_email},
    )

    assert response.status_code == 200
    assert response.json()["email"] == new_email


def test_manager_can_not_modify_owner(auth_client, create_user):
    # Création de SUPER_ADMIN
    super_admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    admin_client = auth_client(super_admin)

    # Création de l'owner
    response_owner = admin_client.post(
        "/users",
        json={
            "email": unique_email("owner"),
            "password": "password",
            "role": "OWNER",
            "company_id": 1,
        },
    )

    assert response_owner.status_code == 201
    owner_id = response_owner.json()["id"]

    # Créationn du manager
    response_manager = admin_client.post(
        "/users",
        json={
            "email": unique_email("manager"),
            "password": "password",
            "role": "MANAGER",
            "company_id": 1,
        },
    )

    assert response_manager.status_code == 201
    manager_data = response_manager.json()

    manager = User(
        id=manager_data["id"],
        email=manager_data["email"],
        role=UserRole(manager_data["role"]),
        company_id=manager_data["company_id"],
    )

    manager_client = auth_client(manager)

    response = manager_client.patch(
        f"/users/{owner_id}",
        json={"email": "owner@testmodify.com"},
    )

    assert response.status_code == 403


def test_manager_cannot_escalate_role(auth_client, create_user):
    manager = create_user(UserRole.MANAGER, company_id=1)
    client = auth_client(manager)

    # Création d’un driver
    response_driver = client.post(
        "/users",
        json={
            "email": unique_email("driver"),
            "password": "password",
            "role": "DRIVER",
            "company_id": 1,
        },
    )
    driver_id = response_driver.json()["id"]

    # Tentative d’escalade
    response = client.patch(
        f"/users/{driver_id}",
        json={"role": "OWNER"},
    )

    assert response.status_code == 403


def test_owner_cannot_escalate_to_super_admin(auth_client, create_user):
    owner = create_user(UserRole.OWNER, company_id=1)
    client = auth_client(owner)

    response_driver = client.post(
        "/users",
        json={
            "email": unique_email("driver"),
            "password": "password",
            "role": "DRIVER",
            "company_id": 1,
        },
    )
    driver_id = response_driver.json()["id"]

    response = client.patch(
        f"/users/{driver_id}",
        json={"role": "SUPER_ADMIN"},
    )

    assert response.status_code == 403


def test_owner_cannot_change_company(auth_client, create_user):
    owner = create_user(UserRole.OWNER, company_id=1)
    client = auth_client(owner)

    response_driver = client.post(
        "/users",
        json={
            "email": unique_email("driver"),
            "password": "password",
            "role": "DRIVER",
            "company_id": 1,
        },
    )
    driver_id = response_driver.json()["id"]

    response = client.patch(
        f"/users/{driver_id}",
        json={"company_id": 2},
    )

    assert response.status_code == 403


def test_admin_can_change_company(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN)
    client = auth_client(admin)

    response_user = client.post(
        "/users",
        json={
            "email": unique_email("user"),
            "password": "password",
            "role": "DRIVER",
            "company_id": 1,
        },
    )
    user_id = response_user.json()["id"]

    response = client.patch(
        f"/users/{user_id}",
        json={"company_id": 2},
    )

    assert response.status_code == 200
    assert response.json()["company_id"] == 2


def test_password_is_hashed_on_update(session, auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN)
    client = auth_client(admin)

    response_user = client.post(
        "/users",
        json={
            "email": unique_email("user"),
            "password": "password",
            "role": "DRIVER",
            "company_id": 1,
        },
    )
    user_id = response_user.json()["id"]

    # Update password
    client.patch(
        f"/users/{user_id}",
        json={"password": "newpassword"},
    )

    # Vérification DB directe
    user = session.get(User, user_id)

    assert user.password_hash != "newpassword"
    assert user.password_hash is not None


def test_user_cannot_self_promote(auth_client, create_user):
    manager = create_user(UserRole.MANAGER, company_id=1)
    client = auth_client(manager)

    response = client.patch(
        f"/users/{manager.id}",
        json={"role": "OWNER"},
    )

    assert response.status_code == 403


def test_unknown_field_is_ignored(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN)
    client = auth_client(admin)

    response_user = client.post(
        "/users",
        json={
            "email": unique_email("user"),
            "password": "password",
            "role": "DRIVER",
            "company_id": 1,
        },
    )
    user_id = response_user.json()["id"]

    response = client.patch(
        f"/users/{user_id}",
        json={"unknown_field": "test"},
    )

    # Selon config Pydantic → souvent 200
    assert response.status_code in [200, 422]


def test_cannot_update_user_with_existing_email(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN)
    client = auth_client(admin)

    # User 1
    res1 = client.post(
        "/users",
        json={
            "email": unique_email("user1"),
            "password": "password",
            "role": "DRIVER",
            "company_id": 1,
        },
    )
    user1_id = res1.json()["id"]

    # User 2
    res2 = client.post(
        "/users",
        json={
            "email": unique_email("user2"),
            "password": "password",
            "role": "DRIVER",
            "company_id": 1,
        },
    )
    user2 = res2.json()

    # Tentative de duplication
    response = client.patch(
        f"/users/{user2['id']}",
        json={"email": res1.json()["email"]},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already used"


# =========================
# TEST HARD DELETE
# =========================


def test_admin_can_delete_user(auth_client, create_user, session):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    owner = create_user(UserRole.OWNER, company_id=1)

    owner_id = owner.id  # Stocker l'id avant le delete

    client = auth_client(admin)

    response = client.delete(f"/users/{owner.id}")

    assert response.status_code == 204

    # 🔥 Forcer SQLAlchemy à vider son cache
    session.expire_all()

    # Vérifier que l'owner est bien supprimé dans la db
    deleted = session.get(User, owner_id)
    assert deleted is None


def test_admin_delete_nonexistent_user(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.delete("/users/99999")

    assert response.status_code == 404


def test_owner_canot_delete(auth_client, create_user):
    owner = create_user(UserRole.OWNER, company_id=1)
    manager = create_user(UserRole.MANAGER, company_id=1)

    client = auth_client(owner)

    response = client.delete(f"/users/{manager.id}")

    assert response.status_code == 403


def test_manager_cannot_delete_user(auth_client, create_user):
    manager = create_user(UserRole.MANAGER, company_id=1)
    driver = create_user(UserRole.DRIVER, company_id=1)

    client = auth_client(manager)

    response = client.delete(f"/users/{driver.id}")

    assert response.status_code == 403


def test_admin_cannot_delete_self(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.delete(f"/users/{admin.id}")

    assert response.status_code == 403


# =========================
# TEST DESACTIVATION
# =========================


def test_admin_can_deactivate(auth_client, create_user, session):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    owner = create_user(UserRole.OWNER, company_id=1)

    owner_id = owner.id
    client = auth_client(admin)

    # Desactivation
    response = client.patch(f"/users/{owner.id}/deactivate", json={"is_active": False})

    assert response.status_code == 200
    assert response.json()["is_active"] == False

    # Vérification réelle en base
    session.expire_all()
    updated = session.get(User, owner_id)
    assert updated.is_active is False


def test_admin_deactivate_nonexistant_user(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.patch("/users/9999/deactivate")

    assert response.status_code == 404


def test_admin_cannot_deactivate_self(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.patch(f"/users/{admin.id}/deactivate", json={"is_active": False})

    assert response.status_code == 403


def test_deactivate_already_inactive_user(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    user = create_user(UserRole.OWNER, company_id=1)

    client = auth_client(admin)

    # Première désactivation
    client.patch(f"/users/{user.id}/deactivate", json={"is_active": False})

    # Deuxième tentative
    response = client.patch(f"/users/{user.id}/deactivate", json={"is_active": False})

    assert response.status_code in (200, 400)


def test_owner_cannot_deactivate_admin(auth_client, create_user):
    owner = create_user(UserRole.OWNER, company_id=1)
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)

    client = auth_client(owner)

    response = client.patch(f"/users/{admin.id}/deactivate", json={"is_active": False})

    assert response.status_code == 403


def test_owner_can_deactivate(auth_client, create_user, session):
    owner = create_user(UserRole.OWNER, company_id=1)
    manager = create_user(UserRole.MANAGER, company_id=1)

    manager_id = manager.id
    client = auth_client(owner)

    response = client.patch(
        f"/users/{manager.id}/deactivate", json={"is_active": False}
    )

    assert response.status_code == 200
    assert response.json()["is_active"] == False

    # Vérification réelle en base
    session.expire_all()
    updated = session.get(User, manager_id)
    assert updated.is_active is False


def test_owner_cannot_deactivate_outside_his_company(auth_client, create_user):
    owner = create_user(UserRole.OWNER, company_id=1)
    manager = create_user(UserRole.MANAGER, company_id=2)

    client = auth_client(owner)

    response = client.patch(
        f"/users/{manager.id}/deactivate", json={"is_active": False}
    )

    assert response.status_code == 403


def test_manager_cannot_deactivate(auth_client, create_user):
    manager = create_user(UserRole.MANAGER, company_id=1)
    driver = create_user(UserRole.DRIVER, company_id=1)

    client = auth_client(manager)

    response = client.patch(f"/users/{driver.id}/deactivate", json={"is_active": False})

    assert response.status_code == 403


def test_driver_cannot_deactivate(auth_client, create_user):
    driver_1 = create_user(UserRole.DRIVER, company_id=1)
    driver_2 = create_user(UserRole.DRIVER, company_id=1)

    client = auth_client(driver_1)

    response = client.patch(
        f"/users/{driver_2.id}/deactivate", json={"is_active": False}
    )

    assert response.status_code == 403


def test_cannot_deactivate_already_inactive_user(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN)
    client = auth_client(admin)

    # Création user
    res = client.post(
        "/users",
        json={
            "email": unique_email("user"),
            "password": "password",
            "role": "DRIVER",
            "company_id": 1,
        },
    )
    user_id = res.json()["id"]

    # Désactivation 1
    res1 = client.patch(f"/users/{user_id}/deactivate")
    assert res1.status_code == 200

    # Désactivation 2 (doit fail)
    res2 = client.patch(f"/users/{user_id}/deactivate")

    assert res2.status_code == 400
    assert res2.json()["detail"] == "User already inactive"


# =========================
# TEST REACTIVATION
# =========================


def test_admin_can_reactivate(auth_client, create_user, session):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    owner = create_user(UserRole.SUPER_ADMIN, company_id=None)

    # Désactivation de l'owner
    owner.is_active = False
    session.commit()
    session.refresh(owner)

    owner_id = owner.id
    client = auth_client(admin)

    response = client.patch(f"/users/{owner_id}/reactivate", json={"is_active": True})

    assert response.status_code == 200
    assert response.json()["is_active"] == True

    # Vérification réelle en base
    session.expire_all()
    updated = session.get(User, owner_id)
    assert updated.is_active is True


def test_admin_reactivate_nonexistant_user(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    client = auth_client(admin)

    response = client.patch("/users/9999/reactivate")

    assert response.status_code == 404


def test_admin_cannot_reactivate_self(auth_client, create_user, session):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    admin.is_active = False

    client = auth_client(admin)
    session.commit()
    session.refresh(admin)

    response = client.patch(f"/users/{admin.id}/reactivate", json={"is_active": True})

    assert response.status_code == 403


def test_admin_reactivate_already_active_user(auth_client, create_user):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    owner = create_user(UserRole.OWNER, company_id=1)

    client = auth_client(admin)

    response = client.patch(f"/users/{owner.id}/reactivate", json={"is_active": True})

    assert response.status_code == 400


def test_owner_cannot_reactivate_admin(auth_client, create_user, session):
    admin = create_user(UserRole.SUPER_ADMIN, company_id=None)
    owner = create_user(UserRole.OWNER, company_id=1)
    admin.is_active = False
    session.commit()
    session.refresh(admin)

    client = auth_client(owner)

    response = client.patch(f"/users/{admin.id}/reactivate", json={"is_active": True})

    assert response.status_code == 403


def test_owner_can_reactivate(auth_client, create_user, session):
    owner = create_user(UserRole.OWNER, company_id=1)
    manager = create_user(UserRole.MANAGER, company_id=1)
    manager.is_active = False
    session.commit()
    session.refresh(manager)
    manager_id = manager.id

    client = auth_client(owner)

    response = client.patch(f"/users/{manager_id}/reactivate", json={"is_active": True})

    assert response.status_code == 200
    assert response.json()["is_active"] == True

    # Vérification réelle en base
    session.expire_all()
    updated = session.get(User, manager_id)
    assert updated.is_active is True


def test_owner_cannot_reactivate_outside_his_company(auth_client, create_user, session):
    owner = create_user(UserRole.OWNER, company_id=1)
    manager = create_user(UserRole.MANAGER, company_id=2)
    manager.is_active = False
    session.commit()
    session.refresh(manager)
    manager_id = manager.id

    client = auth_client(owner)

    response = client.patch(f"/users/{manager_id}/reactivate", json={"is_active": True})

    assert response.status_code == 403


def test_manager_cannot_reactivate(auth_client, create_user, session):
    manager = create_user(UserRole.MANAGER, company_id=1)
    driver = create_user(UserRole.DRIVER, company_id=1)
    driver.is_active = False
    session.commit()
    session.refresh(driver)

    client = auth_client(manager)

    response = client.patch(f"/users/{driver.id}/reactivate", json={"is_active": True})

    assert response.status_code == 403


# Driver cannot desactivate
def test_driver_cannot_reactivate(auth_client, create_user, session):
    driver_1 = create_user(UserRole.DRIVER, company_id=1)
    driver_2 = create_user(UserRole.DRIVER, company_id=1)
    driver_2.is_active = False
    session.commit()
    session.refresh(driver_2)

    client = auth_client(driver_1)

    response = client.patch(
        f"/users/{driver_2.id}/reactivate", json={"is_active": True}
    )

    assert response.status_code == 403
