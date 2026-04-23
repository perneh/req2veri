"""Load demo data. Run: DATABASE_URL=... python -m scripts.seed from backend directory."""

from sqlmodel import Session, create_engine, select

from app.models import Requirement, SubRequirement, TestObjectVersion, TestRun, User, VerificationTest
from app.models.enums import Priority, RequirementStatus, TestMethod, TestStatus
from app.security import hash_password


def seed() -> None:
    import os

    url = os.environ.get(
        "DATABASE_URL", "postgresql+psycopg2://req2veri:req2veri@localhost:5432/req2veri"
    )
    engine = create_engine(url)
    with Session(engine) as session:
        if not session.exec(select(User).where(User.username == "demo")).first():
            session.add(
                User(
                    username="demo",
                    email="demo@example.com",
                    hashed_password=hash_password("demo12345"),
                )
            )
            session.commit()

        if session.exec(select(Requirement).where(Requirement.key == "REQ-001")).first():
            return

        r1 = Requirement(
            key="REQ-001",
            title="User authentication",
            description="The system shall authenticate users securely.",
            status=RequirementStatus.approved,
            priority=Priority.high,
        )
        session.add(r1)
        session.commit()
        session.refresh(r1)

        sr1 = SubRequirement(
            key="REQ-001.1",
            parent_requirement_id=r1.id,  # type: ignore[arg-type]
            title="Password policy",
            description="Passwords must meet complexity rules.",
            status=RequirementStatus.implemented,
            priority=Priority.medium,
        )
        session.add(sr1)
        session.commit()
        session.refresh(sr1)

        t1 = VerificationTest(
            key="TEST-001",
            title="Login with valid credentials",
            description="Verify successful login flow.",
            precondition="User account exists and is active.",
            action="Submit valid username and password on the login form.",
            method=TestMethod.test,
            status=TestStatus.passed,
            requirement_id=r1.id,
            sub_requirement_id=None,
            expected_result="HTTP 200 and session token returned",
            actual_result="Passed in CI pipeline #1042",
        )
        t2 = VerificationTest(
            key="TEST-002",
            title="Password complexity enforced",
            description="Verify password rules on registration.",
            precondition="Registration form is available.",
            action="Attempt registration with passwords that violate the policy.",
            method=TestMethod.analysis,
            status=TestStatus.not_run,
            requirement_id=None,
            sub_requirement_id=sr1.id,
            expected_result="Weak passwords rejected",
            actual_result="",
        )
        session.add(t1)
        session.add(t2)
        session.commit()
        session.refresh(t1)

        v1 = TestObjectVersion(
            key="build-1042",
            name="Release candidate 1.0.0",
            description="CI build from main branch",
        )
        session.add(v1)
        session.commit()
        session.refresh(v1)

        session.add(
            TestRun(
                verification_test_id=t1.id,  # type: ignore[arg-type]
                test_object_version_id=v1.id,  # type: ignore[arg-type]
                status=TestStatus.passed,
                expected_result=t1.expected_result,
                actual_result="OK",
            )
        )
        session.commit()


if __name__ == "__main__":
    seed()
    print("Seed completed.")
