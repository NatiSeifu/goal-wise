from pathlib import Path


def test_makefile_exposes_backend_migration_targets() -> None:
    makefile = Path(__file__).parents[2] / "Makefile"
    content = makefile.read_text()

    assert "backend-migrate:" in content
    assert "alembic upgrade head" in content
    assert "backend-migration-current:" in content
    assert "alembic current" in content
    assert "backend-migration-downgrade:" in content
    assert "alembic downgrade -1" in content
