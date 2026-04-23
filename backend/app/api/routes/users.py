from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import CurrentUser
from app.models import User
from app.schemas.auth import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> list[User]:
    return list(session.exec(select(User).order_by(User.id)).all())


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser) -> User:
    return user
