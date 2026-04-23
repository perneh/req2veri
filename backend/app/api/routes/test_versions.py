from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.dependencies import CurrentUser
from app.models import TestObjectVersion, TestRun
from app.repositories.version_repo import VersionRepository
from app.schemas.versioning import TestObjectVersionCreate, TestObjectVersionRead, TestRunCreate, TestRunRead

router = APIRouter(prefix="/test-object-versions", tags=["test-object-versions"])


@router.get("", response_model=list[TestObjectVersionRead])
def list_versions(_: CurrentUser, session: Annotated[Session, Depends(get_session)]):
    return VersionRepository(session).list_versions()


@router.post("", response_model=TestObjectVersionRead, status_code=201)
def create_version(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    data: TestObjectVersionCreate,
):
    repo = VersionRepository(session)
    if repo.get_by_key(data.key):
        raise HTTPException(status_code=409, detail="Version key already exists")
    v = TestObjectVersion(key=data.key, name=data.name, description=data.description)
    return repo.create_version(v)


@router.get("/{version_id}/runs", response_model=list[TestRunRead])
def list_runs(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    version_id: int,
):
    repo = VersionRepository(session)
    if repo.get_version(version_id) is None:
        raise HTTPException(status_code=404, detail="Version not found")
    return repo.list_runs_for_version(version_id)


@router.post("/{version_id}/runs", response_model=TestRunRead, status_code=201)
def create_run(
    _: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    version_id: int,
    data: TestRunCreate,
):
    repo = VersionRepository(session)
    if repo.get_version(version_id) is None:
        raise HTTPException(status_code=404, detail="Version not found")
    from app.services.verification_test_service import VerificationTestService

    VerificationTestService(session).get(data.verification_test_id)
    run = TestRun(
        verification_test_id=data.verification_test_id,
        test_object_version_id=version_id,
        status=data.status,
        expected_result=data.expected_result,
        actual_result=data.actual_result,
    )
    return repo.create_run(run)
