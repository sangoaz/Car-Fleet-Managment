from sqlmodel import Session, select

from app.models import VehiculeAssignment, Vehicule


def is_driver_assigned(session: Session, user_id: int, vehicule_id: int) -> bool:
    assignment = session.exec(
        select(VehiculeAssignment)
        .where(VehiculeAssignment.user_id == user_id)
        .where(VehiculeAssignment.vehicule_id == vehicule_id)
        .where(VehiculeAssignment.end_date == None)
    ).first()

    return assignment is not None


def get_driver_vehicules(session: Session, user_id: int):
    return session.exec(
        select(Vehicule)
        .join(VehiculeAssignment)
        .where(VehiculeAssignment.user_id == user_id)
        .where(VehiculeAssignment.end_date == None)
    ).all()
