"""Confirm, overshoot, override, quit, completion + write-back, summary and records (bolt 007)."""

import logging
from typing import Any

import pytest
from fastapi.testclient import TestClient

from tests.conftest import set_available

PROTOTYPE_ACTUALS = {
    "B-24187-01": ("1241.5", "g"),
    "B-24187-02": ("385.4", "g"),
    "B-24187-03": ("94.2", "g"),
    "B-24187-04": ("23.980", "kg"),
    "B-24187-05": ("9.621", "kg"),
}


def _start(client: TestClient) -> dict[str, Any]:
    body: dict[str, Any] = client.post("/api/sessions", json={"batchId": "B-24187"}).json()
    return body


def _scale_of(session: dict[str, Any]) -> str:
    active = session["activeComponentId"]
    scale: str = next(c for c in session["components"] if c["componentId"] == active)["scale"][
        "scaleId"
    ]
    return scale


def _put(dummy: TestClient, session: dict[str, Any], value: str, unit: str) -> None:
    dummy.post(
        f"/api/control/scales/{_scale_of(session)}/simulate",
        json={"profile": "exact", "net": {"value": value, "unit": unit}},
    )


def _weigh_all(client: TestClient, dummy: TestClient) -> dict[str, Any]:
    session = _start(client)
    while session["status"] == "IN_PROGRESS":
        value, unit = PROTOTYPE_ACTUALS[session["activeComponentId"]]
        _put(dummy, session, value, unit)
        response = client.post(f"/api/sessions/{session['sessionId']}/confirm")
        assert response.status_code == 200, response.text
        session = response.json()
    return session


