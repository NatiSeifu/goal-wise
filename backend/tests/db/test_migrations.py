from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_initial_migration_runs_against_sqlite(tmp_path: Path) -> None:
    backend_root = Path(__file__).parents[2]
    database_path = tmp_path / "goalwise-test.db"
    database_url = f"sqlite+pysqlite:///{database_path}"

    alembic_config = Config(str(backend_root / "alembic.ini"))
    alembic_config.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(alembic_config, "head")

    engine = create_engine(database_url)
    inspector = inspect(engine)

    assert set(inspector.get_table_names()) >= {
        "alembic_version",
        "login_attempts",
        "users",
        "sessions",
    }
    assert _column_names(inspector.get_columns("users")) >= {
        "id",
        "email_normalized",
        "password_hash",
        "time_zone",
        "created_at",
        "updated_at",
    }
    assert _column_names(inspector.get_columns("sessions")) >= {
        "id",
        "user_id",
        "session_token_hash",
        "csrf_token_hash",
        "issued_at",
        "last_seen_at",
        "expires_at",
        "revoked_at",
    }
    assert _column_names(inspector.get_columns("login_attempts")) >= {
        "id",
        "email_normalized",
        "source_hash",
        "failed_at",
    }


def test_initial_migration_can_downgrade_sqlite(tmp_path: Path) -> None:
    backend_root = Path(__file__).parents[2]
    database_path = tmp_path / "goalwise-test.db"
    database_url = f"sqlite+pysqlite:///{database_path}"

    alembic_config = Config(str(backend_root / "alembic.ini"))
    alembic_config.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "base")

    engine = create_engine(database_url)
    inspector = inspect(engine)

    assert "users" not in inspector.get_table_names()
    assert "sessions" not in inspector.get_table_names()
    assert "login_attempts" not in inspector.get_table_names()


def _column_names(columns: list[dict[str, object]]) -> set[str]:
    return {str(column["name"]) for column in columns}
