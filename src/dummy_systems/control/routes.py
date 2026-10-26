"""Training control endpoints: failure injection, scale simulation, reset.

These have no real-world counterpart and are never affected by availability toggles.
"""

from collections.abc import Callable

from fastapi import APIRouter

from dummy_systems.common.models import ApiModel
from dummy_systems.control.availability import Availability
from dummy_systems.scale.bank import ScaleBank
from dummy_systems.scale.models import (
    CalibrationUpdate,
    LoadRequest,
    ScaleStatus,
    SimulationRequest,
)


class AvailabilityState(ApiModel):
    systems: dict[str, bool]


class AvailabilityUpdate(ApiModel):
    available: bool


class ResetResult(ApiModel):
    reset: bool


def build_router(
    availability: Availability, bank: ScaleBank, reset_all: Callable[[], None]
) -> APIRouter:
    router = APIRouter(prefix="/api/control", tags=["Training control (training only)"])

    def scale_status(scale_id: str) -> ScaleStatus:
        return ScaleStatus(
            scale_id=scale_id,
            available=availability.is_available(scale_id),
            calibration_due=bank.calibration_due(scale_id),
            calibration_valid=bank.calibration_valid(scale_id),
            simulating=bank.simulating(scale_id),
        )

    @router.get("/availability", response_model=AvailabilityState)
    def get_availability() -> AvailabilityState:
        return AvailabilityState(systems=availability.snapshot())

    @router.put("/availability/{system}", response_model=AvailabilityState)
    def set_availability(system: str, update: AvailabilityUpdate) -> AvailabilityState:
        availability.set(system, update.available)
        return AvailabilityState(systems=availability.snapshot())

    @router.post("/scales/{scale_id}/simulate", response_model=ScaleStatus)
    def simulate(scale_id: str, request: SimulationRequest) -> ScaleStatus:
        bank.simulate(scale_id, request.profile, request.net)
        return scale_status(scale_id)

    @router.post("/scales/{scale_id}/load", response_model=ScaleStatus)
    def load(scale_id: str, request: LoadRequest) -> ScaleStatus:
        bank.place(scale_id, request.gross)
        return scale_status(scale_id)

    @router.put("/scales/{scale_id}/calibration", response_model=ScaleStatus)
    def set_calibration(scale_id: str, update: CalibrationUpdate) -> ScaleStatus:
        bank.set_calibration(scale_id, update.calibration_due)
        return scale_status(scale_id)

    @router.post("/reset", response_model=ResetResult)
    def reset() -> ResetResult:
        reset_all()
        return ResetResult(reset=True)

    return router
