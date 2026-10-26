"""Session, operator and session-aware training endpoints (bolt 006-weighing-station)."""

from dataclasses import replace
from typing import Any

from fastapi.testclient import TestClient

from tests.conftest import FakeTicker, set_available
from weighingms.api.app import create_app
from weighingms.api.container import build_container
from weighingms.domain.weighing.session import ComponentState


def _start(client: TestClient, batch_id: str = "B-24187") -> dict[str, Any]:
    response = client.post("/api/sessions", json={"batchId": batch_id})
    assert response.status_code in (200, 201), response.text
    body: dict[str, Any] = response.json()
    return body


def _weigh(dummy: TestClient, scale: str, value: str, unit: str) -> None:
    dummy.post(
        f"/api/control/scales/{scale}/simulate",
        json={"profile": "exact", "net": {"value": value, "unit": unit}},
    )


def _live(client: TestClient, sid: str) -> dict[str, Any]:
    body: dict[str, Any] = client.get(f"/api/sessions/{sid}/live").json()
    return body


def test_start_session_activates_the_first_component(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    response = wms_client.post("/api/sessions", json={"batchId": "B-24187"})

    assert response.status_code == 201
    session = response.json()
    assert session["status"] == "IN_PROGRESS"
    assert session["progress"] == {"done": 0, "total": 5}
    assert session["activeComponentId"] == "B-24187-01"
    assert [c["state"] for c in session["components"]] == ["ACTIVE"] + ["PENDING"] * 4
    assert session["active"] == {
        "componentId": "B-24187-01",
        "containerId": "C-09",
        "tare": {"value": "214.0", "unit": "g"},
        "displayMax": {"value": "1650.0", "unit": "g"},
    }
    assert (session["orderRef"], session["machineRef"], session["shadeCode"]) == (
        "SO-9931",
        "JET-04",
        "Teal 4C",
    )
    assert dummy_client.get("/api/batches/B-24187").json()["status"] == "WEIGHING"


def test_selecting_the_batch_again_resumes_the_same_session(wms_client: TestClient) -> None:
    first = _start(wms_client)
    wms_client.post(f"/api/sessions/{first['sessionId']}/components/B-24187-03/activate")

    again = wms_client.post("/api/sessions", json={"batchId": "B-24187"})

    assert again.status_code == 200
    assert again.json()["sessionId"] == first["sessionId"]
    assert again.json()["activeComponentId"] == "B-24187-03"


def test_session_survives_an_app_restart(
    wms_client: TestClient, settings: Any, dummy_client: TestClient
) -> None:
    sid = _start(wms_client)["sessionId"]
    restarted = build_container(settings, orgatex_client=dummy_client, devices_client=dummy_client)

    with TestClient(create_app(restarted)) as client:
        assert client.get(f"/api/sessions/{sid}").json()["activeComponentId"] == "B-24187-01"


def test_weighed_batch_cannot_be_started(wms_client: TestClient, dummy_client: TestClient) -> None:
    dummy_client.patch("/api/batches/B-24188/status", json={"status": "WEIGHED"})

    response = wms_client.post("/api/sessions", json={"batchId": "B-24188"})

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "BATCH_NOT_SELECTABLE"


def test_unknown_batch_and_orgatex_down(wms_client: TestClient, dummy_client: TestClient) -> None:
    assert wms_client.post("/api/sessions", json={"batchId": "B-0"}).status_code == 404
    set_available(dummy_client, "orgatex", False)

    response = wms_client.post("/api/sessions", json={"batchId": "B-24187"})

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "ORGATEX_UNAVAILABLE"


def test_weighing_in_progress_continues_when_orgatex_drops(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    sid = _start(wms_client)["sessionId"]
    set_available(dummy_client, "orgatex", False)

    assert wms_client.post("/api/sessions", json={"batchId": "B-24187"}).status_code == 200
    activated = wms_client.post(f"/api/sessions/{sid}/components/B-24187-02/activate")
    assert activated.status_code == 200
    assert _live(wms_client, sid)["componentId"] == "B-24187-02"


def test_live_evaluation_tolerance_boundaries(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    sid = _start(wms_client)["sessionId"]
    wms_client.post(f"/api/sessions/{sid}/components/B-24187-03/activate")

    results = {}
    for value in ("93.4", "93.5", "94.0", "94.5", "94.6"):
        _weigh(dummy_client, "scale-3kg", value, "g")
        live = _live(wms_client, sid)
        results[value] = (live["zone"], live["canConfirm"])

    assert results == {
        "93.4": ("NEAR", False),
        "93.5": ("WITHIN", True),
        "94.0": ("WITHIN", True),
        "94.5": ("WITHIN", True),
        "94.6": ("OVER", False),
    }


def test_overshoot_surplus_in_live_response(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    sid = _start(wms_client)["sessionId"]
    wms_client.post(f"/api/sessions/{sid}/components/B-24187-03/activate")
    _weigh(dummy_client, "scale-3kg", "96.4", "g")

    live = _live(wms_client, sid)

    assert live["surplus"] == {"value": "2.4", "unit": "g"}
    assert live["surplusPct"] == "2.6"
    assert live["statusText"] == "OVER TOLERANCE — SURPLUS +2.4 g"


def test_scale_switch_to_the_floor_scale(wms_client: TestClient, dummy_client: TestClient) -> None:
    sid = _start(wms_client)["sessionId"]

    session = wms_client.post(f"/api/sessions/{sid}/components/B-24187-04/activate").json()
    _weigh(dummy_client, "scale-32kg", "24.048", "kg")
    live = _live(wms_client, sid)

    assert session["active"]["containerId"] == "D-03"
    assert session["active"]["tare"] == {"value": "1.850", "unit": "kg"}
    assert live["scaleId"] == "scale-32kg"
    assert live["net"] == {"value": "24.048", "unit": "kg"}
    assert live["zone"] == "WITHIN"
    states = {c["componentId"]: c["state"] for c in session["components"]}
    assert states["B-24187-01"] == "PENDING"
    assert states["B-24187-04"] == "ACTIVE"


def test_activation_tares_the_scale(wms_client: TestClient, dummy_client: TestClient) -> None:
    _weigh(dummy_client, "scale-3kg", "214.0", "g")  # empty container on the scale

    sid = _start(wms_client)["sessionId"]

    assert _live(wms_client, sid)["net"] == {"value": "0.0", "unit": "g"}


def test_retare_resets_the_weight(wms_client: TestClient, dummy_client: TestClient) -> None:
    sid = _start(wms_client)["sessionId"]
    _weigh(dummy_client, "scale-3kg", "50.0", "g")

    live = wms_client.post(f"/api/sessions/{sid}/retare").json()

    assert live["net"] == {"value": "0.0", "unit": "g"}


def test_scale_offline_and_calibration_expired(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    sid = _start(wms_client)["sessionId"]
    _weigh(dummy_client, "scale-3kg", "1240.0", "g")
    set_available(dummy_client, "scale-3kg", False)

    offline = _live(wms_client, sid)
    assert (offline["zone"], offline["canConfirm"], offline["net"]) == ("OFFLINE", False, None)
    assert wms_client.post(f"/api/sessions/{sid}/retare").status_code == 503

    set_available(dummy_client, "scale-3kg", True)
    wms_client.put(
        "/api/training/scales/scale-3kg/calibration", json={"calibrationDue": "2026-01-01"}
    )
    other = _start(wms_client, "B-24190")["sessionId"]  # fresh calibration lookup
    _weigh(dummy_client, "scale-3kg", "2480.0", "g")
    expired = _live(wms_client, other)
    assert expired["calibrationValid"] is False
    assert expired["canConfirm"] is False


def test_done_component_cannot_be_activated(wms_client: TestClient, container: Any) -> None:
    sid = _start(wms_client)["sessionId"]
    session = container.sessions.get(sid)
    session.progress_of("B-24187-02").state = ComponentState.DONE
    container.sessions._sessions.save(session)

    response = wms_client.post(f"/api/sessions/{sid}/components/B-24187-02/activate")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "COMPONENT_ALREADY_DONE"


def test_unknown_session(wms_client: TestClient) -> None:
    response = wms_client.get("/api/sessions/WS-NOPE/live")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "SESSION_NOT_FOUND"


def test_operator_identification(wms_client: TestClient, container: Any) -> None:
    assert wms_client.get("/api/operators/current").json() == {
        "operatorId": "OP-1001",
        "name": "R. Karim",
        "shift": "Shift A",
        "role": "OPERATOR",
    }

    signed_in = wms_client.post("/api/operators/sign-in", json={"badgeId": "1002"}).json()

    assert signed_in["name"] == "M. Hossain"
    assert wms_client.get("/api/operators/current").json()["operatorId"] == "OP-1002"
    assert [e["type"] for e in container.audit.events()] == ["OPERATOR_CHANGE"]
    unknown = wms_client.post("/api/operators/sign-in", json={"badgeId": "0000"})
    assert unknown.status_code == 404
    assert unknown.json()["error"]["code"] == "OPERATOR_NOT_FOUND"


def test_session_records_the_operator_who_started_it(
    wms_client: TestClient, container: Any
) -> None:
    wms_client.post("/api/operators/sign-in", json={"badgeId": "1002"})

    sid = _start(wms_client)["sessionId"]

    assert container.sessions.get(sid).started_by == "OP-1002"


def test_training_simulation_uses_the_active_component(
    wms_client: TestClient, ticker: FakeTicker
) -> None:
    sid = _start(wms_client)["sessionId"]
    wms_client.post(f"/api/sessions/{sid}/components/B-24187-03/activate")

    dispense = wms_client.post(
        "/api/training/simulate", json={"sessionId": sid, "kind": "dispense"}
    )
    ticker.advance(60)

    assert dispense.json()["landing"] == {"value": "94.2", "unit": "g"}
    assert _live(wms_client, sid)["net"] == {"value": "94.2", "unit": "g"}

    overshoot = wms_client.post(
        "/api/training/simulate", json={"sessionId": sid, "kind": "overshoot"}
    )
    ticker.advance(60)
    assert overshoot.json()["landing"] == {"value": "96.4", "unit": "g"}
    assert _live(wms_client, sid)["zone"] == "OVER"

    wms_client.post("/api/training/reset-weighing", json={"sessionId": sid})
    assert _live(wms_client, sid)["net"] == {"value": "0.0", "unit": "g"}


def test_training_reset_clears_sessions_and_operator(wms_client: TestClient) -> None:
    sid = _start(wms_client)["sessionId"]
    wms_client.post("/api/operators/sign-in", json={"badgeId": "1002"})

    wms_client.post("/api/training/reset")

    assert wms_client.get(f"/api/sessions/{sid}").status_code == 404
    assert wms_client.get("/api/operators/current").json()["operatorId"] == "OP-1001"


def test_training_routes_absent_when_training_mode_is_off(
    settings: Any, dummy_client: TestClient
) -> None:
    production = replace(settings, station=replace(settings.station, training_mode=False))
    built = build_container(production, orgatex_client=dummy_client, devices_client=dummy_client)

    with TestClient(create_app(built)) as client:
        assert client.get("/api/training/availability").status_code == 404
        assert client.get("/api/batches").status_code == 200
