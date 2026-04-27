from collections import defaultdict

from sqlmodel import Session, func, select

from app.models import Requirement, SubRequirement, TestRun, VerificationTest
from app.models.enums import TestStatus
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
        requirement_ids = list(self.session.exec(select(Requirement.id)).all())
        sub_to_parent = {
            int(sub.id): int(sub.parent_requirement_id)
            for sub in self.session.exec(select(SubRequirement)).all()
            if sub.id is not None
        }

        req_to_test_ids: dict[int, set[int]] = defaultdict(set)
        tests = list(self.session.exec(select(VerificationTest)).all())
        for te in tests:
            if te.id is None:
                continue
            rid: int | None = None
            if te.requirement_id is not None:
                rid = te.requirement_id
            elif te.sub_requirement_id is not None:
                rid = sub_to_parent.get(te.sub_requirement_id)
            if rid is not None:
                req_to_test_ids[rid].add(te.id)

        latest_run_status_by_test: dict[int, TestStatus] = {}
        runs = list(
            self.session.exec(
                select(TestRun).order_by(
                    TestRun.verification_test_id,
                    TestRun.ran_at.desc(),
                    TestRun.id.desc(),
                )
            ).all()
        )
        for run in runs:
            if run.verification_test_id not in latest_run_status_by_test:
                latest_run_status_by_test[run.verification_test_id] = run.status

        verified = 0
        for rid in requirement_ids:
            test_ids = req_to_test_ids.get(int(rid), set())
            if not test_ids:
                continue
            if all(latest_run_status_by_test.get(tid) == TestStatus.passed for tid in test_ids):
                verified += 1

        runs_total = int(
            self.session.exec(select(func.count()).select_from(TestRun)).one()
        )

        def count_status(st: TestStatus) -> int:
            if runs_total > 0:
                return int(
                    self.session.exec(
                        select(func.count())
                        .select_from(TestRun)
                        .where(TestRun.status == st)
                    ).one()
                )
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
