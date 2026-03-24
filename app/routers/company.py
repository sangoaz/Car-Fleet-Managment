"""Routes relatives aux entreprises"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session

from app.database import get_session
from app.deps.auth import get_current_user, require_admin
from app.models import Company, User
from app.schemas import CompanyCreate, CompanyRead
from app.permissions.companies import (
    can_create_company,
    can_read_company,
)
from app.utils.company import get_company_or_404

router = APIRouter(prefix="/companies", tags=["Company"])


# Enregistrer une nouvelle entreprise
@router.post("/", status_code=201, response_model=CompanyRead)
def create_company(
    company: CompanyCreate,
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
@router.get("/{company_id}", response_model=CompanyRead)
def get_company(
    company_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    company = get_company_or_404(session, company_id)

    if not can_read_company(current_user, company):
        raise HTTPException(status_code=403, detail="Not allowed")

    return company


# Désactiver une entreprise
@router.delete("/{company_id}/deactivate", response_model=CompanyRead)
def soft_delete_company(
    company_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):

    company = get_company_or_404(session, company_id)

    if not company.is_active:
        raise HTTPException(status_code=400, detail="Company already inactive")

    company.is_active = False

    session.commit()

    return company


# Réactiver une entreprise
@router.patch("/{company_id}/reactivate", response_model=CompanyRead)
def reactivate_company(
    company_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):

    company = get_company_or_404(session, company_id)

    if company.is_active:
        raise HTTPException(status_code=400, detail="Company already active")

    company.is_active = True

    session.commit()

    return company
