"""Immutable calculation snapshot persistence model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UUID_STRING_LENGTH, UTCDateTime, new_uuid_str, utc_now

if TYPE_CHECKING:
    from app.models.ai_explanation import AIExplanation
    from app.models.goal import Goal
    from app.models.user import User
    from app.models.weekly_plan import WeeklyPlan


class CalculationSnapshot(Base):
    __tablename__ = "calculation_snapshots"
    __table_args__ = (
        Index("ix_calculation_snapshots_user_calculated", "user_id", "calculated_at"),
        Index(
            "ix_calculation_snapshots_user_goal_calculated",
            "user_id",
            "goal_id",
            "calculated_at",
        ),
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
    formula_version: Mapped[str] = mapped_column(String(40), nullable=False)
    trigger: Mapped[str] = mapped_column(String(80), nullable=False)
    normalized_input_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    result_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        nullable=False,
        default=utc_now,
    )

    user: Mapped[User] = relationship(back_populates="calculation_snapshots")
    goal: Mapped[Goal] = relationship(back_populates="calculation_snapshots")
    weekly_plans: Mapped[list[WeeklyPlan]] = relationship(
        back_populates="snapshot",
        cascade="all, delete-orphan",
    )
    ai_explanations: Mapped[list[AIExplanation]] = relationship(
        back_populates="snapshot",
        cascade="all, delete-orphan",
    )
