"""Device and connection status for the status strip (FR-24, FR-20). Never raises."""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from weighingms.application.ports import (
    OrgatexPort,
    PrinterProbe,
    ScalePort,
    ScaleUnavailable,
    ScannerPort,
)
from weighingms.clock import Clock, Ticker, monotonic, utc_now
from weighingms.config import StationConfig
from weighingms.domain.scale_selection import ScaleDefinition

log = logging.getLogger("weighingms.devices")

DeviceState = Literal["UP", "DOWN", "DEGRADED"]
ORGATEX_PROBE_INTERVAL_SECONDS = 2.0


@dataclass(frozen=True)
class DeviceStatusEntry:
    device: str
    label: str
    state: DeviceState
    text: str


@dataclass(frozen=True)
class DeviceStatusReport:
    checked_at: datetime
    devices: list[DeviceStatusEntry]
    orgatex_last_contact: datetime | None


class DeviceStatusService:
    def __init__(
        self,
        station: StationConfig,
        scales: ScalePort,
        scanner: ScannerPort,
        printer: PrinterProbe,
        orgatex: OrgatexPort,
        clock: Clock = utc_now,
        ticker: Ticker = monotonic,
    ) -> None:
        self._station = station
        self._scales = scales
        self._scanner = scanner
        self._printer = printer
        self._orgatex = orgatex
        self._clock = clock
        self._ticker = ticker
        self._orgatex_probe: tuple[float, bool] | None = None
        self._last_states: dict[str, DeviceState] = {}

    def report(self) -> DeviceStatusReport:
        entries = [self._scale(scale) for scale in self._station.scales.values()]
        entries.append(self._simple("scanner", "SCANNER", self._scanner.is_available()))
        entries.append(self._simple("printer", "PRINTER", self._printer.is_available()))
        orgatex_up = self._orgatex_reachable()
        entries.append(
            DeviceStatusEntry(
                "orgatex",
                "ORGATEX",
                "UP" if orgatex_up else "DOWN",
                "LINKED" if orgatex_up else "OFFLINE",
            )
        )
        self._log_transitions(entries)
        return DeviceStatusReport(
            checked_at=self._clock(),
            devices=entries,
            orgatex_last_contact=self._orgatex.last_contact(),
        )

    def _scale(self, scale: ScaleDefinition) -> DeviceStatusEntry:
        try:
            state = self._scales.status(scale.scale_id)
        except ScaleUnavailable:
            return DeviceStatusEntry(scale.scale_id, scale.strip_label, "DOWN", "OFFLINE")
        if not state.calibration_valid:
            return DeviceStatusEntry(scale.scale_id, scale.strip_label, "DEGRADED", "CAL EXPIRED")
        return DeviceStatusEntry(scale.scale_id, scale.strip_label, "UP", "READY")

    @staticmethod
    def _simple(device: str, label: str, up: bool) -> DeviceStatusEntry:
        return DeviceStatusEntry(
            device, label, "UP" if up else "DOWN", "READY" if up else "OFFLINE"
        )

    def _orgatex_reachable(self) -> bool:
        now = self._ticker()
        if self._orgatex_probe and now - self._orgatex_probe[0] < ORGATEX_PROBE_INTERVAL_SECONDS:
            return self._orgatex_probe[1]
        reachable = self._orgatex.ping()
        self._orgatex_probe = (now, reachable)
        return reachable

    def _log_transitions(self, entries: list[DeviceStatusEntry]) -> None:
        for entry in entries:
            previous = self._last_states.get(entry.device)
            if previous is not None and previous != entry.state:
                level = logging.INFO if entry.state == "UP" else logging.WARNING
                log.log(level, "%s %s -> %s (%s)", entry.label, previous, entry.state, entry.text)
            self._last_states[entry.device] = entry.state
