"""Tolerance bands (FR-12): explicit, per component, configurable — never a universal tolerance."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from weighingms.domain.quantity import Quantity
from weighingms.domain.scale_selection import ScaleClass

ToleranceSource = Literal["RECIPE", "DEFAULT"]


@dataclass(frozen=True)
class ToleranceBand:
    """Inclusive acceptable range around a target."""

    target: Quantity
    plus_minus: Quantity
    source: ToleranceSource

    @property
    def minimum(self) -> Quantity:
        return (self.target - self.plus_minus).rounded()

    @property
    def maximum(self) -> Quantity:
        return (self.target + self.plus_minus).rounded()

    def contains(self, weight: Quantity) -> bool:
        return self.minimum <= weight <= self.maximum


@dataclass(frozen=True)
class DefaultToleranceRule:
    """±percent of target, never tighter than the minimum for the scale class (TA-03)."""

    percent: Decimal
    min_precision: Quantity
    min_floor: Quantity

    def plus_minus(self, target: Quantity, scale_class: ScaleClass) -> Quantity:
        floor = self.min_precision if scale_class == "PRECISION" else self.min_floor
        proportional = Quantity(target.value * self.percent / 100, target.unit).rounded()
        return max(proportional, floor.to(target.unit), key=lambda q: q.value).rounded()


def band_for(
    target: Quantity,
    recipe_tolerance: Quantity | None,
    scale_class: ScaleClass,
    default_rule: DefaultToleranceRule,
) -> ToleranceBand:
    if recipe_tolerance is not None:
        return ToleranceBand(target, recipe_tolerance.to(target.unit), "RECIPE")
    return ToleranceBand(target, default_rule.plus_minus(target, scale_class), "DEFAULT")
