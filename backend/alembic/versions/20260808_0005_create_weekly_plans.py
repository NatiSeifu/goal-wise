"""Create weekly plan table.

Revision ID: 20260808_0005
Revises: 20260808_0004
Create Date: 2026-08-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260808_0005"
down_revision: str | None = "20260808_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "weekly_plans",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("goal_id", sa.String(length=36), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("opening_allowance_cents", sa.Integer(), nullable=False),
        sa.Column("created_from_snapshot_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_from_snapshot_id"],
            ["calculation_snapshots.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "goal_id",
            "week_start",
            name="uq_weekly_plans_user_goal_week_start",
        ),
    )
    op.create_index(
        "ix_weekly_plans_user_week_start",
        "weekly_plans",
        ["user_id", "week_start"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_weekly_plans_user_week_start", table_name="weekly_plans")
    op.drop_table("weekly_plans")
