"""Authentication persistence queries."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User, UserSession


def get_user_by_normalized_email(
    db_session: Session,
    *,
    email_normalized: str,
) -> User | None:
    return db_session.scalar(
        select(User).where(User.email_normalized == email_normalized),
    )


def create_user(
    db_session: Session,
    *,
    email_normalized: str,
    password_hash: str,
    time_zone: str,
) -> User:
    user = User(
        email_normalized=email_normalized,
        password_hash=password_hash,
        time_zone=time_zone,
    )
    db_session.add(user)
    db_session.flush()
    return user


def create_session(
    db_session: Session,
    *,
    user_id: str,
    session_token_hash: str,
    csrf_token_hash: str,
    issued_at: datetime,
    last_seen_at: datetime,
    expires_at: datetime,
) -> UserSession:
    user_session = UserSession(
        user_id=user_id,
        session_token_hash=session_token_hash,
        csrf_token_hash=csrf_token_hash,
        issued_at=issued_at,
        last_seen_at=last_seen_at,
        expires_at=expires_at,
    )
    db_session.add(user_session)
    db_session.flush()
    return user_session


def get_session_by_token_hash(
    db_session: Session,
    *,
    session_token_hash: str,
) -> UserSession | None:
    return db_session.scalar(
        select(UserSession).where(UserSession.session_token_hash == session_token_hash),
    )


def get_active_session_by_token_hash(
    db_session: Session,
    *,
    session_token_hash: str,
    now: datetime,
) -> UserSession | None:
    return db_session.scalar(
        select(UserSession).where(
            UserSession.session_token_hash == session_token_hash,
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > now,
        ),
    )


def revoke_session(
    db_session: Session,
    *,
    user_session: UserSession,
    revoked_at: datetime,
) -> UserSession:
    user_session.revoked_at = revoked_at
    db_session.flush()
    return user_session
