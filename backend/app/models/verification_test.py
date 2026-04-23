from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import TestMethod, TestStatus

if TYPE_CHECKING:
    from app.models.requirement import Requirement
    from app.models.sub_requirement import SubRequirement
    from app.models.test_run import TestRun


class VerificationTest(SQLModel, table=True):
    __tablename__ = "verification_tests"

    id: int | None = Field(default=None, primary_key=True)
    key: str = Field(index=True, unique=True, max_length=32)
    title: str = Field(max_length=512)
    description: str = Field(default="", max_length=8192)
    precondition: str = Field(default="", max_length=8192)
    action: str = Field(default="", max_length=8192)
    method: TestMethod = Field(
        default=TestMethod.test,
        sa_column=Column(SAEnum(TestMethod, native_enum=False)),
    )
    status: TestStatus = Field(
        default=TestStatus.not_run,
        sa_column=Column(SAEnum(TestStatus, native_enum=False)),
    )
    requirement_id: int | None = Field(default=None, foreign_key="requirements.id", index=True)
    sub_requirement_id: int | None = Field(
        default=None, foreign_key="sub_requirements.id", index=True
    )
    expected_result: str = Field(default="", max_length=8192)
    actual_result: str = Field(default="", max_length=8192)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: str = Field(default="", max_length=64)

    requirement: Optional["Requirement"] = Relationship(back_populates="verification_tests")
    sub_requirement: Optional["SubRequirement"] = Relationship(back_populates="verification_tests")
    runs: list["TestRun"] = Relationship(
        back_populates="verification_test",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
