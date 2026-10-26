"""Tolerance bands (FR-12): from the recipe, or from the configured default rule (TA-03)."""

from tests.conftest import STATION_CONFIG
from weighingms.config import load_station_config
from weighingms.domain.quantity import Quantity
from weighingms.domain.tolerance import band_for

DEFAULT_RULE = load_station_config(STATION_CONFIG).default_tolerance


def test_recipe_tolerance_defines_an_inclusive_band() -> None:
    band = band_for(Quantity.of("94.0", "g"), Quantity.of("0.5", "g"), "PRECISION", DEFAULT_RULE)

    assert (band.minimum.display(), band.maximum.display(), band.source) == (
        "93.5",
        "94.5",
        "RECIPE",
    )
    assert band.contains(Quantity.of("93.5", "g"))
    assert band.contains(Quantity.of("94.5", "g"))
    assert not band.contains(Quantity.of("93.4", "g"))
    assert not band.contains(Quantity.of("94.6", "g"))


def test_kilogram_band() -> None:
    band = band_for(Quantity.of("24.000", "kg"), Quantity.of("0.120", "kg"), "FLOOR", DEFAULT_RULE)

    assert (band.minimum.display(), band.maximum.display()) == ("23.880", "24.120")


def test_default_rule_is_half_a_percent_of_target() -> None:
    band = band_for(Quantity.of("6.200", "kg"), None, "FLOOR", DEFAULT_RULE)

    assert band.plus_minus.display() == "0.031"
    assert band.source == "DEFAULT"


def test_default_rule_never_goes_below_the_scale_minimum() -> None:
    small_dye = band_for(Quantity.of("9.5", "g"), None, "PRECISION", DEFAULT_RULE)
    small_aux = band_for(Quantity.of("1.000", "kg"), None, "FLOOR", DEFAULT_RULE)

    assert small_dye.plus_minus.display() == "0.2"
    assert small_aux.plus_minus.display() == "0.010"


def test_tolerance_given_in_another_unit_is_converted() -> None:
    band = band_for(Quantity.of("1.000", "kg"), Quantity.of("10", "g"), "PRECISION", DEFAULT_RULE)

    assert (band.minimum.display(), band.maximum.display()) == ("0.990", "1.010")
