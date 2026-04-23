from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import SubRequirement
from app.repositories.sub_requirement_repo import SubRequirementRepository
from app.schemas.sub_requirement import SubRequirementCreate, SubRequirementUpdate
from app.services.history_service import HistoryService
from app.services.requirement_service import RequirementService


class SubRequirementService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = SubRequirementRepository(session)
        self.req_service = RequirementService(session)

    def list_for_requirement(self, requirement_id: int) -> list[SubRequirement]:
        self.req_service.get(requirement_id)
        return self.repo.list_for_requirement(requirement_id)

    def get(self, sub_id: int) -> SubRequirement:
        s = self.repo.get(sub_id)
        if s is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sub-requirement not found"
            )
        return s

    def create(self, requirement_id: int, data: SubRequirementCreate, *, actor: str) -> SubRequirement:
        self.req_service.get(requirement_id)
        existing = self.session.exec(
            select(SubRequirement).where(SubRequirement.key == data.key)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Sub-requirement key already exists"
            )
        obj = SubRequirement(
            key=data.key,
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            parent_requirement_id=requirement_id,
        )
        obj.updated_by = actor
        created = self.repo.create(obj)
        HistoryService(self.session).record_sub_requirement_snapshot(created, actor=actor)
        return created

    def update(self, sub_id: int, data: SubRequirementUpdate, *, actor: str) -> SubRequirement:
        s = self.get(sub_id)
        HistoryService(self.session).record_sub_requirement_snapshot(s, actor=actor)
        payload = data.model_dump(exclude_unset=True)
        if "key" in payload and payload["key"] != s.key:
            if self.session.exec(
                select(SubRequirement).where(SubRequirement.key == payload["key"])
            ).first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="Sub-requirement key already exists"
                )
        for k, v in payload.items():
            setattr(s, k, v)
        s.updated_at = datetime.utcnow()
        s.updated_by = actor
        return self.repo.update(s)

    def delete(self, sub_id: int) -> None:
        s = self.get(sub_id)
        self.repo.delete(s)
