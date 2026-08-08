"""Authentication API routes."""

from datetime import UTC, datetime

from fastapi import APIRouter, Request, Response

from app.api.constants import SESSION_COOKIE_MAX_AGE_SECONDS, SESSION_COOKIE_NAME
from app.api.dependencies import CsrfSessionDep, CurrentSessionDep, DbSessionDep, SettingsDep
from app.api.errors import error_response
from app.core.config import Settings
from app.models import User
from app.schemas.auth import AuthPayload, AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.services.auth import (
    DuplicateEmailError,
    InvalidCredentialsError,
    InvalidPasswordError,
    LoginRateLimitedError,
    login_user,
    logout_session,
    refresh_csrf_token,
    register_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=AuthResponse, status_code=201)
def register(
    payload: RegisterRequest,
    response: Response,
    request: Request,
    db_session: DbSessionDep,
    settings: SettingsDep,
) -> AuthResponse | Response:
    try:
        user = register_user(
            db_session,
            email=payload.email,
            password=payload.password,
            time_zone=payload.time_zone,
        )
        login_result = login_user(
            db_session,
            email=payload.email,
            password=payload.password,
            source_identifier=_source_identifier(request),
            session_secret=settings.session_secret,
            now=_utc_now(),
        )
    except DuplicateEmailError:
        db_session.rollback()
        return error_response(
            status_code=409,
            code="email_conflict",
            message="Email is already registered.",
        )
    except InvalidPasswordError:
        db_session.rollback()
        return error_response(
            status_code=422,
            code="validation_error",
            message="Request validation failed.",
        )

    db_session.commit()
    _set_session_cookie(response, token=login_result.session_token, settings=settings)
    return _auth_response(user=user, csrf_token=login_result.csrf_token)


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    response: Response,
    request: Request,
    db_session: DbSessionDep,
    settings: SettingsDep,
) -> AuthResponse | Response:
    try:
        login_result = login_user(
            db_session,
            email=payload.email,
            password=payload.password,
            source_identifier=_source_identifier(request),
            session_secret=settings.session_secret,
            now=_utc_now(),
        )
    except LoginRateLimitedError:
        db_session.rollback()
        return error_response(
            status_code=429,
            code="rate_limited",
            message="Too many login attempts. Try again later.",
        )
    except InvalidCredentialsError:
        db_session.commit()
        return error_response(
            status_code=401,
            code="invalid_credentials",
            message="Invalid email or password.",
        )

    db_session.commit()
    _set_session_cookie(response, token=login_result.session_token, settings=settings)
    return _auth_response(user=login_result.user, csrf_token=login_result.csrf_token)


@router.post("/logout", status_code=204)
def logout(
    response: Response,
    current_session: CsrfSessionDep,
    db_session: DbSessionDep,
) -> Response:
    logout_session(db_session, user_session=current_session.user_session, now=_utc_now())
    db_session.commit()
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    response.status_code = 204
    return response


@router.get("/me", response_model=AuthResponse)
def me(
    current_session: CurrentSessionDep,
    db_session: DbSessionDep,
    settings: SettingsDep,
) -> AuthResponse | Response:
    csrf_token = refresh_csrf_token(
        db_session,
        user_session=current_session.user_session,
        session_secret=settings.session_secret,
    )
    db_session.commit()
    return _auth_response(user=current_session.user, csrf_token=csrf_token)


def _auth_response(*, user: User, csrf_token: str) -> AuthResponse:
    return AuthResponse(
        item=AuthPayload(
            user=UserResponse(
                id=user.id,
                email=user.email_normalized,
                time_zone=user.time_zone,
            ),
            csrf_token=csrf_token,
        ),
    )


def _set_session_cookie(response: Response, *, token: str, settings: Settings) -> None:
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        max_age=SESSION_COOKIE_MAX_AGE_SECONDS,
        httponly=True,
        secure=settings.secure_cookies,
        samesite=settings.cookie_samesite,
        path="/",
    )


def _source_identifier(request: Request) -> str:
    if request.client is None:
        return "unknown"
    return request.client.host


def _utc_now() -> datetime:
    return datetime.now(UTC)
