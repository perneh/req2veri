from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import Session, func, select

from app.models import SubRequirement, VerificationTest
from app.models.entity_history import RequirementHistory, SubRequirementHistory, VerificationTestHistory
from app.repositories.requirement_repo import RequirementRepository
from app.repositories.sub_requirement_repo import SubRequirementRepository
from app.repositories.verification_test_repo import VerificationTestRepository
from app.schemas.requirement import RequirementRead
from app.schemas.sub_requirement import SubRequirementRead
from app.schemas.verification_test import VerificationTestRead


class HistoryService:
    def __init__(self, session: Session):
        self.session = session
        self.reqs = RequirementRepository(session)
        self.subs = SubRequirementRepository(session)
        self.tests = VerificationTestRepository(session)

    def _requirement_or_404(self, requirement_id: int) -> None:
        if self.reqs.get(requirement_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")

    def _sub_or_404(self, sub_requirement_id: int) -> None:
        if self.subs.get(sub_requirement_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sub-requirement not found")

    def _test_or_404(self, verification_test_id: int) -> None:
        if self.tests.get(verification_test_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")

    @staticmethod
    def _validate_test_parent_refs(
        session: Session,
        requirement_id: int | None,
        sub_requirement_id: int | None,
    ) -> None:
        if requirement_id is not None and sub_requirement_id is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot set both requirement_id and sub_requirement_id",
            )
        with session.no_autoflush:
            if requirement_id is not None:
                if RequirementRepository(session).get(requirement_id) is None:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")
            if sub_requirement_id is not None:
                if session.get(SubRequirement, sub_requirement_id) is None:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sub-requirement not found")

    # --- Requirement ---

    def _next_requirement_version(self, requirement_id: int) -> int:
        m = self.session.exec(
            select(func.coalesce(func.max(RequirementHistory.version), 0)).where(
                RequirementHistory.requirement_id == requirement_id
            )
        ).one()
        return int(m) + 1

    def record_requirement_snapshot(self, req: Requirement, *, actor: str) -> None:
        if req.id is None:
            return
        snap = RequirementRead.model_validate(req).model_dump(mode="json")
        v = self._next_requirement_version(req.id)
        self.session.add(
            RequirementHistory(
                requirement_id=req.id,
                version=v,
                snapshot=snap,
                created_by=actor,
            )
        )
        self.session.commit()

    def list_requirement_history(self, requirement_id: int) -> list[RequirementHistory]:
        self._requirement_or_404(requirement_id)
        stmt = (
            select(RequirementHistory)
            .where(RequirementHistory.requirement_id == requirement_id)
            .order_by(RequirementHistory.version.desc())
        )
        return list(self.session.exec(stmt).all())

    def get_requirement_history(self, requirement_id: int, history_id: int) -> RequirementHistory:
        self._requirement_or_404(requirement_id)
        h = self.session.get(RequirementHistory, history_id)
        if h is None or h.requirement_id != requirement_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History entry not found")
        return h

    def restore_requirement(self, requirement_id: int, history_id: int, *, actor: str) -> Requirement:
        h = self.get_requirement_history(requirement_id, history_id)
        req = self.reqs.get(requirement_id)
        if req is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")
        self.record_requirement_snapshot(req, actor=actor)
        data = RequirementRead.model_validate(h.snapshot)
        req.key = data.key
        req.title = data.title
        req.description = data.description
        req.status = data.status
        req.priority = data.priority
        req.approved_by = data.approved_by
        req.approved_at = data.approved_at
        req.updated_at = datetime.utcnow()
        req.updated_by = actor
        return self.reqs.update(req)

    def delete_requirement_history(self, requirement_id: int, history_id: int) -> None:
        h = self.get_requirement_history(requirement_id, history_id)
        self.session.delete(h)
        self.session.commit()

    # --- Sub-requirement ---

    def _next_sub_version(self, sub_requirement_id: int) -> int:
        m = self.session.exec(
            select(func.coalesce(func.max(SubRequirementHistory.version), 0)).where(
                SubRequirementHistory.sub_requirement_id == sub_requirement_id
            )
        ).one()
        return int(m) + 1

    def record_sub_requirement_snapshot(self, sub: SubRequirement, *, actor: str) -> None:
        if sub.id is None:
            return
        snap = SubRequirementRead.model_validate(sub).model_dump(mode="json")
        v = self._next_sub_version(sub.id)
        self.session.add(
            SubRequirementHistory(
                sub_requirement_id=sub.id,
                version=v,
                snapshot=snap,
                created_by=actor,
            )
        )
        self.session.commit()

    def list_sub_requirement_history(self, sub_requirement_id: int) -> list[SubRequirementHistory]:
        self._sub_or_404(sub_requirement_id)
        stmt = (
            select(SubRequirementHistory)
            .where(SubRequirementHistory.sub_requirement_id == sub_requirement_id)
            .order_by(SubRequirementHistory.version.desc())
        )
        return list(self.session.exec(stmt).all())

    def get_sub_requirement_history(self, sub_requirement_id: int, history_id: int) -> SubRequirementHistory:
        self._sub_or_404(sub_requirement_id)
        h = self.session.get(SubRequirementHistory, history_id)
        if h is None or h.sub_requirement_id != sub_requirement_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History entry not found")
        return h

    def restore_sub_requirement(self, sub_requirement_id: int, history_id: int, *, actor: str) -> SubRequirement:
        h = self.get_sub_requirement_history(sub_requirement_id, history_id)
        sub = self.subs.get(sub_requirement_id)
        if sub is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sub-requirement not found")
        self.record_sub_requirement_snapshot(sub, actor=actor)
        data = SubRequirementRead.model_validate(h.snapshot)
        sub.parent_requirement_id = data.parent_requirement_id
        sub.key = data.key
        sub.title = data.title
        sub.description = data.description
        sub.status = data.status
        sub.priority = data.priority
        sub.approved_by = data.approved_by
        sub.approved_at = data.approved_at
        sub.updated_at = datetime.utcnow()
        sub.updated_by = actor
        return self.subs.update(sub)

    def delete_sub_requirement_history(self, sub_requirement_id: int, history_id: int) -> None:
        h = self.get_sub_requirement_history(sub_requirement_id, history_id)
        self.session.delete(h)
        self.session.commit()

    # --- Verification test ---

    def _next_test_version(self, verification_test_id: int) -> int:
        m = self.session.exec(
            select(func.coalesce(func.max(VerificationTestHistory.version), 0)).where(
                VerificationTestHistory.verification_test_id == verification_test_id
            )
        ).one()
        return int(m) + 1

    def record_verification_test_snapshot(self, test: VerificationTest, *, actor: str) -> None:
        if test.id is None:
            return
        snap = VerificationTestRead.model_validate(test).model_dump(mode="json")
        v = self._next_test_version(test.id)
        self.session.add(
            VerificationTestHistory(
                verification_test_id=test.id,
                version=v,
                snapshot=snap,
                created_by=actor,
            )
        )
        self.session.commit()

    def list_verification_test_history(self, verification_test_id: int) -> list[VerificationTestHistory]:
        self._test_or_404(verification_test_id)
        stmt = (
            select(VerificationTestHistory)
            .where(VerificationTestHistory.verification_test_id == verification_test_id)
            .order_by(VerificationTestHistory.version.desc())
        )
        return list(self.session.exec(stmt).all())

    def get_verification_test_history(self, verification_test_id: int, history_id: int) -> VerificationTestHistory:
        self._test_or_404(verification_test_id)
        h = self.session.get(VerificationTestHistory, history_id)
        if h is None or h.verification_test_id != verification_test_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History entry not found")
        return h

    def restore_verification_test(self, verification_test_id: int, history_id: int, *, actor: str) -> VerificationTest:
        h = self.get_verification_test_history(verification_test_id, history_id)
        test = self.tests.get(verification_test_id)
        if test is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
        self.record_verification_test_snapshot(test, actor=actor)
        data = VerificationTestRead.model_validate(h.snapshot)
        test.key = data.key
        test.title = data.title
        test.description = data.description
        test.precondition = data.precondition
        test.action = data.action
        test.method = data.method
        test.status = data.status
        test.requirement_id = data.requirement_id
        test.sub_requirement_id = data.sub_requirement_id
        test.expected_result = data.expected_result
        test.actual_result = data.actual_result
        self._validate_test_parent_refs(self.session, test.requirement_id, test.sub_requirement_id)
        test.updated_at = datetime.utcnow()
        test.updated_by = actor
        return self.tests.update(test)

    def delete_verification_test_history(self, verification_test_id: int, history_id: int) -> None:
        h = self.get_verification_test_history(verification_test_id, history_id)
        self.session.delete(h)
        self.session.commit()
