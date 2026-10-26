"""Immutable traceability records (FR-13, FR-21, Brief BR-11, DR-02)."""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from weighingms.domain.quantity import Quantity

WeighingResult = Literal["IN_TOLERANCE", "OVERRIDDEN"]


@dataclass(frozen=True)
class WeighingRecord:
    """What was weighed, against what, by whom, on which scale, from which lot, into what."""

    record_id: str
    session_id: str
    batch_id: str
    component_id: str
    dyestuff_code: str
    dyestuff_name: str
    target: Quantity
    actual: Quantity
    tolerance_min: Quantity
    tolerance_max: Quantity
    result: WeighingResult
    surplus: Quantity | None
    operator_id: str
    lot_id: str
    container_id: str
    tare: Quantity
    scale_id: str
    confirmed_at: datetime


@dataclass(frozen=True)
class Override:
    """Supervisor authorisation to accept a weighing outside tolerance (BR-13)."""

    override_id: str
    record_id: str
    supervisor_id: str
    reason: str
    authorised_at: datetime
