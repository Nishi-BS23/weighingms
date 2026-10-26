"""Exact quantities in grams or kilograms. Floating point is never used (NFR-11, Brief NFR-16)."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

Unit = Literal["g", "kg"]

DISPLAY_STEP: dict[Unit, Decimal] = {"g": Decimal("0.1"), "kg": Decimal("0.001")}
"""Display precision per unit: grams 1 decimal place, kilograms 3 (prototype `dp()`)."""

_GRAMS_PER: dict[Unit, Decimal] = {"g": Decimal(1), "kg": Decimal(1000)}


@dataclass(frozen=True, order=False)
class Quantity:
    value: Decimal
    unit: Unit

    @classmethod
    def of(cls, value: str | int | Decimal, unit: Unit) -> "Quantity":
        return cls(Decimal(value), unit)

    def to(self, unit: Unit) -> "Quantity":
        if unit == self.unit:
            return self
        return Quantity(self.value * _GRAMS_PER[self.unit] / _GRAMS_PER[unit], unit)

    def rounded(self) -> "Quantity":
        """Rounded to the unit's display precision."""
        return Quantity(
            self.value.quantize(DISPLAY_STEP[self.unit], rounding=ROUND_HALF_UP), self.unit
        )

    def display(self) -> str:
        """Value at display precision, e.g. '94.0' (g) or '24.000' (kg)."""
        return str(self.rounded().value)

    def __add__(self, other: "Quantity") -> "Quantity":
        return Quantity(self.value + other.to(self.unit).value, self.unit)

    def __sub__(self, other: "Quantity") -> "Quantity":
        return Quantity(self.value - other.to(self.unit).value, self.unit)

    def __lt__(self, other: "Quantity") -> bool:
        return self.value < other.to(self.unit).value

    def __le__(self, other: "Quantity") -> bool:
        return self.value <= other.to(self.unit).value

    def __gt__(self, other: "Quantity") -> bool:
        return self.value > other.to(self.unit).value

    def __ge__(self, other: "Quantity") -> bool:
        return self.value >= other.to(self.unit).value

    def is_zero_or_less(self) -> bool:
        return self.value <= 0
