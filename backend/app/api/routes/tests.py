from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.dependencies import CurrentUser
from app.models.enums import TestStatus
from app.schemas.verification_test import VerificationTestCreate, VerificationTestRead, VerificationTestUpdate
from app.services.verification_test_service import VerificationTestService

router = APIRouter(prefix="/tests", tags=["tests"])

ReferenceFilter = Literal["any", "linked", "unlinked"]


@router.get("", response_model=list[VerificationTestRead])
def list_tests(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    q: str | None = None,
    status: TestStatus | None = None,
    reference: ReferenceFilter = "any",
    skip: int = 0,
    limit: int = Query(200, le=500),
):
    return VerificationTestService(session).list_all(
        q=q, status=status, skip=skip, limit=limit, reference=reference
    )


@router.post("", response_model=VerificationTestRead, status_code=201)
def create_test_root(
    user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    data: VerificationTestCreate,
):
    """Create a verification test with optional link to a requirement or sub-requirement (or neither)."""
    return VerificationTestService(session).create(data, actor=user.username)


@router.get("/{test_id}", response_model=VerificationTestRead)
def get_test(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    test_id: int,
):
    return VerificationTestService(session).get(test_id)


@router.patch("/{test_id}", response_model=VerificationTestRead)
def update_test(
    user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    test_id: int,
    data: VerificationTestUpdate,
):
    return VerificationTestService(session).update(test_id, data, actor=user.username)


@router.delete("/{test_id}", status_code=204)
def delete_test(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    test_id: int,
):
    VerificationTestService(session).delete(test_id)
