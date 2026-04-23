"""initial schema

Revision ID: 20260422_0001
Revises:
Create Date: 2026-04-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260422_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "requirements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("description", sa.String(length=8192), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("priority", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_requirements_key"), "requirements", ["key"], unique=True)

    op.create_table(
        "test_object_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=4096), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_test_object_versions_key"), "test_object_versions", ["key"], unique=True)

    op.create_table(
        "sub_requirements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=48), nullable=False),
        sa.Column("parent_requirement_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("description", sa.String(length=8192), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("priority", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["parent_requirement_id"], ["requirements.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sub_requirements_key"), "sub_requirements", ["key"], unique=True)
    op.create_index(op.f("ix_sub_requirements_parent_requirement_id"), "sub_requirements", ["parent_requirement_id"], unique=False)

    op.create_table(
        "verification_tests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("description", sa.String(length=8192), nullable=False),
        sa.Column("method", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("requirement_id", sa.Integer(), nullable=True),
        sa.Column("sub_requirement_id", sa.Integer(), nullable=True),
        sa.Column("expected_result", sa.String(length=8192), nullable=False),
        sa.Column("actual_result", sa.String(length=8192), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["requirement_id"], ["requirements.id"]),
        sa.ForeignKeyConstraint(["sub_requirement_id"], ["sub_requirements.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_verification_tests_key"), "verification_tests", ["key"], unique=True)
    op.create_index(op.f("ix_verification_tests_requirement_id"), "verification_tests", ["requirement_id"], unique=False)
    op.create_index(op.f("ix_verification_tests_sub_requirement_id"), "verification_tests", ["sub_requirement_id"], unique=False)

    op.create_table(
        "test_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("verification_test_id", sa.Integer(), nullable=False),
        sa.Column("test_object_version_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("expected_result", sa.String(length=8192), nullable=False),
        sa.Column("actual_result", sa.String(length=8192), nullable=False),
        sa.Column("ran_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["test_object_version_id"], ["test_object_versions.id"]),
        sa.ForeignKeyConstraint(["verification_test_id"], ["verification_tests.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_test_runs_test_object_version_id"), "test_runs", ["test_object_version_id"], unique=False)
    op.create_index(op.f("ix_test_runs_verification_test_id"), "test_runs", ["verification_test_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_test_runs_verification_test_id"), table_name="test_runs")
    op.drop_index(op.f("ix_test_runs_test_object_version_id"), table_name="test_runs")
    op.drop_table("test_runs")
    op.drop_index(op.f("ix_verification_tests_sub_requirement_id"), table_name="verification_tests")
    op.drop_index(op.f("ix_verification_tests_requirement_id"), table_name="verification_tests")
    op.drop_index(op.f("ix_verification_tests_key"), table_name="verification_tests")
    op.drop_table("verification_tests")
    op.drop_index(op.f("ix_sub_requirements_parent_requirement_id"), table_name="sub_requirements")
    op.drop_index(op.f("ix_sub_requirements_key"), table_name="sub_requirements")
    op.drop_table("sub_requirements")
    op.drop_index(op.f("ix_test_object_versions_key"), table_name="test_object_versions")
    op.drop_table("test_object_versions")
    op.drop_index(op.f("ix_requirements_key"), table_name="requirements")
    op.drop_table("requirements")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
