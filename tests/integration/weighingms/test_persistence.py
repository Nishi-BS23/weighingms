"""SQLite persistence: migrations, aggregate round trip, open-session uniqueness, audit, state."""

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import inspect, text

from tests.conftest import STATION_CONFIG
from weighingms.config import load_station_config
from weighingms.domain.errors import Conflict, SessionNotFound
from weighingms.domain.quantity import Quantity
from weighingms.domain.tolerance import ToleranceBand
from weighingms.domain.weighing.session import (
    Activation,
    ComponentSpec,
    ComponentState,
    RecipeSnapshot,
    SessionStatus,
    WeighingSession,
)
from weighingms.infrastructure.persistence.db import create_station_engine, migrate
from weighingms.infrastructure.persistence.repositories import (
    AuditLog,
    SessionRepository,
    StationState,
)

NOW = datetime(2026, 10, 26, 7, 0, tzinfo=UTC)
STATION = load_station_config(STATION_CONFIG)


@pytest.fixture
def engine(tmp_path: Path):  # type: ignore[no-untyped-def]
    engine = create_station_engine(tmp_path / "wms.db")
    migrate(engine)
    yield engine
    engine.dispose()


def _session(session_id: str = "WS-1", batch_id: str = "B-24187") -> WeighingSession:
    target = Quantity.of("24.000", "kg")
    spec = ComponentSpec(
        component_id="B-24187-04",
        sequence=4,
        dyestuff_code="AUX-0101",
        name="Sodium Sulphate",
        short_name="Na2SO4",
        colour_hex="#c9d2dc",
        target=target,
        band=ToleranceBand(target, Quantity.of("0.120", "kg"), "RECIPE"),
        scale=STATION.scale_policy.select(target),
        lot_id="2026-0112",
    )
    recipe = RecipeSnapshot("R-TEAL4C-480", "3", "Teal 4C", "SO-9931", "JET-04", (spec,))
    return WeighingSession.start(session_id, batch_id, "STN-01", recipe, "OP-1001", NOW)


def test_migration_creates_the_schema(engine) -> None:  # type: ignore[no-untyped-def]
    tables = set(inspect(engine).get_table_names())

    assert {"weighing_sessions", "session_components", "station_state", "audit_events"} <= tables
    with engine.connect() as conn:
        mode = conn.execute(text("PRAGMA journal_mode")).scalar()
        sync = conn.execute(text("PRAGMA synchronous")).scalar()
    assert (mode, sync) == ("wal", 2)  # WAL + FULL


def test_migration_is_idempotent(engine) -> None:  # type: ignore[no-untyped-def]
    migrate(engine)


def test_session_round_trip_keeps_exact_decimals_and_activation(engine) -> None:  # type: ignore[no-untyped-def]
    repo = SessionRepository(engine)
    session = _session()
    session.activate("B-24187-04", Activation("D-03", Quantity.of("1.850", "kg"), NOW))
    repo.add(session)

    loaded = repo.get("WS-1")

    spec = loaded.recipe.components[0]
    assert spec.target == Quantity(Decimal("24.000"), "kg")
    assert spec.band.minimum.display() == "23.880"
    assert spec.scale.label == "32 kg floor"
    assert loaded.active is not None
    assert loaded.active.activation == Activation("D-03", Quantity(Decimal("1.850"), "kg"), NOW)
    assert loaded.started_at == NOW


def test_save_updates_component_state(engine) -> None:  # type: ignore[no-untyped-def]
    repo = SessionRepository(engine)
    session = _session()
    repo.add(session)
    session.activate("B-24187-04", Activation("D-03", Quantity.of("1.850", "kg"), NOW))

    repo.save(session)

    assert repo.get("WS-1").components[0].state is ComponentState.ACTIVE


def test_only_one_open_session_per_batch(engine) -> None:  # type: ignore[no-untyped-def]
    repo = SessionRepository(engine)
    repo.add(_session("WS-1"))

    with pytest.raises(Conflict):
        repo.add(_session("WS-2"))

    completed = repo.get("WS-1")
    completed.status = SessionStatus.COMPLETED
    repo.save(completed)
    repo.add(_session("WS-3"))
    assert repo.find_open("B-24187") is not None
    assert repo.find_open("B-24187").session_id == "WS-3"  # type: ignore[union-attr]


def test_unknown_session(engine) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(SessionNotFound):
        SessionRepository(engine).get("WS-NOPE")


def test_clear(engine) -> None:  # type: ignore[no-untyped-def]
    repo = SessionRepository(engine)
    repo.add(_session())

    repo.clear()

    assert repo.find_open("B-24187") is None


def test_audit_log_and_station_state(engine) -> None:  # type: ignore[no-untyped-def]
    audit, state = AuditLog(engine), StationState(engine)

    audit.add("OPERATOR_CHANGE", "OP-1002", NOW, detail={"from": "OP-1001", "to": "OP-1002"})
    state.set("current_operator_id", "OP-1002")

    events = audit.events()
    assert [(e["type"], e["actorId"], e["detail"]["to"]) for e in events] == [
        ("OPERATOR_CHANGE", "OP-1002", "OP-1002")
    ]
    assert state.get("current_operator_id") == "OP-1002"
    audit.clear()
    state.clear()
    assert audit.events() == [] and state.get("current_operator_id") is None
