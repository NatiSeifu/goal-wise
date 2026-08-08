"""Create calculation snapshot table.

Revision ID: 20260808_0004
Revises: 20260807_0003
Create Date: 2026-08-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260808_0004"
down_revision: str | None = "20260807_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "calculation_snapshots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("goal_id", sa.String(length=36), nullable=False),
        sa.Column("formula_version", sa.String(length=40), nullable=False),
        sa.Column("trigger", sa.String(length=80), nullable=False),
        sa.Column("normalized_input_json", sa.JSON(), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_calculation_snapshots_user_calculated",
        "calculation_snapshots",
        ["user_id", "calculated_at"],
        unique=False,
    )
    op.create_index(
        "ix_calculation_snapshots_user_goal_calculated",
        "calculation_snapshots",
        ["user_id", "goal_id", "calculated_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_calculation_snapshots_user_goal_calculated",
        table_name="calculation_snapshots",
    )
    op.drop_index(
        "ix_calculation_snapshots_user_calculated",
        table_name="calculation_snapshots",
    )
    op.drop_table("calculation_snapshots")
