"""Expected income source persistence model."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UUID_STRING_LENGTH, UTCDateTime, new_uuid_str, utc_now

if TYPE_CHECKING:
    from app.models.user import User


class IncomeSource(Base):
    __tablename__ = "income_sources"
    __table_args__ = (
        CheckConstraint("amount_cents > 0", name="ck_income_sources_amount_cents_positive"),
        Index("ix_income_sources_user_active", "user_id", "active"),
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
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    next_date: Mapped[date] = mapped_column(Date, nullable=False)
    frequency: Mapped[str] = mapped_column(String(20), nullable=False)
    confidence: Mapped[str] = mapped_column(String(20), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
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

    user: Mapped[User] = relationship(back_populates="income_sources")
