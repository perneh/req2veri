from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.dependencies import CurrentUser
from app.schemas.history import HistoryEntryMeta, SubRequirementHistoryDetail
from app.schemas.sub_requirement import SubRequirementRead, SubRequirementUpdate
from app.schemas.verification_test import VerificationTestCreate, VerificationTestRead
from app.services.history_service import HistoryService
from app.services.sub_requirement_service import SubRequirementService
from app.services.verification_test_service import VerificationTestService

router = APIRouter(prefix="/subrequirements", tags=["subrequirements"])


@router.get("/{sub_requirement_id}", response_model=SubRequirementRead)
def get_sub(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    sub_requirement_id: int,
):
    return SubRequirementService(session).get(sub_requirement_id)


@router.get("/{sub_requirement_id}/history", response_model=list[HistoryEntryMeta])
def list_sub_requirement_history(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    sub_requirement_id: int,
) -> list:
    return HistoryService(session).list_sub_requirement_history(sub_requirement_id)


@router.get("/{sub_requirement_id}/history/{history_id}", response_model=SubRequirementHistoryDetail)
def get_sub_requirement_history_entry(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    sub_requirement_id: int,
    history_id: int,
):
    h = HistoryService(session).get_sub_requirement_history(sub_requirement_id, history_id)
    return SubRequirementHistoryDetail(
        id=h.id,  # type: ignore[arg-type]
        version=h.version,
        created_at=h.created_at,
        created_by=h.created_by,
        snapshot=SubRequirementRead.model_validate(h.snapshot),
    )


@router.post("/{sub_requirement_id}/history/{history_id}/restore", response_model=SubRequirementRead)
def restore_sub_requirement_version(
    user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    sub_requirement_id: int,
    history_id: int,
):
    return HistoryService(session).restore_sub_requirement(sub_requirement_id, history_id, actor=user.username)


@router.delete("/{sub_requirement_id}/history/{history_id}", status_code=204)
def delete_sub_requirement_history_entry(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    sub_requirement_id: int,
    history_id: int,
) -> None:
    HistoryService(session).delete_sub_requirement_history(sub_requirement_id, history_id)


@router.patch("/{sub_requirement_id}", response_model=SubRequirementRead)
def update_sub(
    user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    sub_requirement_id: int,
    data: SubRequirementUpdate,
):
    return SubRequirementService(session).update(sub_requirement_id, data, actor=user.username)


@router.delete("/{sub_requirement_id}", status_code=204)
def delete_sub(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    sub_requirement_id: int,
):
    SubRequirementService(session).delete(sub_requirement_id)


@router.get("/{sub_requirement_id}/tests", response_model=list[VerificationTestRead])
def list_tests(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    sub_requirement_id: int,
):
    return VerificationTestService(session).list_for_sub_requirement(sub_requirement_id)


@router.post("/{sub_requirement_id}/tests", response_model=VerificationTestRead, status_code=201)
def create_test(
    user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    sub_requirement_id: int,
    data: VerificationTestCreate,
):
    body = data.model_copy(update={"sub_requirement_id": sub_requirement_id, "requirement_id": None})
    return VerificationTestService(session).create(body, actor=user.username)
