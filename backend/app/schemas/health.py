"""Health endpoint schemas."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    service: str
    status: str
    checks: dict[str, str]
