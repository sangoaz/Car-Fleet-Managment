from fastapi import HTTPException
from sqlmodel import Session

from app.enums import UserRole


def check_vehicle_access(user, vehicule):
    if user.role != UserRole.SUPER_ADMIN:
        if user.company_id != vehicule.company_id:
            raise HTTPException(status_code=403, detail="Not allowed")


def ensure_driver(user):
    if user.role != UserRole.DRIVER:
        raise HTTPException(
            status_code=400,
            detail="Vehicle can only be assigned to a driver",
        )


def check_same_company(user, vehicule):
    if user.company_id != vehicule.company_id:
        raise HTTPException(
            status_code=403,
            detail="Driver must belong to same company",
        )
