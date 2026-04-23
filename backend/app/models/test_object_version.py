from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.test_run import TestRun


class TestObjectVersion(SQLModel, table=True):
    """Represents a version or build of the system under test (CI/CD target)."""

    __tablename__ = "test_object_versions"

    id: int | None = Field(default=None, primary_key=True)
    key: str = Field(index=True, unique=True, max_length=64)
    name: str = Field(max_length=255)
    description: str = Field(default="", max_length=4096)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    runs: list["TestRun"] = Relationship(
        back_populates="version",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
