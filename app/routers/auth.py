from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.database import get_session
from app.deps.auth import get_current_user
from app.models import User, Company
from app.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):

    user = session.exec(select(User).where(User.email == form_data.username)).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive account")

    if user.company_id:
        company = session.get(Company, user.company_id)
        if not company or not company.is_active:
            raise HTTPException(403, detail="Company inactive")

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "company_id": user.company_id,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
