"""Reusable FastAPI dependencies."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session

from app.api.constants import SESSION_COOKIE_NAME
from app.api.errors import ApiError
from app.core.config import Settings, get_settings
from app.db.session import get_db_session
from app.services.auth import (
    CurrentSession,
    InvalidCsrfTokenError,
    InvalidSessionError,
    get_current_session,
    validate_csrf_token,
)

DbSessionDep = Annotated[Session, Depends(get_db_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
CsrfHeaderDep = Annotated[str | None, Header(alias="X-CSRF-Token")]


def utc_now() -> datetime:
    return datetime.now(UTC)


NowDep = Annotated[datetime, Depends(utc_now)]


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
        return get_current_session(
            db_session,
            session_token=session_token,
            session_secret=settings.session_secret,
            now=datetime.now(UTC),
        )
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
