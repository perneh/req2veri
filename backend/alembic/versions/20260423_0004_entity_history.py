"""version history snapshots for requirements, sub-requirements, tests

Revision ID: 20260423_0004
Revises: 20260423_0003
Create Date: 2026-04-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260423_0004"
down_revision: Union[str, None] = "20260423_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "requirement_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("requirement_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["requirement_id"], ["requirements.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_requirement_history_requirement_id"), "requirement_history", ["requirement_id"], unique=False)
    op.create_index(op.f("ix_requirement_history_version"), "requirement_history", ["version"], unique=False)

    op.create_table(
        "sub_requirement_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("sub_requirement_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["sub_requirement_id"], ["sub_requirements.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_sub_requirement_history_sub_requirement_id"),
        "sub_requirement_history",
        ["sub_requirement_id"],
        unique=False,
    )
    op.create_index(op.f("ix_sub_requirement_history_version"), "sub_requirement_history", ["version"], unique=False)

    op.create_table(
        "verification_test_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("verification_test_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["verification_test_id"], ["verification_tests.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_verification_test_history_verification_test_id"),
        "verification_test_history",
        ["verification_test_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_verification_test_history_version"), "verification_test_history", ["version"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_verification_test_history_version"), table_name="verification_test_history")
    op.drop_index(op.f("ix_verification_test_history_verification_test_id"), table_name="verification_test_history")
    op.drop_table("verification_test_history")

    op.drop_index(op.f("ix_sub_requirement_history_version"), table_name="sub_requirement_history")
    op.drop_index(op.f("ix_sub_requirement_history_sub_requirement_id"), table_name="sub_requirement_history")
    op.drop_table("sub_requirement_history")

    op.drop_index(op.f("ix_requirement_history_version"), table_name="requirement_history")
    op.drop_index(op.f("ix_requirement_history_requirement_id"), table_name="requirement_history")
    op.drop_table("requirement_history")
