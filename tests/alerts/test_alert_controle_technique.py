from datetime import date, timedelta

from app.models import Vehicule, Entretien
from app.enums import EntretienType
from app.services.alerts.controle_technique import check_controle_technique_alert


def test_ct_warning_if_no_entretien(session):
    vehicule = Vehicule(
        plate="CT-001",
        model="Test",
        km=50000,
        company_id=999,
    )
    session.add(vehicule)
    session.commit()

    alert = check_controle_technique_alert(
        session=session,
        vehicule_id=vehicule.id,
    )

    assert alert.type == "CONTROLE_TECHNIQUE"
    assert alert.status == "warning"


def test_ct_ok(session):
    vehicule = Vehicule(
        plate="CT-002",
        model="Test",
        km=50000,
        company_id=999,
    )
    session.add(vehicule)
    session.commit()

    entretien = Entretien(
        vehicule_id=vehicule.id,
        type=EntretienType.CONTROLE_TECHNIQUE,
        km=48000,
        date=date.today() - timedelta(days=300),
    )
    session.add(entretien)
    session.commit()

    alert = check_controle_technique_alert(
        session=session,
        vehicule_id=vehicule.id,
    )

    assert alert.status == "ok"


def test_ct_alert_if_expired(session):
    vehicule = Vehicule(
        plate="CT-003",
        model="Test",
        km=50000,
        company_id=999,
    )
    session.add(vehicule)
    session.commit()

    entretien = Entretien(
        vehicule_id=vehicule.id,
        type=EntretienType.CONTROLE_TECHNIQUE,
        km=45000,
        date=date.today() - timedelta(days=800),
    )
    session.add(entretien)
    session.commit()

    alert = check_controle_technique_alert(
        session=session,
        vehicule_id=vehicule.id,
    )

    assert alert.status == "alert"
