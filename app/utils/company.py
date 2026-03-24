from fastapi import HTTPException
from sqlmodel import Session

from app.models import Company


def get_company_or_404(session: Session, company_id: int) -> Company:
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Entreprise introuvable")
    return company
