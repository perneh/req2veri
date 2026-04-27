from sqlmodel import Session, select

from app.models import TestObjectVersion, TestRun


class VersionRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_version(self, version_id: int) -> TestObjectVersion | None:
        return self.session.get(TestObjectVersion, version_id)

    def get_by_key(self, key: str) -> TestObjectVersion | None:
        return self.session.exec(select(TestObjectVersion).where(TestObjectVersion.key == key)).first()

    def list_versions(self) -> list[TestObjectVersion]:
        return list(
            self.session.exec(select(TestObjectVersion).order_by(TestObjectVersion.created_at.desc())).all()
        )

    def create_version(self, obj: TestObjectVersion) -> TestObjectVersion:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def list_runs_for_version(self, version_id: int) -> list[TestRun]:
        return list(
            self.session.exec(
                select(TestRun)
                .where(TestRun.test_object_version_id == version_id)
                .order_by(TestRun.ran_at.desc())
            ).all()
        )

    def create_run(self, run: TestRun) -> TestRun:
        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)
        return run

    def get_run_for_version_and_test(self, version_id: int, test_id: int) -> TestRun | None:
        stmt = select(TestRun).where(
            TestRun.test_object_version_id == version_id,
            TestRun.verification_test_id == test_id,
        )
        return self.session.exec(stmt).first()

    def update_run(self, run: TestRun) -> TestRun:
        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)
        return run
