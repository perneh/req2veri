from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import Priority, RequirementStatus
from app.schemas.sub_requirement import SubRequirementRead


class RequirementBase(BaseModel):
    key: str = Field(max_length=32)
    title: str
    description: str = ""
    status: RequirementStatus = RequirementStatus.draft
    priority: Priority = Priority.medium


class RequirementCreate(RequirementBase):
    pass


class RequirementUpdate(BaseModel):
    key: str | None = None
    title: str | None = None
    description: str | None = None
    status: RequirementStatus | None = None
    priority: Priority | None = None


class RequirementRead(RequirementBase):
    id: int
    created_at: datetime
    updated_at: datetime
    updated_by: str

    model_config = {"from_attributes": True}


class RequirementHierarchyItem(BaseModel):
    """One requirement with all its sub-requirements (for overview tree)."""

    requirement: RequirementRead
    sub_requirements: list[SubRequirementRead]


class RequirementCoverage(BaseModel):
    requirement_id: int
    requirement_key: str
    tests_total: int
    tests_passed: int
    subrequirements_total: int
    subrequirements_with_test: int
    all_subrequirements_have_test: bool
