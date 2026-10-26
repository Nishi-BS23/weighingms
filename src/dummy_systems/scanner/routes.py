"""Dummy Scanner endpoints — training contract."""

from fastapi import APIRouter, Depends, Query

from dummy_systems.common.models import DeviceStatus
from dummy_systems.control.availability import Availability
from dummy_systems.scanner.queue import Scan, ScanBatch, ScanQueue, ScanRequest


def build_router(queue: ScanQueue, availability: Availability) -> APIRouter:
    router = APIRouter(
        prefix="/api/scanner",
        tags=["Dummy Scanner (training contract)"],
        dependencies=[Depends(availability.dependency("scanner"))],
    )

    @router.post("/scans", response_model=Scan)
    def scan(request: ScanRequest) -> Scan:
        return queue.add(request.code)

    @router.get("/scans", response_model=ScanBatch)
    def scans(after: int = Query(0, ge=0)) -> ScanBatch:
        return queue.after(after)

    @router.get("/status", response_model=DeviceStatus)
    def status() -> DeviceStatus:
        return DeviceStatus(available=True)

    return router
