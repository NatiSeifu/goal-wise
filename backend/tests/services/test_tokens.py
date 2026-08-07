import re

import pytest
from app.services.tokens import (
    TOKEN_BYTES,
    generate_csrf_token,
    generate_opaque_token,
    generate_session_token,
    hash_csrf_token,
    hash_sensitive_value,
    hash_session_token,
    hash_source_identifier,
    verify_csrf_token_hash,
    verify_session_token_hash,
)
from pydantic import SecretStr


def test_generated_session_tokens_are_url_safe_and_high_entropy() -> None:
    token = generate_session_token()

    assert re.fullmatch(r"[A-Za-z0-9_-]+", token)
    assert len(token) >= 40


def test_generated_csrf_tokens_are_distinct() -> None:
    tokens = {generate_csrf_token() for _ in range(20)}

    assert len(tokens) == 20


def test_generate_opaque_token_rejects_low_entropy_size() -> None:
    with pytest.raises(ValueError, match=str(TOKEN_BYTES)):
        generate_opaque_token(nbytes=16)


def test_session_token_hash_is_stable_and_does_not_include_raw_token() -> None:
    token = "raw-session-token"
    secret = SecretStr("test-secret")

    first_hash = hash_session_token(token, secret)
    second_hash = hash_session_token(token, secret)

    assert first_hash == second_hash
    assert first_hash.startswith("sha256:")
    assert token not in first_hash


def test_token_hash_changes_for_different_tokens_and_secrets() -> None:
    token = "raw-session-token"

    assert hash_session_token(token, "first-secret") != hash_session_token(token, "second-secret")
    assert hash_session_token(token, "first-secret") != hash_session_token(
        "different-token",
        "first-secret",
    )


def test_session_and_csrf_hashes_are_domain_separated() -> None:
    token = "same-raw-token"
    secret = "test-secret"

    assert hash_session_token(token, secret) != hash_csrf_token(token, secret)


def test_verify_session_token_hash_accepts_matching_token_only() -> None:
    token_hash = hash_session_token("raw-session-token", "test-secret")

    assert verify_session_token_hash("raw-session-token", token_hash, "test-secret") is True
    assert verify_session_token_hash("wrong-token", token_hash, "test-secret") is False


def test_verify_csrf_token_hash_accepts_matching_token_only() -> None:
    token_hash = hash_csrf_token("raw-csrf-token", "test-secret")

    assert verify_csrf_token_hash("raw-csrf-token", token_hash, "test-secret") is True
    assert verify_csrf_token_hash("wrong-token", token_hash, "test-secret") is False


def test_source_identifier_hash_does_not_store_source_identifier() -> None:
    source_identifier = "203.0.113.10"
    source_hash = hash_source_identifier(source_identifier, "test-secret")

    assert source_identifier not in source_hash
    assert source_hash == hash_sensitive_value(source_identifier, "test-secret", purpose="source")
