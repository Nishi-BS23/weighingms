"""Automatic scale selection (FR-8, PDF §5.3)."""

from dataclasses import replace

import pytest

from tests.conftest import STATION_CONFIG
from weighingms.config import load_station_config
from weighingms.domain.quantity import Quantity, Unit

POLICY = load_station_config(STATION_CONFIG).scale_policy


@pytest.mark.parametrize(
    ("value", "unit", "expected"),
    [
        ("1240.0", "g", "3 kg precision"),
        ("386.0", "g", "3 kg precision"),
        ("94.0", "g", "3 kg precision"),
        ("24.000", "kg", "32 kg floor"),
        ("9.600", "kg", "32 kg floor"),
        ("3.000", "kg", "3 kg precision"),
        ("3000.0", "g", "3 kg precision"),
        ("3.001", "kg", "32 kg floor"),
        ("0.250", "kg", "3 kg precision"),
        ("3.500", "kg", "32 kg floor"),
    ],
)
def test_scale_is_selected_from_the_target_quantity(value: str, unit: Unit, expected: str) -> None:
    assert POLICY.select(Quantity.of(value, unit)).label == expected


def test_threshold_is_configurable() -> None:
    lower = replace(POLICY, threshold=Quantity.of("2", "kg"))

    assert lower.select(Quantity.of("2.5", "kg")).label == "32 kg floor"
    assert lower.select(Quantity.of("2.0", "kg")).label == "3 kg precision"