def test_confirm_records_and_advances_to_the_next_component(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    session = _start(wms_client)
    _put(dummy_client, session, "1241.5", "g")

    after = wms_client.post(f"/api/sessions/{session['sessionId']}/confirm").json()

    blue = after["components"][0]
    assert (blue["state"], blue["actual"]) == ("DONE", {"value": "1241.5", "unit": "g"})
    assert after["activeComponentId"] == "B-24187-02"
    assert after["progress"] == {"done": 1, "total": 5}
    records = wms_client.get("/api/weighing-records", params={"batchId": "B-24187"}).json()
    assert len(records) == 1
    record = records[0]
    assert record["result"] == "IN_TOLERANCE"
    assert record["actual"] == {"value": "1241.5", "unit": "g"}
    assert (record["toleranceMin"]["value"], record["toleranceMax"]["value"]) == (
        "1234.0",
        "1246.0",
    )
    assert (record["lotId"], record["containerId"], record["scaleId"]) == (
        "2026-0341",
        "C-09",
        "scale-3kg",
    )
    assert record["tare"] == {"value": "214.0", "unit": "g"}
    assert record["operatorId"] == "OP-1001"
    assert record["confirmedAt"]


def test_confirm_rereads_the_scale_and_rejects_out_of_tolerance(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    session = _start(wms_client)
    _put(dummy_client, session, "1200.0", "g")

    response = wms_client.post(f"/api/sessions/{session['sessionId']}/confirm")

    assert response.status_code == 409
    error = response.json()["error"]
    assert error["code"] == "OUT_OF_TOLERANCE"
    assert error["message"] == "Remazol Brill. Blue RSPL: 1200.0 g is outside 1234.0 – 1246.0 g."
    assert wms_client.get("/api/weighing-records", params={"batchId": "B-24187"}).json() == []


def test_confirm_with_the_scale_down_is_refused(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    session = _start(wms_client)
    _put(dummy_client, session, "1241.5", "g")
    set_available(dummy_client, "scale-3kg", False)

    response = wms_client.post(f"/api/sessions/{session['sessionId']}/confirm")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "SCALE_UNAVAILABLE"


def test_confirm_with_expired_calibration_is_refused(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    session = _start(wms_client)
    _put(dummy_client, session, "1241.5", "g")
    dummy_client.put(
        "/api/control/scales/scale-3kg/calibration", json={"calibrationDue": "2026-01-01"}
    )

    response = wms_client.post(f"/api/sessions/{session['sessionId']}/confirm")

    assert response.json()["error"]["code"] == "SCALE_CALIBRATION_EXPIRED"


def test_overshoot_blocks_then_recovery_by_removing_excess(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    session = _start(wms_client)
    sid = session["sessionId"]
    wms_client.post(f"/api/sessions/{sid}/components/B-24187-03/activate")
    _put(dummy_client, {**session, "activeComponentId": "B-24187-03"}, "96.4", "g")

    live = wms_client.get(f"/api/sessions/{sid}/live").json()
    blocked = wms_client.post(f"/api/sessions/{sid}/confirm")
    _put(dummy_client, {**session, "activeComponentId": "B-24187-03"}, "94.3", "g")
    recovered = wms_client.post(f"/api/sessions/{sid}/confirm")

    assert (live["zone"], live["canConfirm"]) == ("OVER", False)
    assert live["surplus"] == {"value": "2.4", "unit": "g"}
    assert set(live["allowedActions"]) == {"RETARE", "QUIT", "OVERRIDE"}
    assert "93.5 – 94.5 g" in live["guidance"]
    assert blocked.status_code == 409
    assert recovered.status_code == 200
    yellow = next(c for c in recovered.json()["components"] if c["componentId"] == "B-24187-03")
    assert yellow["actual"] == {"value": "94.3", "unit": "g"}


def test_supervisor_override(
    wms_client: TestClient, dummy_client: TestClient, container: Any
) -> None:
    session = _start(wms_client)
    sid = session["sessionId"]
    _put(dummy_client, session, "1260.0", "g")

    wrong_pin = wms_client.post(
        f"/api/sessions/{sid}/override", json={"supervisorPin": "1111", "reason": "Lab approved"}
    )
    no_reason = wms_client.post(
        f"/api/sessions/{sid}/override", json={"supervisorPin": "2468", "reason": ""}
    )
    ok = wms_client.post(
        f"/api/sessions/{sid}/override",
        json={"supervisorPin": "2468", "reason": "Lab approved the extra dye"},
    )

    assert wrong_pin.status_code == 403
    assert wrong_pin.json()["error"]["code"] == "OVERRIDE_NOT_AUTHORISED"
    assert no_reason.status_code == 422
    assert ok.status_code == 200
    assert ok.json()["components"][0]["state"] == "DONE"
    record = wms_client.get("/api/weighing-records", params={"batchId": "B-24187"}).json()[0]
    assert record["result"] == "OVERRIDDEN"
    assert record["surplus"] == {"value": "20.0", "unit": "g"}
    overrides = container.sessions.overrides_for_session(sid)
    assert [(o.supervisor_id, o.reason) for o in overrides] == [
        ("SV-2001", "Lab approved the extra dye")
    ]
    audit = [e for e in container.audit.events(sid) if e["type"] == "OVERRIDE"]
    assert audit[0]["actorId"] == "SV-2001"
    assert audit[0]["detail"]["reason"] == "Lab approved the extra dye"


def test_override_not_needed_within_tolerance(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    session = _start(wms_client)
    _put(dummy_client, session, "1240.0", "g")

    response = wms_client.post(
        f"/api/sessions/{session['sessionId']}/override",
        json={"supervisorPin": "2468", "reason": "x"},
    )

    assert response.json()["error"]["code"] == "OVERRIDE_NOT_NEEDED"


def test_pin_is_never_logged(
    wms_client: TestClient,
    dummy_client: TestClient,
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(logging.getLogger("weighingms"), "propagate", True)
    session = _start(wms_client)
    _put(dummy_client, session, "1260.0", "g")

    with caplog.at_level(logging.DEBUG):
        for pin in ("9753", "2468"):
            wms_client.post(
                f"/api/sessions/{session['sessionId']}/override",
                json={"supervisorPin": pin, "reason": "reason"},
            )

    assert "9753" not in caplog.text
    assert "2468" not in caplog.text


def test_quit_records_nothing_and_resume_keeps_done_components(
    wms_client: TestClient, dummy_client: TestClient, container: Any
) -> None:
    session = _start(wms_client)
    sid = session["sessionId"]
    _put(dummy_client, session, "1241.5", "g")
    session = wms_client.post(f"/api/sessions/{sid}/confirm").json()
    _put(dummy_client, session, "300.0", "g")

    quit_response = wms_client.post(f"/api/sessions/{sid}/quit").json()
    resumed = wms_client.post("/api/sessions", json={"batchId": "B-24187"})

    assert quit_response["activeComponentId"] is None
    assert quit_response["status"] == "IN_PROGRESS"
    assert len(wms_client.get("/api/weighing-records", params={"batchId": "B-24187"}).json()) == 1
    abandon = [e for e in container.audit.events(sid) if e["type"] == "ABANDON"]
    assert abandon[0]["detail"] == {"componentId": "B-24187-02", "netAtQuit": "300.0"}
    assert resumed.status_code == 200
    assert resumed.json()["progress"] == {"done": 1, "total": 5}
    assert resumed.json()["activeComponentId"] == "B-24187-02"


def test_incomplete_batch_cannot_be_completed(wms_client: TestClient) -> None:
    session = _start(wms_client)

    response = wms_client.post(f"/api/sessions/{session['sessionId']}/complete")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "BATCH_INCOMPLETE"


def test_full_batch_completes_and_writes_back_once(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    session = _weigh_all(wms_client, dummy_client)

    assert (session["status"], session["syncStatus"]) == ("COMPLETED", "SYNCED")
    postings = dummy_client.get("/api/batches/B-24187/consumption").json()
    assert len(postings) == 1
    posting = postings[0]["posting"]
    assert posting["idempotencyKey"] == session["sessionId"]
    assert [(line["componentId"], line["actual"]["value"]) for line in posting["lines"]] == [
        (cid, value) for cid, (value, _) in PROTOTYPE_ACTUALS.items()
    ]
    assert dummy_client.get("/api/batches/B-24187").json()["status"] == "WEIGHED"
    sid = session["sessionId"]
    assert wms_client.post(f"/api/sessions/{sid}/complete").status_code == 200
    assert wms_client.post(f"/api/sessions/{sid}/sync").json()["syncStatus"] == "SYNCED"
    assert len(dummy_client.get("/api/batches/B-24187/consumption").json()) == 1


def test_orgatex_down_at_completion_leaves_write_back_pending_then_retry(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    session = _start(wms_client)
    sid = session["sessionId"]
    while session["progress"]["done"] < 4:
        value, unit = PROTOTYPE_ACTUALS[session["activeComponentId"]]
        _put(dummy_client, session, value, unit)
        session = wms_client.post(f"/api/sessions/{sid}/confirm").json()
    set_available(dummy_client, "orgatex", False)
    _put(dummy_client, session, "9.621", "kg")

    completed = wms_client.post(f"/api/sessions/{sid}/confirm").json()
    still_down = wms_client.post(f"/api/sessions/{sid}/sync").json()
    set_available(dummy_client, "orgatex", True)
    retried = wms_client.post(f"/api/sessions/{sid}/sync").json()

    assert (completed["status"], completed["syncStatus"]) == ("COMPLETED", "PENDING")
    assert still_down["syncStatus"] == "PENDING"
    assert retried["syncStatus"] == "SYNCED"
    assert len(dummy_client.get("/api/batches/B-24187/consumption").json()) == 1


def test_summary_matches_the_prototype_screen_3(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    session = _weigh_all(wms_client, dummy_client)

    summary = wms_client.get(f"/api/sessions/{session['sessionId']}/summary").json()

    assert summary["completed"] is True
    assert summary["componentsWeighed"] == {"done": 5, "total": 5}
    assert summary["allWithinTolerance"] is True
    assert summary["totalDispensed"] == {"value": "35.322", "unit": "kg"}
    assert summary["operatorName"] == "R. Karim"
    assert summary["elapsedText"].endswith(" s")
    assert summary["writeBack"]["status"] == "SYNCED"
    assert summary["writeBack"]["consumptionId"].startswith("CNS-")
    assert [(r["shortName"], r["actual"]["value"], r["result"]) for r in summary["results"]] == [
        ("Blue RSPL", "1241.5", "IN_TOLERANCE"),
        ("Red RB", "385.4", "IN_TOLERANCE"),
        ("Yellow RGB", "94.2", "IN_TOLERANCE"),
        ("Na2SO4", "23.980", "IN_TOLERANCE"),
        ("Soda Ash", "9.621", "IN_TOLERANCE"),
    ]


def test_completed_session_rejects_further_weighing(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    session = _weigh_all(wms_client, dummy_client)
    sid = session["sessionId"]

    for path in ("confirm", "quit"):
        response = wms_client.post(f"/api/sessions/{sid}/{path}")
        assert response.json()["error"]["code"] == "SESSION_COMPLETED"
    assert wms_client.post("/api/sessions", json={"batchId": "B-24187"}).status_code == 409
