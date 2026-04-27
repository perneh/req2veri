"""add unique test run constraint per version/test

Revision ID: 20260427_0005
Revises: 20260423_0004
Create Date: 2026-04-27
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260427_0005"
down_revision: Union[str, None] = "20260423_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_test_runs_test_version",
        "test_runs",
        ["verification_test_id", "test_object_version_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_test_runs_test_version", "test_runs", type_="unique")
