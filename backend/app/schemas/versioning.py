from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import TestStatus


class TestObjectVersionCreate(BaseModel):
    key: str = Field(max_length=64)
    name: str
    description: str = ""


class TestObjectVersionRead(BaseModel):
    id: int
    key: str
    name: str
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TestRunCreate(BaseModel):
    """Create a run for POST /test-object-versions/{version_id}/runs (version comes from path)."""

    verification_test_id: int
    status: TestStatus = TestStatus.not_run
    information: str = ""
    ran_at: datetime | None = None


class TestRunUpsert(BaseModel):
    """Upsert a run for PUT /test-object-versions/{version_id}/runs/{test_id}."""

    status: TestStatus = TestStatus.not_run
    information: str = ""
    ran_at: datetime | None = None


class TestRunRead(BaseModel):
    id: int
    verification_test_id: int
    test_object_version_id: int
    status: TestStatus
    information: str
    reported_by: str
    ran_at: datetime

    model_config = {"from_attributes": True}
