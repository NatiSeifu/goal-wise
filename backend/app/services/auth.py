"""Authentication application service behavior."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from pydantic import SecretStr
from sqlalchemy.orm import Session

from app.models import User, UserSession
from app.repositories.auth import (
    clear_failed_login_attempts,
    count_recent_failed_login_attempts,
    create_session,
    create_user,
    get_active_session_by_token_hash,
    get_user_by_normalized_email,
    record_failed_login_attempt,
    revoke_session,
    touch_session,
    update_session_csrf_token_hash,
)
from app.services.email import normalize_email
from app.services.passwords import hash_password, is_valid_password_length, verify_password
from app.services.tokens import (
    generate_csrf_token,
    generate_session_token,
    hash_csrf_token,
    hash_session_token,
    hash_source_identifier,
    verify_csrf_token_hash,
)

MIN_PASSWORD_LENGTH = 12
LOGIN_FAILURE_LIMIT = 5
LOGIN_FAILURE_WINDOW = timedelta(minutes=10)
SESSION_IDLE_TIMEOUT = timedelta(minutes=30)
SESSION_ABSOLUTE_TIMEOUT = timedelta(hours=24)


class AuthError(Exception):
    """Base class for expected auth service failures."""


class DuplicateEmailError(AuthError):
    """Raised when registration uses an email that already exists."""


class InvalidPasswordError(AuthError):
    """Raised when a password fails local password policy."""


class InvalidCredentialsError(AuthError):
    """Raised for generic login failure."""


class LoginRateLimitedError(AuthError):
    """Raised when the login attempt limit has been reached."""


class InvalidSessionError(AuthError):
    """Raised when a session token is missing, expired, revoked, or unknown."""


class InvalidCsrfTokenError(AuthError):
    """Raised when an unsafe authenticated request has an invalid CSRF token."""


@dataclass(frozen=True)
class LoginResult:
    user: User
    user_session: UserSession
    session_token: str
    csrf_token: str


@dataclass(frozen=True)
class CurrentSession:
    user: User
    user_session: UserSession


def register_user(
    db_session: Session,
    *,
    email: str,
    password: str,
    time_zone: str,
) -> User:
    email_normalized = normalize_email(email)
    if get_user_by_normalized_email(db_session, email_normalized=email_normalized) is not None:
        raise DuplicateEmailError

    if not is_valid_password_length(password):
        raise InvalidPasswordError

    return create_user(
        db_session,
        email_normalized=email_normalized,
        password_hash=hash_password(password),
        time_zone=time_zone,
    )


def login_user(
    db_session: Session,
    *,
    email: str,
    password: str,
    source_identifier: str,
    session_secret: SecretStr | str,
    now: datetime,
) -> LoginResult:
    email_normalized = normalize_email(email)
    source_hash = hash_source_identifier(source_identifier, session_secret)
    failure_window_start = now - LOGIN_FAILURE_WINDOW

    if (
        count_recent_failed_login_attempts(
            db_session,
            email_normalized=email_normalized,
            source_hash=source_hash,
            since=failure_window_start,
        )
        >= LOGIN_FAILURE_LIMIT
    ):
        raise LoginRateLimitedError

    user = get_user_by_normalized_email(db_session, email_normalized=email_normalized)
    if user is None or not verify_password(user.password_hash, password):
        record_failed_login_attempt(
            db_session,
            email_normalized=email_normalized,
            source_hash=source_hash,
            failed_at=now,
        )
        raise InvalidCredentialsError

    clear_failed_login_attempts(
        db_session,
        email_normalized=email_normalized,
        source_hash=source_hash,
    )

    session_token = generate_session_token()
    csrf_token = generate_csrf_token()
    user_session = create_session(
        db_session,
        user_id=user.id,
        session_token_hash=hash_session_token(session_token, session_secret),
        csrf_token_hash=hash_csrf_token(csrf_token, session_secret),
        issued_at=now,
        last_seen_at=now,
        expires_at=now + SESSION_ABSOLUTE_TIMEOUT,
    )

    return LoginResult(
        user=user,
        user_session=user_session,
        session_token=session_token,
        csrf_token=csrf_token,
    )


def get_current_session(
    db_session: Session,
    *,
    session_token: str,
    session_secret: SecretStr | str,
    now: datetime,
) -> CurrentSession:
    session_token_hash = hash_session_token(session_token, session_secret)
    user_session = get_active_session_by_token_hash(
        db_session,
        session_token_hash=session_token_hash,
        now=now,
    )
    if user_session is None:
        raise InvalidSessionError

    if user_session.last_seen_at <= now - SESSION_IDLE_TIMEOUT:
        revoke_session(db_session, user_session=user_session, revoked_at=now)
        raise InvalidSessionError

    return CurrentSession(user=user_session.user, user_session=user_session)


def record_session_activity(
    db_session: Session,
    *,
    user_session: UserSession,
    last_seen_at: datetime,
) -> UserSession:
    return touch_session(
        db_session,
        user_session=user_session,
        last_seen_at=last_seen_at,
    )


def logout_session(
    db_session: Session,
    *,
    user_session: UserSession,
    now: datetime,
) -> None:
    revoke_session(db_session, user_session=user_session, revoked_at=now)


def validate_csrf_token(
    *,
    user_session: UserSession,
    csrf_token: str,
    session_secret: SecretStr | str,
) -> None:
    if not verify_csrf_token_hash(csrf_token, user_session.csrf_token_hash, session_secret):
        raise InvalidCsrfTokenError


def refresh_csrf_token(
    db_session: Session,
    *,
    user_session: UserSession,
    session_secret: SecretStr | str,
) -> str:
    csrf_token = generate_csrf_token()
    update_session_csrf_token_hash(
        db_session,
        user_session=user_session,
        csrf_token_hash=hash_csrf_token(csrf_token, session_secret),
    )
    return csrf_token
