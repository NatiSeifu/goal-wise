"""Opaque auth token generation and hashing helpers."""

import hashlib
import hmac
import secrets
from typing import Literal

from pydantic import SecretStr

TOKEN_BYTES = 32
TOKEN_HASH_ALGORITHM = "sha256"

TokenPurpose = Literal["session", "csrf", "source"]


def generate_opaque_token(*, nbytes: int = TOKEN_BYTES) -> str:
    if nbytes < TOKEN_BYTES:
        raise ValueError(f"auth tokens must use at least {TOKEN_BYTES} random bytes")

    return secrets.token_urlsafe(nbytes)


def generate_session_token() -> str:
    return generate_opaque_token()


def generate_csrf_token() -> str:
    return generate_opaque_token()


def hash_session_token(token: str, session_secret: SecretStr | str) -> str:
    return hash_sensitive_value(token, session_secret, purpose="session")


def hash_csrf_token(token: str, session_secret: SecretStr | str) -> str:
    return hash_sensitive_value(token, session_secret, purpose="csrf")


def hash_source_identifier(source_identifier: str, session_secret: SecretStr | str) -> str:
    return hash_sensitive_value(source_identifier, session_secret, purpose="source")


def verify_session_token_hash(
    token: str,
    expected_hash: str,
    session_secret: SecretStr | str,
) -> bool:
    return hmac.compare_digest(hash_session_token(token, session_secret), expected_hash)


def verify_csrf_token_hash(token: str, expected_hash: str, session_secret: SecretStr | str) -> bool:
    return hmac.compare_digest(hash_csrf_token(token, session_secret), expected_hash)


def hash_sensitive_value(
    value: str,
    session_secret: SecretStr | str,
    *,
    purpose: TokenPurpose,
) -> str:
    secret = _secret_value(session_secret)
    digest = hmac.new(
        key=secret.encode(),
        msg=f"{purpose}:{value}".encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return f"{TOKEN_HASH_ALGORITHM}:{digest}"


def _secret_value(session_secret: SecretStr | str) -> str:
    if isinstance(session_secret, SecretStr):
        return session_secret.get_secret_value()
    return session_secret
