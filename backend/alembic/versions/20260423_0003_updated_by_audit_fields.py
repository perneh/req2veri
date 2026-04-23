"""add updated_by for requirement/sub-requirement/test

Revision ID: 20260423_0003
Revises: 20260422_0002
Create Date: 2026-04-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260423_0003"
down_revision: Union[str, None] = "20260422_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "requirements",
        sa.Column("updated_by", sa.String(length=64), nullable=False, server_default=""),
    )
    op.add_column(
        "sub_requirements",
        sa.Column("updated_by", sa.String(length=64), nullable=False, server_default=""),
    )
    op.add_column(
        "verification_tests",
        sa.Column("updated_by", sa.String(length=64), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("verification_tests", "updated_by")
    op.drop_column("sub_requirements", "updated_by")
    op.drop_column("requirements", "updated_by")
