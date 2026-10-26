"""Dummy device wire contracts (scale, scanner, training control) as WeighingMS parses them."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class _Wire(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")


class WireQuantity(_Wire):
    value: Decimal
    unit: Literal["g", "kg"]


class WireReading(_Wire):
    scale_id: str
    gross: WireQuantity
    tare: WireQuantity
    net: WireQuantity
    stable: bool
    read_at: datetime


class WireScaleStatus(_Wire):
    scale_id: str
    calibration_due: date
    calibration_valid: bool


class WireScan(_Wire):
    seq: int
    code: str
    scanned_at: datetime


class WireScanBatch(_Wire):
    scans: list[WireScan]
    last_seq: int


class WireAvailability(_Wire):
    systems: dict[str, bool]


class WirePrintReceipt(_Wire):
    ticket_id: str
    printed_at: datetime
