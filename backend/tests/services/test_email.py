from app.services.email import normalize_email


def test_normalize_email_trims_and_casefolds() -> None:
    assert normalize_email("  Nati.Seifu@Example.COM  ") == "nati.seifu@example.com"


def test_normalize_email_uses_casefold_for_unicode_compatibility() -> None:
    assert normalize_email("USER\u00df@Example.com") == "userss@example.com"
