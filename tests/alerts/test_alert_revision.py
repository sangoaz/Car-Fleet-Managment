from datetime import date, timedelta

from app.models import Vehicule, Entretien
from app.enums import EntretienType
from app.services.alerts.revision import check_revision_alert


def test_revision_warning_if_no_entretien(session):
    vehicule = Vehicule(plate="REV-001", model="Test", km=40000)
    session.add(vehicule)
    session.commit()

    alert = check_revision_alert(
        session=session,
        vehicule_id=vehicule.id,
        vehicule_km=vehicule.km,
    )

    assert alert.type == "REVISION"
    assert alert.status == "warning"


def test_revision_ok(session):
    vehicule = Vehicule(plate="REV-002", model="Test", km=50000)
    session.add(vehicule)
    session.commit()

    entretien = Entretien(
        vehicule_id=vehicule.id,
        type=EntretienType.REVISION,
        km=30000,
        date=date.today() - timedelta(days=300),
    )
    session.add(entretien)
    session.commit()

    alert = check_revision_alert(
        session=session,
        vehicule_id=vehicule.id,
        vehicule_km=vehicule.km,
    )

    assert alert.status == "ok"


def test_revision_alert_by_km(session):
    vehicule = Vehicule(plate="REV-003", model="Test", km=80000)
    session.add(vehicule)
    session.commit()

    entretien = Entretien(
        vehicule_id=vehicule.id,
        type=EntretienType.REVISION,
        km=40000,
        date=date.today(),
    )
    session.add(entretien)
    session.commit()

    alert = check_revision_alert(
        session=session,
        vehicule_id=vehicule.id,
        vehicule_km=vehicule.km,
    )

    assert alert.status == "alert"


def test_revision_alert_by_date(session):
    vehicule = Vehicule(plate="REV-004", model="Test", km=50000)
    session.add(vehicule)
    session.commit()

    entretien = Entretien(
        vehicule_id=vehicule.id,
        type=EntretienType.REVISION,
        km=45000,
        date=date.today() - timedelta(days=900),
    )
    session.add(entretien)
    session.commit()

    alert = check_revision_alert(
        session=session,
        vehicule_id=vehicule.id,
        vehicule_km=vehicule.km,
    )

    assert alert.status == "alert"
