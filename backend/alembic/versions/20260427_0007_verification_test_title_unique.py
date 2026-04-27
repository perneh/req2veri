"""make verification test title unique

Revision ID: 20260427_0007
Revises: 20260427_0006
Create Date: 2026-04-27
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260427_0007"
down_revision: Union[str, None] = "20260427_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_verification_tests_title",
        "verification_tests",
        ["title"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_verification_tests_title", "verification_tests", type_="unique")
