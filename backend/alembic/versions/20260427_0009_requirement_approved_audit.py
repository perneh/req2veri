"""add approved_by and approved_at on requirements and sub_requirements

Revision ID: 20260427_0009
Revises: 20260427_0008
Create Date: 2026-04-27
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260427_0009"
down_revision: Union[str, None] = "20260427_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "requirements",
        sa.Column("approved_by", sa.String(length=64), nullable=False, server_default=""),
    )
    op.add_column("requirements", sa.Column("approved_at", sa.DateTime(), nullable=True))
    op.add_column(
        "sub_requirements",
        sa.Column("approved_by", sa.String(length=64), nullable=False, server_default=""),
    )
    op.add_column("sub_requirements", sa.Column("approved_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("sub_requirements", "approved_at")
    op.drop_column("sub_requirements", "approved_by")
    op.drop_column("requirements", "approved_at")
    op.drop_column("requirements", "approved_by")
