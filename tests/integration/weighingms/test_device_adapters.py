"""Device adapters against the real dummy devices (unit 004-device-integration)."""

from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from tests.conftest import FIXED_NOW, MutableClock, set_available
from weighingms.application.ports import ScaleUnavailable, ScannerUnavailable
from weighingms.domain.quantity import Quantity
from weighingms.infrastructure.devices.peripherals_adapter import (
    HttpPrinterAdapter,
    HttpScannerAdapter,
)
from weighingms.infrastructure.devices.scale_adapter import HttpScaleAdapter
from weighingms.infrastructure.devices.training_adapter import HttpTrainingControl


@pytest.fixture
def scales(dummy_client: TestClient, wms_clock: MutableClock) -> HttpScaleAdapter:
    return HttpScaleAdapter(dummy_client, clock=wms_clock)


@pytest.fixture
def training(dummy_client: TestClient) -> HttpTrainingControl:
    return HttpTrainingControl(dummy_client)


def test_reading_is_returned_as_exact_quantities(
    scales: HttpScaleAdapter, training: HttpTrainingControl
) -> None:
    training.simulate("scale-3kg", "exact", Quantity.of("93.4", "g"))

    reading = scales.read_weight("scale-3kg")

    assert reading.net == Quantity(Decimal("93.4"), "g")
    assert reading.stable is True
    assert reading.read_at == FIXED_NOW


def test_floor_scale_reads_in_kilograms(
    scales: HttpScaleAdapter, training: HttpTrainingControl
) -> None:
    training.simulate("scale-32kg", "exact", Quantity.of("23.880", "kg"))

    assert scales.read_weight("scale-32kg").net == Quantity(Decimal("23.880"), "kg")


def test_unavailable_scale_raises_and_never_returns_zero(
    scales: HttpScaleAdapter, dummy_client: TestClient
) -> None:
    set_available(dummy_client, "scale-3kg", False)

    with pytest.raises(ScaleUnavailable) as error:
        scales.read_weight("scale-3kg")
    assert error.value.code == "SCALE_UNAVAILABLE"


def test_stale_reading_counts_as_unavailable(
    scales: HttpScaleAdapter, wms_clock: MutableClock
) -> None:
    wms_clock.advance(3)

    with pytest.raises(ScaleUnavailable) as error:
        scales.read_weight("scale-3kg")
    assert error.value.details == {"reason": "stale reading"}


def test_tare_zeroes_net(scales: HttpScaleAdapter, training: HttpTrainingControl) -> None:
    training.simulate("scale-32kg", "exact", Quantity.of("1.850", "kg"))

    reading = scales.tare("scale-32kg")

    assert reading.net.display() == "0.000"
    assert reading.tare.display() == "1.850"


def test_tare_failure_raises(scales: HttpScaleAdapter, dummy_client: TestClient) -> None:
    set_available(dummy_client, "scale-32kg", False)

    with pytest.raises(ScaleUnavailable):
        scales.tare("scale-32kg")


def test_status_reports_calibration(
    scales: HttpScaleAdapter, training: HttpTrainingControl
) -> None:
    assert scales.status("scale-3kg").calibration_valid is True

    training.set_calibration("scale-3kg", date(2026, 1, 1))

    state = scales.status("scale-3kg")
    assert state.calibration_valid is False
    assert state.calibration_due == date(2026, 1, 1)


def test_scans_are_delivered_once_in_order(
    dummy_client: TestClient, training: HttpTrainingControl
) -> None:
    scanner = HttpScannerAdapter(dummy_client)
    training.scan("B-24187")
    training.scan("B-24190")

    first, last = scanner.scans_after(0)
    again, _ = scanner.scans_after(last)

    assert [s.code for s in first] == ["B-24187", "B-24190"]
    assert last == 2
    assert again == []


def test_scanner_cursor_survives_a_scanner_restart(
    dummy_client: TestClient, training: HttpTrainingControl
) -> None:
    scanner = HttpScannerAdapter(dummy_client)
    training.scan("B-24187")
    training.scan("B-24187")
    training.reset()
    training.scan("B-24191")

    scans, last = scanner.scans_after(2)

    assert [s.code for s in scans] == ["B-24191"]
    assert last == 1


def test_scanner_unavailable(dummy_client: TestClient, training: HttpTrainingControl) -> None:
    scanner = HttpScannerAdapter(dummy_client)
    set_available(dummy_client, "scanner", False)

    assert scanner.is_available() is False
    with pytest.raises(ScannerUnavailable):
        scanner.scans_after(0)
    with pytest.raises(ScannerUnavailable):
        training.scan("B-24187")


def test_printer_probe(dummy_client: TestClient) -> None:
    probe = HttpPrinterAdapter(dummy_client)

    assert probe.is_available() is True
    set_available(dummy_client, "printer", False)
    assert probe.is_available() is False


def test_training_availability_round_trip(training: HttpTrainingControl) -> None:
    systems = training.set_availability("orgatex", False)

    assert systems["orgatex"] is False
    assert training.availability()["orgatex"] is False
