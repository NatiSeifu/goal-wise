"""Savings goal persistence model."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UUID_STRING_LENGTH, UTCDateTime, new_uuid_str, utc_now

if TYPE_CHECKING:
    from app.models.user import User


class Goal(Base):
    __tablename__ = "goals"
    __table_args__ = (
        CheckConstraint("target_cents > 0", name="ck_goals_target_cents_positive"),
        CheckConstraint(
            "initial_saved_cents >= 0",
            name="ck_goals_initial_saved_cents_nonnegative",
        ),
        CheckConstraint(
            "current_saved_cents >= 0",
            name="ck_goals_current_saved_cents_nonnegative",
        ),
        Index("ix_goals_user_id", "user_id"),
        Index(
            "uq_goals_one_active_per_user",
            "user_id",
            unique=True,
            sqlite_where=text("status = 'active'"),
            postgresql_where=text("status = 'active'"),
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
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    target_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    initial_saved_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    current_saved_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        nullable=False,
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    user: Mapped[User] = relationship(back_populates="goals")
