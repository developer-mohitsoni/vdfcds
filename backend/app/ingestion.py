import argparse
import hashlib
import json
import logging
import time as time_module
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx

from app.models import ActualRecord, ForecastRecord
from app.pipeline import (
    DataValidationError,
    aggregate_hourly_actuals,
    build_hourly_observations,
    decision_cutoff,
    select_decision_time_forecasts,
)

LOGGER = logging.getLogger(__name__)

API_BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"
FORECAST_SOURCE_URL = f"{API_BASE_URL}/datasets/WINDFOR/stream"
ACTUAL_SOURCE_URL = f"{API_BASE_URL}/datasets/FUELHH/stream"

PERIOD_START = datetime(2026, 1, 1, tzinfo=UTC)
PERIOD_END = datetime(2026, 2, 1, tzinfo=UTC)
FORECAST_FETCH_START = datetime(2025, 12, 15, tzinfo=UTC)
FORECAST_FETCH_END = datetime(2026, 2, 1, tzinfo=UTC)
ACTUAL_FETCH_START = PERIOD_START
ACTUAL_FETCH_END = datetime(2026, 2, 2, tzinfo=UTC)


def _iso_z(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def iter_date_chunks(
    start: datetime,
    end: datetime,
    *,
    chunk_days: int,
) -> Iterator[tuple[datetime, datetime]]:
    if chunk_days < 1:
        raise ValueError("chunk_days must be at least 1")
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("chunk boundaries must include a timezone")
    if start >= end:
        raise ValueError("start must be before end")

    cursor = start.astimezone(UTC)
    boundary = end.astimezone(UTC)
    while cursor < boundary:
        chunk_end = min(cursor + timedelta(days=chunk_days), boundary)
        yield cursor, chunk_end
        cursor = chunk_end


class ElexonClient:
    def __init__(
        self,
        *,
        http_client: httpx.Client | None = None,
        chunk_days: int = 1,
        max_attempts: int = 3,
    ) -> None:
        self._client = http_client or httpx.Client(timeout=60.0)
        self._owns_client = http_client is None
        self._chunk_days = chunk_days
        self._max_attempts = max_attempts

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "ElexonClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def fetch_dataset(
        self,
        dataset: str,
        start: datetime,
        end: datetime,
    ) -> list[dict[str, Any]]:
        url = f"{API_BASE_URL}/datasets/{dataset}/stream"
        records: list[dict[str, Any]] = []
        for chunk_start, chunk_end in iter_date_chunks(
            start,
            end,
            chunk_days=self._chunk_days,
        ):
            inclusive_end = chunk_end - timedelta(milliseconds=1)
            params = {
                "publishDateTimeFrom": _iso_z(chunk_start),
                "publishDateTimeTo": _iso_z(inclusive_end),
            }
            LOGGER.info(
                "Fetching %s records published from %s to %s",
                dataset,
                params["publishDateTimeFrom"],
                params["publishDateTimeTo"],
            )
            payload = self._request_json(url, params)
            if not isinstance(payload, list) or not all(
                isinstance(record, dict) for record in payload
            ):
                raise DataValidationError(f"Unexpected {dataset} API response shape")
            records.extend(payload)
        return records

    def _request_json(self, url: str, params: dict[str, str]) -> Any:
        for attempt in range(1, self._max_attempts + 1):
            try:
                response = self._client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPError, ValueError):
                if attempt == self._max_attempts:
                    raise
                time_module.sleep(2 ** (attempt - 1))
        raise AssertionError("Retry loop exited unexpectedly")


