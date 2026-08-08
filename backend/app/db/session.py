"""SQLAlchemy engine and session helpers."""

from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session as OrmSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings


def _sqlite_connect_args(database_url: str) -> dict[str, bool]:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def make_engine(database_url: str, *, echo: bool = False) -> Engine:
    engine_kwargs: dict[str, object] = {}
    if database_url.endswith(":memory:"):
        engine_kwargs["poolclass"] = StaticPool

    return create_engine(
        database_url,
        connect_args=_sqlite_connect_args(database_url),
        echo=echo,
        future=True,
        **engine_kwargs,
    )


def make_session_factory(engine: Engine) -> sessionmaker[OrmSession]:
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


engine = make_engine(get_settings().database_url)
SessionLocal = make_session_factory(engine)


def get_db_session() -> Generator[OrmSession, None, None]:
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
