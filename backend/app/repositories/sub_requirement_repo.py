from sqlmodel import Session, func, select

from app.models import SubRequirement, VerificationTest


class SubRequirementRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, sub_id: int) -> SubRequirement | None:
        return self.session.get(SubRequirement, sub_id)

    def list_for_requirement(self, requirement_id: int) -> list[SubRequirement]:
        stmt = (
            select(SubRequirement)
            .where(SubRequirement.parent_requirement_id == requirement_id)
            .order_by(SubRequirement.key)
        )
        return list(self.session.exec(stmt).all())

    def create(self, obj: SubRequirement) -> SubRequirement:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, obj: SubRequirement) -> SubRequirement:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, obj: SubRequirement) -> None:
        self.session.delete(obj)
        self.session.commit()

    def count_for_parent(self, requirement_id: int) -> int:
        stmt = (
            select(func.count()).select_from(SubRequirement).where(
                SubRequirement.parent_requirement_id == requirement_id
            )
        )
        return int(self.session.exec(stmt).one())

    def count_tests(self, sub_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(VerificationTest)
            .where(VerificationTest.sub_requirement_id == sub_id)
        )
        return int(self.session.exec(stmt).one())
