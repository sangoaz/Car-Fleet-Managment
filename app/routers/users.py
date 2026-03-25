"""Routes relatives à la gestions des utilisateurs"""

from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlmodel import select, func, Session
from sqlalchemy import desc

from app.database import get_session
from app.deps.auth import require_roles, require_admin
from app.enums import UserRole
from app.models import User
from app.permissions.users import (
    can_create_user,
    can_deactivate_user,
    can_delete_user,
    can_modify_user,
    can_reactivate_user,
)
from app.schemas import UserCreate, UserRead, UserUpdate
from app.security import hash_password
from app.utils.users import get_user_or_404

router = APIRouter(prefix="/users", tags=["Users"])


# Route de création de l'utilisateur
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(
        require_roles(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.MANAGER)
    ),
):

    if not can_create_user(current_user, user_in.role):
        raise HTTPException(status_code=403, detail="Not allowed")

    if current_user.role != UserRole.SUPER_ADMIN:
        user_in.company_id = current_user.company_id

    hashed_password = hash_password(user_in.password)

    user = User(
        email=user_in.email,
        password_hash=hashed_password,
        role=user_in.role,
        company_id=user_in.company_id,
    )

    existing = session.exec(select(User).where(User.email == user_in.email)).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already used")

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


# Route de lecture de l'utilisateur
@router.get("/", response_model=list[UserRead])
def list_users(
    company_id: int | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(
        require_roles(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.MANAGER)
    ),
):
    statement = select(User)

    if current_user.role != UserRole.SUPER_ADMIN:
        statement = statement.where(User.company_id == current_user.company_id)
    elif company_id:
        statement = statement.where(User.company_id == company_id)

    return session.exec(statement).all()


# Route d'update de l'utilisateur
@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(
        require_roles(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.MANAGER)
    ),
):
    user = get_user_or_404(session, user_id)

    if not can_modify_user(current_user, user):
        raise HTTPException(status_code=403, detail="Not allowed")

    # 🔐 ROLE
    if getattr(user_in, "role", None) is not None:
        if not can_create_user(current_user, user_in.role):
            raise HTTPException(status_code=403, detail="Role change not allowed")
        user.role = user_in.role

    if user.id == current_user.id and getattr(user_in, "role", None) is not None:
        raise HTTPException(status_code=403, detail="Cannot change your own role")

    # 🔐 COMPANY
    if getattr(user_in, "company_id", None) is not None:
        if current_user.role != UserRole.SUPER_ADMIN:
            raise HTTPException(status_code=403, detail="Company change not allowed")
        user.company_id = user_in.company_id

    # 🔐 PASSWORD
    if getattr(user_in, "password", None) is not None:
        user.password_hash = hash_password(user_in.password)

    # 🔐 EMAIL
    if getattr(user_in, "email", None) is not None:
        existing = session.exec(select(User).where(User.email == user_in.email)).first()

        if existing and existing.id != user.id:
            raise HTTPException(status_code=400, detail="Email already used")

        user.email = user_in.email

    session.commit()
    session.refresh(user)

    return user


# Route de hard delete par le super_admin
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    user = get_user_or_404(session, user_id)

    if not can_delete_user(current_user, user):
        raise HTTPException(status_code=403, detail="Not allowed")

    session.delete(user)
    session.commit()


# Route de soft delete (desactivation du compte)
@router.patch("/{user_id}/deactivate", response_model=UserRead)
def deactivate_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.OWNER)),
):
    user = get_user_or_404(session, user_id)

    if not user.is_active:
        raise HTTPException(400, "User already inactive")

    if not can_deactivate_user(current_user, user):
        raise HTTPException(status_code=403, detail="Not allowed")

    user.is_active = False

    session.commit()
    session.refresh(user)

    return user


# Route de réactivation d'un utilisateur
@router.patch("/{user_id}/reactivate", response_model=UserRead)
def reactivate_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.OWNER)),
):
    user = get_user_or_404(session, user_id)

    if user.is_active:
        raise HTTPException(status_code=400, detail="User already active")

    if not can_reactivate_user(current_user, user):
        raise HTTPException(status_code=403, detail="Not allowed")

    user.is_active = True

    session.commit()
    session.refresh(user)

    return user
