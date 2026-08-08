from datetime import datetime, timedelta

import pytest
from app.db.base import Base
from app.db.session import make_engine, make_session_factory
from app.db.types import utc_now
from app.repositories.auth import (
    count_recent_failed_login_attempts,
    create_user,
)
from app.services.auth import (
    LOGIN_FAILURE_LIMIT,
    SESSION_ABSOLUTE_TIMEOUT,
    SESSION_IDLE_TIMEOUT,
    DuplicateEmailError,
    InvalidCredentialsError,
    InvalidPasswordError,
    InvalidSessionError,
    LoginRateLimitedError,
    LoginResult,
    get_current_session,
    login_user,
    logout_session,
    record_session_activity,
    register_user,
)
from app.services.email import normalize_email
from app.services.passwords import hash_password, verify_password
from app.services.tokens import (
    hash_csrf_token,
    hash_session_token,
    hash_source_identifier,
)
from sqlalchemy import Engine
from sqlalchemy.orm import Session

SESSION_SECRET = "test-session-secret"
SOURCE_IDENTIFIER = "203.0.113.10"


@pytest.fixture
def engine() -> Engine:
    sqlite_engine = make_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(sqlite_engine)
    return sqlite_engine


@pytest.fixture
def db_session(engine: Engine) -> Session:
    session_factory = make_session_factory(engine)
    with session_factory() as session:
        yield session


def test_register_user_stores_normalized_email_and_password_hash(db_session: Session) -> None:
    user = register_user(
        db_session,
        email="  Nati@Example.COM ",
        password="correct horse battery staple",
        time_zone="America/Los_Angeles",
    )

    assert user.email_normalized == "nati@example.com"
    assert user.password_hash.startswith("$argon2id$")
    assert "correct horse battery staple" not in user.password_hash
    assert verify_password(user.password_hash, "correct horse battery staple")


def test_register_user_rejects_duplicate_normalized_email(db_session: Session) -> None:
    register_user(
        db_session,
        email="nati@example.com",
        password="correct horse battery staple",
        time_zone="America/Los_Angeles",
    )

    with pytest.raises(DuplicateEmailError):
        register_user(
            db_session,
            email="  NATI@example.com ",
            password="correct horse battery staple",
            time_zone="America/Los_Angeles",
        )


def test_register_user_rejects_short_password(db_session: Session) -> None:
    with pytest.raises(InvalidPasswordError):
        register_user(
            db_session,
            email="nati@example.com",
            password="too-short",
            time_zone="America/Los_Angeles",
        )


def test_login_user_creates_session_with_hashed_tokens(db_session: Session) -> None:
    now = utc_now()
    user = create_user(
        db_session,
        email_normalized="nati@example.com",
        password_hash=hash_password("correct horse battery staple"),
        time_zone="America/Los_Angeles",
    )

    result = login_user(
        db_session,
        email="NATI@example.com",
        password="correct horse battery staple",
        source_identifier=SOURCE_IDENTIFIER,
        session_secret=SESSION_SECRET,
        now=now,
    )

    assert result.user == user
    assert result.user_session.user_id == user.id
    assert result.user_session.expires_at == now + SESSION_ABSOLUTE_TIMEOUT
    assert result.session_token not in result.user_session.session_token_hash
    assert result.csrf_token not in result.user_session.csrf_token_hash
    assert result.user_session.session_token_hash == hash_session_token(
        result.session_token,
        SESSION_SECRET,
    )
    assert result.user_session.csrf_token_hash == hash_csrf_token(result.csrf_token, SESSION_SECRET)


def test_login_user_records_failed_attempt_for_missing_user(db_session: Session) -> None:
    now = utc_now()

    with pytest.raises(InvalidCredentialsError):
        login_user(
            db_session,
            email="missing@example.com",
            password="correct horse battery staple",
            source_identifier=SOURCE_IDENTIFIER,
            session_secret=SESSION_SECRET,
            now=now,
        )

    assert (
        count_recent_failed_login_attempts(
            db_session,
            email_normalized="missing@example.com",
            source_hash=hash_source_identifier(SOURCE_IDENTIFIER, SESSION_SECRET),
            since=now - timedelta(minutes=10),
        )
        == 1
    )


def test_login_user_records_failed_attempt_for_wrong_password(db_session: Session) -> None:
    now = utc_now()
    create_user(
        db_session,
        email_normalized="nati@example.com",
        password_hash=hash_password("correct horse battery staple"),
        time_zone="America/Los_Angeles",
    )

    with pytest.raises(InvalidCredentialsError):
        login_user(
            db_session,
            email="nati@example.com",
            password="wrong horse battery staple",
            source_identifier=SOURCE_IDENTIFIER,
            session_secret=SESSION_SECRET,
            now=now,
        )

    assert (
        count_recent_failed_login_attempts(
            db_session,
            email_normalized="nati@example.com",
            source_hash=hash_source_identifier(SOURCE_IDENTIFIER, SESSION_SECRET),
            since=now - timedelta(minutes=10),
        )
        == 1
    )


