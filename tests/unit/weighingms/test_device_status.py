"""Device-status aggregation rules with in-memory ports (unit 004-device-integration)."""

import logging
from dataclasses import dataclass, field
from datetime import date, datetime

import pytest

from tests.conftest import FIXED_NOW, STATION_CONFIG, FakeTicker
from weighingms.application.devices import DeviceStatusService
from weighingms.application.ports import ScaleState, ScaleUnavailable
from weighingms.config import load_station_config

STATION = load_station_config(STATION_CONFIG)


@dataclass
class Scales:
    down: set[str] = field(default_factory=set)
    expired: set[str] = field(default_factory=set)

    def status(self, scale_id: str) -> ScaleState:
        if scale_id in self.down:
            raise ScaleUnavailable("down")
        return ScaleState(scale_id, date(2027, 1, 1), scale_id not in self.expired)


@dataclass
class Probe:
    up: bool = True

    def is_available(self) -> bool:
        return self.up


@dataclass
class Orgatex:
    up: bool = True
    pings: int = 0

    def ping(self) -> bool:
        self.pings += 1
        return self.up

    def last_contact(self) -> datetime | None:
        return FIXED_NOW if self.up else None


def _service(
    scales: Scales, scanner: Probe, printer: Probe, orgatex: Orgatex, ticker: FakeTicker
) -> DeviceStatusService:
    return DeviceStatusService(
        STATION,
        scales,  # type: ignore[arg-type]
        scanner,  # type: ignore[arg-type]
        printer,
        orgatex,  # type: ignore[arg-type]
        clock=lambda: FIXED_NOW,
        ticker=ticker,
    )


def _summary(service: DeviceStatusService) -> list[tuple[str, str, str]]:
    return [(d.label, d.state, d.text) for d in service.report().devices]


def test_all_devices_up() -> None:
    service = _service(Scales(), Probe(), Probe(), Orgatex(), FakeTicker())

    assert _summary(service) == [
        ("SCALE 3 kg", "UP", "READY"),
        ("SCALE 32 kg", "UP", "READY"),
        ("SCANNER", "UP", "READY"),
        ("PRINTER", "UP", "READY"),
        ("ORGATEX", "UP", "LINKED"),
    ]
    assert service.report().orgatex_last_contact == FIXED_NOW


def test_down_and_degraded_devices() -> None:
    scales = Scales(down={"scale-32kg"}, expired={"scale-3kg"})
    service = _service(scales, Probe(False), Probe(False), Orgatex(False), FakeTicker())

    assert _summary(service) == [
        ("SCALE 3 kg", "DEGRADED", "CAL EXPIRED"),
        ("SCALE 32 kg", "DOWN", "OFFLINE"),
        ("SCANNER", "DOWN", "OFFLINE"),
        ("PRINTER", "DOWN", "OFFLINE"),
        ("ORGATEX", "DOWN", "OFFLINE"),
    ]


def test_orgatex_probe_is_cached_for_two_seconds() -> None:
    orgatex, ticker = Orgatex(), FakeTicker()
    service = _service(Scales(), Probe(), Probe(), orgatex, ticker)

    service.report()
    ticker.advance(1.0)
    service.report()
    assert orgatex.pings == 1

    ticker.advance(1.5)
    service.report()
    assert orgatex.pings == 2


def test_only_state_transitions_are_logged(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The app's logging setup stops propagation; caplog listens on the root logger.
    monkeypatch.setattr(logging.getLogger("weighingms"), "propagate", True)
    scales = Scales()
    service = _service(scales, Probe(), Probe(), Orgatex(), FakeTicker())
    service.report()

    with caplog.at_level(logging.INFO, logger="weighingms.devices"):
        scales.down.add("scale-3kg")
        service.report()
        service.report()
        scales.down.clear()
        service.report()

    messages = [(r.levelname, r.getMessage()) for r in caplog.records]
    assert messages == [
        ("WARNING", "SCALE 3 kg UP -> DOWN (OFFLINE)"),
        ("INFO", "SCALE 3 kg DOWN -> UP (READY)"),
    ]
