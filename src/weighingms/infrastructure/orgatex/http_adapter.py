"""The single OrgaTEX adapter (Brief IR-07): HTTP to the Dummy OrgaTEX training contract."""

import logging
import time
from datetime import UTC, datetime
from typing import Any

import httpx
from pydantic import BaseModel, ValidationError

from weighingms.application.ports import (
    BatchQueue,
    ConsumptionAck,
    ConsumptionPayload,
    OrgatexBadData,
    OrgatexBatch,
    OrgatexComponent,
    OrgatexRecipe,
    OrgatexUnavailable,
    WriteBackStatus,
)
from weighingms.domain.errors import BatchNotFound
from weighingms.domain.quantity import Quantity
from weighingms.infrastructure.orgatex.contract import (
    WireBatch,
    WireBatchList,
    WireConsumptionReceipt,
    WireQuantity,
    WireRecipe,
)

log = logging.getLogger("weighingms.orgatex")

_UNAVAILABLE_MESSAGE = "OrgaTEX is not reachable. Check the connection and retry."


class HttpOrgatexAdapter:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client
        self._last_contact: datetime | None = None

    def list_batches(self) -> BatchQueue:
        wire = self._get(WireBatchList, "/api/batches")
        return BatchQueue(received_at=wire.generated_at, batches=[_batch(b) for b in wire.batches])

    def get_batch(self, batch_id: str) -> OrgatexBatch:
        return _batch(self._get(WireBatch, f"/api/batches/{batch_id}", batch_id))

    def get_recipe(self, batch_id: str) -> OrgatexRecipe:
        wire = self._get(WireRecipe, f"/api/batches/{batch_id}/recipe", batch_id)
        return OrgatexRecipe(
            recipe_id=wire.recipe_id,
            batch_id=wire.batch_id,
            shade_code=wire.shade_code,
            version=wire.version,
            components=[
                OrgatexComponent(
                    component_id=c.component_id,
                    sequence=c.sequence,
                    dyestuff_code=c.dyestuff_code,
                    name=c.name,
                    colour_hex=c.colour_hex,
                    target=_quantity(c.target_qty),
                    tolerance=_quantity(c.tolerance) if c.tolerance else None,
                    lot_id=c.lot_id,
                )
                for c in wire.components
            ],
        )

    def set_batch_status(self, batch_id: str, status: WriteBackStatus) -> None:
        self._call("PATCH", f"/api/batches/{batch_id}/status", batch_id, json={"status": status})

    def post_consumption(self, payload: ConsumptionPayload) -> ConsumptionAck:
        body = {
            "idempotencyKey": payload.idempotency_key,
            "sessionId": payload.session_id,
            "stationId": payload.station_id,
            "operatorId": payload.operator_id,
            "completedAt": payload.completed_at.isoformat(),
            "lines": [
                {
                    "componentId": line.component_id,
                    "dyestuffCode": line.dyestuff_code,
                    "lotId": line.lot_id,
                    "target": _wire_quantity(line.target),
                    "actual": _wire_quantity(line.actual),
                    "scaleId": line.scale_id,
                    "operatorId": line.operator_id,
                    "confirmedAt": line.confirmed_at.isoformat(),
                    "result": line.result,
                }
                for line in payload.lines
            ],
        }
        path = f"/api/batches/{payload.batch_id}/consumption"
        response = self._call("POST", path, payload.batch_id, json=body)
        receipt = _parse(WireConsumptionReceipt, response)
        return ConsumptionAck(
            consumption_id=receipt.consumption_id,
            received_at=receipt.received_at,
            duplicate=receipt.duplicate,
        )

    def ping(self) -> bool:
        try:
            self._call("GET", "/api/batches", quiet=True)
        except (OrgatexUnavailable, OrgatexBadData):
            return False
        return True

    def last_contact(self) -> datetime | None:
        return self._last_contact

    def _get[M: BaseModel](self, model: type[M], path: str, batch_id: str | None = None) -> M:
        return _parse(model, self._call("GET", path, batch_id))

    def _call(
        self,
        method: str,
        path: str,
        batch_id: str | None = None,
        json: Any = None,
        quiet: bool = False,
    ) -> httpx.Response:
        started = time.perf_counter()
        try:
            response = self._client.request(method, path, json=json)
        except httpx.HTTPError as exc:
            log.warning("OrgaTEX %s %s failed: %s", method, path, exc.__class__.__name__)
            raise OrgatexUnavailable(_UNAVAILABLE_MESSAGE) from exc
        elapsed_ms = (time.perf_counter() - started) * 1000
        level = logging.DEBUG if quiet else logging.INFO
        log.log(
            level, "OrgaTEX %s %s -> %s (%.0f ms)", method, path, response.status_code, elapsed_ms
        )
        if response.status_code == 404 and batch_id is not None:
            raise BatchNotFound(
                f"Batch {batch_id} does not exist in OrgaTEX.", {"batchId": batch_id}
            )
        if response.status_code >= 500:
            raise OrgatexUnavailable(_UNAVAILABLE_MESSAGE, {"status": response.status_code})
        if response.status_code >= 400:
            raise OrgatexBadData(
                f"OrgaTEX rejected the request ({response.status_code}).",
                {"status": response.status_code},
            )
        self._last_contact = datetime.now(UTC).replace(microsecond=0)
        return response


def _parse[M: BaseModel](model: type[M], response: httpx.Response) -> M:
    try:
        return model.model_validate_json(response.content)
    except ValidationError as exc:
        log.warning("OrgaTEX returned unexpected data: %s", exc.errors()[:3])
        raise OrgatexBadData("OrgaTEX returned data WeighingMS cannot read.") from exc


def _quantity(wire: WireQuantity) -> Quantity:
    return Quantity(wire.value, wire.unit)


def _wire_quantity(quantity: Quantity) -> dict[str, str]:
    return {"value": str(quantity.value), "unit": quantity.unit}


def _batch(wire: WireBatch) -> OrgatexBatch:
    return OrgatexBatch(
        batch_id=wire.batch_id,
        order_ref=wire.order_ref,
        machine_ref=wire.machine_ref,
        fabric_desc=wire.fabric_desc,
        fabric_weight_kg=wire.fabric_weight_kg,
        shade_code=wire.shade_code,
        recipe_id=wire.recipe_id,
        component_count=wire.component_count,
        status=wire.status,
        released_at=wire.released_at,
    )
