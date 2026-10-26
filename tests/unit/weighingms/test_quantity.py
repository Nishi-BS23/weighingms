"""Exact quantities (NFR-11)."""

from decimal import Decimal

from weighingms.domain.quantity import Quantity


def test_conversion_between_grams_and_kilograms_is_exact() -> None:
    assert Quantity.of("1850", "g").to("kg") == Quantity(Decimal("1.85"), "kg")
    assert Quantity.of("0.214", "kg").to("g").value == Decimal("214.000")


def test_display_precision_is_one_decimal_for_grams_and_three_for_kilograms() -> None:
    assert Quantity.of("94", "g").display() == "94.0"
    assert Quantity.of("93.46", "g").display() == "93.5"
    assert Quantity.of("24", "kg").display() == "24.000"
    assert Quantity.of("9.6485", "kg").display() == "9.649"


def test_arithmetic_and_comparison_across_units() -> None:
    assert (Quantity.of("1", "kg") - Quantity.of("250", "g")) == Quantity(Decimal("0.750"), "kg")
    assert (Quantity.of("94.0", "g") + Quantity.of("0.5", "g")).display() == "94.5"
    assert Quantity.of("3", "kg") <= Quantity.of("3000.0", "g")
    assert Quantity.of("3.001", "kg") > Quantity.of("3000", "g")
    assert Quantity.of("0", "g").is_zero_or_less()


def test_no_float_drift() -> None:
    total = sum((Quantity.of("0.1", "g") for _ in range(10)), Quantity.of("0", "g"))

    assert total == Quantity(Decimal("1.0"), "g")
