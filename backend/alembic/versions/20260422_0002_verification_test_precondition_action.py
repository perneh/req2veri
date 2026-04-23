"""add precondition and action to verification_tests

Revision ID: 20260422_0002
Revises: 20260422_0001
Create Date: 2026-04-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260422_0002"
down_revision: Union[str, None] = "20260422_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "verification_tests",
        sa.Column("precondition", sa.String(length=8192), nullable=False, server_default=""),
    )
    op.add_column(
        "verification_tests",
        sa.Column("action", sa.String(length=8192), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("verification_tests", "action")
    op.drop_column("verification_tests", "precondition")
