from app.services.vehicule_assignment_service import (
    is_driver_assigned,
    get_driver_vehicules,
)
from app.models import VehiculeAssignment, Vehicule
from app.enums import UserRole
from datetime import UTC


def test_driver_is_assigned(session, create_user, vehicule_db):
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)

    assignment = VehiculeAssignment(
        vehicule_id=vehicule_db.id,
        user_id=driver.id,
    )

    session.add(assignment)
    session.commit()

    result = is_driver_assigned(session, driver.id, vehicule_db.id)

    assert result is True


def test_driver_not_assigned(session, create_user, vehicule_db):
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)

    result = is_driver_assigned(session, driver.id, vehicule_db.id)

    assert result is False


from datetime import datetime


def test_driver_assignment_ended(session, create_user, vehicule_db):
    driver = create_user(UserRole.DRIVER, company_id=vehicule_db.company_id)

    assignment = VehiculeAssignment(
        vehicule_id=vehicule_db.id,
        user_id=driver.id,
        end_date=datetime.now(UTC),
    )

    session.add(assignment)
    session.commit()

    result = is_driver_assigned(session, driver.id, vehicule_db.id)

    assert result is False


def test_get_driver_vehicules_returns_only_assigned(session, create_user, company_db):
    driver = create_user(UserRole.DRIVER, company_id=company_db.id)

    vehicule1 = Vehicule(
        plate="A",
        model="Test",
        km=1000,
        company_id=company_db.id,
    )

    vehicule2 = Vehicule(
        plate="B",
        model="Test",
        km=1000,
        company_id=company_db.id,
    )

    session.add_all([vehicule1, vehicule2])
    session.commit()

    # Assigner seulement vehicule1
    assignment = VehiculeAssignment(
        vehicule_id=vehicule1.id,
        user_id=driver.id,
    )

    session.add(assignment)
    session.commit()

    result = get_driver_vehicules(session, driver.id)

    assert len(result) == 1
    assert result[0].id == vehicule1.id


def test_get_driver_vehicules_excludes_ended_assignments(
    session, create_user, company_db
):
    driver = create_user(UserRole.DRIVER, company_id=company_db.id)

    vehicule = Vehicule(
        plate="A",
        model="Test",
        km=1000,
        company_id=company_db.id,
    )

    session.add(vehicule)
    session.commit()

    assignment = VehiculeAssignment(
        vehicule_id=vehicule.id,
        user_id=driver.id,
        end_date=datetime.now(UTC),
    )

    session.add(assignment)
    session.commit()

    result = get_driver_vehicules(session, driver.id)

    assert result == []
