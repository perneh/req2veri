from sqlmodel import Session, col, func, select

from app.models import Requirement, SubRequirement, VerificationTest
from app.models.enums import RequirementStatus, TestStatus


class RequirementRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, req_id: int) -> Requirement | None:
        return self.session.get(Requirement, req_id)

    def get_by_key(self, key: str) -> Requirement | None:
        return self.session.exec(select(Requirement).where(Requirement.key == key)).first()

    def list(
        self,
        *,
        q: str | None = None,
        status: RequirementStatus | None = None,
        priority: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Requirement]:
        stmt = select(Requirement)
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                (Requirement.key.ilike(like))
                | (Requirement.title.ilike(like))
                | (Requirement.description.ilike(like))
            )
        if status is not None:
            stmt = stmt.where(Requirement.status == status)
        if priority is not None:
            stmt = stmt.where(Requirement.priority == priority)
        stmt = stmt.offset(skip).limit(limit).order_by(Requirement.key)
        return list(self.session.exec(stmt).all())

    def create(self, obj: Requirement) -> Requirement:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, obj: Requirement) -> Requirement:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, obj: Requirement) -> None:
        self.session.delete(obj)
        self.session.commit()

    def count_verified(self) -> int:
        stmt = select(func.count()).select_from(Requirement).where(
            Requirement.status == RequirementStatus.verified
        )
        return int(self.session.exec(stmt).one())

    def coverage_for(self, req_id: int) -> dict:
        req = self.get(req_id)
        if req is None:
            return {}
        tests_direct = self.session.exec(
            select(VerificationTest).where(VerificationTest.requirement_id == req_id)
        ).all()
        subs = self.session.exec(
            select(SubRequirement).where(SubRequirement.parent_requirement_id == req_id)
        ).all()
        sub_ids = [s.id for s in subs if s.id is not None]
        tests_on_subs: list[VerificationTest] = []
        if sub_ids:
            tests_on_subs = list(
                self.session.exec(
                    select(VerificationTest).where(col(VerificationTest.sub_requirement_id).in_(sub_ids))  # type: ignore[arg-type]
                ).all()
            )
        all_tests = list(tests_direct) + tests_on_subs
        passed = sum(1 for t in all_tests if t.status == TestStatus.passed)
        sub_with_test = 0
        for s in subs:
            if s.id is None:
                continue
            cnt = self.session.exec(
                select(func.count())
                .select_from(VerificationTest)
                .where(VerificationTest.sub_requirement_id == s.id)
            ).one()
            if int(cnt) > 0:
                sub_with_test += 1
        return {
            "tests_total": len(all_tests),
            "tests_passed": passed,
            "subrequirements_total": len(subs),
            "subrequirements_with_test": sub_with_test,
            "all_subrequirements_have_test": len(subs) == 0 or sub_with_test == len(subs),
        }
