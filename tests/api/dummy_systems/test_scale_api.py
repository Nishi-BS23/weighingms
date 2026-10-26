"""Dummy Scale training contract (story 004 of unit 001-training-substitutes)."""

from typing import Any

from fastapi.testclient import TestClient

from tests.conftest import FakeTicker


def _simulate(client: TestClient, scale: str, profile: str, value: str, unit: str) -> Any:
    body = {"profile": profile, "net": {"value": value, "unit": unit}}
    return client.post(f"/api/control/scales/{scale}/simulate", json=body)


def _net(client: TestClient, scale: str) -> dict[str, Any]:
    reading: dict[str, Any] = client.get(f"/api/scales/{scale}/weight").json()
    return reading


def test_two_scales_are_listed(dummy_client: TestClient) -> None:
    scales = dummy_client.get("/api/scales").json()

    assert [(s["scaleId"], s["scaleClass"], s["label"]) for s in scales] == [
        ("scale-3kg", "PRECISION", "3 kg precision"),
        ("scale-32kg", "FLOOR", "32 kg floor"),
    ]
    assert scales[0]["capacity"] == {"value": "3", "unit": "kg"}
    assert scales[0]["resolution"] == {"value": "0.1", "unit": "g"}
    assert scales[1]["resolution"] == {"value": "0.001", "unit": "kg"}
    assert all(s["available"] for s in scales)


def test_initial_reading_is_zero_and_stable(dummy_client: TestClient) -> None:
    reading = _net(dummy_client, "scale-3kg")

    assert reading["net"] == {"value": "0.0", "unit": "g"}
    assert reading["gross"] == {"value": "0.0", "unit": "g"}
    assert reading["stable"] is True
    assert reading["readAt"] == "2026-10-26T07:47:03Z"


def test_exact_profile_is_deterministic(dummy_client: TestClient) -> None:
    _simulate(dummy_client, "scale-3kg", "exact", "93.4", "g")

    assert _net(dummy_client, "scale-3kg")["net"] == {"value": "93.4", "unit": "g"}


def test_readings_are_rounded_to_the_scale_resolution(dummy_client: TestClient) -> None:
    _simulate(dummy_client, "scale-3kg", "exact", "93.46", "g")
    _simulate(dummy_client, "scale-32kg", "exact", "23.8804", "kg")

    assert _net(dummy_client, "scale-3kg")["net"]["value"] == "93.5"
    assert _net(dummy_client, "scale-32kg")["net"]["value"] == "23.880"


def test_units_are_converted_exactly(dummy_client: TestClient) -> None:
    _simulate(dummy_client, "scale-32kg", "exact", "1850", "g")

    assert _net(dummy_client, "scale-32kg")["net"] == {"value": "1.850", "unit": "kg"}


def test_dispense_ramp_rises_then_settles_on_the_landing_value(
    dummy_client: TestClient, ticker: FakeTicker
) -> None:
    _simulate(dummy_client, "scale-3kg", "dispense", "94.2", "g")

    ticker.advance(0.2)
    moving = _net(dummy_client, "scale-3kg")
    ticker.advance(60)
    settled = _net(dummy_client, "scale-3kg")

    assert 0 < float(moving["net"]["value"]) < 94.2
    assert moving["stable"] is False
    assert settled["net"]["value"] == "94.2"
    assert settled["stable"] is True


def test_tare_zeroes_the_net_weight(dummy_client: TestClient) -> None:
    _simulate(dummy_client, "scale-32kg", "exact", "1.850", "kg")

    reading = dummy_client.post("/api/scales/scale-32kg/tare").json()

    assert reading["net"]["value"] == "0.000"
    assert reading["tare"]["value"] == "1.850"
    assert reading["gross"]["value"] == "1.850"


def test_tare_during_a_ramp_continues_relative_to_the_new_tare(
    dummy_client: TestClient, ticker: FakeTicker
) -> None:
    _simulate(dummy_client, "scale-3kg", "dispense", "100.0", "g")
    ticker.advance(0.5)
    before = float(_net(dummy_client, "scale-3kg")["net"]["value"])

    dummy_client.post("/api/scales/scale-3kg/tare")
    ticker.advance(60)

    expected = round(100.0 - before, 1)
    assert float(_net(dummy_client, "scale-3kg")["net"]["value"]) == expected


def test_readings_are_clamped_to_capacity(dummy_client: TestClient) -> None:
    _simulate(dummy_client, "scale-3kg", "exact", "3500", "g")

    assert _net(dummy_client, "scale-3kg")["gross"]["value"] == "3000.0"


def test_negative_weight_is_rejected(dummy_client: TestClient) -> None:
    response = _simulate(dummy_client, "scale-3kg", "exact", "-1", "g")

    assert response.status_code == 422


def test_unknown_scale_is_404(dummy_client: TestClient) -> None:
    for response in (
        dummy_client.get("/api/scales/scale-99/weight"),
        dummy_client.get("/api/scales/scale-99/status"),
        dummy_client.post("/api/scales/scale-99/tare"),
    ):
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "SCALE_NOT_FOUND"


def test_status_reports_calibration(dummy_client: TestClient) -> None:
    status = dummy_client.get("/api/scales/scale-3kg/status").json()

    assert status["calibrationValid"] is True
    assert status["simulating"] is False

    dummy_client.put(
        "/api/control/scales/scale-3kg/calibration", json={"calibrationDue": "2026-01-01"}
    )
    expired = dummy_client.get("/api/scales/scale-3kg/status").json()
    assert expired["calibrationValid"] is False
    assert expired["calibrationDue"] == "2026-01-01"


def test_load_places_a_new_container(dummy_client: TestClient) -> None:
    _simulate(dummy_client, "scale-32kg", "exact", "23.980", "kg")
    dummy_client.post("/api/scales/scale-32kg/tare")

    dummy_client.post(
        "/api/control/scales/scale-32kg/load", json={"gross": {"value": "1.850", "unit": "kg"}}
    )
    reading = dummy_client.post("/api/scales/scale-32kg/tare").json()

    assert (reading["gross"]["value"], reading["tare"]["value"], reading["net"]["value"]) == (
        "1.850",
        "1.850",
        "0.000",
    )
    negative = dummy_client.post(
        "/api/control/scales/scale-32kg/load", json={"gross": {"value": "-1", "unit": "kg"}}
    )
    assert negative.status_code == 422
