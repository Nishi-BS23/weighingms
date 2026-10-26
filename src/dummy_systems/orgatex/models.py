"""Dummy OrgaTEX training contract models. Not the real OrgaTEX interface (requirements TA-01)."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field, field_serializer

from dummy_systems.common.models import ApiModel, Quantity

BatchStatus = Literal["QUEUED", "WEIGHING", "WEIGHED", "CANCELLED"]
DyestuffType = Literal["DYE", "AUXILIARY", "SALT", "ALKALI"]
WeighingResult = Literal["IN_TOLERANCE", "OVERRIDDEN"]


class Batch(ApiModel):
    batch_id: str
    order_ref: str
    machine_ref: str
    fabric_desc: str
    fabric_weight_kg: Decimal
    shade_code: str
    recipe_id: str
    component_count: int
    status: BatchStatus
    released_at: datetime

    @field_serializer("fabric_weight_kg")
    def _weight_as_string(self, value: Decimal) -> str:
        return str(value)


class BatchList(ApiModel):
    generated_at: datetime
    batches: list[Batch]


class RecipeComponent(ApiModel):
    component_id: str
    sequence: int
    dyestuff_code: str
    name: str
    dyestuff_type: DyestuffType
    colour_hex: str
    target_qty: Quantity
    tolerance: Quantity | None = None
    lot_id: str


class Recipe(ApiModel):
    recipe_id: str
    batch_id: str
    shade_code: str
    version: str
    training_data_note: str | None = None
    components: list[RecipeComponent]


class ConsumptionLine(ApiModel):
    component_id: str
    dyestuff_code: str
    lot_id: str
    target: Quantity
    actual: Quantity
    scale_id: str
    operator_id: str
    confirmed_at: datetime
    result: WeighingResult


class ConsumptionPosting(ApiModel):
    idempotency_key: str = Field(min_length=1)
    session_id: str
    station_id: str
    operator_id: str
    completed_at: datetime
    lines: list[ConsumptionLine] = Field(min_length=1)


class ConsumptionReceipt(ApiModel):
    consumption_id: str
    batch_id: str
    received_at: datetime
    duplicate: bool


class StoredConsumption(ApiModel):
    consumption_id: str
    batch_id: str
    received_at: datetime
    posting: ConsumptionPosting


class StatusUpdate(ApiModel):
    status: BatchStatus
