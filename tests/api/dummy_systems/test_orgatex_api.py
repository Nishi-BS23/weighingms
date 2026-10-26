"""Dummy OrgaTEX training contract (stories 001-003 of unit 001-training-substitutes)."""

from typing import Any

from fastapi.testclient import TestClient

PROTOTYPE_RECIPE = [
    # (sequence, code, name, target, unit, tolerance, lot)
    (1, "DYE-1180", "Remazol Brill. Blue RSPL", "1240.0", "g", "6.0", "2026-0341"),
    (2, "DYE-2204", "Remazol Red RB", "386.0", "g", "2.0", "2026-0298"),
    (3, "DYE-4471", "Remazol Yellow RGB", "94.0", "g", "0.5", "2026-0387"),
    (4, "AUX-0101", "Sodium Sulphate", "24.000", "kg", "0.120", "2026-0112"),
    (5, "AUX-0107", "Soda Ash", "9.600", "kg", "0.048", "2026-0155"),
]


def _posting(key: str = "SESSION-1") -> dict[str, Any]:
    return {
        "idempotencyKey": key,
        "sessionId": key,
        "stationId": "STN-01",
        "operatorId": "OP-1001",
        "completedAt": "2026-10-26T07:48:22Z",
        "lines": [
            {
                "componentId": "B-24187-03",
                "dyestuffCode": "DYE-4471",
                "lotId": "2026-0387",
                "target": {"value": "94.0", "unit": "g"},
                "actual": {"value": "94.2", "unit": "g"},
                "scaleId": "scale-3kg",
                "operatorId": "OP-1001",
                "confirmedAt": "2026-10-26T07:45:00Z",
                "result": "IN_TOLERANCE",
            }
        ],
    }


def test_batch_queue_lists_the_four_prototype_batches(dummy_client: TestClient) -> None:
    response = dummy_client.get("/api/batches")

    assert response.status_code == 200
    body = response.json()
    assert body["generatedAt"] == "2026-10-26T07:47:03Z"
    assert [b["batchId"] for b in body["batches"]] == ["B-24187", "B-24188", "B-24190", "B-24191"]
    assert set(body["batches"][0]) == {
        "batchId",
        "orderRef",
        "machineRef",
        "fabricDesc",
        "fabricWeightKg",
        "shadeCode",
        "recipeId",
        "componentCount",
        "status",
        "releasedAt",
    }


def test_batch_queue_filters_by_status(dummy_client: TestClient) -> None:
    dummy_client.patch("/api/batches/B-24188/status", json={"status": "WEIGHED"})

    queued = dummy_client.get("/api/batches", params={"status": "QUEUED"}).json()["batches"]

    assert [b["batchId"] for b in queued] == ["B-24187", "B-24190", "B-24191"]


def test_batch_detail_matches_the_prototype(dummy_client: TestClient) -> None:
    batch = dummy_client.get("/api/batches/B-24187").json()

    assert batch["orderRef"] == "SO-9931"
    assert batch["machineRef"] == "JET-04"
    assert batch["fabricDesc"] == "100% CTN knit"
    assert batch["fabricWeightKg"] == "480"
    assert batch["shadeCode"] == "Teal 4C"
    assert batch["componentCount"] == 5
    assert batch["status"] == "QUEUED"


def test_unknown_batch_returns_standard_404(dummy_client: TestClient) -> None:
    for path in ("/api/batches/B-00000", "/api/batches/B-00000/recipe"):
        response = dummy_client.get(path)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "BATCH_NOT_FOUND"


def test_recipe_for_b24187_is_exactly_the_prototype_recipe(dummy_client: TestClient) -> None:
    recipe = dummy_client.get("/api/batches/B-24187/recipe").json()

    assert recipe["shadeCode"] == "Teal 4C"
    actual = [
        (
            c["sequence"],
            c["dyestuffCode"],
            c["name"],
            c["targetQty"]["value"],
            c["targetQty"]["unit"],
            c["tolerance"]["value"],
            c["lotId"],
        )
        for c in recipe["components"]
    ]
    assert actual == PROTOTYPE_RECIPE


def test_quantities_are_serialised_as_strings(dummy_client: TestClient) -> None:
    recipe = dummy_client.get("/api/batches/B-24187/recipe").json()

    for component in recipe["components"]:
        assert isinstance(component["targetQty"]["value"], str)
        assert isinstance(component["tolerance"]["value"], str)


def test_every_batch_has_a_consistent_recipe(dummy_client: TestClient) -> None:
    for batch in dummy_client.get("/api/batches").json()["batches"]:
        recipe = dummy_client.get(f"/api/batches/{batch['batchId']}/recipe").json()
        assert len(recipe["components"]) == batch["componentCount"]
        if batch["batchId"] != "B-24187":
            assert "invented training data" in recipe["trainingDataNote"]


def test_component_without_tolerance_is_allowed(dummy_client: TestClient) -> None:
    recipe = dummy_client.get("/api/batches/B-24190/recipe").json()

    soda_ash = recipe["components"][-1]
    assert soda_ash["name"] == "Soda Ash"
    assert soda_ash["tolerance"] is None


def test_consumption_posting_is_stored_and_retrievable(dummy_client: TestClient) -> None:
    response = dummy_client.post("/api/batches/B-24187/consumption", json=_posting())

    assert response.status_code == 200
    receipt = response.json()
    assert receipt["duplicate"] is False
    assert receipt["consumptionId"].startswith("CNS-")
    stored = dummy_client.get("/api/batches/B-24187/consumption").json()
    assert len(stored) == 1
    assert stored[0]["posting"]["lines"][0]["actual"] == {"value": "94.2", "unit": "g"}


def test_consumption_posting_is_idempotent(dummy_client: TestClient) -> None:
    first = dummy_client.post("/api/batches/B-24187/consumption", json=_posting()).json()
    second = dummy_client.post("/api/batches/B-24187/consumption", json=_posting()).json()

    assert second["duplicate"] is True
    assert second["consumptionId"] == first["consumptionId"]
    assert len(dummy_client.get("/api/batches/B-24187/consumption").json()) == 1


def test_consumption_posting_validation(dummy_client: TestClient) -> None:
    no_lines = {**_posting(), "lines": []}

    assert dummy_client.post("/api/batches/B-24187/consumption", json=no_lines).status_code == 422
    unknown = dummy_client.post("/api/batches/B-00000/consumption", json=_posting())
    assert unknown.status_code == 404


def test_status_write_back_is_visible_in_the_queue(dummy_client: TestClient) -> None:
    response = dummy_client.patch("/api/batches/B-24187/status", json={"status": "WEIGHING"})

    assert response.status_code == 200
    assert response.json()["status"] == "WEIGHING"
    queue = dummy_client.get("/api/batches").json()["batches"]
    assert queue[0]["status"] == "WEIGHING"


def test_invalid_status_is_rejected(dummy_client: TestClient) -> None:
    response = dummy_client.patch("/api/batches/B-24187/status", json={"status": "DONE"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_unknown_route_uses_standard_error_body(dummy_client: TestClient) -> None:
    response = dummy_client.get("/api/nothing-here")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
