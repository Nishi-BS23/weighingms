"""Tolerance evaluation (story 002/003; Workbook Step 22 boundary cases)."""

from decimal import Decimal

import pytest

from weighingms.domain.quantity import Quantity
from weighingms.domain.tolerance import ToleranceBand
from weighingms.domain.weighing.evaluation import Action, WeighingZone, display_max, evaluate

YELLOW = ToleranceBand(Quantity.of("94.0", "g"), Quantity.of("0.5", "g"), "RECIPE")
SODIUM = ToleranceBand(Quantity.of("24.000", "kg"), Quantity.of("0.120", "kg"), "RECIPE")


@pytest.mark.parametrize(
    ("net", "zone", "can_confirm"),
    [
        ("93.4", WeighingZone.NEAR, False),  # below tolerance → cannot confirm
        ("93.5", WeighingZone.WITHIN, True),  # lower boundary → can confirm
        ("94.0", WeighingZone.WITHIN, True),  # target → can confirm
        ("94.5", WeighingZone.WITHIN, True),  # upper boundary → can confirm
        ("94.6", WeighingZone.OVER, False),  # over → cannot confirm
    ],
)
def test_workbook_step_22_yellow_rgb_boundaries(
    net: str, zone: WeighingZone, can_confirm: bool
) -> None:
    evaluation = evaluate(YELLOW, Quantity.of(net, "g"))

    assert evaluation.zone is zone
    assert evaluation.can_confirm is can_confirm


def test_under_and_near_zones() -> None:
    assert evaluate(YELLOW, Quantity.of("84.5", "g")).zone is WeighingZone.UNDER
    assert evaluate(YELLOW, Quantity.of("84.6", "g")).zone is WeighingZone.NEAR


def test_remaining_and_status_text_while_dispensing() -> None:
    evaluation = evaluate(YELLOW, Quantity.of("60.0", "g"))

    assert evaluation.remaining.display() == "34.0"
    assert evaluation.status_text == "DISPENSE — 34.0 g REMAINING"
    assert evaluation.allowed_actions == (Action.RETARE, Action.QUIT, Action.OVERRIDE)


def test_within_tolerance_status_and_actions() -> None:
    evaluation = evaluate(YELLOW, Quantity.of("94.2", "g"))

    assert evaluation.status_text == "WITHIN TOLERANCE — PRESS OK TO CONFIRM"
    assert evaluation.allowed_actions[0] is Action.CONFIRM
    assert evaluation.remaining.display() == "0.0"


def test_overshoot_surplus_matches_the_prototype() -> None:
    evaluation = evaluate(YELLOW, Quantity.of("96.4", "g"))

    assert evaluation.zone is WeighingZone.OVER
    assert evaluation.surplus is not None and evaluation.surplus.display() == "2.4"
    assert evaluation.surplus_pct == Decimal("2.6")
    assert evaluation.status_text == "OVER TOLERANCE — SURPLUS +2.4 g"


def test_kilogram_component() -> None:
    assert evaluate(SODIUM, Quantity.of("23.879", "kg")).zone is WeighingZone.NEAR
    assert evaluate(SODIUM, Quantity.of("23.880", "kg")).can_confirm
    assert evaluate(SODIUM, Quantity.of("24.120", "kg")).can_confirm
    assert evaluate(SODIUM, Quantity.of("24.121", "kg")).zone is WeighingZone.OVER


def test_reading_in_another_unit_is_converted_and_rounded_like_the_display() -> None:
    evaluation = evaluate(SODIUM, Quantity.of("23880.4", "g"))

    assert evaluation.net == Quantity(Decimal("23.880"), "kg")
    assert evaluation.can_confirm


def test_scale_offline_never_allows_confirmation() -> None:
    evaluation = evaluate(YELLOW, None)

    assert evaluation.zone is WeighingZone.OFFLINE
    assert evaluation.can_confirm is False
    assert evaluation.net is None
    assert evaluation.status_text == "SCALE OFFLINE — CHECK CONNECTION"
    assert evaluation.allowed_actions == (Action.QUIT,)


def test_expired_calibration_blocks_confirmation() -> None:
    evaluation = evaluate(YELLOW, Quantity.of("94.0", "g"), calibration_valid=False)

    assert evaluation.zone is WeighingZone.WITHIN
    assert evaluation.can_confirm is False
    assert evaluation.status_text == "SCALE CALIBRATION EXPIRED — CALL SUPERVISOR"


def test_empty_scale_offers_no_override() -> None:
    assert Action.OVERRIDE not in evaluate(YELLOW, Quantity.of("0.0", "g")).allowed_actions


def test_negative_net_counts_as_nothing_dispensed() -> None:
    evaluation = evaluate(YELLOW, Quantity.of("-3.0", "g"))

    assert evaluation.zone is WeighingZone.UNDER
    assert evaluation.remaining.display() == "97.0"


@pytest.mark.parametrize(
    ("target", "tol", "unit", "expected"),
    [
        ("94.0", "0.5", "g", "125.0"),
        ("386.0", "2.0", "g", "515.0"),
        ("1240.0", "6.0", "g", "1650.0"),
        ("24.000", "0.120", "kg", "32.000"),
        ("9.600", "0.048", "kg", "13.000"),
    ],
)
def test_display_max_is_close_to_the_prototype_bar_scale(
    target: str, tol: str, unit: str, expected: str
) -> None:
    band = ToleranceBand(Quantity.of(target, unit), Quantity.of(tol, unit), "RECIPE")  # type: ignore[arg-type]

    assert display_max(band).display() == expected
    assert display_max(band) > band.maximum
