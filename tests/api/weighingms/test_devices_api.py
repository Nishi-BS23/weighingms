"""Device status, scans and training endpoints (unit 004-device-integration)."""

from fastapi.testclient import TestClient

from tests.conftest import set_available


def _states(client: TestClient) -> dict[str, tuple[str, str]]:
    body = client.get("/api/devices/status").json()
    return {d["device"]: (d["state"], d["text"]) for d in body["devices"]}


def test_device_status_all_up(wms_client: TestClient) -> None:
    body = wms_client.get("/api/devices/status").json()

    assert body["stationName"] == "STATION 01"
    assert body["language"] == "EN"
    assert [d["label"] for d in body["devices"]] == [
        "SCALE 3 kg",
        "SCALE 32 kg",
        "SCANNER",
        "PRINTER",
        "ORGATEX",
    ]
    assert all(d["state"] == "UP" for d in body["devices"])
    assert body["orgatexLastContact"] is not None


def test_failed_devices_are_reported(wms_client: TestClient, dummy_client: TestClient) -> None:
    for system in ("scale-3kg", "scanner", "printer", "orgatex"):
        set_available(dummy_client, system, False)

    states = _states(wms_client)

    assert states == {
        "scale-3kg": ("DOWN", "OFFLINE"),
        "scale-32kg": ("UP", "READY"),
        "scanner": ("DOWN", "OFFLINE"),
        "printer": ("DOWN", "OFFLINE"),
        "orgatex": ("DOWN", "OFFLINE"),
    }


def test_expired_calibration_is_degraded(wms_client: TestClient) -> None:
    wms_client.put(
        "/api/training/scales/scale-32kg/calibration", json={"calibrationDue": "2026-01-01"}
    )

    assert _states(wms_client)["scale-32kg"] == ("DEGRADED", "CAL EXPIRED")


def test_scans_via_training_and_scanner_endpoints(wms_client: TestClient) -> None:
    scan = wms_client.post("/api/training/scan", json={"code": "B-24187"}).json()

    assert scan["seq"] == 1
    batch = wms_client.get("/api/scanner/scans", params={"after": 0}).json()
    assert [s["code"] for s in batch["scans"]] == ["B-24187"]
    assert batch["lastSeq"] == 1


def test_scanner_down_is_503(wms_client: TestClient, dummy_client: TestClient) -> None:
    set_available(dummy_client, "scanner", False)

    response = wms_client.get("/api/scanner/scans")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "SCANNER_UNAVAILABLE"


def test_training_availability_simulate_and_reset(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    toggled = wms_client.put("/api/training/availability/printer", json={"available": False})
    assert toggled.json()["systems"]["printer"] is False

    simulated = wms_client.post(
        "/api/training/scales/scale-3kg/simulate",
        json={"profile": "exact", "net": {"value": "94.0", "unit": "g"}},
    )
    assert simulated.status_code == 200
    assert dummy_client.get("/api/scales/scale-3kg/weight").json()["net"]["value"] == "94.0"

    assert wms_client.post("/api/training/reset").json() == {"reset": True}
    assert all(wms_client.get("/api/training/availability").json()["systems"].values())


def test_training_validation(wms_client: TestClient) -> None:
    response = wms_client.post("/api/training/scan", json={"code": ""})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_invalid_simulated_weight_is_rejected(wms_client: TestClient) -> None:
    for value in ("-5", "abc", "1e3", ""):
        response = wms_client.post(
            "/api/training/scales/scale-3kg/simulate",
            json={"profile": "exact", "net": {"value": value, "unit": "g"}},
        )

        assert response.status_code == 422, value
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"
