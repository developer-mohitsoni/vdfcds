from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.analytics import compute_metrics, group_daily_metrics
from app.config import get_settings
from app.models import (
    DailyAccuracyResponse,
    DataStatus,
    ErrorDistributionBin,
    ErrorDistributionResponse,
    EvolutionRevisionResponse,
    ForecastEvolutionResponse,
    HourlyObservation,
    OverviewResponse,
    ResponsePeriod,
    TimeseriesResponse,
    WindSnapshot,
)
from app.snapshot import SnapshotRepository, SnapshotUnavailableError

JANUARY_START = date(2026, 1, 1)
JANUARY_END = date(2026, 1, 31)

router = APIRouter(prefix="/api/v1")


@dataclass(frozen=True)
class DateRange:
    start: date
    end: date


@lru_cache
def get_repository() -> SnapshotRepository:
    return SnapshotRepository(get_settings().snapshot_path)


def get_snapshot(
    repository: Annotated[SnapshotRepository, Depends(get_repository)],
) -> WindSnapshot:
    try:
        return repository.load()
    except SnapshotUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "SNAPSHOT_UNAVAILABLE",
                "message": str(error),
            },
        ) from error


def get_date_range(
    from_date: Annotated[date, Query(alias="from")] = JANUARY_START,
    to_date: Annotated[date, Query(alias="to")] = JANUARY_END,
) -> DateRange:
    if from_date < JANUARY_START or to_date > JANUARY_END or from_date > to_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "code": "INVALID_DATE_RANGE",
                "message": "Date range must be within 2026-01-01 and 2026-01-31.",
            },
        )
    return DateRange(start=from_date, end=to_date)


def _filter_hours(
    snapshot: WindSnapshot,
    selected_range: DateRange,
) -> list[HourlyObservation]:
    return [
        item
        for item in snapshot.hours
        if selected_range.start <= item.start_time.date() <= selected_range.end
    ]


def _response_period(selected_range: DateRange) -> ResponsePeriod:
    return ResponsePeriod.model_validate({"from": selected_range.start, "to": selected_range.end})


def _data_status(snapshot: WindSnapshot) -> DataStatus:
    stable_after = snapshot.period.end_exclusive + timedelta(days=1)
    snapshot_status = "ready" if snapshot.generated_at >= stable_after else "stale"
    return DataStatus(
        status=snapshot_status,
        generatedAt=snapshot.generated_at,
        schemaVersion=snapshot.schema_version,
        completeHours=snapshot.coverage.complete_hours,
    )


@router.get("/overview", response_model=OverviewResponse)
def overview(
    snapshot: Annotated[WindSnapshot, Depends(get_snapshot)],
    selected_range: Annotated[DateRange, Depends(get_date_range)],
) -> OverviewResponse:
    hours = _filter_hours(snapshot, selected_range)
    return OverviewResponse(
        period=_response_period(selected_range),
        metrics=compute_metrics(hours),
        dataStatus=_data_status(snapshot),
    )


@router.get("/timeseries", response_model=TimeseriesResponse)
def timeseries(
    snapshot: Annotated[WindSnapshot, Depends(get_snapshot)],
    selected_range: Annotated[DateRange, Depends(get_date_range)],
) -> TimeseriesResponse:
    return TimeseriesResponse(
        period=_response_period(selected_range),
        points=_filter_hours(snapshot, selected_range),
    )


@router.get("/daily-accuracy", response_model=DailyAccuracyResponse)
def daily_accuracy(
    snapshot: Annotated[WindSnapshot, Depends(get_snapshot)],
    selected_range: Annotated[DateRange, Depends(get_date_range)],
) -> DailyAccuracyResponse:
    hours = _filter_hours(snapshot, selected_range)
    return DailyAccuracyResponse(
        period=_response_period(selected_range),
        days=group_daily_metrics(hours),
    )


@router.get("/forecast-evolution", response_model=ForecastEvolutionResponse)
def forecast_evolution(
    start_time: Annotated[datetime, Query(alias="startTime")],
    snapshot: Annotated[WindSnapshot, Depends(get_snapshot)],
) -> ForecastEvolutionResponse:
    if start_time.tzinfo is None or start_time.utcoffset() is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "code": "INVALID_START_TIME",
                "message": "startTime must include a timezone.",
            },
        )
    target = start_time.astimezone(UTC)
    observation = next((item for item in snapshot.hours if item.start_time == target), None)
    if observation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "TARGET_NOT_FOUND",
                "message": "No January 2026 hourly observation exists for startTime.",
            },
        )

    revisions = [
        EvolutionRevisionResponse(
            publishTime=item.publish_time,
            generationMw=item.generation_mw,
            eligibleAtCutoff=item.eligible_at_cutoff,
            selected=item.publish_time == observation.forecast_publish_time,
        )
        for item in snapshot.forecast_evolution
        if item.start_time == target
    ]
    return ForecastEvolutionResponse(
        startTime=target,
        decisionCutoff=observation.decision_cutoff,
        selectedPublishTime=observation.forecast_publish_time,
        selectedForecastMw=observation.forecast_mw,
        actualMw=observation.actual_mw,
        revisions=revisions,
    )


@router.get("/error-distribution", response_model=ErrorDistributionResponse)
def error_distribution(
    snapshot: Annotated[WindSnapshot, Depends(get_snapshot)],
    selected_range: Annotated[DateRange, Depends(get_date_range)],
) -> ErrorDistributionResponse:
    errors = [
        item.error_mw
        for item in _filter_hours(snapshot, selected_range)
        if item.error_mw is not None
    ]
    boundaries: list[tuple[float | None, float | None]] = [
        (None, -4_000),
        (-4_000, -3_000),
        (-3_000, -2_000),
        (-2_000, -1_000),
        (-1_000, 0),
        (0, 1_000),
        (1_000, 2_000),
        (2_000, 3_000),
        (3_000, 4_000),
        (4_000, None),
    ]
    total = len(errors)
    bins: list[ErrorDistributionBin] = []
    for lower, upper in boundaries:
        count = sum(
            (lower is None or error >= lower) and (upper is None or error < upper)
            for error in errors
        )
        if lower is None:
            label = f"< {upper:,.0f}"
        elif upper is None:
            label = f"≥ {lower:,.0f}"
        else:
            label = f"{lower:,.0f} to {upper:,.0f}"
        bins.append(
            ErrorDistributionBin(
                label=label,
                lowerBoundMw=lower,
                upperBoundMw=upper,
                count=count,
                percentage=count / total * 100 if total else 0,
            )
        )
    return ErrorDistributionResponse(
        period=_response_period(selected_range),
        totalObservations=total,
        bins=bins,
    )
