"""Persisted generated explanations tied to immutable snapshots."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UUID_STRING_LENGTH, UTCDateTime, new_uuid_str, utc_now

if TYPE_CHECKING:
    from app.models.calculation_snapshot import CalculationSnapshot
    from app.models.user import User


class AIExplanation(Base):
    __tablename__ = "ai_explanations"
    __table_args__ = (
        UniqueConstraint(
            "snapshot_id",
            "provider",
            "model",
            "prompt_version",
            "response_schema_version",
            name="uq_ai_explanations_snapshot_version",
        ),
        Index("ix_ai_explanations_user_snapshot", "user_id", "snapshot_id"),
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
    snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("calculation_snapshots.id", ondelete="CASCADE"),
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(80), nullable=False)
    response_schema_version: Mapped[str] = mapped_column(String(80), nullable=False)
    response_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        nullable=False,
        default=utc_now,
    )

    user: Mapped[User] = relationship(back_populates="ai_explanations")
    snapshot: Mapped[CalculationSnapshot] = relationship(
        back_populates="ai_explanations",
    )
