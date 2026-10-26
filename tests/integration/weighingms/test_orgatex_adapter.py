"""The OrgaTEX adapter against the real Dummy OrgaTEX (no mocks — the dummy is the test double)."""

from datetime import UTC, datetime
from decimal import Decimal

import httpx
import pytest
from fastapi.testclient import TestClient

from tests.conftest import set_available
from weighingms.application.ports import (
    ConsumptionLine,
    ConsumptionPayload,
    OrgatexBadData,
    OrgatexUnavailable,
)
from weighingms.domain.errors import BatchNotFound
from weighingms.domain.quantity import Quantity
from weighingms.infrastructure.orgatex.http_adapter import HttpOrgatexAdapter

AT = datetime(2026, 10, 26, 7, 48, 22, tzinfo=UTC)


def _payload(key: str = "S-1") -> ConsumptionPayload:
    return ConsumptionPayload(
        batch_id="B-24187",
        idempotency_key=key,
        session_id=key,
        station_id="STN-01",
        operator_id="OP-1001",
        completed_at=AT,
        lines=[
            ConsumptionLine(
                component_id="B-24187-03",
                dyestuff_code="DYE-4471",
                lot_id="2026-0387",
                target=Quantity.of("94.0", "g"),
                actual=Quantity.of("94.2", "g"),
                scale_id="scale-3kg",
                operator_id="OP-1001",
                confirmed_at=AT,
                result="IN_TOLERANCE",
            )
        ],
    )


def test_batch_queue_is_mapped(orgatex_adapter: HttpOrgatexAdapter) -> None:
    queue = orgatex_adapter.list_batches()

    assert [b.batch_id for b in queue.batches] == ["B-24187", "B-24188", "B-24190", "B-24191"]
    first = queue.batches[0]
    assert (first.order_ref, first.machine_ref, first.shade_code) == (
        "SO-9931",
        "JET-04",
        "Teal 4C",
    )
    assert first.fabric_weight_kg == Decimal("480")
    assert orgatex_adapter.last_contact() is not None


def test_recipe_is_mapped_with_exact_quantities(orgatex_adapter: HttpOrgatexAdapter) -> None:
    recipe = orgatex_adapter.get_recipe("B-24187")

    yellow = recipe.components[2]
    assert yellow.name == "Remazol Yellow RGB"
    assert yellow.target == Quantity(Decimal("94.0"), "g")
    assert yellow.tolerance == Quantity(Decimal("0.5"), "g")
    assert yellow.lot_id == "2026-0387"


def test_unknown_batch_raises_batch_not_found(orgatex_adapter: HttpOrgatexAdapter) -> None:
    with pytest.raises(BatchNotFound):
        orgatex_adapter.get_batch("B-00000")


def test_unavailable_orgatex_raises(
    orgatex_adapter: HttpOrgatexAdapter, dummy_client: TestClient
) -> None:
    set_available(dummy_client, "orgatex", False)

    with pytest.raises(OrgatexUnavailable):
        orgatex_adapter.list_batches()


def test_connection_failure_raises_unavailable() -> None:
    adapter = HttpOrgatexAdapter(httpx.Client(base_url="http://127.0.0.1:1", timeout=0.5))

    with pytest.raises(OrgatexUnavailable):
        adapter.list_batches()
    assert adapter.last_contact() is None


def test_status_write_back(orgatex_adapter: HttpOrgatexAdapter, dummy_client: TestClient) -> None:
    orgatex_adapter.set_batch_status("B-24187", "WEIGHING")

    assert dummy_client.get("/api/batches/B-24187").json()["status"] == "WEIGHING"


def test_consumption_posting_is_idempotent(
    orgatex_adapter: HttpOrgatexAdapter, dummy_client: TestClient
) -> None:
    first = orgatex_adapter.post_consumption(_payload())
    second = orgatex_adapter.post_consumption(_payload())

    assert first.duplicate is False
    assert second.duplicate is True
    assert second.consumption_id == first.consumption_id
    stored = dummy_client.get("/api/batches/B-24187/consumption").json()
    assert len(stored) == 1
    assert stored[0]["posting"]["lines"][0]["actual"] == {"value": "94.2", "unit": "g"}


def test_malformed_response_is_bad_data() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": True})

    client = httpx.Client(base_url="http://orgatex", transport=httpx.MockTransport(handler))

    with pytest.raises(OrgatexBadData):
        HttpOrgatexAdapter(client).list_batches()


def test_client_error_is_bad_data() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={})

    client = httpx.Client(base_url="http://orgatex", transport=httpx.MockTransport(handler))

    with pytest.raises(OrgatexBadData):
        HttpOrgatexAdapter(client).set_batch_status("B-24187", "WEIGHED")
