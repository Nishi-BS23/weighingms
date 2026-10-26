"""Weighing-session use cases: start/resume, activate, live evaluation, re-tare, confirm,
supervisor override, quit, completion with OrgaTEX write-back."""

import logging
import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass

from weighingms.application.batches import BatchService, StationRecipe
from weighingms.application.operators import OperatorService
from weighingms.application.ports import (
    AuditStore,
    ConsumptionLine,
    ConsumptionPayload,
    OrgatexPort,
    RecordStore,
    ScalePort,
    ScaleUnavailable,
    SessionStore,
)
from weighingms.clock import Clock, Ticker, monotonic, utc_now
from weighingms.config import StationConfig
from weighingms.domain.errors import (
    BatchNotSelectable,
    DomainError,
    NoActiveComponent,
    OverrideNotAuthorised,
    SessionCompleted,
)
from weighingms.domain.quantity import Quantity
from weighingms.domain.weighing.evaluation import Evaluation, evaluate
from weighingms.domain.weighing.records import Override, WeighingRecord
from weighingms.domain.weighing.session import (
    Activation,
    ComponentSpec,
    RecipeSnapshot,
    SessionStatus,
    SyncStatus,
    WeighingSession,
)

log = logging.getLogger("weighingms.sessions")

CALIBRATION_CACHE_SECONDS = 2.0


@dataclass(frozen=True)
class LiveReading:
    """Evaluation of the active component's scale, for the weighing panel."""

    session_id: str
    spec: ComponentSpec
    evaluation: Evaluation


