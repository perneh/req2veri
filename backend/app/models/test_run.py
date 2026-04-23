from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import TestStatus

if TYPE_CHECKING:
    from app.models.test_object_version import TestObjectVersion
    from app.models.verification_test import VerificationTest


class TestRun(SQLModel, table=True):
    """Recorded execution of a verification test against a specific object version."""

    __tablename__ = "test_runs"

    id: int | None = Field(default=None, primary_key=True)
    verification_test_id: int = Field(foreign_key="verification_tests.id", index=True)
    test_object_version_id: int = Field(foreign_key="test_object_versions.id", index=True)
    status: TestStatus = Field(
        default=TestStatus.not_run,
        sa_column=Column(SAEnum(TestStatus, native_enum=False)),
    )
    expected_result: str = Field(default="", max_length=8192)
    actual_result: str = Field(default="", max_length=8192)
    ran_at: datetime = Field(default_factory=datetime.utcnow)

    verification_test: "VerificationTest" = Relationship(back_populates="runs")
    version: "TestObjectVersion" = Relationship(back_populates="runs")
