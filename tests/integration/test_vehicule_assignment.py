from app.enums import UserRole
from app.models import VehiculeAssignment
from datetime import datetime, UTC


# =========================
# TESTS D'ASSIGNATION
# =========================


def test_owner_can_assign_driver(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)

    client = auth_client(owner)

    res = client.post(
        f"/vehicules/{vehicule_db.id}/assignments/",
        json={"driver_id": driver.id},
    )

    assert res.status_code == 200

    data = res.json()

    assert data["vehicule_id"] == vehicule_db.id
    assert data["user_id"] == driver.id


def test_driver_cannot_assign_vehicle(auth_client, create_user, vehicule_db):
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)

    client = auth_client(driver)

    res = client.post(
        f"/vehicules/{vehicule_db.id}/assignments/",
        json={"driver_id": driver.id},
    )

    assert res.status_code == 403


def test_cannot_assign_driver_from_other_company(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)

    other_driver = create_user(UserRole.DRIVER, company_id=None)

    client = auth_client(owner)

    res = client.post(
        f"/vehicules/{vehicule_db.id}/assignments/",
        json={"driver_id": other_driver.id},
    )

    assert res.status_code == 403


def test_cannot_assign_same_driver_twice(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)

    client = auth_client(owner)

    client.post(
        f"/vehicules/{vehicule_db.id}/assignments/",
        json={"driver_id": driver.id},
    )

    res = client.post(
        f"/vehicules/{vehicule_db.id}/assignments/",
        json={"driver_id": driver.id},
    )

    assert res.status_code == 400


def test_can_reassign_after_unassign(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)

    client = auth_client(owner)

    first = client.post(
        f"/vehicules/{vehicule_db.id}/assignments/",
        json={"driver_id": driver.id},
    )

    assignment_id = first.json()["id"]

    client.delete(f"/vehicules/{vehicule_db.id}/assignments/{assignment_id}")

    second = client.post(
        f"/vehicules/{vehicule_db.id}/assignments/",
        json={"driver_id": driver.id},
    )

    assert second.status_code == 200


def test_vehicule_not_found(auth_client, create_user, vehicule_db):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)

    client = auth_client(owner)

    res = client.post(
        f"/vehicules/9999/assignments/",
        json={"driver_id": driver.id},
    )

    assert res.status_code == 404
    assert res.json()["detail"] == "Véhicule introuvable"


# =========================
# TESTS D'AFFICHAGE DES ASSIGNATIONS
# =========================


def test_list_vehicle_assignments(auth_client, create_user, vehicule_db, session):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)

    assignment = VehiculeAssignment(
        vehicule_id=vehicule_db.id,
        user_id=driver.id,
    )

    session.add(assignment)
    session.commit()

    client = auth_client(owner)

    res = client.get(f"/vehicules/{vehicule_db.id}/assignments/")

    assert res.status_code == 200
    assert len(res.json()) == 1


def test_vehicule_list_not_found(auth_client, create_user, vehicule_db, session):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)

    assignment = VehiculeAssignment(
        vehicule_id=9999,
        user_id=driver.id,
    )

    session.add(assignment)
    session.commit()

    client = auth_client(owner)

    res = client.get(f"/vehicules/9999/assignments/")

    assert res.status_code == 404
    assert res.json()["detail"] == "Véhicule introuvable"


# =========================
# TESTS DESASSIGNATION
# =========================


def test_owner_can_unassign_driver(auth_client, create_user, vehicule_db, session):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)

    assignment = VehiculeAssignment(
        vehicule_id=vehicule_db.id,
        user_id=driver.id,
    )

    session.add(assignment)
    session.commit()
    session.refresh(assignment)

    client = auth_client(owner)

    res = client.delete(f"/vehicules/{vehicule_db.id}/assignments/{assignment.id}")

    assert res.status_code == 200

    session.refresh(assignment)

    assert assignment.end_date is not None


def test_cannot_unassign_twice(auth_client, create_user, vehicule_db, session):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)

    assignment = VehiculeAssignment(
        vehicule_id=vehicule_db.id,
        user_id=driver.id,
        end_date=datetime.now(UTC),
    )

    session.add(assignment)
    session.commit()

    client = auth_client(owner)

    res = client.delete(f"/vehicules/{vehicule_db.id}/assignments/{assignment.id}")

    assert res.status_code == 400


def test_owner_cannot_unassign_vehicule_not_found(
    auth_client, create_user, vehicule_db, session
):
    owner = create_user(UserRole.OWNER, company_id=vehicule_db.company_id)
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)

    assignment = VehiculeAssignment(
        vehicule_id=vehicule_db.id,
        user_id=driver.id,
    )

    session.add(assignment)
    session.commit()
    session.refresh(assignment)

    client = auth_client(owner)

    res = client.delete(f"/vehicules/9999/assignments/{assignment.id}")

    assert res.status_code == 404
    assert res.json()["detail"] == "Véhicule introuvable"
