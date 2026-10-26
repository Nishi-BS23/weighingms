"""WeighingMS batch endpoints used by Screen 1 and the recipe rail (FR-1, FR-3, FR-4)."""

from fastapi.testclient import TestClient

from tests.conftest import set_available

EXPECTED_RECIPE = [
    # (short name, target, unit, min, max, scale)
    ("Blue RSPL", "1240.0", "g", "1234.0", "1246.0", "3 kg precision"),
    ("Red RB", "386.0", "g", "384.0", "388.0", "3 kg precision"),
    ("Yellow RGB", "94.0", "g", "93.5", "94.5", "3 kg precision"),
    ("Na2SO4", "24.000", "kg", "23.880", "24.120", "32 kg floor"),
    ("Soda Ash", "9.600", "kg", "9.552", "9.648", "32 kg floor"),
]


def test_queue_comes_from_orgatex_with_station_fields(wms_client: TestClient) -> None:
    response = wms_client.get("/api/batches")

    assert response.status_code == 200
    body = response.json()
    assert body["receivedAt"] == "2026-10-26T07:47:03Z"
    rows = [(b["batchId"], b["fabricLot"], b["status"], b["selectable"]) for b in body["batches"]]
    assert rows == [
        ("B-24187", "100% CTN knit · 480 kg", "QUEUED", True),
        ("B-24188", "100% CTN knit · 520 kg", "QUEUED", True),
        ("B-24190", "CVC fleece · 310 kg", "QUEUED", True),
        ("B-24191", "Viscose jersey · 190 kg", "QUEUED", True),
    ]
    assert response.headers["X-Request-ID"]


def test_weighed_batch_is_not_selectable(wms_client: TestClient, dummy_client: TestClient) -> None:
    dummy_client.patch("/api/batches/B-24188/status", json={"status": "WEIGHED"})

    batch = wms_client.get("/api/batches/B-24188").json()

    assert batch["selectable"] is False
    assert batch["notSelectableReason"] == "Batch has already been weighed."


def test_batch_detail(wms_client: TestClient) -> None:
    batch = wms_client.get("/api/batches/B-24187").json()

    assert (batch["orderRef"], batch["machineRef"], batch["shadeCode"]) == (
        "SO-9931",
        "JET-04",
        "Teal 4C",
    )
    assert batch["componentCount"] == 5
    assert batch["fabricWeightKg"] == "480"


def test_recipe_is_enriched_with_scale_and_band(wms_client: TestClient) -> None:
    recipe = wms_client.get("/api/batches/B-24187/recipe").json()

    actual = [
        (
            c["shortName"],
            c["target"]["value"],
            c["target"]["unit"],
            c["tolerance"]["minimum"]["value"],
            c["tolerance"]["maximum"]["value"],
            c["scale"]["label"],
        )
        for c in recipe["components"]
    ]
    assert actual == EXPECTED_RECIPE
    yellow = recipe["components"][2]
    assert yellow["dyestuffCode"] == "DYE-4471"
    assert yellow["lotId"] == "2026-0387"
    assert yellow["colourHex"] == "#d9a520"
    assert yellow["tolerance"]["plusMinus"] == {"value": "0.5", "unit": "g"}
    assert yellow["tolerance"]["source"] == "RECIPE"


def test_default_tolerance_is_used_when_recipe_has_none(wms_client: TestClient) -> None:
    soda_ash = wms_client.get("/api/batches/B-24190/recipe").json()["components"][-1]

    assert soda_ash["tolerance"]["source"] == "DEFAULT"
    assert soda_ash["tolerance"]["plusMinus"] == {"value": "0.031", "unit": "kg"}


def test_unknown_batch_is_404(wms_client: TestClient) -> None:
    response = wms_client.get("/api/batches/B-00000/recipe")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "BATCH_NOT_FOUND"


def test_orgatex_unavailable_is_503_with_a_plain_message(
    wms_client: TestClient, dummy_client: TestClient
) -> None:
    set_available(dummy_client, "orgatex", False)

    response = wms_client.get("/api/batches")

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "ORGATEX_UNAVAILABLE"
    assert error["message"] == "OrgaTEX is not reachable. Check the connection and retry."


def test_validation_and_unknown_route_errors_use_the_standard_body(wms_client: TestClient) -> None:
    response = wms_client.get("/api/nope")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_health(wms_client: TestClient) -> None:
    assert wms_client.get("/api/health").json() == {"status": "ok", "service": "weighingms"}