def build_snapshot(
    raw_forecasts: Sequence[dict[str, Any]],
    raw_actuals: Sequence[dict[str, Any]],
    *,
    generated_at: datetime,
) -> dict[str, Any]:
    forecasts = [ForecastRecord.model_validate(record) for record in raw_forecasts]
    actuals = [
        ActualRecord.model_validate(record)
        for record in raw_actuals
        if str(record.get("fuelType", "")).upper() == "WIND"
    ]

    january_forecasts = [
        record for record in forecasts if PERIOD_START <= record.start_time < PERIOD_END
    ]
    january_actuals = [
        record for record in actuals if PERIOD_START <= record.start_time < PERIOD_END
    ]
    selected = select_decision_time_forecasts(january_forecasts)
    hourly_actuals = aggregate_hourly_actuals(january_actuals)
    observations = build_hourly_observations(
        selected,
        hourly_actuals,
        period_start=PERIOD_START,
        period_end=PERIOD_END,
    )

    expected_hours = len(observations)
    forecast_hours = sum(item.forecast_mw is not None for item in observations)
    actual_hours = sum(item.actual_mw is not None for item in observations)
    complete_hours = sum(item.error_mw is not None for item in observations)

    evolution = [
        {
            "startTime": _iso_z(record.start_time),
            "publishTime": _iso_z(record.publish_time),
            "generationMw": record.generation,
            "eligibleAtCutoff": record.publish_time <= decision_cutoff(record.start_time),
        }
        for record in sorted(
            january_forecasts,
            key=lambda item: (item.start_time, item.publish_time),
        )
    ]

    return {
        "schemaVersion": "1.0",
        "generatedAt": _iso_z(generated_at),
        "period": {
            "start": _iso_z(PERIOD_START),
            "endExclusive": _iso_z(PERIOD_END),
            "timezone": "GMT (UTC)",
        },
        "methodology": {
            "forecastSelection": "Latest revision published by D-1 09:50 GMT",
            "actualAggregation": "Arithmetic mean of the two WIND half-hours",
            "errorConvention": "forecastMw - actualMw",
            "missingData": "Missing values remain null and are excluded from metrics",
        },
        "provenance": {
            "forecastSource": FORECAST_SOURCE_URL,
            "actualSource": ACTUAL_SOURCE_URL,
            "rawForecastRecords": len(raw_forecasts),
            "rawActualRecords": len(raw_actuals),
            "retainedForecastRecords": len(january_forecasts),
            "retainedWindActualRecords": len(january_actuals),
        },
        "coverage": {
            "expectedHours": expected_hours,
            "forecastHours": forecast_hours,
            "actualHours": actual_hours,
            "completeHours": complete_hours,
            "coveragePercent": round(complete_hours / expected_hours * 100, 2),
        },
        "hours": [item.model_dump(mode="json", by_alias=True) for item in observations],
        "forecastEvolution": evolution,
    }


def write_snapshot(snapshot: dict[str, Any], output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(output)

    provenance_path = output.with_name(f"{output.stem}.provenance.json")
    provenance = {
        "snapshotFile": output.name,
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "generatedAt": snapshot["generatedAt"],
        "sourceUrls": [
            snapshot["provenance"]["forecastSource"],
            snapshot["provenance"]["actualSource"],
        ],
    }
    provenance_path.write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return provenance_path


def parse_args() -> argparse.Namespace:
    repository_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="Regenerate the January 2026 WindSight UK Elexon snapshot."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=repository_root / "data" / "processed" / "january-2026.v1.json",
    )
    parser.add_argument("--chunk-days", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    with ElexonClient(chunk_days=args.chunk_days) as client:
        raw_forecasts = client.fetch_dataset("WINDFOR", FORECAST_FETCH_START, FORECAST_FETCH_END)
        raw_actuals = client.fetch_dataset("FUELHH", ACTUAL_FETCH_START, ACTUAL_FETCH_END)
    snapshot = build_snapshot(
        raw_forecasts,
        raw_actuals,
        generated_at=datetime.now(UTC),
    )
    provenance_path = write_snapshot(snapshot, args.output)
    LOGGER.info(
        "Wrote %s complete hours to %s (provenance: %s)",
        snapshot["coverage"]["completeHours"],
        args.output,
        provenance_path,
    )


if __name__ == "__main__":
    main()
