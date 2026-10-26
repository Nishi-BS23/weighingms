"""Automatic scale selection (FR-8, PDF §5.3): target ≤ threshold → precision, else floor."""

from dataclasses import dataclass
from typing import Literal

from weighingms.domain.quantity import Quantity

ScaleClass = Literal["PRECISION", "FLOOR"]


@dataclass(frozen=True)
class ScaleDefinition:
    scale_id: str
    scale_class: ScaleClass
    label: str
    strip_label: str


@dataclass(frozen=True)
class ScaleSelectionPolicy:
    threshold: Quantity
    precision: ScaleDefinition
    floor: ScaleDefinition

    def select(self, target: Quantity) -> ScaleDefinition:
        return self.precision if target <= self.threshold else self.floor
