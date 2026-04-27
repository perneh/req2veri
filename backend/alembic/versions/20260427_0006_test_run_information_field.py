"""replace expected/actual with information on test runs

Revision ID: 20260427_0006
Revises: 20260427_0005
Create Date: 2026-04-27
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260427_0006"
down_revision: Union[str, None] = "20260427_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "test_runs",
        sa.Column("information", sa.String(length=8192), nullable=False, server_default=""),
    )
    op.drop_column("test_runs", "expected_result")
    op.drop_column("test_runs", "actual_result")


def downgrade() -> None:
    op.add_column(
        "test_runs",
        sa.Column("actual_result", sa.String(length=8192), nullable=False, server_default=""),
    )
    op.add_column(
        "test_runs",
        sa.Column("expected_result", sa.String(length=8192), nullable=False, server_default=""),
    )
    op.drop_column("test_runs", "information")
