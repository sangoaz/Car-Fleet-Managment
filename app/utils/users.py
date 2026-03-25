from fastapi import HTTPException
from sqlmodel import Session

from app.enums import UserRole
from app.models import User


def get_user_or_404(session: Session, user_id: int) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user
