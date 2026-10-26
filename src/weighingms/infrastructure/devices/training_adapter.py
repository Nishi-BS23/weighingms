"""Training-control adapter: drives the training substitutes (training build only)."""

from datetime import date
from typing import Any, cast

import httpx

from weighingms.application.ports import ScanEvent, ScannerUnavailable
from weighingms.domain.errors import DependencyUnavailable
from weighingms.domain.quantity import Quantity
from weighingms.infrastructure.devices.contract import WireAvailability, WireScan
from weighingms.infrastructure.devices.http import call, parse


class TrainingControlUnavailable(DependencyUnavailable):
    code = "TRAINING_CONTROL_UNAVAILABLE"


_MESSAGE = "The training substitutes service is not reachable."


class HttpTrainingControl:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def availability(self) -> dict[str, bool]:
        response = self._call("GET", "/api/control/availability")
        return parse(WireAvailability, response, TrainingControlUnavailable, _MESSAGE).systems

    def set_availability(self, system: str, available: bool) -> dict[str, bool]:
        response = self._call(
            "PUT", f"/api/control/availability/{system}", json={"available": available}
        )
        return parse(WireAvailability, response, TrainingControlUnavailable, _MESSAGE).systems

    def reset(self) -> None:
        self._call("POST", "/api/control/reset")

    def simulate(self, scale_id: str, profile: str, net: Quantity) -> dict[str, Any]:
        body = {"profile": profile, "net": {"value": str(net.value), "unit": net.unit}}
        response = self._call("POST", f"/api/control/scales/{scale_id}/simulate", json=body)
        return cast(dict[str, Any], response.json())

    def place_load(self, scale_id: str, gross: Quantity) -> None:
        body = {"gross": {"value": str(gross.value), "unit": gross.unit}}
        self._call("POST", f"/api/control/scales/{scale_id}/load", json=body)

    def set_calibration(self, scale_id: str, due: date) -> dict[str, Any]:
        body = {"calibrationDue": due.isoformat()}
        response = self._call("PUT", f"/api/control/scales/{scale_id}/calibration", json=body)
        return cast(dict[str, Any], response.json())

    def scan(self, code: str) -> ScanEvent:
        message = "The barcode scanner is not available."
        response = call(
            self._client,
            "POST",
            "/api/scanner/scans",
            ScannerUnavailable,
            message,
            json={"code": code},
        )
        wire = parse(WireScan, response, ScannerUnavailable, message)
        return ScanEvent(seq=wire.seq, code=wire.code, scanned_at=wire.scanned_at)

    def _call(self, method: str, path: str, json: Any = None) -> httpx.Response:
        return call(self._client, method, path, TrainingControlUnavailable, _MESSAGE, json=json)
