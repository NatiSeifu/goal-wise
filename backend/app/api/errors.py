"""API error response helpers."""

from fastapi.responses import JSONResponse


class ApiError(Exception):
    def __init__(self, *, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


def error_response(*, status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


def validation_error_response(*, fields: dict[str, list[str]]) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed.",
                "fields": fields,
            },
        },
    )


def planning_import_error_response(*, issues: list[dict[str, object]]) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "planning_import_invalid",
                "message": "The planning CSV could not be imported.",
                "issues": issues,
            },
        },
    )
