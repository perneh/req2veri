from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import Priority, RequirementStatus


class SubRequirementBase(BaseModel):
    key: str = Field(max_length=48)
    title: str
    description: str = ""
    status: RequirementStatus = RequirementStatus.draft
    priority: Priority = Priority.medium


class SubRequirementCreate(SubRequirementBase):
    pass


class SubRequirementUpdate(BaseModel):
    key: str | None = None
    title: str | None = None
    description: str | None = None
    status: RequirementStatus | None = None
    priority: Priority | None = None


class SubRequirementRead(SubRequirementBase):
    id: int
    parent_requirement_id: int
    created_at: datetime
    updated_at: datetime
    updated_by: str

    model_config = {"from_attributes": True}
