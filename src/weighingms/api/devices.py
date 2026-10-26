"""Device status and scanner endpoints (FR-24, FR-20, FR-2 scan path)."""

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query

from weighingms.api.container import Container, get_container
from weighingms.api.schemas import ApiModel

router = APIRouter(tags=["Devices"])


class DeviceOut(ApiModel):
    device: str
    label: str
    state: Literal["UP", "DOWN", "DEGRADED"]
    text: str


class DeviceStatusOut(ApiModel):
    checked_at: datetime
    station_name: str
    language: str
    orgatex_last_contact: datetime | None
    devices: list[DeviceOut]


class ScanOut(ApiModel):
    seq: int
    code: str
    scanned_at: datetime


class ScanBatchOut(ApiModel):
    scans: list[ScanOut]
    last_seq: int


@router.get("/api/devices/status", response_model=DeviceStatusOut)
def device_status(container: Container = Depends(get_container)) -> DeviceStatusOut:
    report = container.devices.report()
    station = container.settings.station
    return DeviceStatusOut(
        checked_at=report.checked_at,
        station_name=station.station_name,
        language=station.language,
        orgatex_last_contact=report.orgatex_last_contact,
        devices=[
            DeviceOut(device=d.device, label=d.label, state=d.state, text=d.text)
            for d in report.devices
        ],
    )


@router.get("/api/scanner/scans", response_model=ScanBatchOut)
def scans(
    after: int = Query(0, ge=0), container: Container = Depends(get_container)
) -> ScanBatchOut:
    events, last_seq = container.scanner.scans_after(after)
    return ScanBatchOut(
        scans=[ScanOut(seq=e.seq, code=e.code, scanned_at=e.scanned_at) for e in events],
        last_seq=last_seq,
    )
