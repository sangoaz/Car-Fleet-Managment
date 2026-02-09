from datetime import date

from app.models import Vehicule, Entretien
from app.enums import EntretienType
from app.services.alerts.freins import check_freins_alert


def test_freins_warning_if_no_entretien(session):
    vehicule = Vehicule(
        plate="PN-001",
        model="Test",
        km=50000,
        company_id=999,
    )
    session.add(vehicule)
    session.commit()

    alert = check_freins_alert(
        session=session,
        vehicule_id=vehicule.id,
        vehicule_km=vehicule.km,
    )

    assert alert.type == "FREINS"
    assert alert.status == "warning"


def test_freins_ok(session):
    vehicule = Vehicule(
        plate="PN-002",
        model="Test",
        km=60000,
        company_id=999,
    )
    session.add(vehicule)
    session.commit()

    entretien = Entretien(
        vehicule_id=vehicule.id,
        type=EntretienType.FREINS,
        km=30000,
        date=date.today(),
    )
    session.add(entretien)
    session.commit()

    alert = check_freins_alert(
        session=session,
        vehicule_id=vehicule.id,
        vehicule_km=vehicule.km,
    )

    assert alert.status == "ok"


def test_freins_alert(session):
    vehicule = Vehicule(
        plate="PN-003",
        model="Test",
        km=130000,
        company_id=999,
    )
    session.add(vehicule)
    session.commit()

    entretien = Entretien(
        vehicule_id=vehicule.id,
        type=EntretienType.FREINS,
        km=35000,
        date=date.today(),
    )
    session.add(entretien)
    session.commit()

    alert = check_freins_alert(
        session=session,
        vehicule_id=vehicule.id,
        vehicule_km=vehicule.km,
    )

    assert alert.status == "alert"
