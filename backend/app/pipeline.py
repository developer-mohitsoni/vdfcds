from collections import defaultdict
from collections.abc import Iterable
from datetime import UTC, datetime, time, timedelta

from app.models import ActualRecord, ForecastRecord, HourlyObservation


class DataValidationError(ValueError):
    """Raised when upstream records conflict or violate processing invariants."""


def decision_cutoff(start_time: datetime) -> datetime:
    delivery_day = start_time.astimezone(UTC).date()
    previous_day = delivery_day - timedelta(days=1)
    return datetime.combine(previous_day, time(hour=9, minute=50), tzinfo=UTC)


def select_decision_time_forecasts(
    records: Iterable[ForecastRecord],
) -> dict[datetime, ForecastRecord]:
    unique: dict[tuple[datetime, datetime], ForecastRecord] = {}
    for record in records:
        key = (record.start_time, record.publish_time)
        existing = unique.get(key)
        if existing is not None and existing.generation != record.generation:
            raise DataValidationError(
                "Conflicting duplicate WINDFOR record for "
                f"{record.start_time.isoformat()} published {record.publish_time.isoformat()}"
            )
        unique[key] = record

    selected: dict[datetime, ForecastRecord] = {}
    for record in unique.values():
        if record.publish_time > decision_cutoff(record.start_time):
            continue
        current = selected.get(record.start_time)
        if current is None or record.publish_time > current.publish_time:
            selected[record.start_time] = record
    return selected


def aggregate_hourly_actuals(records: Iterable[ActualRecord]) -> dict[datetime, float]:
    unique: dict[datetime, ActualRecord] = {}
    for record in records:
        if record.fuel_type.upper() != "WIND":
            continue
        existing = unique.get(record.start_time)
        if existing is not None and existing.generation != record.generation:
            raise DataValidationError(
                f"Conflicting duplicate FUELHH record for {record.start_time.isoformat()}"
            )
        unique[record.start_time] = record

    grouped: dict[datetime, dict[int, float]] = defaultdict(dict)
    for record in unique.values():
        hour = record.start_time.replace(minute=0, second=0, microsecond=0)
        grouped[hour][record.start_time.minute] = record.generation

    return {
        hour: (halves[0] + halves[30]) / 2
        for hour, halves in grouped.items()
        if halves.keys() == {0, 30}
    }


def build_hourly_observations(
    forecasts: dict[datetime, ForecastRecord],
    actuals: dict[datetime, float],
    *,
    period_start: datetime,
    period_end: datetime,
) -> list[HourlyObservation]:
    if period_start.tzinfo is None or period_end.tzinfo is None:
        raise DataValidationError("Period boundaries must include a timezone")
    if period_start >= period_end:
        raise DataValidationError("period_start must be before period_end")

    observations: list[HourlyObservation] = []
    cursor = period_start.astimezone(UTC)
    end = period_end.astimezone(UTC)
    while cursor < end:
        forecast = forecasts.get(cursor)
        actual_mw = actuals.get(cursor)
        forecast_mw = forecast.generation if forecast is not None else None
        error_mw = (
            forecast_mw - actual_mw if forecast_mw is not None and actual_mw is not None else None
        )
        observations.append(
            HourlyObservation(
                startTime=cursor,
                forecastMw=forecast_mw,
                actualMw=actual_mw,
                errorMw=error_mw,
                forecastPublishTime=forecast.publish_time if forecast is not None else None,
                decisionCutoff=decision_cutoff(cursor),
            )
        )
        cursor += timedelta(hours=1)
    return observations
