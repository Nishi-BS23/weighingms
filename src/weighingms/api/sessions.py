"""Weighing-session endpoints used by Screen 2 (FR-2, FR-5 – FR-12, FR-15)."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query, Response, status
from pydantic import Field

from weighingms.api.container import Container, get_container
from weighingms.api.schemas import ApiModel, QuantityOut, ScaleOut, ToleranceOut
from weighingms.application.sessions import LiveReading
from weighingms.application.summary import summarise
from weighingms.domain.weighing.evaluation import display_max
from weighingms.domain.weighing.records import WeighingRecord
from weighingms.domain.weighing.session import ComponentSpec, WeighingSession

router = APIRouter(prefix="/api/sessions", tags=["Weighing sessions"])


class StartSessionIn(ApiModel):
    batch_id: str


class ProgressOut(ApiModel):
    done: int
    total: int


class SessionComponentOut(ApiModel):
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
    state: str
    actual: QuantityOut | None


class ActiveOut(ApiModel):
    component_id: str
    container_id: str
    tare: QuantityOut
    display_max: QuantityOut


class SessionOut(ApiModel):
    session_id: str
    batch_id: str
    order_ref: str
    machine_ref: str
    shade_code: str
    recipe_id: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    sync_status: str
    synced_at: datetime | None
    progress: ProgressOut
    active_component_id: str | None
    active: ActiveOut | None
    components: list[SessionComponentOut]


class LiveOut(ApiModel):
    session_id: str
    component_id: str
    scale_id: str
    zone: str
    net: QuantityOut | None
    remaining: QuantityOut
    surplus: QuantityOut | None
    surplus_pct: str | None
    can_confirm: bool
    scale_available: bool
    calibration_valid: bool
    stable: bool
    status_text: str
    allowed_actions: list[str]
    guidance: str | None


class OverrideIn(ApiModel):
    supervisor_pin: str = Field(min_length=1, max_length=32)
    reason: str = Field(min_length=1, max_length=500)


class RecordOut(ApiModel):
    record_id: str
    session_id: str
    batch_id: str
    component_id: str
    dyestuff_code: str
    dyestuff_name: str
    target: QuantityOut
    actual: QuantityOut
    tolerance_min: QuantityOut
    tolerance_max: QuantityOut
    result: str
    surplus: QuantityOut | None
    operator_id: str
    lot_id: str
    container_id: str
    tare: QuantityOut
    scale_id: str
    confirmed_at: datetime

    @classmethod
    def of(cls, r: WeighingRecord) -> "RecordOut":
        return cls(
            record_id=r.record_id,
            session_id=r.session_id,
            batch_id=r.batch_id,
            component_id=r.component_id,
            dyestuff_code=r.dyestuff_code,
            dyestuff_name=r.dyestuff_name,
            target=QuantityOut.of(r.target),
            actual=QuantityOut.of(r.actual),
            tolerance_min=QuantityOut.of(r.tolerance_min),
            tolerance_max=QuantityOut.of(r.tolerance_max),
            result=r.result,
            surplus=QuantityOut.of(r.surplus) if r.surplus else None,
            operator_id=r.operator_id,
            lot_id=r.lot_id,
            container_id=r.container_id,
            tare=QuantityOut.of(r.tare),
            scale_id=r.scale_id,
            confirmed_at=r.confirmed_at,
        )


class ResultOut(ApiModel):
    component_id: str
    sequence: int
    name: str
    short_name: str
    target: QuantityOut
    actual: QuantityOut | None
    result: str | None


class WriteBackOut(ApiModel):
    status: str
    at: datetime | None
    consumption_id: str | None


class SummaryOut(ApiModel):
    session_id: str
    batch_id: str
    order_ref: str
    machine_ref: str
    shade_code: str
    completed: bool
    completed_at: datetime | None
    components_weighed: ProgressOut
    all_within_tolerance: bool
    overridden_count: int
    total_dispensed: QuantityOut
    elapsed_seconds: int
    elapsed_text: str
    operator_name: str
    write_back: WriteBackOut
    results: list[ResultOut]


def tolerance_out(spec: ComponentSpec) -> ToleranceOut:
    return ToleranceOut(
        plus_minus=QuantityOut.of(spec.band.plus_minus),
        minimum=QuantityOut.of(spec.band.minimum),
        maximum=QuantityOut.of(spec.band.maximum),
        source=spec.band.source,
    )


def session_out(session: WeighingSession) -> SessionOut:
    recipe = session.recipe
    components = []
    for progress in session.components:
        spec = recipe.spec(progress.component_id)
        components.append(
            SessionComponentOut(
                component_id=spec.component_id,
                sequence=spec.sequence,
                dyestuff_code=spec.dyestuff_code,
                name=spec.name,
                short_name=spec.short_name,
                colour_hex=spec.colour_hex,
                target=QuantityOut.of(spec.target),
                tolerance=tolerance_out(spec),
                scale=ScaleOut.of(spec.scale),
                lot_id=spec.lot_id,
                state=progress.state.value,
                actual=QuantityOut.of(progress.actual) if progress.actual else None,
            )
        )
    active = session.active
    active_out = None
    if active is not None and active.activation is not None:
        spec = recipe.spec(active.component_id)
        active_out = ActiveOut(
            component_id=active.component_id,
            container_id=active.activation.container_id,
            tare=QuantityOut.of(active.activation.tare.to(spec.target.unit)),
            display_max=QuantityOut.of(display_max(spec.band)),
        )
    return SessionOut(
        session_id=session.session_id,
        batch_id=session.batch_id,
        order_ref=recipe.order_ref,
        machine_ref=recipe.machine_ref,
        shade_code=recipe.shade_code,
        recipe_id=recipe.recipe_id,
        status=session.status.value,
        started_at=session.started_at,
        completed_at=session.completed_at,
        sync_status=session.sync_status.value,
        synced_at=session.synced_at,
        progress=ProgressOut(done=session.done_count, total=len(session.components)),
        active_component_id=active.component_id if active else None,
        active=active_out,
        components=components,
    )


def live_out(live: LiveReading) -> LiveOut:
    e = live.evaluation
    return LiveOut(
        session_id=live.session_id,
        component_id=live.spec.component_id,
        scale_id=live.spec.scale.scale_id,
        zone=e.zone.value,
        net=QuantityOut.of(e.net) if e.net else None,
        remaining=QuantityOut.of(e.remaining),
        surplus=QuantityOut.of(e.surplus) if e.surplus else None,
        surplus_pct=str(e.surplus_pct) if e.surplus_pct is not None else None,
        can_confirm=e.can_confirm,
        scale_available=e.scale_available,
        calibration_valid=e.calibration_valid,
        stable=e.stable,
        status_text=e.status_text,
        allowed_actions=[a.value for a in e.allowed_actions],
        guidance=e.guidance,
    )


@router.post("", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def start_session(
    body: StartSessionIn, response: Response, container: Container = Depends(get_container)
) -> SessionOut:
    session, created = container.sessions.start_or_resume(body.batch_id)
    if not created:
        response.status_code = status.HTTP_200_OK
    return session_out(session)


@router.get("/{session_id}", response_model=SessionOut)
def get_session(session_id: str, container: Container = Depends(get_container)) -> SessionOut:
    return session_out(container.sessions.get(session_id))


@router.post("/{session_id}/components/{component_id}/activate", response_model=SessionOut)
def activate(
    session_id: str, component_id: str, container: Container = Depends(get_container)
) -> SessionOut:
    return session_out(container.sessions.activate(session_id, component_id))


@router.get("/{session_id}/live", response_model=LiveOut)
def live(session_id: str, container: Container = Depends(get_container)) -> LiveOut:
    return live_out(container.sessions.live(session_id))


@router.post("/{session_id}/retare", response_model=LiveOut)
def retare(session_id: str, container: Container = Depends(get_container)) -> LiveOut:
    return live_out(container.sessions.retare(session_id))


@router.post("/{session_id}/confirm", response_model=SessionOut)
def confirm(session_id: str, container: Container = Depends(get_container)) -> SessionOut:
    return session_out(container.sessions.confirm(session_id))


@router.post("/{session_id}/override", response_model=SessionOut)
def override(
    session_id: str, body: OverrideIn, container: Container = Depends(get_container)
) -> SessionOut:
    session = container.sessions.override(session_id, body.supervisor_pin, body.reason.strip())
    return session_out(session)


@router.post("/{session_id}/quit", response_model=SessionOut)
def quit_component(session_id: str, container: Container = Depends(get_container)) -> SessionOut:
    return session_out(container.sessions.quit(session_id))


@router.post("/{session_id}/complete", response_model=SessionOut)
def complete(session_id: str, container: Container = Depends(get_container)) -> SessionOut:
    return session_out(container.sessions.complete(session_id))


@router.post("/{session_id}/sync", response_model=SessionOut)
def sync(session_id: str, container: Container = Depends(get_container)) -> SessionOut:
    return session_out(container.sessions.sync(session_id))


@router.get("/{session_id}/summary", response_model=SummaryOut)
def summary(session_id: str, container: Container = Depends(get_container)) -> SummaryOut:
    session = container.sessions.get(session_id)
    s = summarise(
        session,
        container.sessions.records_for_session(session_id),
        container.settings.station.operators,
        container.clock(),
    )
    recipe = session.recipe
    return SummaryOut(
        session_id=session.session_id,
        batch_id=session.batch_id,
        order_ref=recipe.order_ref,
        machine_ref=recipe.machine_ref,
        shade_code=recipe.shade_code,
        completed=session.status.value == "COMPLETED",
        completed_at=session.completed_at,
        components_weighed=ProgressOut(done=session.done_count, total=len(session.components)),
        all_within_tolerance=s.all_within_tolerance,
        overridden_count=s.overridden_count,
        total_dispensed=QuantityOut.of(s.total_dispensed),
        elapsed_seconds=s.elapsed_seconds,
        elapsed_text=s.elapsed_text,
        operator_name=s.operator_name,
        write_back=WriteBackOut(
            status=session.sync_status.value,
            at=session.synced_at,
            consumption_id=session.consumption_id,
        ),
        results=[
            ResultOut(
                component_id=r.spec.component_id,
                sequence=r.spec.sequence,
                name=r.spec.name,
                short_name=r.spec.short_name,
                target=QuantityOut.of(r.spec.target),
                actual=QuantityOut.of(r.record.actual) if r.record else None,
                result=r.record.result if r.record else None,
            )
            for r in s.results
        ],
    )


records_router = APIRouter(prefix="/api/weighing-records", tags=["Weighing records"])


@records_router.get("", response_model=list[RecordOut])
def weighing_records(
    batch_id: str = Query(alias="batchId", min_length=1),
    container: Container = Depends(get_container),
) -> list[RecordOut]:
    return [RecordOut.of(r) for r in container.sessions.records_for_batch(batch_id)]
