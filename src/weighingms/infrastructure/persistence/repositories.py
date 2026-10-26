"""SQLite repositories for the weighing-station aggregate, station state and audit log."""

import json
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, cast

from sqlalchemy import Engine, delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from weighingms.domain.errors import Conflict, SessionNotFound
from weighingms.domain.quantity import Quantity, Unit
from weighingms.domain.scale_selection import ScaleClass, ScaleDefinition
from weighingms.domain.tolerance import ToleranceBand, ToleranceSource
from weighingms.domain.weighing.records import Override, WeighingRecord, WeighingResult
from weighingms.domain.weighing.session import (
    Activation,
    ComponentProgress,
    ComponentSpec,
    ComponentState,
    RecipeSnapshot,
    SessionStatus,
    SyncStatus,
    WeighingSession,
)
from weighingms.infrastructure.persistence.tables import (
    AuditEventRow,
    OverrideRow,
    PrintJobRow,
    RecordRow,
    SessionComponentRow,
    SessionRow,
    StationStateRow,
)

SNAPSHOT_VERSION = 1


class SessionRepository:
    """Persists the WeighingSession aggregate (one row + one row per component)."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def get(self, session_id: str) -> WeighingSession:
        with Session(self._engine) as db:
            row = db.get(SessionRow, session_id)
            if row is None:
                raise SessionNotFound(f"Weighing session {session_id} does not exist.")
            return _to_domain(row)

    def find_open(self, batch_id: str) -> WeighingSession | None:
        with Session(self._engine) as db:
            row = db.scalars(
                select(SessionRow).where(
                    SessionRow.batch_id == batch_id,
                    SessionRow.status == SessionStatus.IN_PROGRESS,
                )
            ).first()
            return None if row is None else _to_domain(row)

    def add(self, session: WeighingSession) -> None:
        try:
            with Session(self._engine) as db, db.begin():
                db.add(_to_row(session))
        except IntegrityError as exc:
            raise Conflict(
                f"Batch {session.batch_id} already has an open weighing session."
            ) from exc

    def save(self, session: WeighingSession) -> None:
        with Session(self._engine) as db, db.begin():
            db.merge(_to_row(session))

    def save_with_record(
        self, session: WeighingSession, record: WeighingRecord, override: Override | None = None
    ) -> None:
        """Store the new record (and override) together with the session state, atomically."""
        try:
            with Session(self._engine) as db, db.begin():
                db.add(_record_row(record))
                if override is not None:
                    db.flush()
                    db.add(_override_row(override))
                db.merge(_to_row(session))
        except IntegrityError as exc:
            raise Conflict(f"{record.dyestuff_name} has already been recorded.") from exc

    def clear(self) -> None:
        """Training reset: remove all sessions, records and overrides."""
        with Session(self._engine) as db, db.begin():
            db.execute(delete(OverrideRow))
            db.execute(delete(RecordRow))
            db.execute(delete(SessionComponentRow))
            db.execute(delete(SessionRow))


class RecordRepository:
    """Read side of the insert-only weighing records (records are written by save_with_record)."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def for_session(self, session_id: str) -> list[WeighingRecord]:
        return self._query(select(RecordRow).where(RecordRow.session_id == session_id))

    def for_batch(self, batch_id: str) -> list[WeighingRecord]:
        return self._query(select(RecordRow).where(RecordRow.batch_id == batch_id))

    def overrides_for_session(self, session_id: str) -> list[Override]:
        with Session(self._engine) as db:
            rows = db.scalars(
                select(OverrideRow)
                .join(RecordRow, RecordRow.record_id == OverrideRow.record_id)
                .where(RecordRow.session_id == session_id)
            ).all()
            return [
                Override(
                    override_id=r.override_id,
                    record_id=r.record_id,
                    supervisor_id=r.supervisor_id,
                    reason=r.reason,
                    authorised_at=datetime.fromisoformat(r.authorised_at),
                )
                for r in rows
            ]

    def _query(self, query: Any) -> list[WeighingRecord]:
        with Session(self._engine) as db:
            rows = db.scalars(query.order_by(RecordRow.confirmed_at, RecordRow.record_id)).all()
            return [_record_from_row(r) for r in rows]


