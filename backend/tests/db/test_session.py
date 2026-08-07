from app.db.session import make_engine, make_session_factory
from sqlalchemy import text


def test_make_engine_supports_sqlite_memory_database() -> None:
    engine = make_engine("sqlite+pysqlite:///:memory:")

    with engine.connect() as connection:
        value = connection.execute(text("select 1")).scalar_one()

    assert value == 1


def test_session_factory_creates_usable_session() -> None:
    engine = make_engine("sqlite+pysqlite:///:memory:")
    session_factory = make_session_factory(engine)

    with session_factory() as session:
        value = session.execute(text("select 1")).scalar_one()

    assert value == 1
