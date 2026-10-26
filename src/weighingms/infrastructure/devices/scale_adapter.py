"""Scale adapter (training: Dummy Scale API). A failed or stale read is unavailable — never 0."""

import logging
from datetime import timedelta

import httpx

from weighingms.application.ports import ScaleReading, ScaleState, ScaleUnavailable
from weighingms.clock import Clock, utc_now
from weighingms.domain.quantity import Quantity
from weighingms.infrastructure.devices.contract import WireQuantity, WireReading, WireScaleStatus
from weighingms.infrastructure.devices.http import call, parse

log = logging.getLogger("weighingms.devices")

MAX_READING_AGE = timedelta(seconds=2)
"""Brief IR-13: disconnection detected within 2 seconds."""


def _message(scale_id: str) -> str:
    return f"Scale {scale_id} is not responding. Check the connection."


class HttpScaleAdapter:
    def __init__(self, client: httpx.Client, clock: Clock = utc_now) -> None:
        self._client = client
        self._clock = clock

    def read_weight(self, scale_id: str) -> ScaleReading:
        response = call(
            self._client,
            "GET",
            f"/api/scales/{scale_id}/weight",
            ScaleUnavailable,
            _message(scale_id),
        )
        reading = self._reading(response, scale_id)
        if self._clock() - reading.read_at > MAX_READING_AGE:
            raise ScaleUnavailable(_message(scale_id), {"reason": "stale reading"})
        return reading

    def tare(self, scale_id: str) -> ScaleReading:
        try:
            response = call(
                self._client,
                "POST",
                f"/api/scales/{scale_id}/tare",
                ScaleUnavailable,
                _message(scale_id),
            )
        except ScaleUnavailable:
            log.warning("Tare failed on %s", scale_id)
            raise
        return self._reading(response, scale_id)

    def status(self, scale_id: str) -> ScaleState:
        response = call(
            self._client,
            "GET",
            f"/api/scales/{scale_id}/status",
            ScaleUnavailable,
            _message(scale_id),
        )
        wire = parse(WireScaleStatus, response, ScaleUnavailable, _message(scale_id))
        return ScaleState(
            scale_id=wire.scale_id,
            calibration_due=wire.calibration_due,
            calibration_valid=wire.calibration_valid,
        )

    @staticmethod
    def _reading(response: httpx.Response, scale_id: str) -> ScaleReading:
        wire = parse(WireReading, response, ScaleUnavailable, _message(scale_id))
        return ScaleReading(
            scale_id=wire.scale_id,
            gross=_quantity(wire.gross),
            tare=_quantity(wire.tare),
            net=_quantity(wire.net),
            stable=wire.stable,
            read_at=wire.read_at,
        )


def _quantity(wire: WireQuantity) -> Quantity:
    return Quantity(wire.value, wire.unit)
