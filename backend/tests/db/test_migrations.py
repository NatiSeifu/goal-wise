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
        "calculation_snapshots",
        "financial_profiles",
        "goals",
        "income_sources",
        "login_attempts",
        "planned_expenses",
        "sessions",
        "users",
        "weekly_plans",
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
    assert _column_names(inspector.get_columns("goals")) >= {
        "id",
        "user_id",
        "name",
        "target_cents",
        "initial_saved_cents",
        "current_saved_cents",
        "start_date",
        "target_date",
        "status",
        "archived_at",
        "created_at",
        "updated_at",
    }
    assert _column_names(inspector.get_columns("financial_profiles")) >= {
        "id",
        "user_id",
        "starting_cash_cents",
        "balance_as_of_date",
        "reserve_buffer_cents",
        "reserve_buffer_confirmed",
        "created_at",
        "updated_at",
    }
    assert _column_names(inspector.get_columns("income_sources")) >= {
        "id",
        "user_id",
        "name",
        "amount_cents",
        "next_date",
        "frequency",
        "confidence",
        "active",
        "created_at",
        "updated_at",
    }
    assert _column_names(inspector.get_columns("planned_expenses")) >= {
        "id",
        "user_id",
        "name",
        "amount_cents",
        "next_date",
        "frequency",
        "classification",
        "active",
        "created_at",
        "updated_at",
    }
    calculation_snapshot_columns = _column_names(inspector.get_columns("calculation_snapshots"))
    assert calculation_snapshot_columns >= {
        "id",
        "user_id",
        "goal_id",
        "formula_version",
        "trigger",
        "normalized_input_json",
        "result_json",
        "calculated_at",
        "created_at",
    }
    assert "updated_at" not in calculation_snapshot_columns
    assert _column_names(inspector.get_columns("weekly_plans")) >= {
        "id",
        "user_id",
        "goal_id",
        "week_start",
        "opening_allowance_cents",
        "created_from_snapshot_id",
        "created_at",
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
    assert "goals" not in inspector.get_table_names()
    assert "financial_profiles" not in inspector.get_table_names()
    assert "income_sources" not in inspector.get_table_names()
    assert "planned_expenses" not in inspector.get_table_names()
    assert "calculation_snapshots" not in inspector.get_table_names()
    assert "weekly_plans" not in inspector.get_table_names()


def _column_names(columns: list[dict[str, object]]) -> set[str]:
    return {str(column["name"]) for column in columns}
