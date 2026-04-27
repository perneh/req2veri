from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import Session, func, select

from app.models import SubRequirement, VerificationTest
from app.repositories.sub_requirement_repo import SubRequirementRepository
from app.repositories.verification_test_repo import VerificationTestRepository
from app.schemas.verification_test import VerificationTestCreate, VerificationTestUpdate
from app.services.history_service import HistoryService
from app.services.requirement_service import RequirementService


def _validate_parent_state(
    session: Session,
    requirement_id: int | None,
    sub_requirement_id: int | None,
) -> None:
    """Allow no link, or exactly one of requirement / sub-requirement; forbid both set."""
    if requirement_id is not None and sub_requirement_id is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot set both requirement_id and sub_requirement_id",
        )
    # Avoid autoflush: a pending VerificationTest with an invalid FK would flush before
    # the parent lookup and raise IntegrityError instead of a clean 404.
    with session.no_autoflush:
        if requirement_id is not None:
            RequirementService(session).get(requirement_id)
        if sub_requirement_id is not None:
            sub = session.get(SubRequirement, sub_requirement_id)
            if sub is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Sub-requirement not found"
                )


class VerificationTestService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = VerificationTestRepository(session)
        self.sub_repo = SubRequirementRepository(session)
        self.req_service = RequirementService(session)

    def list_all(
        self,
        *,
        q: str | None,
        status,
        skip: int,
        limit: int,
        reference: str = "any",
    ) -> list[VerificationTest]:
        return self.repo.list_all(q=q, status=status, skip=skip, limit=limit, reference=reference)

    def list_for_requirement(self, requirement_id: int) -> list[VerificationTest]:
        self.req_service.get(requirement_id)
        return self.repo.list_for_requirement(requirement_id)

    def list_for_sub_requirement(self, sub_requirement_id: int) -> list[VerificationTest]:
        if self.sub_repo.get(sub_requirement_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sub-requirement not found")
        return self.repo.list_for_sub_requirement(sub_requirement_id)

    def get(self, test_id: int) -> VerificationTest:
        t = self.repo.get(test_id)
        if t is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
        return t

    def _next_available_key(self, base: str, *, current_id: int | None = None) -> str:
        base = base[:32]
        candidate = base
        i = 2
        while True:
            existing = self.repo.get_by_key(candidate)
            if existing is None or existing.id == current_id:
                return candidate
            suffix = f"-{i}"
            candidate = f"{base[: max(1, 32 - len(suffix))]}{suffix}"
            i += 1

    def _derive_link_based_key(
        self,
        *,
        requirement_id: int | None,
        sub_requirement_id: int | None,
        current_id: int | None = None,
    ) -> str:
        if sub_requirement_id is not None:
            sub = self.session.get(SubRequirement, sub_requirement_id)
            if sub is not None:
                base = sub.key
                if base.upper().startswith("REQ-"):
                    base = "VER-" + base[4:]
                else:
                    base = "VER-" + base
                return self._next_available_key(base, current_id=current_id)
        if requirement_id is not None:
            req = self.req_service.get(requirement_id)
            base = req.key
            if base.upper().startswith("REQ-"):
                base = "VER-" + base[4:]
            else:
                base = "VER-" + base
            return self._next_available_key(base, current_id=current_id)

        existing_count = int(
            self.session.exec(
                select(func.count())
                .select_from(VerificationTest)
                .where(
                    VerificationTest.requirement_id.is_(None),
                    VerificationTest.sub_requirement_id.is_(None),
                )
            ).one()
        )
        return self._next_available_key(f"NOT-LINKED-{existing_count + 1:03d}", current_id=current_id)

    def create(self, data: VerificationTestCreate, *, actor: str) -> VerificationTest:
        _validate_parent_state(self.session, data.requirement_id, data.sub_requirement_id)
        if self.repo.get_by_title(data.title):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Test title already exists")
        obj = VerificationTest.model_validate(data)
        if obj.key:
            if self.repo.get_by_key(obj.key):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Test key already exists")
        else:
            obj.key = self._derive_link_based_key(
                requirement_id=obj.requirement_id, sub_requirement_id=obj.sub_requirement_id
            )
        obj.updated_by = actor
        created = self.repo.create(obj)
        HistoryService(self.session).record_verification_test_snapshot(created, actor=actor)
        return created

    def update(self, test_id: int, data: VerificationTestUpdate, *, actor: str) -> VerificationTest:
        t = self.get(test_id)
        HistoryService(self.session).record_verification_test_snapshot(t, actor=actor)
        payload = data.model_dump(exclude_unset=True)
        old_key = t.key
        old_title = t.title
        if "requirement_id" in payload and payload["requirement_id"] is not None:
            t.sub_requirement_id = None
        if "sub_requirement_id" in payload and payload["sub_requirement_id"] is not None:
            t.requirement_id = None
        for k, v in payload.items():
            setattr(t, k, v)
        _validate_parent_state(self.session, t.requirement_id, t.sub_requirement_id)
        if "key" in payload and payload["key"] != old_key:
            if self.repo.get_by_key(payload["key"]):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="Test key already exists"
                )
        if "title" in payload and payload["title"] != old_title:
            if self.repo.get_by_title(payload["title"]):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="Test title already exists"
                )
        if "key" not in payload and (
            ("requirement_id" in payload) or ("sub_requirement_id" in payload)
        ):
            t.key = self._derive_link_based_key(
                requirement_id=t.requirement_id,
                sub_requirement_id=t.sub_requirement_id,
                current_id=t.id,
            )
        t.updated_at = datetime.utcnow()
        t.updated_by = actor
        return self.repo.update(t)

    def delete(self, test_id: int) -> None:
        t = self.get(test_id)
        self.repo.delete(t)
