from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.models.enums import TestMethod, TestStatus


class VerificationTestBase(BaseModel):
    key: str | None = Field(default=None, max_length=32)
    title: str
    description: str = ""
    precondition: str = ""
    action: str = ""
    method: TestMethod = TestMethod.test
    status: TestStatus = TestStatus.not_run
    requirement_id: int | None = None
    sub_requirement_id: int | None = None
    expected_result: str = ""
    actual_result: str = ""

    @model_validator(mode="after")
    def at_most_one_parent(self) -> "VerificationTestBase":
        rid, sid = self.requirement_id, self.sub_requirement_id
        if rid is not None and sid is not None:
            raise ValueError("Cannot set both requirement_id and sub_requirement_id")
        return self


class VerificationTestCreate(VerificationTestBase):
    """Create a test optionally linked to a requirement, a sub-requirement, or neither (standalone)."""


class VerificationTestUpdate(BaseModel):
    key: str | None = None
    title: str | None = None
    description: str | None = None
    precondition: str | None = None
    action: str | None = None
    method: TestMethod | None = None
    status: TestStatus | None = None
    requirement_id: int | None = None
    sub_requirement_id: int | None = None
    expected_result: str | None = None
    actual_result: str | None = None

    @model_validator(mode="after")
    def at_most_one_parent(self) -> "VerificationTestUpdate":
        rid, sid = self.requirement_id, self.sub_requirement_id
        if rid is not None and sid is not None:
            raise ValueError("Cannot set both requirement_id and sub_requirement_id")
        return self


class VerificationTestRead(VerificationTestBase):
    id: int
    created_at: datetime
    updated_at: datetime
    updated_by: str

    model_config = {"from_attributes": True}
