from datetime import date

from app.models import Vehicule, Entretien
from app.enums import EntretienType
from app.services.alerts.pneus import check_pneus_alert


def test_pneus_warning_if_no_entretien(session):
    vehicule = Vehicule(
        plate="PN-001",
        model="Test",
        km=50000,
        company_id=999,
    )
    session.add(vehicule)
    session.commit()

    alert = check_pneus_alert(
        session=session,
        vehicule_id=vehicule.id,
        vehicule_km=vehicule.km,
    )

    assert alert.type == "PNEUS"
    assert alert.status == "warning"


def test_pneus_ok(session):
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
        type=EntretienType.PNEUS,
        km=30000,
        date=date.today(),
    )
    session.add(entretien)
    session.commit()

    alert = check_pneus_alert(
        session=session,
        vehicule_id=vehicule.id,
        vehicule_km=vehicule.km,
    )

    assert alert.status == "ok"


def test_pneus_alert(session):
    vehicule = Vehicule(
        plate="PN-003",
        model="Test",
        km=80000,
        company_id=999,
    )
    session.add(vehicule)
    session.commit()

    entretien = Entretien(
        vehicule_id=vehicule.id,
        type=EntretienType.PNEUS,
        km=35000,
        date=date.today(),
    )
    session.add(entretien)
    session.commit()

    alert = check_pneus_alert(
        session=session,
        vehicule_id=vehicule.id,
        vehicule_km=vehicule.km,
    )

    assert alert.status == "alert"
