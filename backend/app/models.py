from datetime import UTC, date, datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Megawatts = Annotated[float, Field(ge=0)]


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must include a timezone")
    return value.astimezone(UTC)


class ApiRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    publish_time: datetime = Field(alias="publishTime")
    start_time: datetime = Field(alias="startTime")

    _publish_time_utc = field_validator("publish_time")(_aware_utc)
    _start_time_utc = field_validator("start_time")(_aware_utc)


class ForecastRecord(ApiRecord):
    dataset: Literal["WINDFOR"] | None = None
    generation: Megawatts

    @field_validator("start_time")
    @classmethod
    def start_must_be_hourly(cls, value: datetime) -> datetime:
        if value.minute != 0 or value.second != 0 or value.microsecond != 0:
            raise ValueError("forecast startTime must be aligned to an hour")
        return value


class ActualRecord(ApiRecord):
    dataset: Literal["FUELHH"] | None = None
    settlement_date: date = Field(alias="settlementDate")
    settlement_period: int = Field(alias="settlementPeriod", ge=1, le=50)
    fuel_type: str = Field(alias="fuelType")
    generation: Megawatts

    @field_validator("start_time")
    @classmethod
    def start_must_be_half_hourly(cls, value: datetime) -> datetime:
        if value.minute not in {0, 30} or value.second != 0 or value.microsecond != 0:
            raise ValueError("actual startTime must be aligned to a half-hour")
        return value


class HourlyObservation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    start_time: datetime = Field(alias="startTime")
    forecast_mw: float | None = Field(alias="forecastMw")
    actual_mw: float | None = Field(alias="actualMw")
    error_mw: float | None = Field(alias="errorMw")
    forecast_publish_time: datetime | None = Field(alias="forecastPublishTime")
    decision_cutoff: datetime = Field(alias="decisionCutoff")


class MetricSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    mae_mw: float | None = Field(alias="maeMw")
    rmse_mw: float | None = Field(alias="rmseMw")
    mean_bias_mw: float | None = Field(alias="meanBiasMw")
    wape_percent: float | None = Field(alias="wapePercent")
    p90_absolute_error_mw: float | None = Field(alias="p90AbsoluteErrorMw")
    expected_hours: int = Field(alias="expectedHours")
    complete_hours: int = Field(alias="completeHours")
    coverage_percent: float = Field(alias="coveragePercent")


class DailyMetricSummary(BaseModel):
    date: date
    metrics: MetricSummary


class SnapshotPeriod(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    start: datetime
    end_exclusive: datetime = Field(alias="endExclusive")
    timezone: str


class SnapshotCoverage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    expected_hours: int = Field(alias="expectedHours")
    forecast_hours: int = Field(alias="forecastHours")
    actual_hours: int = Field(alias="actualHours")
    complete_hours: int = Field(alias="completeHours")
    coverage_percent: float = Field(alias="coveragePercent")


class ForecastRevision(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    start_time: datetime = Field(alias="startTime")
    publish_time: datetime = Field(alias="publishTime")
    generation_mw: float = Field(alias="generationMw")
    eligible_at_cutoff: bool = Field(alias="eligibleAtCutoff")


class WindSnapshot(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: str = Field(alias="schemaVersion")
    generated_at: datetime = Field(alias="generatedAt")
    period: SnapshotPeriod
    methodology: dict[str, Any]
    provenance: dict[str, Any]
    coverage: SnapshotCoverage
    hours: list[HourlyObservation]
    forecast_evolution: list[ForecastRevision] = Field(alias="forecastEvolution")


class ResponsePeriod(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_date: date = Field(alias="from")
    to_date: date = Field(alias="to")


class DataStatus(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: Literal["ready", "stale"]
    generated_at: datetime = Field(alias="generatedAt")
    schema_version: str = Field(alias="schemaVersion")
    complete_hours: int = Field(alias="completeHours")


class OverviewResponse(BaseModel):
    period: ResponsePeriod
    metrics: MetricSummary
    data_status: DataStatus = Field(alias="dataStatus")


class TimeseriesResponse(BaseModel):
    period: ResponsePeriod
    points: list[HourlyObservation]


class DailyAccuracyResponse(BaseModel):
    period: ResponsePeriod
    days: list[DailyMetricSummary]


class EvolutionRevisionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    publish_time: datetime = Field(alias="publishTime")
    generation_mw: float = Field(alias="generationMw")
    eligible_at_cutoff: bool = Field(alias="eligibleAtCutoff")
    selected: bool


class ForecastEvolutionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    start_time: datetime = Field(alias="startTime")
    decision_cutoff: datetime = Field(alias="decisionCutoff")
    selected_publish_time: datetime | None = Field(alias="selectedPublishTime")
    selected_forecast_mw: float | None = Field(alias="selectedForecastMw")
    actual_mw: float | None = Field(alias="actualMw")
    revisions: list[EvolutionRevisionResponse]


class ErrorDistributionBin(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    label: str
    lower_bound_mw: float | None = Field(alias="lowerBoundMw")
    upper_bound_mw: float | None = Field(alias="upperBoundMw")
    count: int
    percentage: float


class ErrorDistributionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    period: ResponsePeriod
    total_observations: int = Field(alias="totalObservations")
    bins: list[ErrorDistributionBin]
