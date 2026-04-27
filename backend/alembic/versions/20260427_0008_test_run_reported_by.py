"""add reported_by field on test runs

Revision ID: 20260427_0008
Revises: 20260427_0007
Create Date: 2026-04-27
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260427_0008"
down_revision: Union[str, None] = "20260427_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "test_runs",
        sa.Column("reported_by", sa.String(length=64), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("test_runs", "reported_by")