class SessionService:
    def __init__(
        self,
        sessions: SessionStore,
        records: RecordStore,
        audit: AuditStore,
        batches: BatchService,
        operators: OperatorService,
        orgatex: OrgatexPort,
        scales: ScalePort,
        station: StationConfig,
        clock: Clock = utc_now,
        ticker: Ticker = monotonic,
        container_placed: Callable[[str, Quantity], None] | None = None,
    ) -> None:
        """`container_placed` (training mode only) simulates the operator swapping in the new
        component's empty container before the scale is tared."""
        self._container_placed = container_placed
        self._sessions = sessions
        self._records = records
        self._audit = audit
        self._batches = batches
        self._operators = operators
        self._orgatex = orgatex
        self._scales = scales
        self._station = station
        self._clock = clock
        self._ticker = ticker
        self._lock = threading.RLock()
        self._calibration: dict[str, tuple[float, bool]] = {}

    # ── Commands ───────────────────────────────────────────────────────────

    def start_or_resume(self, batch_id: str) -> tuple[WeighingSession, bool]:
        """Return the batch's open session, or start one. The bool is True when started."""
        with self._lock:
            existing = self._sessions.find_open(batch_id)
            if existing is not None:
                if existing.active is None:
                    self._activate_next(existing)
                    self._sessions.save(existing)
                log.info(
                    "Session %s resumed for %s (%s of %s done)",
                    existing.session_id,
                    batch_id,
                    existing.done_count,
                    len(existing.components),
                )
                return existing, False

            batch = self._batches.batch(batch_id)
            if not batch.selectable:
                raise BatchNotSelectable(
                    f"Batch {batch_id} cannot be weighed: {batch.not_selectable_reason}",
                    {"batchId": batch_id, "status": batch.batch.status},
                )
            recipe = self._batches.recipe(batch_id)
            session = WeighingSession.start(
                session_id=_new_id("WS"),
                batch_id=batch_id,
                station_id=self._station.station_id,
                recipe=_snapshot(recipe, batch.batch.order_ref, batch.batch.machine_ref),
                operator_id=self._operators.current().operator_id,
                now=self._clock(),
            )
            self._activate_next(session)
            self._sessions.add(session)
            self._write_back_status(batch_id)
            log.info("Session %s started for %s", session.session_id, batch_id)
            return session, True

    def activate(self, session_id: str, component_id: str) -> WeighingSession:
        with self._lock:
            session = self._sessions.get(session_id)
            spec = session.recipe.spec(component_id)
            session.activate(component_id, self._activation(spec))
            self._sessions.save(session)
            return session

    def confirm(self, session_id: str) -> WeighingSession:
        """Record the active component if — on a fresh reading — it is within tolerance."""
        with self._lock:
            session = self._sessions.get(session_id)
            evaluation = self._fresh_evaluation(session)
            record = session.confirm(
                evaluation, _new_id("WR"), self._operators.current().operator_id, self._clock()
            )
            self._finish_component(session, record)
            log.info(
                "Confirmed %s %s %s on %s",
                record.component_id,
                record.actual.display(),
                record.actual.unit,
                record.scale_id,
            )
            return self._after_completion(session)

    def override(self, session_id: str, supervisor_pin: str, reason: str) -> WeighingSession:
        """Accept a weighing outside tolerance on supervisor authority (FR-21, Step 24)."""
        with self._lock:
            supervisor = self._operators.supervisor_for_pin(supervisor_pin)
            if supervisor is None:
                log.warning("Override refused for %s: PIN not accepted", session_id)
                raise OverrideNotAuthorised("The supervisor PIN was not accepted.")
            session = self._sessions.get(session_id)
            spec = self._active_spec(session)
            evaluation = self._fresh_evaluation(session, require_calibration=False)
            now = self._clock()
            record = session.override(
                evaluation, _new_id("WR"), self._operators.current().operator_id, now
            )
            override = Override(
                _new_id("OV"), record.record_id, supervisor.operator_id, reason, now
            )
            self._finish_component(session, record, override)
            self._audit.add(
                "OVERRIDE",
                supervisor.operator_id,
                now,
                session_id=session.session_id,
                detail={
                    "componentId": spec.component_id,
                    "actual": record.actual.display(),
                    "unit": record.actual.unit,
                    "band": [spec.band.minimum.display(), spec.band.maximum.display()],
                    "zone": evaluation.zone.value,
                    "reason": reason,
                    "recordId": record.record_id,
                },
            )
            log.info("Override by %s on %s", supervisor.operator_id, spec.component_id)
            return self._after_completion(session)

    def quit(self, session_id: str) -> WeighingSession:
        """Abandon the active component and leave the batch (FR-22). Nothing is recorded."""
        with self._lock:
            session = self._sessions.get(session_id)
            spec = self._active_spec(session)
            try:
                net = self._scales.read_weight(spec.scale.scale_id).net.to(spec.target.unit)
                net_text: str | None = net.display()
            except ScaleUnavailable:
                net_text = None
            session.abandon()
            self._sessions.save(session)
            self._audit.add(
                "ABANDON",
                self._operators.current().operator_id,
                self._clock(),
                session_id=session.session_id,
                detail={"componentId": spec.component_id, "netAtQuit": net_text},
            )
            log.info("Weighing of %s abandoned (net %s)", spec.component_id, net_text)
            return session

    def complete(self, session_id: str) -> WeighingSession:
        with self._lock:
            session = self._sessions.get(session_id)
            if session.complete(self._clock()):
                self._sessions.save(session)
                self._write_back(session)
            return session

    def sync(self, session_id: str) -> WeighingSession:
        """Retry the OrgaTEX write-back of a completed batch (TA-13)."""
        with self._lock:
            session = self._sessions.get(session_id)
            if (
                session.status is SessionStatus.COMPLETED
                and session.sync_status is not SyncStatus.SYNCED
            ):
                self._write_back(session)
            return session

    def retare(self, session_id: str) -> LiveReading:
        session = self._sessions.get(session_id)
        spec = self._active_spec(session)
        self._scales.tare(spec.scale.scale_id)
        return self.live(session_id)

    # ── Queries ────────────────────────────────────────────────────────────

    def get(self, session_id: str) -> WeighingSession:
        return self._sessions.get(session_id)

    def live(self, session_id: str) -> LiveReading:
        session = self._sessions.get(session_id)
        spec = self._active_spec(session)
        scale_id = spec.scale.scale_id
        try:
            reading = self._scales.read_weight(scale_id)
        except ScaleUnavailable:
            evaluation = evaluate(spec.band, None)
        else:
            evaluation = evaluate(
                spec.band,
                reading.net,
                calibration_valid=self._calibration_valid(scale_id),
                stable=reading.stable,
            )
        return LiveReading(session_id=session.session_id, spec=spec, evaluation=evaluation)

    def records_for_session(self, session_id: str) -> list[WeighingRecord]:
        return self._records.for_session(session_id)

    def records_for_batch(self, batch_id: str) -> list[WeighingRecord]:
        return self._records.for_batch(batch_id)

    def overrides_for_session(self, session_id: str) -> list[Override]:
        return self._records.overrides_for_session(session_id)

    def clear(self) -> None:
        """Training reset: forget all sessions."""
        with self._lock:
            self._sessions.clear()
            self._calibration.clear()

    # ── Internals ──────────────────────────────────────────────────────────

    def _fresh_evaluation(
        self, session: WeighingSession, require_calibration: bool = True
    ) -> Evaluation:
        """Re-read the scale now; never trust a weight sent by the UI (FR-13)."""
        spec = self._active_spec(session)
        reading = self._scales.read_weight(spec.scale.scale_id)  # ScaleUnavailable → 503
        calibration_valid = True
        if require_calibration:
            calibration_valid = self._scales.status(spec.scale.scale_id).calibration_valid
        return evaluate(
            spec.band, reading.net, calibration_valid=calibration_valid, stable=reading.stable
        )

    def _finish_component(
        self, session: WeighingSession, record: WeighingRecord, override: Override | None = None
    ) -> None:
        """Move on to the next component (or complete) and store everything in one transaction."""
        if session.all_done:
            session.complete(self._clock())
        else:
            self._activate_next(session)
        self._sessions.save_with_record(session, record, override)

    def _after_completion(self, session: WeighingSession) -> WeighingSession:
        if session.status is SessionStatus.COMPLETED and session.sync_status is SyncStatus.PENDING:
            log.info("Batch %s completed", session.batch_id)
            self._write_back(session)
        return session

    def _write_back(self, session: WeighingSession) -> None:
        """Post actual consumption to OrgaTEX, idempotently (key = session ID)."""
        sequence = {c.component_id: c.sequence for c in session.recipe.components}
        records = sorted(
            self._records.for_session(session.session_id), key=lambda r: sequence[r.component_id]
        )
        payload = ConsumptionPayload(
            batch_id=session.batch_id,
            idempotency_key=session.session_id,
            session_id=session.session_id,
            station_id=session.station_id,
            operator_id=session.started_by,
            completed_at=session.completed_at or self._clock(),
            lines=[
                ConsumptionLine(
                    component_id=r.component_id,
                    dyestuff_code=r.dyestuff_code,
                    lot_id=r.lot_id,
                    target=r.target,
                    actual=r.actual,
                    scale_id=r.scale_id,
                    operator_id=r.operator_id,
                    confirmed_at=r.confirmed_at,
                    result=r.result,
                )
                for r in records
            ],
        )
        try:
            ack = self._orgatex.post_consumption(payload)
        except DomainError as exc:
            log.warning("Write-back of %s pending: %s", session.batch_id, exc.code)
            return
        session.mark_synced(ack.consumption_id, self._clock())
        self._sessions.save(session)
        log.info(
            "Consumption for %s written to OrgaTEX (%s%s)",
            session.batch_id,
            ack.consumption_id,
            ", duplicate" if ack.duplicate else "",
        )
        try:
            self._orgatex.set_batch_status(session.batch_id, "WEIGHED")
        except DomainError as exc:
            log.warning("Could not set %s to WEIGHED in OrgaTEX: %s", session.batch_id, exc.code)

    def _activate_next(self, session: WeighingSession) -> None:
        pending = session.next_pending()
        if pending is not None:
            spec = session.recipe.spec(pending.component_id)
            session.activate(pending.component_id, self._activation(spec))

    def _activation(self, spec: ComponentSpec) -> Activation:
        """Choose the container and tare the selected scale so 'Weighed now' starts at zero."""
        container = self._station.containers.container_for(
            spec.dyestuff_code, spec.scale.scale_class
        )
        if self._container_placed is not None:
            try:
                self._container_placed(spec.scale.scale_id, container.tare)
            except DomainError as exc:
                log.warning(
                    "Training: could not place container on %s: %s", spec.scale.scale_id, exc.code
                )
        try:
            self._scales.tare(spec.scale.scale_id)
        except ScaleUnavailable:
            log.warning("Could not tare %s for %s", spec.scale.scale_id, spec.component_id)
        return Activation(
            container_id=container.container_id, tare=container.tare, activated_at=self._clock()
        )

    @staticmethod
    def _active_spec(session: WeighingSession) -> ComponentSpec:
        if session.status is SessionStatus.COMPLETED:
            raise SessionCompleted(f"Batch {session.batch_id} is already completed.")
        active = session.active
        if active is None:
            raise NoActiveComponent(f"No component is being weighed for {session.batch_id}.")
        return session.recipe.spec(active.component_id)

    def _calibration_valid(self, scale_id: str) -> bool:
        now = self._ticker()
        cached = self._calibration.get(scale_id)
        if cached and now - cached[0] < CALIBRATION_CACHE_SECONDS:
            return cached[1]
        try:
            valid = self._scales.status(scale_id).calibration_valid
        except ScaleUnavailable:
            valid = True  # availability is judged by the weight read itself
        self._calibration[scale_id] = (now, valid)
        return valid

    def _write_back_status(self, batch_id: str) -> None:
        try:
            self._orgatex.set_batch_status(batch_id, "WEIGHING")
        except DomainError as exc:
            log.warning("Could not set %s to WEIGHING in OrgaTEX: %s", batch_id, exc.code)


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


def _snapshot(recipe: StationRecipe, order_ref: str, machine_ref: str) -> RecipeSnapshot:
    return RecipeSnapshot(
        recipe_id=recipe.recipe_id,
        version=recipe.version,
        shade_code=recipe.shade_code,
        order_ref=order_ref,
        machine_ref=machine_ref,
        components=tuple(
            ComponentSpec(
                component_id=c.component_id,
                sequence=c.sequence,
                dyestuff_code=c.dyestuff_code,
                name=c.name,
                short_name=c.short_name,
                colour_hex=c.colour_hex,
                target=c.target,
                band=c.band,
                scale=c.scale,
                lot_id=c.lot_id,
            )
            for c in recipe.components
        ),
    )
