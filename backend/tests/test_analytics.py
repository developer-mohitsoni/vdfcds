from datetime import UTC, datetime, timedelta

import pytest

from app.analytics import compute_metrics, group_daily_metrics
from app.models import HourlyObservation


def observation(
    hour: int,
    forecast_mw: float | None,
    actual_mw: float | None,
    *,
    day: int = 1,
) -> HourlyObservation:
    start = datetime(2026, 1, day, hour, tzinfo=UTC)
    error = forecast_mw - actual_mw if forecast_mw is not None and actual_mw is not None else None
    return HourlyObservation(
        startTime=start,
        forecastMw=forecast_mw,
        actualMw=actual_mw,
        errorMw=error,
        forecastPublishTime=(start - timedelta(days=1)),
        decisionCutoff=(start - timedelta(days=1)).replace(hour=9, minute=50),
    )


def test_metric_formulas_match_known_fixture() -> None:
    rows = [
        observation(0, 110, 100),
        observation(1, 180, 200),
        observation(2, 330, 300),
    ]

    metrics = compute_metrics(rows)

    assert metrics.mae_mw == pytest.approx(20)
    assert metrics.rmse_mw == pytest.approx(21.602468)
    assert metrics.mean_bias_mw == pytest.approx(6.666667)
    assert metrics.wape_percent == pytest.approx(10)
    assert metrics.p90_absolute_error_mw == pytest.approx(28)
    assert metrics.expected_hours == 3
    assert metrics.complete_hours == 3
    assert metrics.coverage_percent == 100


def test_missing_observations_are_excluded_without_being_fabricated() -> None:
    rows = [
        observation(0, 110, 100),
        observation(1, None, 200),
        observation(2, 300, None),
    ]

    metrics = compute_metrics(rows)

    assert metrics.mae_mw == 10
    assert metrics.expected_hours == 3
    assert metrics.complete_hours == 1
    assert metrics.coverage_percent == pytest.approx(33.333333)


def test_empty_period_returns_null_metrics_and_zero_coverage() -> None:
    metrics = compute_metrics([])

    assert metrics.mae_mw is None
    assert metrics.rmse_mw is None
    assert metrics.mean_bias_mw is None
    assert metrics.wape_percent is None
    assert metrics.p90_absolute_error_mw is None
    assert metrics.expected_hours == 0
    assert metrics.complete_hours == 0
    assert metrics.coverage_percent == 0


def test_daily_metrics_group_by_utc_delivery_date() -> None:
    rows = [
        observation(23, 110, 100, day=1),
        observation(0, 240, 200, day=2),
    ]

    daily = group_daily_metrics(rows)

    assert [item.date.isoformat() for item in daily] == ["2026-01-01", "2026-01-02"]
    assert daily[0].metrics.mae_mw == 10
    assert daily[1].metrics.mae_mw == 40
