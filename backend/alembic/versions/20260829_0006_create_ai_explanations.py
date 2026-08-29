"""Create persisted AI explanation table.

Revision ID: 20260829_0006
Revises: 20260808_0005
Create Date: 2026-08-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260829_0006"
down_revision: str | None = "20260808_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_explanations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("snapshot_id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("prompt_version", sa.String(length=80), nullable=False),
        sa.Column("response_schema_version", sa.String(length=80), nullable=False),
        sa.Column("response_json", sa.JSON(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["snapshot_id"], ["calculation_snapshots.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "snapshot_id",
            "provider",
            "model",
            "prompt_version",
            "response_schema_version",
            name="uq_ai_explanations_snapshot_version",
        ),
    )
    op.create_index(
        "ix_ai_explanations_user_snapshot",
        "ai_explanations",
        ["user_id", "snapshot_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_ai_explanations_user_snapshot", table_name="ai_explanations")
    op.drop_table("ai_explanations")
