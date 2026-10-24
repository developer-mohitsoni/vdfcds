from datetime import UTC, date, datetime
from typing import Annotated, Literal

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
