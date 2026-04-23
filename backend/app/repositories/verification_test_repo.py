from sqlalchemy import and_, or_
from sqlmodel import Session, func, select

from app.models import VerificationTest
from app.models.enums import TestStatus


class VerificationTestRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, test_id: int) -> VerificationTest | None:
        return self.session.get(VerificationTest, test_id)

    def get_by_key(self, key: str) -> VerificationTest | None:
        return self.session.exec(select(VerificationTest).where(VerificationTest.key == key)).first()

    def list_for_requirement(self, requirement_id: int) -> list[VerificationTest]:
        stmt = (
            select(VerificationTest)
            .where(VerificationTest.requirement_id == requirement_id)
            .order_by(VerificationTest.key)
        )
        return list(self.session.exec(stmt).all())

    def list_for_sub_requirement(self, sub_requirement_id: int) -> list[VerificationTest]:
        stmt = (
            select(VerificationTest)
            .where(VerificationTest.sub_requirement_id == sub_requirement_id)
            .order_by(VerificationTest.key)
        )
        return list(self.session.exec(stmt).all())

    def list_all(
        self,
        *,
        q: str | None = None,
        status: TestStatus | None = None,
        skip: int = 0,
        limit: int = 200,
        reference: str = "any",
    ) -> list[VerificationTest]:
        stmt = select(VerificationTest)
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                (VerificationTest.key.ilike(like))
                | (VerificationTest.title.ilike(like))
                | (VerificationTest.description.ilike(like))
                | (VerificationTest.precondition.ilike(like))
                | (VerificationTest.action.ilike(like))
            )
        if status is not None:
            stmt = stmt.where(VerificationTest.status == status)
        if reference == "linked":
            stmt = stmt.where(
                or_(
                    VerificationTest.requirement_id.is_not(None),
                    VerificationTest.sub_requirement_id.is_not(None),
                )
            )
        elif reference == "unlinked":
            stmt = stmt.where(
                and_(
                    VerificationTest.requirement_id.is_(None),
                    VerificationTest.sub_requirement_id.is_(None),
                )
            )
        stmt = stmt.offset(skip).limit(limit).order_by(VerificationTest.key)
        return list(self.session.exec(stmt).all())

    def create(self, obj: VerificationTest) -> VerificationTest:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, obj: VerificationTest) -> VerificationTest:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, obj: VerificationTest) -> None:
        self.session.delete(obj)
        self.session.commit()

    def count_by_status(self, status: TestStatus) -> int:
        stmt = (
            select(func.count())
            .select_from(VerificationTest)
            .where(VerificationTest.status == status)
        )
        return int(self.session.exec(stmt).one())

    def count_all(self) -> int:
        stmt = select(func.count()).select_from(VerificationTest)
        return int(self.session.exec(stmt).one())
