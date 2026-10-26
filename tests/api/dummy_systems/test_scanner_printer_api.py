"""Dummy Scanner and Dummy Printer (stories 005 and 006 of unit 001-training-substitutes)."""

from fastapi.testclient import TestClient

TICKET = {
    "batchId": "B-24187",
    "sessionId": "S-1",
    "reprint": False,
    "lines": ["FCI DYEING — WEIGHING TICKET", "BATCH   B-24187"],
    "barcodeValue": "B-24187",
}


def test_scans_are_delivered_in_order_with_a_cursor(dummy_client: TestClient) -> None:
    first = dummy_client.post("/api/scanner/scans", json={"code": "B-24187"}).json()
    second = dummy_client.post("/api/scanner/scans", json={"code": "B-24187"}).json()

    assert (first["seq"], second["seq"]) == (1, 2)
    batch = dummy_client.get("/api/scanner/scans", params={"after": 1}).json()
    assert [s["seq"] for s in batch["scans"]] == [2]
    assert batch["lastSeq"] == 2
    assert dummy_client.get("/api/scanner/scans").json()["lastSeq"] == 2


def test_empty_scan_is_rejected(dummy_client: TestClient) -> None:
    assert dummy_client.post("/api/scanner/scans", json={"code": ""}).status_code == 422


def test_scanner_status(dummy_client: TestClient) -> None:
    assert dummy_client.get("/api/scanner/status").json() == {"available": True}


def test_printed_tickets_are_stored_and_retrievable(dummy_client: TestClient) -> None:
    receipt = dummy_client.post("/api/tickets", json=TICKET).json()

    assert receipt["status"] == "PRINTED"
    assert receipt["ticketId"].startswith("TKT-")
    tickets = dummy_client.get("/api/tickets").json()
    assert [t["ticketId"] for t in tickets] == [receipt["ticketId"]]
    one = dummy_client.get(f"/api/tickets/{receipt['ticketId']}").json()
    assert one["lines"] == TICKET["lines"]
    assert one["barcodeValue"] == "B-24187"


def test_ticket_without_lines_is_rejected(dummy_client: TestClient) -> None:
    assert dummy_client.post("/api/tickets", json={**TICKET, "lines": []}).status_code == 422


def test_unknown_ticket_is_404(dummy_client: TestClient) -> None:
    response = dummy_client.get("/api/tickets/TKT-NOPE")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TICKET_NOT_FOUND"


def test_printer_status(dummy_client: TestClient) -> None:
    assert dummy_client.get("/api/printer/status").json() == {"available": True}
