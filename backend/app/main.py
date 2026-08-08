"""FastAPI application entrypoint."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.errors import ApiError, error_response, validation_error_response
from app.api.health import router as health_router
from app.api.v1.router import api_router

app = FastAPI(title="GoalWise API")
app.include_router(health_router)
app.include_router(api_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    fields: dict[str, list[str]] = {}
    for error in exc.errors():
        location = error.get("loc", ())
        field = ".".join(str(part) for part in location if part != "body")
        if not field:
            field = "body"
        fields.setdefault(field, []).append(str(error.get("msg", "Invalid value.")))

    return validation_error_response(fields=fields)


@app.exception_handler(ApiError)
async def api_error_handler(
    _request: Request,
    exc: ApiError,
) -> JSONResponse:
    return error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
    )
