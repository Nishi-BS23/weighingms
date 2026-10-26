"""WeighingSession aggregate invariants (stories 002/001, 002/007, 002/010)."""

from datetime import UTC, datetime

import pytest

from tests.conftest import STATION_CONFIG
from weighingms.config import load_station_config
from weighingms.domain.errors import ComponentAlreadyDone, ComponentNotFound, SessionCompleted
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

NOW = datetime(2026, 10, 26, 7, 0, tzinfo=UTC)
STATION = load_station_config(STATION_CONFIG)
NAMES = ["Blue RSPL", "Red RB", "Yellow RGB", "Sodium Sulphate", "Soda Ash"]


def _spec(seq: int) -> ComponentSpec:
    target = Quantity.of("100.0", "g")
    return ComponentSpec(
        component_id=f"C{seq}",
        sequence=seq,
        dyestuff_code=f"D{seq}",
        name=NAMES[seq - 1],
        short_name=NAMES[seq - 1],
        colour_hex="#000000",
        target=target,
        band=ToleranceBand(target, Quantity.of("1.0", "g"), "RECIPE"),
        scale=STATION.scale_policy.select(target),
        lot_id="L",
    )


def _session() -> WeighingSession:
    recipe = RecipeSnapshot(
        "R", "1", "Teal 4C", "SO", "JET", tuple(_spec(i) for i in (3, 1, 5, 2, 4))
    )
    return WeighingSession.start("S", "B", "STN-01", recipe, "OP-1001", NOW)


ACTIVATION = Activation("C-12", Quantity.of("214", "g"), NOW)


def test_new_session_has_all_components_pending_in_sequence() -> None:
    session = _session()

    assert [c.component_id for c in session.components] == ["C1", "C2", "C3", "C4", "C5"]
    assert all(c.state is ComponentState.PENDING for c in session.components)
    assert session.next_pending() is not None and session.next_pending().component_id == "C1"  # type: ignore[union-attr]
    assert session.status is SessionStatus.IN_PROGRESS
    assert [e.name for e in session.pull_events()] == ["SessionStarted"]


def test_activating_another_component_returns_the_previous_one_to_pending() -> None:
    session = _session()
    session.activate("C1", ACTIVATION)

    session.activate("C3", ACTIVATION)

    states = {c.component_id: c.state for c in session.components}
    assert states["C1"] is ComponentState.PENDING
    assert states["C3"] is ComponentState.ACTIVE
    assert session.active is not None and session.active.component_id == "C3"
    assert session.progress_of("C1").activation is None


def test_only_one_component_is_ever_active() -> None:
    session = _session()
    for cid in ("C1", "C2", "C5", "C2"):
        session.activate(cid, ACTIVATION)

    assert sum(1 for c in session.components if c.state is ComponentState.ACTIVE) == 1


def test_done_component_cannot_be_activated() -> None:
    session = _session()
    session.progress_of("C1").state = ComponentState.DONE

    with pytest.raises(ComponentAlreadyDone):
        session.activate("C1", ACTIVATION)
    assert session.done_count == 1


def test_unknown_component() -> None:
    with pytest.raises(ComponentNotFound):
        _session().activate("C9", ACTIVATION)


def test_completed_session_cannot_activate() -> None:
    session = _session()
    session.status = SessionStatus.COMPLETED

    with pytest.raises(SessionCompleted):
        session.activate("C1", ACTIVATION)
