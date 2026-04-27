from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import Session

from app.models import Requirement, SubRequirement
from app.models.enums import RequirementStatus
from app.repositories.requirement_repo import RequirementRepository
from app.repositories.sub_requirement_repo import SubRequirementRepository
from app.schemas.requirement import RequirementCoverage, RequirementCreate, RequirementHierarchyItem, RequirementRead, RequirementUpdate
from app.schemas.sub_requirement import SubRequirementRead
from app.services.approval_metadata import init_approved_fields_on_create, sync_approved_fields_after_status_change
from app.services.history_service import HistoryService


class RequirementService:
    def __init__(self, session: Session):
        self.session = session
        self.reqs = RequirementRepository(session)
        self.subs = SubRequirementRepository(session)

    def list(
        self,
        *,
        q: str | None,
        status: RequirementStatus | None,
        priority: str | None,
        skip: int,
        limit: int,
    ) -> list[Requirement]:
        return self.reqs.list(q=q, status=status, priority=priority, skip=skip, limit=limit)

    def list_hierarchy(self, *, limit: int = 500) -> list[RequirementHierarchyItem]:
        reqs = self.reqs.list(q=None, status=None, priority=None, skip=0, limit=limit)
        return [
            RequirementHierarchyItem(
                requirement=RequirementRead.model_validate(r),
                sub_requirements=[
                    SubRequirementRead.model_validate(s) for s in self.subs.list_for_requirement(r.id)  # type: ignore[arg-type]
                ],
            )
            for r in reqs
        ]

    def get(self, req_id: int) -> Requirement:
        r = self.reqs.get(req_id)
        if r is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")
        return r

    def create(self, data: RequirementCreate, *, actor: str) -> Requirement:
        if self.reqs.get_by_key(data.key):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Requirement key already exists"
            )
        obj = Requirement.model_validate(data)
        obj.updated_by = actor
        init_approved_fields_on_create(obj, status=obj.status, actor=actor)
        created = self.reqs.create(obj)
        HistoryService(self.session).record_requirement_snapshot(created, actor=actor)
        return created

    def update(self, req_id: int, data: RequirementUpdate, *, actor: str) -> Requirement:
        r = self.get(req_id)
        HistoryService(self.session).record_requirement_snapshot(r, actor=actor)
        payload = data.model_dump(exclude_unset=True)
        old_status = r.status
        if "key" in payload and payload["key"] != r.key:
            if self.reqs.get_by_key(payload["key"]):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="Requirement key already exists"
                )
        for k, v in payload.items():
            setattr(r, k, v)
        r.updated_at = datetime.utcnow()
        r.updated_by = actor
        if "status" in payload:
            sync_approved_fields_after_status_change(r, old_status=old_status, new_status=r.status, actor=actor)
        return self.reqs.update(r)

    def delete(self, req_id: int) -> None:
        r = self.get(req_id)
        self.reqs.delete(r)

    def coverage(self, req_id: int) -> RequirementCoverage:
        r = self.get(req_id)
        c = self.reqs.coverage_for(req_id)
        return RequirementCoverage(
            requirement_id=r.id,  # type: ignore[arg-type]
            requirement_key=r.key,
            tests_total=c["tests_total"],
            tests_passed=c["tests_passed"],
            subrequirements_total=c["subrequirements_total"],
            subrequirements_with_test=c["subrequirements_with_test"],
            all_subrequirements_have_test=c["all_subrequirements_have_test"],
        )

    def ensure_sub_belongs(self, req_id: int, sub: SubRequirement) -> None:
        if sub.parent_requirement_id != req_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sub-requirement not found")
