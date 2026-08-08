"""Create login attempt tracking table.

Revision ID: 20260807_0002
Revises: 20260807_0001
Create Date: 2026-08-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260807_0002"
down_revision: str | None = "20260807_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "login_attempts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email_normalized", sa.String(length=320), nullable=False),
        sa.Column("source_hash", sa.String(length=128), nullable=False),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_login_attempts_email_source_failed_at",
        "login_attempts",
        ["email_normalized", "source_hash", "failed_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_login_attempts_email_source_failed_at", table_name="login_attempts")
    op.drop_table("login_attempts")
