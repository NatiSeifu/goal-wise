"""Reusable FastAPI dependencies."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session

from app.api.constants import SESSION_COOKIE_NAME
from app.api.errors import ApiError
from app.core.config import Settings, get_settings
from app.db.session import get_db_session
from app.services.ai_provider import AiProvider, GroqAiProvider
from app.services.auth import (
    CurrentSession,
    InvalidCsrfTokenError,
    InvalidSessionError,
    get_current_session,
    record_session_activity,
    validate_csrf_token,
)

DbSessionDep = Annotated[Session, Depends(get_db_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
CsrfHeaderDep = Annotated[str | None, Header(alias="X-CSRF-Token")]


def utc_now() -> datetime:
    return datetime.now(UTC)


NowDep = Annotated[datetime, Depends(utc_now)]


def get_ai_provider(settings: SettingsDep) -> AiProvider | None:
    """Build the configured provider without making AI mandatory at startup."""

    api_key = settings.groq_api_key
    if not ai_explanations_are_available(settings) or api_key is None:
        return None
    if settings.ai_summary_provider != "groq":
        return None
    return GroqAiProvider(
        api_key=api_key,
        model=settings.ai_summary_model,
    )


AiProviderDep = Annotated[AiProvider | None, Depends(get_ai_provider)]


def ai_explanations_are_available(settings: Settings) -> bool:
    return (
        settings.ai_summary_enabled
        and settings.groq_api_key is not None
        and settings.ai_summary_provider == "groq"
    )


def require_current_session(
    request: Request,
    db_session: DbSessionDep,
    settings: SettingsDep,
) -> CurrentSession:
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    if session_token is None:
        raise ApiError(
            status_code=401,
            code="unauthorized",
            message="Authentication required.",
        )

    try:
        now = datetime.now(UTC)
        current_session = get_current_session(
            db_session,
            session_token=session_token,
            session_secret=settings.session_secret,
            now=now,
        )
        record_session_activity(
            db_session,
            user_session=current_session.user_session,
            last_seen_at=now,
        )
        db_session.commit()
        return current_session
    except InvalidSessionError as exc:
        db_session.rollback()
        raise ApiError(
            status_code=401,
            code="unauthorized",
            message="Authentication required.",
        ) from exc


CurrentSessionDep = Annotated[CurrentSession, Depends(require_current_session)]


def require_csrf_session(
    current_session: CurrentSessionDep,
    settings: SettingsDep,
    x_csrf_token: CsrfHeaderDep = None,
) -> CurrentSession:
    try:
        if x_csrf_token is None:
            raise InvalidCsrfTokenError
        validate_csrf_token(
            user_session=current_session.user_session,
            csrf_token=x_csrf_token,
            session_secret=settings.session_secret,
        )
    except InvalidCsrfTokenError as exc:
        raise ApiError(
            status_code=403,
            code="csrf_failed",
            message="Invalid request token.",
        ) from exc

    return current_session


CsrfSessionDep = Annotated[CurrentSession, Depends(require_csrf_session)]
