"""Confirm, override, abandon and complete on the WeighingSession aggregate (bolt 007)."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from tests.conftest import STATION_CONFIG
from weighingms.config import load_station_config
from weighingms.domain.errors import (
    BatchIncomplete,
    NoActiveComponent,
    OutOfTolerance,
    OverrideNotNeeded,
    ScaleCalibrationExpired,
    SessionCompleted,
)
from weighingms.domain.operators import verify_pin
from weighingms.domain.quantity import Quantity
from weighingms.domain.tolerance import ToleranceBand
from weighingms.domain.weighing.evaluation import Action, WeighingZone, evaluate
from weighingms.domain.weighing.session import (
    Activation,
    ComponentSpec,
    ComponentState,
    RecipeSnapshot,
    SessionStatus,
    SyncStatus,
    WeighingSession,
)

NOW = datetime(2026, 10, 26, 7, 0, tzinfo=UTC)
STATION = load_station_config(STATION_CONFIG)
BAND = ToleranceBand(Quantity.of("94.0", "g"), Quantity.of("0.5", "g"), "RECIPE")


def _session(n: int = 2) -> WeighingSession:
    specs = tuple(
        ComponentSpec(
            component_id=f"C{i}",
            sequence=i,
            dyestuff_code="DYE-4471",
            name="Remazol Yellow RGB",
            short_name="Yellow RGB",
            colour_hex="#d9a520",
            target=BAND.target,
            band=BAND,
            scale=STATION.scale_policy.select(BAND.target),
            lot_id="2026-0387",
        )
        for i in range(1, n + 1)
    )
    session = WeighingSession.start(
        "S", "B-24187", "STN-01", RecipeSnapshot("R", "3", "Teal 4C", "SO", "JET", specs), "OP", NOW
    )
    session.activate("C1", Activation("C-12", Quantity.of("214", "g"), NOW))
    return session


def _eval(net: str, calibration_valid: bool = True):  # type: ignore[no-untyped-def]
    return evaluate(BAND, Quantity.of(net, "g"), calibration_valid=calibration_valid)


def test_confirm_records_the_full_traceability_set() -> None:
    session = _session()

    record = session.confirm(_eval("94.2"), "WR-1", "OP-1001", NOW)

    assert (record.result, record.actual.display(), record.surplus) == (
        "IN_TOLERANCE",
        "94.2",
        None,
    )
    assert (record.tolerance_min.display(), record.tolerance_max.display()) == ("93.5", "94.5")
    assert (record.lot_id, record.container_id, record.scale_id) == (
        "2026-0387",
        "C-12",
        "scale-3kg",
    )
    assert record.tare == Quantity(Decimal("214"), "g")
    assert record.operator_id == "OP-1001"
    progress = session.progress_of("C1")
    assert progress.state is ComponentState.DONE
    assert (progress.record_id, progress.actual) == ("WR-1", record.actual)


@pytest.mark.parametrize("net", ["93.4", "94.6", "0.0"])
def test_confirm_outside_tolerance_is_rejected(net: str) -> None:
    session = _session()

    with pytest.raises(OutOfTolerance):
        session.confirm(_eval(net), "WR-1", "OP", NOW)
    assert session.progress_of("C1").state is ComponentState.ACTIVE


def test_confirm_with_expired_calibration_is_rejected() -> None:
    with pytest.raises(ScaleCalibrationExpired):
        _session().confirm(_eval("94.0", calibration_valid=False), "WR-1", "OP", NOW)


def test_confirm_without_reading_is_rejected() -> None:
    with pytest.raises(OutOfTolerance):
        _session().confirm(evaluate(BAND, None), "WR-1", "OP", NOW)


def test_override_records_an_overridden_weighing_with_surplus() -> None:
    session = _session()

    record = session.override(_eval("96.4"), "WR-1", "OP", NOW)

    assert record.result == "OVERRIDDEN"
    assert record.surplus is not None and record.surplus.display() == "2.4"
    assert session.progress_of("C1").state is ComponentState.DONE


def test_override_of_an_underweight_has_no_surplus() -> None:
    record = _session().override(_eval("90.0"), "WR-1", "OP", NOW)

    assert (record.result, record.surplus) == ("OVERRIDDEN", None)


@pytest.mark.parametrize("net", ["94.0", "0.0"])
def test_override_not_needed_within_tolerance_or_on_an_empty_scale(net: str) -> None:
    with pytest.raises(OverrideNotNeeded):
        _session().override(_eval(net), "WR-1", "OP", NOW)


def test_overshoot_guidance_follows_the_step_24_decision() -> None:
    evaluation = _eval("96.4")

    assert evaluation.zone is WeighingZone.OVER
    assert Action.CONFIRM not in evaluation.allowed_actions
    assert {Action.RETARE, Action.QUIT, Action.OVERRIDE} <= set(evaluation.allowed_actions)
    assert evaluation.guidance is not None
    assert "back within 93.5 – 94.5 g" in evaluation.guidance
    assert "Re-tare" in evaluation.guidance and "supervisor" in evaluation.guidance


def test_removing_the_excess_makes_confirmation_possible_again() -> None:
    session = _session()
    with pytest.raises(OutOfTolerance):
        session.confirm(_eval("96.4"), "WR-1", "OP", NOW)

    record = session.confirm(_eval("94.4"), "WR-1", "OP", NOW)

    assert record.result == "IN_TOLERANCE"


def test_abandon_returns_the_component_to_pending_without_a_record() -> None:
    session = _session()

    session.abandon()

    assert session.progress_of("C1").state is ComponentState.PENDING
    assert session.progress_of("C1").record_id is None
    with pytest.raises(NoActiveComponent):
        session.abandon()


def test_complete_requires_every_component_done() -> None:
    session = _session(2)
    session.confirm(_eval("94.0"), "WR-1", "OP", NOW)

    with pytest.raises(BatchIncomplete) as error:
        session.complete(NOW)
    assert error.value.details == {"done": 1, "total": 2}


def test_complete_and_sync() -> None:
    session = _session(1)
    session.confirm(_eval("94.0"), "WR-1", "OP", NOW)

    assert session.complete(NOW) is True
    assert (session.status, session.sync_status) == (SessionStatus.COMPLETED, SyncStatus.PENDING)
    assert session.complete(NOW) is False  # idempotent
    session.mark_synced("CNS-1", NOW)
    assert (session.sync_status, session.consumption_id) == (SyncStatus.SYNCED, "CNS-1")
    with pytest.raises(SessionCompleted):
        session.abandon()


def test_supervisor_pin_verification() -> None:
    supervisor = STATION.operators.by_id("SV-2001")

    assert supervisor.pin_hash is not None
    assert verify_pin(supervisor.pin_hash, "2468") is True
    assert verify_pin(supervisor.pin_hash, "1234") is False
    assert verify_pin("not-a-hash", "2468") is False
    assert STATION.operators.supervisor_for_pin("2468") == supervisor
    assert STATION.operators.supervisor_for_pin("0000") is None
