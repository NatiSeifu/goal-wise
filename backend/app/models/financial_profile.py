"""Financial profile persistence model."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UUID_STRING_LENGTH, UTCDateTime, new_uuid_str, utc_now

if TYPE_CHECKING:
    from app.models.user import User


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"
    __table_args__ = (
        CheckConstraint(
            "starting_cash_cents >= 0",
            name="ck_financial_profiles_starting_cash_cents_nonnegative",
        ),
        CheckConstraint(
            "reserve_buffer_cents >= 0",
            name="ck_financial_profiles_reserve_buffer_cents_nonnegative",
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
        unique=True,
        index=True,
    )
    starting_cash_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_as_of_date: Mapped[date] = mapped_column(Date, nullable=False)
    reserve_buffer_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    reserve_buffer_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False)
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

    user: Mapped[User] = relationship(back_populates="financial_profile")
