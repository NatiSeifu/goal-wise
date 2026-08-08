"""User persistence model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UUID_STRING_LENGTH, UTCDateTime, new_uuid_str, utc_now

if TYPE_CHECKING:
    from app.models.financial_profile import FinancialProfile
    from app.models.goal import Goal
    from app.models.income_source import IncomeSource
    from app.models.planned_expense import PlannedExpense
    from app.models.session import UserSession


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(UUID_STRING_LENGTH),
        primary_key=True,
        default=new_uuid_str,
    )
    email_normalized: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        unique=True,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    time_zone: Mapped[str] = mapped_column(String(64), nullable=False)
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

    sessions: Mapped[list[UserSession]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    goals: Mapped[list[Goal]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    financial_profile: Mapped[FinancialProfile | None] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    income_sources: Mapped[list[IncomeSource]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    planned_expenses: Mapped[list[PlannedExpense]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
