from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.dependencies import CurrentUser
from app.models import Requirement
from app.models.enums import RequirementStatus
from app.schemas.requirement import (
    RequirementCoverage,
    RequirementCreate,
    RequirementHierarchyItem,
    RequirementRead,
    RequirementUpdate,
)
from app.schemas.sub_requirement import SubRequirementCreate, SubRequirementRead, SubRequirementUpdate
from app.schemas.verification_test import VerificationTestCreate, VerificationTestRead, VerificationTestUpdate
from app.services.requirement_service import RequirementService
from app.services.sub_requirement_service import SubRequirementService
from app.services.verification_test_service import VerificationTestService

router = APIRouter(prefix="/requirements", tags=["requirements"])


@router.get("", response_model=list[RequirementRead])
def list_requirements(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    q: str | None = None,
    status: RequirementStatus | None = None,
    priority: str | None = None,
    skip: int = 0,
    limit: int = Query(100, le=500),
) -> list[Requirement]:
    svc = RequirementService(session)
    return svc.list(q=q, status=status, priority=priority, skip=skip, limit=limit)


@router.get("/hierarchy", response_model=list[RequirementHierarchyItem])
def list_requirements_hierarchy(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> list[RequirementHierarchyItem]:
    return RequirementService(session).list_hierarchy()


@router.post("", response_model=RequirementRead, status_code=201)
def create_requirement(
    user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    data: RequirementCreate,
) -> Requirement:
    return RequirementService(session).create(data, actor=user.username)


@router.get("/{requirement_id}", response_model=RequirementRead)
def get_requirement(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    requirement_id: int,
) -> Requirement:
    return RequirementService(session).get(requirement_id)


@router.patch("/{requirement_id}", response_model=RequirementRead)
def update_requirement(
    user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    requirement_id: int,
    data: RequirementUpdate,
) -> Requirement:
    return RequirementService(session).update(requirement_id, data, actor=user.username)


@router.delete("/{requirement_id}", status_code=204)
def delete_requirement(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    requirement_id: int,
) -> None:
    RequirementService(session).delete(requirement_id)


@router.get("/{requirement_id}/subrequirements", response_model=list[SubRequirementRead])
def list_subrequirements(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    requirement_id: int,
) -> list:
    return SubRequirementService(session).list_for_requirement(requirement_id)


@router.post("/{requirement_id}/subrequirements", response_model=SubRequirementRead, status_code=201)
def create_subrequirement(
    user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    requirement_id: int,
    data: SubRequirementCreate,
):
    return SubRequirementService(session).create(requirement_id, data, actor=user.username)


@router.get("/{requirement_id}/tests", response_model=list[VerificationTestRead])
def list_tests_for_requirement(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    requirement_id: int,
):
    return VerificationTestService(session).list_for_requirement(requirement_id)


@router.post("/{requirement_id}/tests", response_model=VerificationTestRead, status_code=201)
def create_test_for_requirement(
    user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    requirement_id: int,
    data: VerificationTestCreate,
):
    body = data.model_copy(update={"requirement_id": requirement_id, "sub_requirement_id": None})
    return VerificationTestService(session).create(body, actor=user.username)


@router.get("/{requirement_id}/coverage", response_model=RequirementCoverage)
def requirement_coverage(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    requirement_id: int,
):
    return RequirementService(session).coverage(requirement_id)


@router.get("/{requirement_id}/traceability")
def traceability(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    requirement_id: int,
):
    req = RequirementService(session).get(requirement_id)
    subs = SubRequirementService(session).list_for_requirement(requirement_id)
    tests_direct = VerificationTestService(session).list_for_requirement(requirement_id)
    sub_payload = []
    for s in subs:
        st = VerificationTestService(session).list_for_sub_requirement(s.id)  # type: ignore[arg-type]
        sub_payload.append(
            {
                "sub_requirement": SubRequirementRead.model_validate(s).model_dump(),
                "tests": [VerificationTestRead.model_validate(t).model_dump() for t in st],
            }
        )
    return {
        "requirement": RequirementRead.model_validate(req).model_dump(),
        "tests_on_requirement": [VerificationTestRead.model_validate(t).model_dump() for t in tests_direct],
        "sub_requirements": sub_payload,
    }
