from datetime import date, timedelta

from app.models import Vehicule, Entretien
from app.enums import EntretienType
from app.services.alerts.vidange import check_vidange_alert


def test_vidange_warning_if_no_entretien(session):
    vehicule = Vehicule(
        plate="VID-001",
        model="Test",
        km=50000,
        company_id=999,
    )
    session.add(vehicule)
    session.commit()

    alert = check_vidange_alert(
        session=session,
        vehicule_id=vehicule.id,
        vehicule_km=vehicule.km,
    )

    assert alert.status == "warning"
    assert alert.type == "VIDANGE"


def test_vidange_ok(session):
    vehicule = Vehicule(
        plate="VID-002",
        model="Test",
        km=52000,
        company_id=999,
    )
    session.add(vehicule)
    session.commit()

    entretien = Entretien(
        vehicule_id=vehicule.id,
        type=EntretienType.VIDANGE,
        km=45000,
        date=date.today() - timedelta(days=100),
    )
    session.add(entretien)
    session.commit()

    alert = check_vidange_alert(
        session=session,
        vehicule_id=vehicule.id,
        vehicule_km=vehicule.km,
    )

    assert alert.status == "ok"


def test_vidange_alert_by_km(session):
    vehicule = Vehicule(
        plate="VID-003",
        model="Test",
        km=70000,
        company_id=999,
    )
    session.add(vehicule)
    session.commit()

    entretien = Entretien(
        vehicule_id=vehicule.id,
        type=EntretienType.VIDANGE,
        km=50000,
        date=date.today(),
    )
    session.add(entretien)
    session.commit()

    alert = check_vidange_alert(
        session=session,
        vehicule_id=vehicule.id,
        vehicule_km=vehicule.km,
    )

    assert alert.status == "alert"


def test_vidange_alert_by_date(session):
    vehicule = Vehicule(
        plate="VID-004",
        model="Test",
        km=52000,
        company_id=999,
    )
    session.add(vehicule)
    session.commit()

    entretien = Entretien(
        vehicule_id=vehicule.id,
        type=EntretienType.VIDANGE,
        km=50000,
        date=date.today() - timedelta(days=400),
    )
    session.add(entretien)
    session.commit()

    alert = check_vidange_alert(
        session=session,
        vehicule_id=vehicule.id,
        vehicule_km=vehicule.km,
    )

    assert alert.status == "alert"
