"""Ports: what WeighingMS needs from the outside world, in WeighingMS's own terms.

Adapters in `weighingms.infrastructure` implement these against the (dummy) external systems.
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal, Protocol

from weighingms.domain.errors import DependencyUnavailable, DomainError
from weighingms.domain.quantity import Quantity
from weighingms.domain.weighing.records import Override, WeighingRecord
from weighingms.domain.weighing.session import WeighingSession

BatchStatus = str
"""OrgaTEX batch status as received; unknown values are kept and treated as non-selectable."""

WriteBackStatus = Literal["WEIGHING", "WEIGHED"]


@dataclass(frozen=True)
class OrgatexBatch:
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


@dataclass(frozen=True)
class BatchQueue:
    received_at: datetime
    batches: list[OrgatexBatch]


@dataclass(frozen=True)
class OrgatexComponent:
    component_id: str
    sequence: int
    dyestuff_code: str
    name: str
    colour_hex: str
    target: Quantity
    tolerance: Quantity | None
    lot_id: str


@dataclass(frozen=True)
class OrgatexRecipe:
    recipe_id: str
    batch_id: str
    shade_code: str
    version: str
    components: list[OrgatexComponent]


@dataclass(frozen=True)
class ConsumptionLine:
    component_id: str
    dyestuff_code: str
    lot_id: str
    target: Quantity
    actual: Quantity
    scale_id: str
    operator_id: str
    confirmed_at: datetime
    result: Literal["IN_TOLERANCE", "OVERRIDDEN"]


@dataclass(frozen=True)
class ConsumptionPayload:
    batch_id: str
    idempotency_key: str
    session_id: str
    station_id: str
    operator_id: str
    completed_at: datetime
    lines: list[ConsumptionLine]


@dataclass(frozen=True)
class ConsumptionAck:
    consumption_id: str
    received_at: datetime
    duplicate: bool


class OrgatexUnavailable(DependencyUnavailable):
    code = "ORGATEX_UNAVAILABLE"


class OrgatexBadData(DomainError):
    status_code = 502
    code = "ORGATEX_BAD_DATA"


class OrgatexPort(Protocol):
    """Everything WeighingMS reads from or writes to OrgaTEX (Brief IR-01 – IR-06)."""

    def list_batches(self) -> BatchQueue: ...

    def get_batch(self, batch_id: str) -> OrgatexBatch: ...

    def get_recipe(self, batch_id: str) -> OrgatexRecipe: ...

    def set_batch_status(self, batch_id: str, status: WriteBackStatus) -> None: ...

    def post_consumption(self, payload: ConsumptionPayload) -> ConsumptionAck: ...

    def ping(self) -> bool:
        """Cheap reachability probe for the status strip (never raises)."""
        ...

    def last_contact(self) -> datetime | None:
        """Time of the last successful call, for the status strip."""
        ...


# ── Scales ──────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ScaleReading:
    scale_id: str
    gross: Quantity
    tare: Quantity
    net: Quantity
    stable: bool
    read_at: datetime


@dataclass(frozen=True)
class ScaleState:
    scale_id: str
    calibration_due: date
    calibration_valid: bool


class ScaleUnavailable(DependencyUnavailable):
    code = "SCALE_UNAVAILABLE"


class ScalePort(Protocol):
    """Weight indicators (Brief IR-10 – IR-14). Failures raise `ScaleUnavailable`, never 0."""

    def read_weight(self, scale_id: str) -> ScaleReading: ...

    def tare(self, scale_id: str) -> ScaleReading: ...

    def status(self, scale_id: str) -> ScaleState: ...


# ── Scanner and printer ─────────────────────────────────────────────────────


@dataclass(frozen=True)
class ScanEvent:
    seq: int
    code: str
    scanned_at: datetime


class ScannerUnavailable(DependencyUnavailable):
    code = "SCANNER_UNAVAILABLE"


class ScannerPort(Protocol):
    def scans_after(self, seq: int) -> tuple[list[ScanEvent], int]:
        """New scans with seq > `seq`, in order, and the last sequence number."""
        ...

    def is_available(self) -> bool: ...


class PrinterProbe(Protocol):
    def is_available(self) -> bool: ...


class PrinterUnavailable(DependencyUnavailable):
    code = "PRINTER_UNAVAILABLE"


@dataclass(frozen=True)
class PrintReceipt:
    ticket_id: str
    printed_at: datetime


class PrinterPort(PrinterProbe, Protocol):
    """Ticket printer (Brief IR-16). It prints rendered lines; content is composed by WeighingMS."""

    def print_ticket(
        self, batch_id: str, session_id: str, lines: list[str], barcode_value: str, reprint: bool
    ) -> PrintReceipt: ...


# ── Training control (training build only) ──────────────────────────────────


class TrainingControlPort(Protocol):
    """Drives the training substitutes. Has no real-world counterpart."""

    def availability(self) -> dict[str, bool]: ...

    def set_availability(self, system: str, available: bool) -> dict[str, bool]: ...

    def reset(self) -> None: ...

    def simulate(self, scale_id: str, profile: str, net: Quantity) -> dict[str, Any]: ...

    def place_load(self, scale_id: str, gross: Quantity) -> None:
        """Simulate the operator putting a load (an empty container) on the scale."""
        ...

    def set_calibration(self, scale_id: str, due: date) -> dict[str, Any]: ...

    def scan(self, code: str) -> ScanEvent: ...


# ── Persistence (implemented in weighingms.infrastructure.persistence) ─────


class SessionStore(Protocol):
    """Repository for the WeighingSession aggregate; enforces one open session per batch."""

    def get(self, session_id: str) -> WeighingSession: ...

    def find_open(self, batch_id: str) -> WeighingSession | None: ...

    def add(self, session: WeighingSession) -> None: ...

    def save(self, session: WeighingSession) -> None: ...

    def save_with_record(
        self, session: WeighingSession, record: WeighingRecord, override: Override | None = None
    ) -> None: ...

    def clear(self) -> None: ...


class RecordStore(Protocol):
    def for_session(self, session_id: str) -> list[WeighingRecord]: ...

    def for_batch(self, batch_id: str) -> list[WeighingRecord]: ...

    def overrides_for_session(self, session_id: str) -> list[Override]: ...


class PrintStore(Protocol):
    def add(
        self, session_id: str, ticket_id: str, reprint: bool, operator_id: str, at: datetime
    ) -> None: ...

    def count_for_session(self, session_id: str) -> int: ...

    def clear(self) -> None: ...


class StateStore(Protocol):
    def get(self, key: str) -> str | None: ...

    def set(self, key: str, value: str) -> None: ...

    def clear(self) -> None: ...


class AuditStore(Protocol):
    def add(
        self,
        event_type: str,
        actor_id: str,
        at: datetime,
        session_id: str | None = None,
        detail: dict[str, Any] | None = None,
    ) -> str: ...

    def events(self, session_id: str | None = None) -> list[dict[str, Any]]: ...

    def clear(self) -> None: ...
