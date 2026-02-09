"""Routes relatives aux entreprises"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import select, func, Session
from sqlalchemy import desc

from app.database import get_session
from app.models import Company
from app.schemas import CreateCompany

router = APIRouter(prefix="/company", tags=["Company"])


# Enregistrer une nouvelle entreprise
@router.post("/", status_code=201)
def create_company(company: CreateCompany, session: Session = Depends(get_session)):
    new_company = Company(
        name=company.name,
    )
    session.add(new_company)
    session.commit()
    session.refresh(new_company)
    return new_company
