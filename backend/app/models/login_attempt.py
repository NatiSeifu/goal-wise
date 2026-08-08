"""Login failure tracking model for rate limiting."""

from datetime import datetime

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import UUID_STRING_LENGTH, UTCDateTime, new_uuid_str, utc_now


class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    __table_args__ = (
        Index(
            "ix_login_attempts_email_source_failed_at",
            "email_normalized",
            "source_hash",
            "failed_at",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(UUID_STRING_LENGTH),
        primary_key=True,
        default=new_uuid_str,
    )
    email_normalized: Mapped[str] = mapped_column(String(320), nullable=False)
    source_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    failed_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        nullable=False,
        default=utc_now,
    )
