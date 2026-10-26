"""Training endpoints (training build only): drive the training substitutes from the UI panel."""

from datetime import date
from typing import Any, Literal

from fastapi import APIRouter, Depends
from pydantic import Field

from weighingms.api.container import Container, get_container
from weighingms.api.devices import ScanOut
from weighingms.api.schemas import ApiModel, QuantityOut
from weighingms.domain.quantity import Quantity, Unit

router = APIRouter(prefix="/api/training", tags=["Training (training build only)"])


class ScanIn(ApiModel):
    code: str = Field(min_length=1, max_length=64)


class AvailabilityOut(ApiModel):
    systems: dict[str, bool]


class AvailabilityIn(ApiModel):
    available: bool


class QuantityIn(ApiModel):
    # A weight placed on a scale: a non-negative decimal string, never a float.
    value: str = Field(pattern=r"^\d{1,6}(\.\d{1,4})?$", examples=["94.2"])
    unit: Unit


class SimulateIn(ApiModel):
    profile: Literal["dispense", "overshoot", "below", "exact"]
    net: QuantityIn


class CalibrationIn(ApiModel):
    calibration_due: date


class ResetOut(ApiModel):
    reset: bool


class SessionSimulateIn(ApiModel):
    session_id: str
    kind: Literal["dispense", "overshoot", "below"]


class SessionSimulateOut(ApiModel):
    landing: QuantityOut


class ResetWeighingIn(ApiModel):
    session_id: str


@router.post("/scan", response_model=ScanOut)
def scan(body: ScanIn, container: Container = Depends(get_container)) -> ScanOut:
    event = container.training.scan(body.code)
    return ScanOut(seq=event.seq, code=event.code, scanned_at=event.scanned_at)


@router.get("/availability", response_model=AvailabilityOut)
def availability(container: Container = Depends(get_container)) -> AvailabilityOut:
    return AvailabilityOut(systems=container.training.availability())


@router.put("/availability/{system}", response_model=AvailabilityOut)
def set_availability(
    system: str, body: AvailabilityIn, container: Container = Depends(get_container)
) -> AvailabilityOut:
    return AvailabilityOut(systems=container.training.set_availability(system, body.available))


@router.post("/reset", response_model=ResetOut)
def reset(container: Container = Depends(get_container)) -> ResetOut:
    container.training.reset()
    for hook in container.reset_hooks:
        hook()
    return ResetOut(reset=True)


@router.post("/scales/{scale_id}/simulate")
def simulate(
    scale_id: str, body: SimulateIn, container: Container = Depends(get_container)
) -> dict[str, Any]:
    net = Quantity.of(body.net.value, body.net.unit)
    return container.training.simulate(scale_id, body.profile, net)


@router.put("/scales/{scale_id}/calibration")
def set_calibration(
    scale_id: str, body: CalibrationIn, container: Container = Depends(get_container)
) -> dict[str, Any]:
    return container.training.set_calibration(scale_id, body.calibration_due)


@router.post("/simulate", response_model=SessionSimulateOut)
def simulate_active(
    body: SessionSimulateIn, container: Container = Depends(get_container)
) -> SessionSimulateOut:
    """Prototype "Simulate dispense / overshoot": landing computed from the active component."""
    landing = container.training_service.simulate(body.session_id, body.kind)
    return SessionSimulateOut(landing=QuantityOut.of(landing))


@router.post("/reset-weighing", response_model=ResetOut)
def reset_weighing(
    body: ResetWeighingIn, container: Container = Depends(get_container)
) -> ResetOut:
    """Prototype "Reset": take the dispensed material off the active scale."""
    container.training_service.reset_weighing(body.session_id)
    return ResetOut(reset=True)