class PrintLog:
    """Successful ticket prints; the first one per session is the original, later ones reprints."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def add(
        self, session_id: str, ticket_id: str, reprint: bool, operator_id: str, at: datetime
    ) -> None:
        with Session(self._engine) as db, db.begin():
            db.add(
                PrintJobRow(
                    print_id=f"PJ-{uuid.uuid4().hex[:12].upper()}",
                    session_id=session_id,
                    ticket_id=ticket_id,
                    reprint=reprint,
                    operator_id=operator_id,
                    printed_at=at.isoformat(),
                )
            )

    def count_for_session(self, session_id: str) -> int:
        with Session(self._engine) as db:
            count = db.scalar(
                select(func.count())
                .select_from(PrintJobRow)
                .where(PrintJobRow.session_id == session_id)
            )
            return int(count or 0)

    def clear(self) -> None:
        with Session(self._engine) as db, db.begin():
            db.execute(delete(PrintJobRow))


class StationState:
    """Small key/value store for station-wide state (e.g. the current operator)."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def get(self, key: str) -> str | None:
        with Session(self._engine) as db:
            row = db.get(StationStateRow, key)
            return None if row is None else row.value

    def set(self, key: str, value: str) -> None:
        with Session(self._engine) as db, db.begin():
            db.merge(StationStateRow(key=key, value=value))

    def clear(self) -> None:
        with Session(self._engine) as db, db.begin():
            db.execute(delete(StationStateRow))


