"""Ticket preview, print and reprint (unit 005-ticket-printing)."""

from typing import Any

from fastapi.testclient import TestClient

from tests.api.weighingms.test_completion_api import _start, _weigh_all
from tests.conftest import set_available


def test_ticket_is_only_available_for_a_completed_batch(wms_client: TestClient) -> None:
    session = _start(wms_client)

    response = wms_client.get(f"/api/sessions/{session['sessionId']}/ticket")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "SESSION_NOT_COMPLETED"


def test_preview_contains_the_prototype_ticket_fields(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    sid = _weigh_all(wms_client, dummy_client)["sessionId"]

    ticket = wms_client.get(f"/api/sessions/{sid}/ticket").json()

    assert ticket["header"] == "FCI DYEING — WEIGHING TICKET"
    assert (ticket["batchId"], ticket["orderRef"], ticket["machineRef"], ticket["shadeCode"]) == (
        "B-24187",
        "SO-9931",
        "JET-04",
        "Teal 4C",
    )
    assert ticket["operatorName"] == "R. Karim"
    assert ticket["date"] == "2026-10-26 13:47"  # FIXED_NOW 07:47 UTC in Asia/Dhaka
    assert [(line["shortName"], line["actual"]["value"]) for line in ticket["lines"]] == [
        ("Blue RSPL", "1241.5"),
        ("Red RB", "385.4"),
        ("Yellow RGB", "94.2"),
        ("Na2SO4", "23.980"),
        ("Soda Ash", "9.621"),
    ]
    assert ticket["resultLine"] == "ALL WITHIN TOLERANCE"
    assert ticket["barcodeValue"] == "B-24187"
    assert ticket["reprint"] is False
    assert "Soda Ash      9.600  9.621 kg" in ticket["text"]


def test_print_then_reprint(
    wms_client: TestClient, dummy_client: TestClient, container: Any
) -> None:
    sid = _weigh_all(wms_client, dummy_client)["sessionId"]

    first = wms_client.post(f"/api/sessions/{sid}/ticket/print").json()
    second = wms_client.post(f"/api/sessions/{sid}/ticket/print").json()

    assert (first["reprint"], second["reprint"]) == (False, True)
    assert second["ticket"]["text"][1] == "*** REPRINT ***"
    printed = dummy_client.get("/api/tickets").json()
    assert [(t["ticketId"], t["reprint"]) for t in printed] == [
        (first["ticketId"], False),
        (second["ticketId"], True),
    ]
    assert printed[0]["lines"][0] == "FCI DYEING — WEIGHING TICKET"
    assert printed[0]["barcodeValue"] == "B-24187"
    assert [e["type"] for e in container.audit.events(sid)] == ["REPRINT"]
    assert wms_client.get(f"/api/sessions/{sid}/ticket").json()["reprint"] is True


def test_printer_down_keeps_the_batch_completed_and_retry_prints_the_original(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    sid = _weigh_all(wms_client, dummy_client)["sessionId"]
    set_available(dummy_client, "printer", False)

    failed = wms_client.post(f"/api/sessions/{sid}/ticket/print")

    assert failed.status_code == 503
    assert failed.json()["error"] == {
        "code": "PRINTER_UNAVAILABLE",
        "message": "Printer not available. Check the printer and try again.",
        "details": {"status": 503},
    }
    assert wms_client.get(f"/api/sessions/{sid}").json()["status"] == "COMPLETED"
    set_available(dummy_client, "printer", True)
    retry = wms_client.post(f"/api/sessions/{sid}/ticket/print").json()
    assert retry["reprint"] is False


def test_overridden_component_on_the_ticket(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    session = _start(wms_client)
    sid = session["sessionId"]
    dummy_client.post(
        "/api/control/scales/scale-3kg/simulate",
        json={"profile": "exact", "net": {"value": "1260.0", "unit": "g"}},
    )
    session = wms_client.post(
        f"/api/sessions/{sid}/override", json={"supervisorPin": "2468", "reason": "Lab approved"}
    ).json()
    actuals = {
        "B-24187-02": ("385.4", "g"),
        "B-24187-03": ("94.2", "g"),
        "B-24187-04": ("23.980", "kg"),
        "B-24187-05": ("9.621", "kg"),
    }
    while session["status"] == "IN_PROGRESS":
        value, unit = actuals[session["activeComponentId"]]
        scale = "scale-3kg" if unit == "g" else "scale-32kg"
        dummy_client.post(
            f"/api/control/scales/{scale}/simulate",
            json={"profile": "exact", "net": {"value": value, "unit": unit}},
        )
        session = wms_client.post(f"/api/sessions/{sid}/confirm").json()

    ticket = wms_client.get(f"/api/sessions/{sid}/ticket").json()

    assert ticket["resultLine"] == "1 OVERRIDDEN (*)"
    assert ticket["lines"][0]["overridden"] is True
