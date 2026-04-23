from datetime import datetime

from pydantic import BaseModel

from app.schemas.requirement import RequirementRead
from app.schemas.sub_requirement import SubRequirementRead
from app.schemas.verification_test import VerificationTestRead


class HistoryEntryMeta(BaseModel):
    id: int
    version: int
    created_at: datetime
    created_by: str

    model_config = {"from_attributes": True}


class RequirementHistoryDetail(HistoryEntryMeta):
    snapshot: RequirementRead


class SubRequirementHistoryDetail(HistoryEntryMeta):
    snapshot: SubRequirementRead


class VerificationTestHistoryDetail(HistoryEntryMeta):
    snapshot: VerificationTestRead
