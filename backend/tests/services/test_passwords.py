import pytest
from app.services.passwords import MIN_PASSWORD_LENGTH, hash_password, verify_password


def test_hash_password_returns_argon2id_hash_without_raw_password() -> None:
    password = "correct horse battery staple"

    password_hash = hash_password(password)

    assert password_hash.startswith("$argon2id$")
    assert password not in password_hash


def test_verify_password_accepts_original_password() -> None:
    password = "correct horse battery staple"
    password_hash = hash_password(password)

    assert verify_password(password_hash, password) is True


def test_verify_password_rejects_incorrect_password() -> None:
    password_hash = hash_password("correct horse battery staple")

    assert verify_password(password_hash, "wrong horse battery staple") is False


def test_hash_password_rejects_short_password() -> None:
    with pytest.raises(ValueError, match=str(MIN_PASSWORD_LENGTH)):
        hash_password("short")


def test_verify_password_rejects_invalid_hash() -> None:
    assert verify_password("not-a-password-hash", "correct horse battery staple") is False
