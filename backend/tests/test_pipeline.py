from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models import ActualRecord, ForecastRecord
from app.pipeline import (
    DataValidationError,
    aggregate_hourly_actuals,
    build_hourly_observations,
    select_decision_time_forecasts,
)


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def forecast(published: str, starts: str, generation: float) -> ForecastRecord:
    return ForecastRecord(
        publishTime=dt(published),
        startTime=dt(starts),
        generation=generation,
    )


def actual(starts: str, generation: float, *, fuel_type: str = "WIND") -> ActualRecord:
    start_time = dt(starts)
    return ActualRecord(
        publishTime=start_time,
        startTime=start_time,
        settlementDate=start_time.date(),
        settlementPeriod=start_time.hour * 2 + (2 if start_time.minute == 30 else 1),
        fuelType=fuel_type,
        generation=generation,
    )


def test_latest_forecast_before_cutoff_is_selected_and_later_revision_is_rejected() -> None:
    target = "2026-01-10T12:00:00Z"
    records = [
        forecast("2026-01-09T08:30:00Z", target, 8_000),
        forecast("2026-01-09T09:49:00Z", target, 8_200),
        forecast("2026-01-09T10:30:00Z", target, 8_700),
    ]

    selected = select_decision_time_forecasts(records)

    assert selected[dt(target)].generation == 8_200
    assert selected[dt(target)].publish_time == dt("2026-01-09T09:49:00Z")


def test_two_half_hour_actuals_are_averaged_into_one_hour() -> None:
    records = [
        actual("2026-01-04T06:00:00Z", 9_000),
        actual("2026-01-04T06:30:00Z", 9_400),
    ]

    hourly = aggregate_hourly_actuals(records)

    assert hourly[dt("2026-01-04T06:00:00Z")] == 9_200


def test_missing_half_hour_is_not_fabricated() -> None:
    hourly = aggregate_hourly_actuals([actual("2026-01-04T06:00:00Z", 9_000)])

    assert dt("2026-01-04T06:00:00Z") not in hourly


def test_non_wind_actuals_are_not_included() -> None:
    records = [
        actual("2026-01-04T06:00:00Z", 9_000),
        actual("2026-01-04T06:30:00Z", 9_400),
        actual("2026-01-04T06:00:00Z", 30_000, fuel_type="CCGT"),
    ]

    hourly = aggregate_hourly_actuals(records)

    assert hourly[dt("2026-01-04T06:00:00Z")] == 9_200


def test_conflicting_duplicate_actual_raises_validation_error() -> None:
    records = [
        actual("2026-01-04T06:00:00Z", 9_000),
        actual("2026-01-04T06:00:00Z", 9_100),
    ]

    with pytest.raises(DataValidationError, match="Conflicting duplicate"):
        aggregate_hourly_actuals(records)


def test_january_grid_has_exact_boundaries_and_does_not_fill_missing_values() -> None:
    forecasts = {
        dt("2026-01-01T00:00:00Z"): forecast("2025-12-31T09:30:00Z", "2026-01-01T00:00:00Z", 7_500),
        dt("2026-02-01T00:00:00Z"): forecast("2026-01-31T09:30:00Z", "2026-02-01T00:00:00Z", 7_800),
    }
    actuals = {dt("2026-01-01T00:00:00Z"): 7_000}

    observations = build_hourly_observations(
        forecasts,
        actuals,
        period_start=datetime(2026, 1, 1, tzinfo=UTC),
        period_end=datetime(2026, 2, 1, tzinfo=UTC),
    )

    assert len(observations) == 744
    assert observations[0].start_time == dt("2026-01-01T00:00:00Z")
    assert observations[-1].start_time == dt("2026-01-31T23:00:00Z")
    assert observations[0].forecast_mw == 7_500
    assert observations[0].actual_mw == 7_000
    assert observations[1].forecast_mw is None
    assert observations[1].actual_mw is None


def test_malformed_or_timezone_naive_record_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ForecastRecord(
            publishTime=datetime(2026, 1, 1, 8, 30),
            startTime=dt("2026-01-02T00:00:00Z"),
            generation=-1,
        )
