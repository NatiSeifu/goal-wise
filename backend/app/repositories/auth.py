"""Authentication persistence queries."""

from datetime import datetime
from typing import cast

from sqlalchemy import delete, func, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session

from app.models import LoginAttempt, User, UserSession


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


def touch_session(
    db_session: Session,
    *,
    user_session: UserSession,
    last_seen_at: datetime,
) -> UserSession:
    user_session.last_seen_at = last_seen_at
    db_session.flush()
    return user_session


def update_session_csrf_token_hash(
    db_session: Session,
    *,
    user_session: UserSession,
    csrf_token_hash: str,
) -> UserSession:
    user_session.csrf_token_hash = csrf_token_hash
    db_session.flush()
    return user_session


def record_failed_login_attempt(
    db_session: Session,
    *,
    email_normalized: str,
    source_hash: str,
    failed_at: datetime,
) -> LoginAttempt:
    login_attempt = LoginAttempt(
        email_normalized=email_normalized,
        source_hash=source_hash,
        failed_at=failed_at,
    )
    db_session.add(login_attempt)
    db_session.flush()
    return login_attempt


def count_recent_failed_login_attempts(
    db_session: Session,
    *,
    email_normalized: str,
    source_hash: str,
    since: datetime,
) -> int:
    count = db_session.scalar(
        select(func.count())
        .select_from(LoginAttempt)
        .where(
            LoginAttempt.email_normalized == email_normalized,
            LoginAttempt.source_hash == source_hash,
            LoginAttempt.failed_at >= since,
        ),
    )
    return int(count or 0)


def clear_failed_login_attempts(
    db_session: Session,
    *,
    email_normalized: str,
    source_hash: str,
) -> int:
    result = cast(
        CursorResult[tuple[object, ...]],
        db_session.execute(
            delete(LoginAttempt).where(
                LoginAttempt.email_normalized == email_normalized,
                LoginAttempt.source_hash == source_hash,
            ),
        ),
    )
    db_session.flush()
    return result.rowcount
