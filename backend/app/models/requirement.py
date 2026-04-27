from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import Priority, RequirementStatus

if TYPE_CHECKING:
    from app.models.sub_requirement import SubRequirement
    from app.models.verification_test import VerificationTest


class Requirement(SQLModel, table=True):
    __tablename__ = "requirements"

    id: int | None = Field(default=None, primary_key=True)
    key: str = Field(index=True, unique=True, max_length=32)
    title: str = Field(max_length=512)
    description: str = Field(default="", max_length=8192)
    status: RequirementStatus = Field(
        default=RequirementStatus.draft,
        sa_column=Column(SAEnum(RequirementStatus, native_enum=False)),
    )
    priority: Priority = Field(
        default=Priority.medium,
        sa_column=Column(SAEnum(Priority, native_enum=False)),
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: str = Field(default="", max_length=64)
    approved_by: str = Field(default="", max_length=64)
    approved_at: datetime | None = Field(default=None)

    sub_requirements: list["SubRequirement"] = Relationship(
        back_populates="parent_requirement",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    verification_tests: list["VerificationTest"] = Relationship(
        back_populates="requirement",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
