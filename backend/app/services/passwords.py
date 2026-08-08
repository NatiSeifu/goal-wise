"""Password policy and Argon2id hashing helpers."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from argon2.low_level import Type

MIN_PASSWORD_LENGTH = 12

_password_hasher = PasswordHasher(type=Type.ID)


def is_valid_password_length(password: str) -> bool:
    return len(password) >= MIN_PASSWORD_LENGTH


def hash_password(password: str) -> str:
    if not is_valid_password_length(password):
        raise ValueError(f"password must be at least {MIN_PASSWORD_LENGTH} characters")

    return _password_hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _password_hasher.verify(password_hash, password)
    except (InvalidHashError, VerificationError, VerifyMismatchError):
        return False
