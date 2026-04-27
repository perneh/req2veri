"""Keep approved_by / approved_at in sync when requirement status changes."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from app.models.enums import RequirementStatus


class _SupportsApprovedAudit(Protocol):
    approved_by: str
    approved_at: datetime | None


def init_approved_fields_on_create(entity: _SupportsApprovedAudit, *, status: RequirementStatus, actor: str) -> None:
    if status == RequirementStatus.approved:
        entity.approved_by = actor
        entity.approved_at = datetime.utcnow()
    else:
        entity.approved_by = ""
        entity.approved_at = None


def sync_approved_fields_after_status_change(
    entity: _SupportsApprovedAudit,
    *,
    old_status: RequirementStatus,
    new_status: RequirementStatus,
    actor: str,
) -> None:
    if new_status == RequirementStatus.approved and old_status != RequirementStatus.approved:
        entity.approved_by = actor
        entity.approved_at = datetime.utcnow()
    elif new_status != RequirementStatus.approved:
        entity.approved_by = ""
        entity.approved_at = None
