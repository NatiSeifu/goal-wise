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


def test_makefile_exposes_backend_database_compose_targets() -> None:
    makefile = Path(__file__).parents[2] / "Makefile"
    content = makefile.read_text()

    assert "backend-db-up:" in content
    assert "docker compose up -d postgres" in content
    assert "backend-db-down:" in content
    assert "docker compose down" in content
    assert "backend-db-logs:" in content
    assert "docker compose logs -f postgres" in content


def test_docker_compose_defines_local_postgres_service() -> None:
    compose_file = Path(__file__).parents[2] / "docker-compose.yml"
    content = compose_file.read_text()

    assert "postgres:16-alpine" in content
    assert "POSTGRES_DB: goalwise_dev" in content
    assert "127.0.0.1:5432:5432" in content
    assert "pg_isready -U goalwise -d goalwise_dev" in content
