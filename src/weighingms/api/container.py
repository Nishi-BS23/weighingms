"""Composition root: builds the application services and adapters once per app."""

from collections.abc import Callable
from dataclasses import dataclass, field

import httpx
from fastapi import Request
from sqlalchemy import Engine

from weighingms.application.batches import BatchService
from weighingms.application.devices import DeviceStatusService
from weighingms.application.operators import OperatorService
from weighingms.application.ports import (
    OrgatexPort,
    PrinterProbe,
    ScalePort,
    ScannerPort,
    TrainingControlPort,
)
from weighingms.application.sessions import SessionService
from weighingms.application.tickets import TicketService
from weighingms.application.training import TrainingService
from weighingms.clock import Clock, utc_now
from weighingms.config import Settings
from weighingms.infrastructure.devices.peripherals_adapter import (
    HttpPrinterAdapter,
    HttpScannerAdapter,
)
from weighingms.infrastructure.devices.scale_adapter import HttpScaleAdapter
from weighingms.infrastructure.devices.training_adapter import HttpTrainingControl
from weighingms.infrastructure.orgatex.http_adapter import HttpOrgatexAdapter
from weighingms.infrastructure.persistence.db import create_station_engine, migrate
from weighingms.infrastructure.persistence.repositories import (
    AuditLog,
    PrintLog,
    RecordRepository,
    SessionRepository,
    StationState,
)

ORGATEX_TIMEOUT_SECONDS = 2.0
DEVICE_TIMEOUT_SECONDS = 1.0


@dataclass
class Container:
    settings: Settings
    orgatex: OrgatexPort
    scales: ScalePort
    scanner: ScannerPort
    printer_probe: PrinterProbe
    training: TrainingControlPort
    batches: BatchService
    devices: DeviceStatusService
    operators: OperatorService
    sessions: SessionService
    training_service: TrainingService
    tickets: TicketService
    audit: AuditLog
    engine: Engine
    clock: Clock
    reset_hooks: list[Callable[[], None]] = field(default_factory=list)
    """Extra training-state resets run by POST /api/training/reset."""

    def close(self) -> None:
        """Release database connections (called on application shutdown)."""
        self.engine.dispose()


def build_container(
    settings: Settings,
    orgatex_client: httpx.Client | None = None,
    devices_client: httpx.Client | None = None,
    clock: Clock = utc_now,
) -> Container:
    """Wire adapters to their HTTP clients. Tests pass in-process clients for the dummy app."""
    orgatex_client = orgatex_client or httpx.Client(
        base_url=settings.orgatex_base_url, timeout=ORGATEX_TIMEOUT_SECONDS
    )
    devices_client = devices_client or httpx.Client(
        base_url=settings.devices_base_url, timeout=DEVICE_TIMEOUT_SECONDS
    )
    station = settings.station
    engine = create_station_engine(settings.db_path)
    migrate(engine)
    audit = AuditLog(engine)
    orgatex = HttpOrgatexAdapter(orgatex_client)
    scales = HttpScaleAdapter(devices_client, clock=clock)
    scanner = HttpScannerAdapter(devices_client)
    printer = HttpPrinterAdapter(devices_client)
    training = HttpTrainingControl(devices_client)
    batches = BatchService(orgatex, station)
    operators = OperatorService(
        station.operators, StationState(engine), audit, station.default_operator_id, clock=clock
    )
    session_repo, record_repo, print_log = (
        SessionRepository(engine),
        RecordRepository(engine),
        PrintLog(engine),
    )
    sessions = SessionService(
        session_repo,
        record_repo,
        audit,
        batches,
        operators,
        orgatex,
        scales,
        station,
        clock=clock,
        container_placed=training.place_load if station.training_mode else None,
    )
    container = Container(
        settings=settings,
        orgatex=orgatex,
        scales=scales,
        scanner=scanner,
        printer_probe=printer,
        training=training,
        batches=batches,
        devices=DeviceStatusService(station, scales, scanner, printer, orgatex, clock=clock),
        operators=operators,
        sessions=sessions,
        training_service=TrainingService(sessions, training),
        tickets=TicketService(
            session_repo, record_repo, print_log, printer, operators, audit, station, clock=clock
        ),
        audit=audit,
        engine=engine,
        clock=clock,
    )
    container.reset_hooks.extend([print_log.clear, sessions.clear, audit.clear, operators.reset])
    return container


def get_container(request: Request) -> Container:
    container: Container = request.app.state.container
    return container
