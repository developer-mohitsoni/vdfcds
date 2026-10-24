import json
from datetime import datetime
from pathlib import Path

import httpx

from app.ingestion import (
    ACTUAL_SOURCE_URL,
    FORECAST_SOURCE_URL,
    ElexonClient,
    build_snapshot,
    iter_date_chunks,
    write_snapshot,
)


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def test_date_chunks_are_contiguous_and_end_at_requested_boundary() -> None:
    chunks = list(
        iter_date_chunks(
            dt("2026-01-01T00:00:00Z"),
            dt("2026-01-04T12:00:00Z"),
            chunk_days=2,
        )
    )

    assert chunks == [
        (dt("2026-01-01T00:00:00Z"), dt("2026-01-03T00:00:00Z")),
        (dt("2026-01-03T00:00:00Z"), dt("2026-01-04T12:00:00Z")),
    ]


def test_elexon_client_fetches_each_chunk_with_publish_time_filters() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=[])

    client = ElexonClient(
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        chunk_days=1,
    )

    result = client.fetch_dataset(
        "WINDFOR",
        dt("2026-01-01T00:00:00Z"),
        dt("2026-01-03T00:00:00Z"),
    )

    assert result == []
    assert len(requests) == 2
    assert requests[0].url.path.endswith("/datasets/WINDFOR/stream")
    assert requests[0].url.params["publishDateTimeFrom"] == "2026-01-01T00:00:00Z"
    assert requests[0].url.params["publishDateTimeTo"] == "2026-01-01T23:59:59.999000Z"


def test_snapshot_retains_january_targets_and_reports_missing_coverage() -> None:
    raw_forecasts = [
        {
            "dataset": "WINDFOR",
            "publishTime": "2025-12-31T09:30:00Z",
            "startTime": "2026-01-01T00:00:00Z",
            "generation": 8_000,
        },
        {
            "dataset": "WINDFOR",
            "publishTime": "2026-01-31T09:30:00Z",
            "startTime": "2026-02-01T00:00:00Z",
            "generation": 9_000,
        },
    ]
    raw_actuals = [
        {
            "dataset": "FUELHH",
            "publishTime": "2026-01-01T00:00:00Z",
            "startTime": "2026-01-01T00:00:00Z",
            "settlementDate": "2026-01-01",
            "settlementPeriod": 1,
            "fuelType": "WIND",
            "generation": 7_000,
        },
        {
            "dataset": "FUELHH",
            "publishTime": "2026-01-01T00:30:00Z",
            "startTime": "2026-01-01T00:30:00Z",
            "settlementDate": "2026-01-01",
            "settlementPeriod": 2,
            "fuelType": "WIND",
            "generation": 7_400,
        },
    ]

    snapshot = build_snapshot(
        raw_forecasts,
        raw_actuals,
        generated_at=dt("2026-02-02T12:00:00Z"),
    )

    assert snapshot["schemaVersion"] == "1.0"
    assert snapshot["coverage"] == {
        "expectedHours": 744,
        "forecastHours": 1,
        "actualHours": 1,
        "completeHours": 1,
        "coveragePercent": 0.13,
    }
    assert len(snapshot["hours"]) == 744
    assert snapshot["hours"][0]["actualMw"] == 7_200
    assert snapshot["hours"][1]["actualMw"] is None
    assert len(snapshot["forecastEvolution"]) == 1
    assert snapshot["provenance"]["forecastSource"] == FORECAST_SOURCE_URL
    assert snapshot["provenance"]["actualSource"] == ACTUAL_SOURCE_URL


def test_versioned_snapshot_and_hash_provenance_are_written(tmp_path: Path) -> None:
    output = tmp_path / "january-2026.v1.json"
    snapshot = {
        "schemaVersion": "1.0",
        "generatedAt": "2026-02-02T12:00:00Z",
        "provenance": {
            "forecastSource": FORECAST_SOURCE_URL,
            "actualSource": ACTUAL_SOURCE_URL,
        },
        "hours": [],
    }

    provenance_path = write_snapshot(snapshot, output)

    assert json.loads(output.read_text(encoding="utf-8")) == snapshot
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    assert provenance["snapshotFile"] == "january-2026.v1.json"
    assert len(provenance["sha256"]) == 64
    assert provenance["sourceUrls"] == [FORECAST_SOURCE_URL, ACTUAL_SOURCE_URL]
    assert provenance_path.name == "january-2026.v1.provenance.json"
