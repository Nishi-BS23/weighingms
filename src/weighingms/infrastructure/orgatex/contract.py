"""The (Dummy) OrgaTEX wire contract as WeighingMS parses it.

Kept separate from the domain so a different OrgaTEX interface only changes this package
(Brief IR-07). These shapes mirror the workbook training contract, not the real OrgaTEX.
"""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class _Wire(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")


class WireQuantity(_Wire):
    value: Decimal
    unit: Literal["g", "kg"]


class WireBatch(_Wire):
    batch_id: str
    order_ref: str
    machine_ref: str
    fabric_desc: str
    fabric_weight_kg: Decimal
    shade_code: str
    recipe_id: str
    component_count: int
    status: str
    released_at: datetime


class WireBatchList(_Wire):
    generated_at: datetime
    batches: list[WireBatch]


class WireComponent(_Wire):
    component_id: str
    sequence: int
    dyestuff_code: str
    name: str
    colour_hex: str
    target_qty: WireQuantity
    tolerance: WireQuantity | None = None
    lot_id: str


class WireRecipe(_Wire):
    recipe_id: str
    batch_id: str
    shade_code: str
    version: str
    components: list[WireComponent]


class WireConsumptionReceipt(_Wire):
    consumption_id: str
    received_at: datetime
    duplicate: bool
