"""Batch queue, batch detail and recipe as the station sees them (FR-1, FR-3, FR-4)."""

from dataclasses import dataclass

from weighingms.application.ports import BatchQueue, OrgatexBatch, OrgatexPort, OrgatexRecipe
from weighingms.config import StationConfig
from weighingms.domain.quantity import Quantity
from weighingms.domain.scale_selection import ScaleDefinition
from weighingms.domain.tolerance import ToleranceBand, band_for

_NOT_SELECTABLE_REASONS = {
    "WEIGHED": "Batch has already been weighed.",
    "CANCELLED": "Batch was cancelled in OrgaTEX.",
}


@dataclass(frozen=True)
class StationBatch:
    batch: OrgatexBatch
    selectable: bool
    not_selectable_reason: str | None

    @property
    def fabric_lot(self) -> str:
        weight = self.batch.fabric_weight_kg.normalize()
        return f"{self.batch.fabric_desc} · {weight:f} kg"


@dataclass(frozen=True)
class StationComponent:
    component_id: str
    sequence: int
    dyestuff_code: str
    name: str
    short_name: str
    colour_hex: str
    target: Quantity
    band: ToleranceBand
    scale: ScaleDefinition
    lot_id: str


@dataclass(frozen=True)
class StationRecipe:
    recipe_id: str
    batch_id: str
    shade_code: str
    version: str
    components: list[StationComponent]


class BatchService:
    def __init__(self, orgatex: OrgatexPort, station: StationConfig) -> None:
        self._orgatex = orgatex
        self._station = station

    def queue(self) -> tuple[BatchQueue, list[StationBatch]]:
        queue = self._orgatex.list_batches()
        return queue, [self._station_batch(b) for b in queue.batches]

    def batch(self, batch_id: str) -> StationBatch:
        return self._station_batch(self._orgatex.get_batch(batch_id))

    def recipe(self, batch_id: str) -> StationRecipe:
        return self.station_recipe(self._orgatex.get_recipe(batch_id))

    def station_recipe(self, recipe: OrgatexRecipe) -> StationRecipe:
        """Enrich an OrgaTEX recipe with WeighingMS's scale assignment and tolerance bands."""
        components = []
        for c in sorted(recipe.components, key=lambda c: c.sequence):
            scale = self._station.scale_policy.select(c.target)
            components.append(
                StationComponent(
                    component_id=c.component_id,
                    sequence=c.sequence,
                    dyestuff_code=c.dyestuff_code,
                    name=c.name,
                    short_name=self._station.short_name(c.name),
                    colour_hex=c.colour_hex,
                    target=c.target,
                    band=band_for(
                        c.target, c.tolerance, scale.scale_class, self._station.default_tolerance
                    ),
                    scale=scale,
                    lot_id=c.lot_id,
                )
            )
        return StationRecipe(
            recipe_id=recipe.recipe_id,
            batch_id=recipe.batch_id,
            shade_code=recipe.shade_code,
            version=recipe.version,
            components=components,
        )

    def _station_batch(self, batch: OrgatexBatch) -> StationBatch:
        selectable = batch.status in self._station.selectable_statuses
        reason = None
        if not selectable:
            reason = _NOT_SELECTABLE_REASONS.get(batch.status, "Batch status is not supported.")
        return StationBatch(batch=batch, selectable=selectable, not_selectable_reason=reason)
