"""Routes relatives à l'assignation des véhicules"""

from datetime import datetime, UTC
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select


from app.database import get_session
from app.deps.auth import get_current_user
from app.enums import UserRole
from app.models import Vehicule, User, VehiculeAssignment
from app.permissions.vehicule_assignement import can_assign_vehicle
from app.schemas import VehiculeAssignmentCreate, VehiculeAssignmentRead
from app.utils.vehicules import get_vehicule_or_404


router = APIRouter(
    prefix="/vehicules/{vehicule_id}/assignments", tags=["vehicule_assignments"]
)


# Assigner un véhicule à un utilisateur
@router.post("/", response_model=VehiculeAssignmentRead)
def assign_driver(
    vehicule_id: int,
    assignment: VehiculeAssignmentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    vehicule = get_vehicule_or_404(session, vehicule_id)

    if not can_assign_vehicle(current_user):
        raise HTTPException(status_code=403, detail="Not allowed")

    driver = session.get(User, assignment.driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    if driver.role != UserRole.DRIVER:
        raise HTTPException(
            status_code=400, detail="Vehicle can only be assigned to a driver"
        )

    if driver.company_id != vehicule.company_id:
        raise HTTPException(
            status_code=403, detail="Driver must belong to same company"
        )

    # Vérifie uniquement les assignations actives
    existing_assignment = session.exec(
        select(VehiculeAssignment)
        .where(VehiculeAssignment.vehicule_id == vehicule_id)
        .where(VehiculeAssignment.user_id == driver.id)
        .where(VehiculeAssignment.end_date == None)
    ).first()

    if existing_assignment:
        raise HTTPException(status_code=400, detail="Driver already assigned")

    assignment_db = VehiculeAssignment(
        vehicule_id=vehicule.id,
        user_id=driver.id,
    )

    session.add(assignment_db)
    session.commit()
    session.refresh(assignment_db)

    return assignment_db


# Liste des drivers d'un véhicule
@router.get("/", response_model=list[VehiculeAssignmentRead])
def list_assignments(
    vehicule_id: int,
    active_only: bool = False,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    vehicule = get_vehicule_or_404(session, vehicule_id)

    query = select(VehiculeAssignment).where(
        VehiculeAssignment.vehicule_id == vehicule_id
    )

    if active_only:
        query = query.where(VehiculeAssignment.end_date == None)

    assignments = session.exec(query).all()

    return assignments


# Désassigner un driver
@router.delete("/{assignment_id}")
def remove_assignment(
    vehicule_id: int,
    assignment_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    vehicule = get_vehicule_or_404(session, vehicule_id)

    if not can_assign_vehicle(current_user):
        raise HTTPException(status_code=403, detail="Not allowed")

    assignment = session.get(VehiculeAssignment, assignment_id)

    if not assignment or assignment.vehicule_id != vehicule_id:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if assignment.end_date is not None:
        raise HTTPException(status_code=400, detail="Assignment already ended")

    assignment.end_date = datetime.now(UTC)

    session.add(assignment)
    session.commit()
    session.refresh(assignment)

    return {"message": "Driver unassigned successfully"}
