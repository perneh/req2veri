from sqlmodel import Session, func, select

from app.models import Requirement, SubRequirement, VerificationTest
from app.models.enums import RequirementStatus, TestStatus
from app.schemas.dashboard import DashboardSummary


class DashboardService:
    def __init__(self, session: Session):
        self.session = session

    def summary(self) -> DashboardSummary:
        req_total = int(
            self.session.exec(select(func.count()).select_from(Requirement)).one()
        )
        sub_total = int(
            self.session.exec(select(func.count()).select_from(SubRequirement)).one()
        )
        tests_total = int(
            self.session.exec(select(func.count()).select_from(VerificationTest)).one()
        )
        verified = int(
            self.session.exec(
                select(func.count())
                .select_from(Requirement)
                .where(Requirement.status == RequirementStatus.verified)
            ).one()
        )

        def count_status(st: TestStatus) -> int:
            return int(
                self.session.exec(
                    select(func.count())
                    .select_from(VerificationTest)
                    .where(VerificationTest.status == st)
                ).one()
            )

        return DashboardSummary(
            requirements_total=req_total,
            subrequirements_total=sub_total,
            tests_total=tests_total,
            requirements_verified=verified,
            tests_passed=count_status(TestStatus.passed),
            tests_failed=count_status(TestStatus.failed),
            tests_not_run=count_status(TestStatus.not_run),
            tests_blocked=count_status(TestStatus.blocked),
        )
