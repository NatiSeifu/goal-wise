"""Runtime health and readiness endpoints."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.dependencies import DbSessionDep
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])

SERVICE_NAME = "goalwise-api"


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        service=SERVICE_NAME,
        status="ok",
        checks={},
    )


@router.get("/ready", response_model=HealthResponse)
def ready(db_session: DbSessionDep) -> HealthResponse | JSONResponse:
    try:
        db_session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={
                "service": SERVICE_NAME,
                "status": "unavailable",
                "checks": {"database": "unavailable"},
            },
        )

    return HealthResponse(
        service=SERVICE_NAME,
        status="ready",
        checks={"database": "ok"},
    )
