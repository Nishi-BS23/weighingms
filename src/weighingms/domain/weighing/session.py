"""The WeighingSession aggregate: one batch being weighed at the station (FR-2, FR-15, FR-16).

Invariants (ddd-01-domain-model.md):
  2. While in progress, at most one component is ACTIVE.
  3. Activating a PENDING component returns the previously ACTIVE one to PENDING.
  4. A DONE component cannot be activated.
  6. The recipe snapshot never changes after the session starts.
  8. Confirm requires the ACTIVE component and an evaluation that allows confirmation.
  9. Override requires a weighing outside tolerance with something on the scale.
 10. DONE never changes; it carries the actual and the record ID.
 11. Abandon returns the ACTIVE component to PENDING and records nothing.
 12. Complete requires every component DONE.
Invariant 1 (one open session per batch) is enforced by the repository.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from weighingms.domain.errors import (
    BatchIncomplete,
    ComponentAlreadyDone,
    ComponentNotFound,
    NoActiveComponent,
    OutOfTolerance,
    OverrideNotNeeded,
    ScaleCalibrationExpired,
    SessionCompleted,
)
from weighingms.domain.quantity import Quantity
from weighingms.domain.scale_selection import ScaleDefinition
from weighingms.domain.tolerance import ToleranceBand
from weighingms.domain.weighing.evaluation import Evaluation, WeighingZone
from weighingms.domain.weighing.records import WeighingRecord, WeighingResult


class SessionStatus(StrEnum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class ComponentState(StrEnum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    DONE = "DONE"


class SyncStatus(StrEnum):
    NOT_SYNCED = "NOT_SYNCED"
    PENDING = "PENDING"
    SYNCED = "SYNCED"


@dataclass(frozen=True)
class ComponentSpec:
    """A recipe component as fixed at session start: target, band, scale and lot."""

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
class RecipeSnapshot:
    recipe_id: str
    version: str
    shade_code: str
    order_ref: str
    machine_ref: str
    components: tuple[ComponentSpec, ...]

    def spec(self, component_id: str) -> ComponentSpec:
        for spec in self.components:
            if spec.component_id == component_id:
                return spec
        raise ComponentNotFound(f"Component {component_id} is not in this recipe.")


@dataclass(frozen=True)
class Activation:
    """Context captured when a component becomes the one being weighed."""

    container_id: str
    tare: Quantity
    activated_at: datetime


@dataclass
class ComponentProgress:
    component_id: str
    sequence: int
    state: ComponentState = ComponentState.PENDING
    activation: Activation | None = None
    record_id: str | None = None
    actual: Quantity | None = None


@dataclass(frozen=True)
class DomainEvent:
    name: str
    payload: dict[str, Any]


@dataclass
class WeighingSession:
    session_id: str
    batch_id: str
    station_id: str
    recipe: RecipeSnapshot
    started_by: str
    started_at: datetime
    components: list[ComponentProgress]
    status: SessionStatus = SessionStatus.IN_PROGRESS
    completed_at: datetime | None = None
    sync_status: SyncStatus = SyncStatus.NOT_SYNCED
    synced_at: datetime | None = None
    consumption_id: str | None = None
    events: list[DomainEvent] = field(default_factory=list, repr=False)

    @classmethod
    def start(
        cls,
        session_id: str,
        batch_id: str,
        station_id: str,
        recipe: RecipeSnapshot,
        operator_id: str,
        now: datetime,
    ) -> "WeighingSession":
        components = [
            ComponentProgress(component_id=c.component_id, sequence=c.sequence)
            for c in sorted(recipe.components, key=lambda c: c.sequence)
        ]
        session = cls(
            session_id=session_id,
            batch_id=batch_id,
            station_id=station_id,
            recipe=recipe,
            started_by=operator_id,
            started_at=now,
            components=components,
        )
        session._record("SessionStarted", batchId=batch_id, operatorId=operator_id)
        return session

    @property
    def active(self) -> ComponentProgress | None:
        return next((c for c in self.components if c.state is ComponentState.ACTIVE), None)

    @property
    def done_count(self) -> int:
        return sum(1 for c in self.components if c.state is ComponentState.DONE)

    def next_pending(self) -> ComponentProgress | None:
        return next((c for c in self.components if c.state is ComponentState.PENDING), None)

    def progress_of(self, component_id: str) -> ComponentProgress:
        for progress in self.components:
            if progress.component_id == component_id:
                return progress
        raise ComponentNotFound(f"Component {component_id} is not in this recipe.")

    def activate(self, component_id: str, activation: Activation) -> None:
        if self.status is SessionStatus.COMPLETED:
            raise SessionCompleted(f"Batch {self.batch_id} is already completed.")
        target = self.progress_of(component_id)
        if target.state is ComponentState.DONE:
            raise ComponentAlreadyDone(
                f"{self.recipe.spec(component_id).name} has already been weighed.",
                {"componentId": component_id},
            )
        current = self.active
        if current is not None and current is not target:
            current.state = ComponentState.PENDING
            current.activation = None
        target.state = ComponentState.ACTIVE
        target.activation = activation
        self._record(
            "ComponentActivated", componentId=component_id, containerId=activation.container_id
        )

    @property
    def all_done(self) -> bool:
        return all(c.state is ComponentState.DONE for c in self.components)

    def confirm(
        self, evaluation: Evaluation, record_id: str, operator_id: str, now: datetime
    ) -> WeighingRecord:
        """Accept the active component's weighing; the evaluation comes from a fresh reading."""
        active = self._require_active()
        if not evaluation.calibration_valid:
            raise ScaleCalibrationExpired(
                "The scale's calibration has expired. Call your supervisor."
            )
        if not evaluation.can_confirm or evaluation.net is None:
            spec = self.recipe.spec(active.component_id)
            shown = evaluation.net.display() if evaluation.net else "no reading"
            low, high, unit = (
                spec.band.minimum.display(),
                spec.band.maximum.display(),
                spec.target.unit,
            )
            raise OutOfTolerance(
                f"{spec.name}: {shown} {unit} is outside {low} – {high} {unit}.",
                {"componentId": active.component_id, "zone": evaluation.zone.value},
            )
        record = self._make_record(
            active, evaluation.net, "IN_TOLERANCE", None, record_id, operator_id, now
        )
        self._mark_done(active, record)
        self._record("ComponentConfirmed", componentId=active.component_id, recordId=record_id)
        return record

    def override(
        self, evaluation: Evaluation, record_id: str, operator_id: str, now: datetime
    ) -> WeighingRecord:
        """Accept a weighing outside tolerance on supervisor authority (checked by the caller)."""
        active = self._require_active()
        net = evaluation.net
        if evaluation.zone is WeighingZone.WITHIN or net is None or net.value <= 0:
            raise OverrideNotNeeded(
                "An override is only for a weighing outside tolerance with material on the scale.",
                {"zone": evaluation.zone.value},
            )
        surplus = evaluation.surplus if evaluation.zone is WeighingZone.OVER else None
        record = self._make_record(active, net, "OVERRIDDEN", surplus, record_id, operator_id, now)
        self._mark_done(active, record)
        self._record("OverrideAuthorised", componentId=active.component_id, recordId=record_id)
        return record

    def abandon(self) -> ComponentProgress:
        """Quit: the active component goes back to PENDING; nothing is recorded for it."""
        active = self._require_active()
        active.state = ComponentState.PENDING
        active.activation = None
        self._record("WeighingAbandoned", componentId=active.component_id)
        return active

    def complete(self, now: datetime) -> bool:
        """Complete the batch. Returns False when it was already completed."""
        if self.status is SessionStatus.COMPLETED:
            return False
        if not self.all_done:
            raise BatchIncomplete(
                f"Batch {self.batch_id} cannot be completed: "
                f"{self.done_count} of {len(self.components)} components weighed.",
                {"done": self.done_count, "total": len(self.components)},
            )
        self.status = SessionStatus.COMPLETED
        self.completed_at = now
        self.sync_status = SyncStatus.PENDING
        self._record("BatchCompleted")
        return True

    def mark_synced(self, consumption_id: str, now: datetime) -> None:
        self.sync_status = SyncStatus.SYNCED
        self.synced_at = now
        self.consumption_id = consumption_id
        self._record("ConsumptionPosted", consumptionId=consumption_id)

    def pull_events(self) -> list[DomainEvent]:
        events, self.events = self.events, []
        return events

    def _require_active(self) -> ComponentProgress:
        if self.status is SessionStatus.COMPLETED:
            raise SessionCompleted(f"Batch {self.batch_id} is already completed.")
        active = self.active
        if active is None:
            raise NoActiveComponent(f"No component is being weighed for {self.batch_id}.")
        return active

    def _make_record(
        self,
        active: ComponentProgress,
        actual: Quantity,
        result: WeighingResult,
        surplus: Quantity | None,
        record_id: str,
        operator_id: str,
        now: datetime,
    ) -> WeighingRecord:
        spec = self.recipe.spec(active.component_id)
        activation = active.activation
        if activation is None:  # an ACTIVE component always has an activation
            raise NoActiveComponent(f"{spec.name} has no weighing context.")
        return WeighingRecord(
            record_id=record_id,
            session_id=self.session_id,
            batch_id=self.batch_id,
            component_id=spec.component_id,
            dyestuff_code=spec.dyestuff_code,
            dyestuff_name=spec.name,
            target=spec.target,
            actual=actual,
            tolerance_min=spec.band.minimum,
            tolerance_max=spec.band.maximum,
            result=result,
            surplus=surplus,
            operator_id=operator_id,
            lot_id=spec.lot_id,
            container_id=activation.container_id,
            tare=activation.tare,
            scale_id=spec.scale.scale_id,
            confirmed_at=now,
        )

    @staticmethod
    def _mark_done(active: ComponentProgress, record: WeighingRecord) -> None:
        active.state = ComponentState.DONE
        active.record_id = record.record_id
        active.actual = record.actual

    def _record(self, name: str, **payload: Any) -> None:
        self.events.append(DomainEvent(name, {"sessionId": self.session_id, **payload}))
