"""Routes relatives à la gestions des utilisateurs"""

from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlmodel import select, func, Session
from sqlalchemy import desc

from app.database import get_session
from app.enums import UserRole
from app.models import User
from app.schemas import UserCreate, UserRead, UserUpdate
from app.deps.auth import require_roles, require_admin
from app.security import hash_password
from app.permissions.users import (
    can_create_user,
    can_deactivate_user,
    can_delete_user,
    can_modify_user,
    can_reactivate_user,
)

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
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not can_modify_user(current_user, user):
        raise HTTPException(status_code=403)

    update_data = user_in.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(user, key, value)

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
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not can_delete_user(current_user, user):
        raise HTTPException(status_code=403)

    session.delete(user)
    session.commit()


# Route de soft delete (desactivation du compte)
@router.patch("/{user_id}/deactivate", response_model=UserRead)
def deactivate_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.OWNER)),
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not can_deactivate_user(current_user, user):
        raise HTTPException(status_code=403)

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
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active:
        raise HTTPException(status_code=400, detail="User already active")

    if not can_reactivate_user(current_user, user):
        raise HTTPException(status_code=403)

    user.is_active = True

    session.commit()
    session.refresh(user)

    return user
