"""Dummy Scale endpoints — training contract, not a real indicator protocol."""

from fastapi import APIRouter

from dummy_systems.common.models import Quantity
from dummy_systems.control.availability import Availability
from dummy_systems.scale.bank import ScaleBank
from dummy_systems.scale.models import ScaleInfo, ScaleReading, ScaleStatus


def build_router(bank: ScaleBank, availability: Availability) -> APIRouter:
    router = APIRouter(prefix="/api/scales", tags=["Dummy Scale (training contract)"])

    @router.get("", response_model=list[ScaleInfo])
    def list_scales() -> list[ScaleInfo]:
        return [
            ScaleInfo(
                scale_id=s.scale_id,
                scale_class=s.scale_class,
                label=s.label,
                capacity=Quantity(value=s.capacity_kg, unit="kg"),
                resolution=Quantity(value=s.resolution, unit=s.unit),
                available=availability.is_available(s.scale_id),
                calibration_due=bank.calibration_due(s.scale_id),
            )
            for s in bank.specs()
        ]

    @router.get("/{scale_id}/status", response_model=ScaleStatus)
    def status(scale_id: str) -> ScaleStatus:
        due = bank.calibration_due(scale_id)
        availability.ensure(scale_id)
        return ScaleStatus(
            scale_id=scale_id,
            available=availability.is_available(scale_id),
            calibration_due=due,
            calibration_valid=bank.calibration_valid(scale_id),
            simulating=bank.simulating(scale_id),
        )

    @router.get("/{scale_id}/weight", response_model=ScaleReading)
    def weight(scale_id: str) -> ScaleReading:
        bank.calibration_due(scale_id)  # 404 for unknown scales before the 503 check
        availability.ensure(scale_id)
        return bank.reading(scale_id)

    @router.post("/{scale_id}/tare", response_model=ScaleReading)
    def tare(scale_id: str) -> ScaleReading:
        bank.calibration_due(scale_id)
        availability.ensure(scale_id)
        return bank.tare(scale_id)

    return router
