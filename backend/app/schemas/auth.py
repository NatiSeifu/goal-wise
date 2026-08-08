"""Auth API request and response schemas."""

from pydantic import BaseModel, Field, field_validator

from app.services.email import normalize_email
from app.services.passwords import MIN_PASSWORD_LENGTH


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=256)
    time_zone: str = Field(default="America/Los_Angeles", min_length=1, max_length=64)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = normalize_email(value)
        local_part, separator, domain = normalized.partition("@")
        if not separator or not local_part or "." not in domain:
            raise ValueError("Must be a valid email address.")
        return value


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=256)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = normalize_email(value)
        local_part, separator, domain = normalized.partition("@")
        if not separator or not local_part or "." not in domain:
            raise ValueError("Must be a valid email address.")
        return value


class UserResponse(BaseModel):
    id: str
    email: str
    time_zone: str


class AuthPayload(BaseModel):
    user: UserResponse
    csrf_token: str


class AuthResponse(BaseModel):
    item: AuthPayload
