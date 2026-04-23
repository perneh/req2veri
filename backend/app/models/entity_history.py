from datetime import datetime
from typing import Any

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class RequirementHistory(SQLModel, table=True):
    __tablename__ = "requirement_history"

    id: int | None = Field(default=None, primary_key=True)
    requirement_id: int = Field(foreign_key="requirements.id", index=True)
    version: int = Field(index=True)
    snapshot: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(default="", max_length=64)


class SubRequirementHistory(SQLModel, table=True):
    __tablename__ = "sub_requirement_history"

    id: int | None = Field(default=None, primary_key=True)
    sub_requirement_id: int = Field(foreign_key="sub_requirements.id", index=True)
    version: int = Field(index=True)
    snapshot: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(default="", max_length=64)


class VerificationTestHistory(SQLModel, table=True):
    __tablename__ = "verification_test_history"

    id: int | None = Field(default=None, primary_key=True)
    verification_test_id: int = Field(foreign_key="verification_tests.id", index=True)
    version: int = Field(index=True)
    snapshot: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(default="", max_length=64)
