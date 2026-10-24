import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api import get_repository
from app.main import app
from app.snapshot import SnapshotRepository


def snapshot_payload() -> dict[str, object]:
    return {
        "schemaVersion": "1.0",
        "generatedAt": "2026-02-03T12:00:00Z",
        "period": {
            "start": "2026-01-01T00:00:00Z",
            "endExclusive": "2026-02-01T00:00:00Z",
            "timezone": "GMT (UTC)",
        },
        "methodology": {},
        "provenance": {
            "forecastSource": "https://example.test/WINDFOR",
            "actualSource": "https://example.test/FUELHH",
        },
        "coverage": {
            "expectedHours": 3,
            "forecastHours": 3,
            "actualHours": 3,
            "completeHours": 3,
            "coveragePercent": 100,
        },
        "hours": [
            {
                "startTime": "2026-01-01T00:00:00Z",
                "forecastMw": 110,
                "actualMw": 100,
                "errorMw": 10,
                "forecastPublishTime": "2025-12-31T08:30:00Z",
                "decisionCutoff": "2025-12-31T09:50:00Z",
            },
            {
                "startTime": "2026-01-01T01:00:00Z",
                "forecastMw": 180,
                "actualMw": 200,
                "errorMw": -20,
                "forecastPublishTime": "2025-12-31T09:30:00Z",
                "decisionCutoff": "2025-12-31T09:50:00Z",
            },
            {
                "startTime": "2026-01-02T00:00:00Z",
                "forecastMw": 330,
                "actualMw": 300,
                "errorMw": 30,
                "forecastPublishTime": "2026-01-01T08:30:00Z",
                "decisionCutoff": "2026-01-01T09:50:00Z",
            },
        ],
        "forecastEvolution": [
            {
                "startTime": "2026-01-01T00:00:00Z",
                "publishTime": "2025-12-31T08:00:00Z",
                "generationMw": 105,
                "eligibleAtCutoff": True,
            },
            {
                "startTime": "2026-01-01T00:00:00Z",
                "publishTime": "2025-12-31T08:30:00Z",
                "generationMw": 110,
                "eligibleAtCutoff": True,
            },
            {
                "startTime": "2026-01-01T00:00:00Z",
                "publishTime": "2025-12-31T10:30:00Z",
                "generationMw": 125,
                "eligibleAtCutoff": False,
            },
        ],
    }


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text(json.dumps(snapshot_payload()), encoding="utf-8")
    repository = SnapshotRepository(snapshot_path)
    app.dependency_overrides[get_repository] = lambda: repository
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_overview_returns_metrics_for_requested_inclusive_dates(client: TestClient) -> None:
    response = client.get("/api/v1/overview?from=2026-01-01&to=2026-01-01")

    assert response.status_code == 200
    body = response.json()
    assert body["period"] == {"from": "2026-01-01", "to": "2026-01-01"}
    assert body["metrics"]["maeMw"] == 15
    assert body["metrics"]["completeHours"] == 2
    assert body["dataStatus"]["status"] == "ready"


def test_timeseries_filters_to_selected_dates(client: TestClient) -> None:
    response = client.get("/api/v1/timeseries?from=2026-01-02&to=2026-01-02")

    assert response.status_code == 200
    points = response.json()["points"]
    assert len(points) == 1
    assert points[0]["startTime"] == "2026-01-02T00:00:00Z"
    assert points[0]["errorMw"] == 30


def test_daily_accuracy_returns_one_metric_row_per_day(client: TestClient) -> None:
    response = client.get("/api/v1/daily-accuracy")

    assert response.status_code == 200
    days = response.json()["days"]
    assert [item["date"] for item in days] == ["2026-01-01", "2026-01-02"]
    assert days[1]["metrics"]["maeMw"] == 30


def test_forecast_evolution_marks_the_selected_pre_cutoff_revision(client: TestClient) -> None:
    response = client.get("/api/v1/forecast-evolution?startTime=2026-01-01T00:00:00Z")

    assert response.status_code == 200
    body = response.json()
    assert body["selectedPublishTime"] == "2025-12-31T08:30:00Z"
    assert body["decisionCutoff"] == "2025-12-31T09:50:00Z"
    assert [revision["selected"] for revision in body["revisions"]] == [False, True, False]


def test_error_distribution_accounts_for_every_complete_observation(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/error-distribution")

    assert response.status_code == 200
    body = response.json()
    assert body["totalObservations"] == 3
    assert sum(bucket["count"] for bucket in body["bins"]) == 3


@pytest.mark.parametrize(
    "query",
    [
        "?from=2026-01-05&to=2026-01-04",
        "?from=2025-12-31&to=2026-01-04",
        "?from=2026-01-01&to=2026-02-01",
    ],
)
def test_invalid_date_ranges_return_validation_error(client: TestClient, query: str) -> None:
    response = client.get(f"/api/v1/overview{query}")

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_DATE_RANGE"


def test_missing_snapshot_returns_structured_service_error(tmp_path: Path) -> None:
    app.dependency_overrides[get_repository] = lambda: SnapshotRepository(tmp_path / "missing.json")
    try:
        response = TestClient(app).get("/api/v1/overview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "SNAPSHOT_UNAVAILABLE"
