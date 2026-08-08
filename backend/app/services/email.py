"""Email normalization helpers for auth identifiers."""


def normalize_email(email: str) -> str:
    return email.strip().casefold()
