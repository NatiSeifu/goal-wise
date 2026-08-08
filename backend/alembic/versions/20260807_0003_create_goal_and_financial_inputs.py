"""Create goal and financial input tables.

Revision ID: 20260807_0003
Revises: 20260807_0002
Create Date: 2026-08-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260807_0003"
down_revision: str | None = "20260807_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "goals",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("target_cents", sa.Integer(), nullable=False),
        sa.Column("initial_saved_cents", sa.Integer(), nullable=False),
        sa.Column("current_saved_cents", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("target_cents > 0", name="ck_goals_target_cents_positive"),
        sa.CheckConstraint(
            "initial_saved_cents >= 0",
            name="ck_goals_initial_saved_cents_nonnegative",
        ),
        sa.CheckConstraint(
            "current_saved_cents >= 0",
            name="ck_goals_current_saved_cents_nonnegative",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_goals_user_id", "goals", ["user_id"], unique=False)
    op.create_index(
        "uq_goals_one_active_per_user",
        "goals",
        ["user_id"],
        unique=True,
        sqlite_where=sa.text("status = 'active'"),
        postgresql_where=sa.text("status = 'active'"),
    )

    op.create_table(
        "financial_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("starting_cash_cents", sa.Integer(), nullable=False),
        sa.Column("balance_as_of_date", sa.Date(), nullable=False),
        sa.Column("reserve_buffer_cents", sa.Integer(), nullable=False),
        sa.Column("reserve_buffer_confirmed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "starting_cash_cents >= 0",
            name="ck_financial_profiles_starting_cash_cents_nonnegative",
        ),
        sa.CheckConstraint(
            "reserve_buffer_cents >= 0",
            name="ck_financial_profiles_reserve_buffer_cents_nonnegative",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_financial_profiles_user_id"), "financial_profiles", ["user_id"], unique=True)

    op.create_table(
        "income_sources",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("next_date", sa.Date(), nullable=False),
        sa.Column("frequency", sa.String(length=20), nullable=False),
        sa.Column("confidence", sa.String(length=20), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "amount_cents > 0",
            name="ck_income_sources_amount_cents_positive",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_income_sources_user_active",
        "income_sources",
        ["user_id", "active"],
        unique=False,
    )

    op.create_table(
        "planned_expenses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("next_date", sa.Date(), nullable=False),
        sa.Column("frequency", sa.String(length=20), nullable=False),
        sa.Column("classification", sa.String(length=20), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "amount_cents > 0",
            name="ck_planned_expenses_amount_cents_positive",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_planned_expenses_user_active",
        "planned_expenses",
        ["user_id", "active"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_planned_expenses_user_active", table_name="planned_expenses")
    op.drop_table("planned_expenses")
    op.drop_index("ix_income_sources_user_active", table_name="income_sources")
    op.drop_table("income_sources")
    op.drop_index(op.f("ix_financial_profiles_user_id"), table_name="financial_profiles")
    op.drop_table("financial_profiles")
    op.drop_index("uq_goals_one_active_per_user", table_name="goals")
    op.drop_index("ix_goals_user_id", table_name="goals")
    op.drop_table("goals")
