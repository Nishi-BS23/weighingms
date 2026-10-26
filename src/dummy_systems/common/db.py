"""SQLite engine factory with the durability settings from the data-stack standard."""

from pathlib import Path
from typing import Any

from sqlalchemy import Engine, create_engine, event


def sqlite_engine(db_path: Path) -> Engine:
    """Create an engine using WAL journaling and synchronous=FULL so commits survive power loss."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}")

    @event.listens_for(engine, "connect")
    def _pragmas(dbapi_connection: Any, _: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=FULL")
        cursor.close()

    return engine