def test_login_user_blocks_after_failed_attempt_limit(db_session: Session) -> None:
    now = utc_now()
    for offset in range(LOGIN_FAILURE_LIMIT):
        with pytest.raises(InvalidCredentialsError):
            login_user(
                db_session,
                email="missing@example.com",
                password=f"wrong-password-{offset}",
                source_identifier=SOURCE_IDENTIFIER,
                session_secret=SESSION_SECRET,
                now=now + timedelta(seconds=offset),
            )

    with pytest.raises(LoginRateLimitedError):
        login_user(
            db_session,
            email="missing@example.com",
            password="correct horse battery staple",
            source_identifier=SOURCE_IDENTIFIER,
            session_secret=SESSION_SECRET,
            now=now + timedelta(seconds=LOGIN_FAILURE_LIMIT),
        )


def test_login_user_clears_failed_attempts_on_success(db_session: Session) -> None:
    now = utc_now()
    source_hash = hash_source_identifier(SOURCE_IDENTIFIER, SESSION_SECRET)
    create_user(
        db_session,
        email_normalized="nati@example.com",
        password_hash=hash_password("correct horse battery staple"),
        time_zone="America/Los_Angeles",
    )
    with pytest.raises(InvalidCredentialsError):
        login_user(
            db_session,
            email="nati@example.com",
            password="wrong horse battery staple",
            source_identifier=SOURCE_IDENTIFIER,
            session_secret=SESSION_SECRET,
            now=now,
        )

    login_user(
        db_session,
        email="nati@example.com",
        password="correct horse battery staple",
        source_identifier=SOURCE_IDENTIFIER,
        session_secret=SESSION_SECRET,
        now=now + timedelta(seconds=1),
    )

    assert (
        count_recent_failed_login_attempts(
            db_session,
            email_normalized="nati@example.com",
            source_hash=source_hash,
            since=now - timedelta(minutes=10),
        )
        == 0
    )


def test_get_current_session_returns_user_without_touching_last_seen(
    db_session: Session,
) -> None:
    now = utc_now()
    login_result = _create_logged_in_user(db_session, now=now)
    later = now + timedelta(minutes=5)

    current_session = get_current_session(
        db_session,
        session_token=login_result.session_token,
        session_secret=SESSION_SECRET,
        now=later,
    )

    assert current_session.user.id == login_result.user.id
    assert current_session.user_session.last_seen_at == now


def test_record_session_activity_updates_last_seen(db_session: Session) -> None:
    now = utc_now()
    login_result = _create_logged_in_user(db_session, now=now)
    later = now + timedelta(minutes=5)

    record_session_activity(
        db_session,
        user_session=login_result.user_session,
        last_seen_at=later,
    )

    assert login_result.user_session.last_seen_at == later


def test_get_current_session_rejects_idle_session(db_session: Session) -> None:
    now = utc_now()
    login_result = _create_logged_in_user(db_session, now=now)

    with pytest.raises(InvalidSessionError):
        get_current_session(
            db_session,
            session_token=login_result.session_token,
            session_secret=SESSION_SECRET,
            now=now + SESSION_IDLE_TIMEOUT + timedelta(seconds=1),
        )

    assert login_result.user_session.revoked_at is not None


def test_get_current_session_rejects_expired_session(db_session: Session) -> None:
    now = utc_now()
    login_result = _create_logged_in_user(db_session, now=now)

    with pytest.raises(InvalidSessionError):
        get_current_session(
            db_session,
            session_token=login_result.session_token,
            session_secret=SESSION_SECRET,
            now=now + SESSION_ABSOLUTE_TIMEOUT + timedelta(seconds=1),
        )


def test_get_current_session_rejects_unknown_session_token(db_session: Session) -> None:
    with pytest.raises(InvalidSessionError):
        get_current_session(
            db_session,
            session_token="unknown-session-token",
            session_secret=SESSION_SECRET,
            now=utc_now(),
        )


def test_logout_session_revokes_current_session(db_session: Session) -> None:
    now = utc_now()
    login_result = _create_logged_in_user(db_session, now=now)

    logout_session(
        db_session,
        user_session=login_result.user_session,
        now=now + timedelta(seconds=1),
    )

    assert login_result.user_session.revoked_at == now + timedelta(seconds=1)


def _create_logged_in_user(db_session: Session, *, now: datetime) -> LoginResult:
    create_user(
        db_session,
        email_normalized=normalize_email("nati@example.com"),
        password_hash=hash_password("correct horse battery staple"),
        time_zone="America/Los_Angeles",
    )
    return login_user(
        db_session,
        email="nati@example.com",
        password="correct horse battery staple",
        source_identifier=SOURCE_IDENTIFIER,
        session_secret=SESSION_SECRET,
        now=now,
    )