class AuditLog:
    """Insert-only audit trail (NFR-18)."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def add(
        self,
        event_type: str,
        actor_id: str,
        at: datetime,
        session_id: str | None = None,
        detail: dict[str, Any] | None = None,
    ) -> str:
        event_id = f"AE-{uuid.uuid4().hex[:12].upper()}"
        with Session(self._engine) as db, db.begin():
            db.add(
                AuditEventRow(
                    event_id=event_id,
                    session_id=session_id,
                    type=event_type,
                    actor_id=actor_id,
                    detail=json.dumps(detail or {}),
                    occurred_at=at.isoformat(),
                )
            )
        return event_id

    def events(self, session_id: str | None = None) -> list[dict[str, Any]]:
        with Session(self._engine) as db:
            query = select(AuditEventRow).order_by(AuditEventRow.occurred_at)
            if session_id is not None:
                query = query.where(AuditEventRow.session_id == session_id)
            return [
                {
                    "eventId": r.event_id,
                    "sessionId": r.session_id,
                    "type": r.type,
                    "actorId": r.actor_id,
                    "detail": json.loads(r.detail),
                    "occurredAt": r.occurred_at,
                }
                for r in db.scalars(query)
            ]

    def clear(self) -> None:
        with Session(self._engine) as db, db.begin():
            db.execute(delete(AuditEventRow))


# ── Mapping ────────────────────────────────────────────────────────────────


def _q(value: Decimal | str, unit: str) -> Quantity:
    return Quantity(Decimal(value), cast(Unit, unit))


def _q_json(q: Quantity) -> dict[str, str]:
    return {"value": str(q.value), "unit": q.unit}


def _recipe_json(recipe: RecipeSnapshot) -> str:
    return json.dumps(
        {
            "snapshotVersion": SNAPSHOT_VERSION,
            "recipeId": recipe.recipe_id,
            "version": recipe.version,
            "shadeCode": recipe.shade_code,
            "orderRef": recipe.order_ref,
            "machineRef": recipe.machine_ref,
            "components": [
                {
                    "componentId": c.component_id,
                    "sequence": c.sequence,
                    "dyestuffCode": c.dyestuff_code,
                    "name": c.name,
                    "shortName": c.short_name,
                    "colourHex": c.colour_hex,
                    "target": _q_json(c.target),
                    "plusMinus": _q_json(c.band.plus_minus),
                    "toleranceSource": c.band.source,
                    "scale": {
                        "scaleId": c.scale.scale_id,
                        "scaleClass": c.scale.scale_class,
                        "label": c.scale.label,
                        "stripLabel": c.scale.strip_label,
                    },
                    "lotId": c.lot_id,
                }
                for c in recipe.components
            ],
        }
    )


def _recipe_from_json(text: str) -> RecipeSnapshot:
    data = json.loads(text)
    components = []
    for c in data["components"]:
        target = _q(c["target"]["value"], c["target"]["unit"])
        components.append(
            ComponentSpec(
                component_id=c["componentId"],
                sequence=c["sequence"],
                dyestuff_code=c["dyestuffCode"],
                name=c["name"],
                short_name=c["shortName"],
                colour_hex=c["colourHex"],
                target=target,
                band=ToleranceBand(
                    target,
                    _q(c["plusMinus"]["value"], c["plusMinus"]["unit"]),
                    cast(ToleranceSource, c["toleranceSource"]),
                ),
                scale=ScaleDefinition(
                    scale_id=c["scale"]["scaleId"],
                    scale_class=cast(ScaleClass, c["scale"]["scaleClass"]),
                    label=c["scale"]["label"],
                    strip_label=c["scale"]["stripLabel"],
                ),
                lot_id=c["lotId"],
            )
        )
    return RecipeSnapshot(
        recipe_id=data["recipeId"],
        version=data["version"],
        shade_code=data["shadeCode"],
        order_ref=data["orderRef"],
        machine_ref=data["machineRef"],
        components=tuple(components),
    )


def _dt(value: str | None) -> datetime | None:
    return None if value is None else datetime.fromisoformat(value)


def _iso(value: datetime | None) -> str | None:
    return None if value is None else value.isoformat()


def _to_row(session: WeighingSession) -> SessionRow:
    row = SessionRow(
        session_id=session.session_id,
        batch_id=session.batch_id,
        station_id=session.station_id,
        status=session.status.value,
        started_by=session.started_by,
        started_at=session.started_at.isoformat(),
        completed_at=_iso(session.completed_at),
        sync_status=session.sync_status.value,
        synced_at=_iso(session.synced_at),
        consumption_id=session.consumption_id,
        recipe=_recipe_json(session.recipe),
    )
    row.components = [
        SessionComponentRow(
            session_id=session.session_id,
            component_id=c.component_id,
            sequence=c.sequence,
            state=c.state.value,
            container_id=c.activation.container_id if c.activation else None,
            tare_value=c.activation.tare.value if c.activation else None,
            tare_unit=c.activation.tare.unit if c.activation else None,
            activated_at=c.activation.activated_at.isoformat() if c.activation else None,
            record_id=c.record_id,
            actual_value=c.actual.value if c.actual else None,
            actual_unit=c.actual.unit if c.actual else None,
        )
        for c in session.components
    ]
    return row


def _to_domain(row: SessionRow) -> WeighingSession:
    components = []
    for c in row.components:
        activation = None
        if c.container_id and c.tare_value is not None and c.tare_unit and c.activated_at:
            activation = Activation(
                container_id=c.container_id,
                tare=_q(c.tare_value, c.tare_unit),
                activated_at=datetime.fromisoformat(c.activated_at),
            )
        components.append(
            ComponentProgress(
                component_id=c.component_id,
                sequence=c.sequence,
                state=ComponentState(c.state),
                activation=activation,
                record_id=c.record_id,
                actual=_q(c.actual_value, c.actual_unit)
                if c.actual_value is not None and c.actual_unit
                else None,
            )
        )
    return WeighingSession(
        session_id=row.session_id,
        batch_id=row.batch_id,
        station_id=row.station_id,
        recipe=_recipe_from_json(row.recipe),
        started_by=row.started_by,
        started_at=datetime.fromisoformat(row.started_at),
        components=components,
        status=SessionStatus(row.status),
        completed_at=_dt(row.completed_at),
        sync_status=SyncStatus(row.sync_status),
        synced_at=_dt(row.synced_at),
        consumption_id=row.consumption_id,
    )


def _record_row(r: WeighingRecord) -> RecordRow:
    unit = r.target.unit
    return RecordRow(
        record_id=r.record_id,
        session_id=r.session_id,
        batch_id=r.batch_id,
        component_id=r.component_id,
        dyestuff_code=r.dyestuff_code,
        dyestuff_name=r.dyestuff_name,
        unit=unit,
        target_value=r.target.value,
        actual_value=r.actual.to(unit).value,
        tolerance_min=r.tolerance_min.to(unit).value,
        tolerance_max=r.tolerance_max.to(unit).value,
        result=r.result,
        surplus_value=r.surplus.to(unit).value if r.surplus else None,
        operator_id=r.operator_id,
        lot_id=r.lot_id,
        container_id=r.container_id,
        tare_value=r.tare.value,
        tare_unit=r.tare.unit,
        scale_id=r.scale_id,
        confirmed_at=r.confirmed_at.isoformat(),
    )


def _record_from_row(row: RecordRow) -> WeighingRecord:
    unit = row.unit
    return WeighingRecord(
        record_id=row.record_id,
        session_id=row.session_id,
        batch_id=row.batch_id,
        component_id=row.component_id,
        dyestuff_code=row.dyestuff_code,
        dyestuff_name=row.dyestuff_name,
        target=_q(row.target_value, unit),
        actual=_q(row.actual_value, unit),
        tolerance_min=_q(row.tolerance_min, unit),
        tolerance_max=_q(row.tolerance_max, unit),
        result=cast(WeighingResult, row.result),
        surplus=_q(row.surplus_value, unit) if row.surplus_value is not None else None,
        operator_id=row.operator_id,
        lot_id=row.lot_id,
        container_id=row.container_id,
        tare=_q(row.tare_value, row.tare_unit),
        scale_id=row.scale_id,
        confirmed_at=datetime.fromisoformat(row.confirmed_at),
    )


def _override_row(o: Override) -> OverrideRow:
    return OverrideRow(
        override_id=o.override_id,
        record_id=o.record_id,
        supervisor_id=o.supervisor_id,
        reason=o.reason,
        authorised_at=o.authorised_at.isoformat(),
    )
