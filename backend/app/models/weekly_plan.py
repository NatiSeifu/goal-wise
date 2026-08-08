"""Weekly plan persistence model."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UUID_STRING_LENGTH, UTCDateTime, new_uuid_str, utc_now

if TYPE_CHECKING:
    from app.models.calculation_snapshot import CalculationSnapshot
    from app.models.goal import Goal
    from app.models.user import User


class WeeklyPlan(Base):
    __tablename__ = "weekly_plans"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "goal_id",
            "week_start",
            name="uq_weekly_plans_user_goal_week_start",
        ),
        Index("ix_weekly_plans_user_week_start", "user_id", "week_start"),
    )

    id: Mapped[str] = mapped_column(
        String(UUID_STRING_LENGTH),
        primary_key=True,
        default=new_uuid_str,
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    goal_id: Mapped[str] = mapped_column(
        ForeignKey("goals.id", ondelete="CASCADE"),
        nullable=False,
    )
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    opening_allowance_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    created_from_snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("calculation_snapshots.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        nullable=False,
        default=utc_now,
    )

    user: Mapped[User] = relationship(back_populates="weekly_plans")
    goal: Mapped[Goal] = relationship(back_populates="weekly_plans")
    snapshot: Mapped[CalculationSnapshot] = relationship(back_populates="weekly_plans")
