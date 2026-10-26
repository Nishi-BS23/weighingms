"""Failure injection and reset (story 007 of unit 001-training-substitutes)."""

import pytest
from fastapi.testclient import TestClient

ENDPOINTS = {
    "orgatex": [("GET", "/api/batches"), ("GET", "/api/batches/B-24187/recipe")],
    "scale-3kg": [("GET", "/api/scales/scale-3kg/weight"), ("POST", "/api/scales/scale-3kg/tare")],
    "scale-32kg": [
        ("GET", "/api/scales/scale-32kg/weight"),
        ("GET", "/api/scales/scale-32kg/status"),
    ],
    "scanner": [("GET", "/api/scanner/scans"), ("GET", "/api/scanner/status")],
    "printer": [("GET", "/api/tickets"), ("GET", "/api/printer/status")],
}


def _toggle(client: TestClient, system: str, available: bool) -> None:
    response = client.put(f"/api/control/availability/{system}", json={"available": available})
    assert response.status_code == 200


@pytest.mark.parametrize("system", list(ENDPOINTS))
def test_unavailable_system_returns_503_only_on_its_own_endpoints(
    dummy_client: TestClient, system: str
) -> None:
    _toggle(dummy_client, system, False)

    for other, endpoints in ENDPOINTS.items():
        for method, path in endpoints:
            response = dummy_client.request(method, path)
            if other == system:
                assert response.status_code == 503, path
                assert response.json()["error"]["code"] == "SYSTEM_UNAVAILABLE"
            else:
                assert response.status_code == 200, path

    _toggle(dummy_client, system, True)
    for method, path in ENDPOINTS[system]:
        assert dummy_client.request(method, path).status_code == 200


def test_availability_snapshot_and_scale_list(dummy_client: TestClient) -> None:
    _toggle(dummy_client, "scale-32kg", False)

    systems = dummy_client.get("/api/control/availability").json()["systems"]
    assert systems == {
        "orgatex": True,
        "scale-3kg": True,
        "scale-32kg": False,
        "scanner": True,
        "printer": True,
    }
    listed = {s["scaleId"]: s["available"] for s in dummy_client.get("/api/scales").json()}
    assert listed == {"scale-3kg": True, "scale-32kg": False}


def test_unknown_system_is_404(dummy_client: TestClient) -> None:
    response = dummy_client.put("/api/control/availability/coffee", json={"available": False})

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "SYSTEM_NOT_FOUND"


def test_control_endpoints_ignore_availability(dummy_client: TestClient) -> None:
    _toggle(dummy_client, "scale-3kg", False)

    simulate = dummy_client.post(
        "/api/control/scales/scale-3kg/simulate",
        json={"profile": "exact", "net": {"value": "10", "unit": "g"}},
    )
    assert simulate.status_code == 200
    assert dummy_client.post("/api/control/reset").status_code == 200


def test_reset_restores_the_seed_state(dummy_client: TestClient) -> None:
    dummy_client.patch("/api/batches/B-24187/status", json={"status": "WEIGHED"})
    dummy_client.post(
        "/api/tickets",
        json={"batchId": "B-24187", "lines": ["x"], "barcodeValue": "B-24187"},
    )
    dummy_client.post("/api/scanner/scans", json={"code": "B-24187"})
    dummy_client.post(
        "/api/control/scales/scale-3kg/simulate",
        json={"profile": "exact", "net": {"value": "50", "unit": "g"}},
    )
    _toggle(dummy_client, "printer", False)

    assert dummy_client.post("/api/control/reset").json() == {"reset": True}

    assert dummy_client.get("/api/batches/B-24187").json()["status"] == "QUEUED"
    assert dummy_client.get("/api/tickets").json() == []
    assert dummy_client.get("/api/scanner/scans").json()["lastSeq"] == 0
    assert dummy_client.get("/api/scales/scale-3kg/weight").json()["net"]["value"] == "0.0"
    assert all(dummy_client.get("/api/control/availability").json()["systems"].values())
