"""Routes relatives aux entreprises"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import select, func, Session
from sqlalchemy import desc

from app.database import get_session
from app.deps.auth import get_current_user
from app.models import Company, User
from app.schemas import CreateCompany
from app.permissions.companies import (
    can_create_company,
    can_delete_company,
    can_modify_company,
    can_read_company,
)

router = APIRouter(prefix="/companies", tags=["Company"])


# Enregistrer une nouvelle entreprise
@router.post("/", status_code=201)
def create_company(
    company: CreateCompany,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not can_create_company(current_user):
        raise HTTPException(status_code=403, detail="Not allowed")

    new_company = Company(
        name=company.name,
    )
    session.add(new_company)
    session.commit()
    session.refresh(new_company)
    return new_company


# Afficher une entreprise
@router.get("/{company_id}")
def get_company(
    company_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    company = session.get(Company, company_id)

    if not company:
        raise HTTPException(status_code=404, detail="Entreprise introuvable")

    if not can_read_company(current_user, company):
        raise HTTPException(status_code=403, detail="Not allowed")

    return company
