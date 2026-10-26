"""API response models: camelCase JSON, quantities as decimal strings with a unit."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from weighingms.application.batches import StationBatch, StationComponent, StationRecipe
from weighingms.domain.quantity import Quantity, Unit
from weighingms.domain.scale_selection import ScaleClass, ScaleDefinition
from weighingms.domain.tolerance import ToleranceSource


class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, frozen=True)


class QuantityOut(ApiModel):
    value: str
    unit: Unit

    @classmethod
    def of(cls, quantity: Quantity) -> "QuantityOut":
        return cls(value=quantity.display(), unit=quantity.unit)


class BatchOut(ApiModel):
    batch_id: str
    order_ref: str
    machine_ref: str
    fabric_desc: str
    fabric_weight_kg: str
    fabric_lot: str
    shade_code: str
    recipe_id: str
    component_count: int
    status: str
    selectable: bool
    not_selectable_reason: str | None
    released_at: datetime

    @classmethod
    def of(cls, sb: StationBatch) -> "BatchOut":
        b = sb.batch
        return cls(
            batch_id=b.batch_id,
            order_ref=b.order_ref,
            machine_ref=b.machine_ref,
            fabric_desc=b.fabric_desc,
            fabric_weight_kg=f"{b.fabric_weight_kg.normalize():f}",
            fabric_lot=sb.fabric_lot,
            shade_code=b.shade_code,
            recipe_id=b.recipe_id,
            component_count=b.component_count,
            status=b.status,
            selectable=sb.selectable,
            not_selectable_reason=sb.not_selectable_reason,
            released_at=b.released_at,
        )


class BatchQueueOut(ApiModel):
    received_at: datetime
    batches: list[BatchOut]


class ToleranceOut(ApiModel):
    plus_minus: QuantityOut
    minimum: QuantityOut
    maximum: QuantityOut
    source: ToleranceSource


class ScaleOut(ApiModel):
    scale_id: str
    scale_class: ScaleClass
    label: str

    @classmethod
    def of(cls, scale: ScaleDefinition) -> "ScaleOut":
        return cls(scale_id=scale.scale_id, scale_class=scale.scale_class, label=scale.label)


class ComponentOut(ApiModel):
    component_id: str
    sequence: int
    dyestuff_code: str
    name: str
    short_name: str
    colour_hex: str
    target: QuantityOut
    tolerance: ToleranceOut
    scale: ScaleOut
    lot_id: str

    @classmethod
    def of(cls, c: StationComponent) -> "ComponentOut":
        return cls(
            component_id=c.component_id,
            sequence=c.sequence,
            dyestuff_code=c.dyestuff_code,
            name=c.name,
            short_name=c.short_name,
            colour_hex=c.colour_hex,
            target=QuantityOut.of(c.target),
            tolerance=ToleranceOut(
                plus_minus=QuantityOut.of(c.band.plus_minus),
                minimum=QuantityOut.of(c.band.minimum),
                maximum=QuantityOut.of(c.band.maximum),
                source=c.band.source,
            ),
            scale=ScaleOut.of(c.scale),
            lot_id=c.lot_id,
        )


class RecipeOut(ApiModel):
    recipe_id: str
    batch_id: str
    shade_code: str
    version: str
    components: list[ComponentOut]

    @classmethod
    def of(cls, r: StationRecipe) -> "RecipeOut":
        return cls(
            recipe_id=r.recipe_id,
            batch_id=r.batch_id,
            shade_code=r.shade_code,
            version=r.version,
            components=[ComponentOut.of(c) for c in r.components],
        )
