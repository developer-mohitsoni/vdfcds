from collections import defaultdict
from collections.abc import Sequence
from datetime import date

import pandas as pd

from app.models import DailyMetricSummary, HourlyObservation, MetricSummary


def compute_metrics(observations: Sequence[HourlyObservation]) -> MetricSummary:
    expected_hours = len(observations)
    complete = [
        observation
        for observation in observations
        if observation.forecast_mw is not None and observation.actual_mw is not None
    ]
    complete_hours = len(complete)
    coverage_percent = complete_hours / expected_hours * 100 if expected_hours else 0.0

    if not complete:
        return MetricSummary(
            maeMw=None,
            rmseMw=None,
            meanBiasMw=None,
            wapePercent=None,
            p90AbsoluteErrorMw=None,
            expectedHours=expected_hours,
            completeHours=0,
            coveragePercent=coverage_percent,
        )

    frame = pd.DataFrame(
        {
            "forecast": [item.forecast_mw for item in complete],
            "actual": [item.actual_mw for item in complete],
        }
    )
    errors = frame["forecast"] - frame["actual"]
    absolute_errors = errors.abs()
    actual_total = float(frame["actual"].abs().sum())

    return MetricSummary(
        maeMw=float(absolute_errors.mean()),
        rmseMw=float((errors.pow(2).mean()) ** 0.5),
        meanBiasMw=float(errors.mean()),
        wapePercent=(float(absolute_errors.sum()) / actual_total * 100 if actual_total else None),
        p90AbsoluteErrorMw=float(absolute_errors.quantile(0.9)),
        expectedHours=expected_hours,
        completeHours=complete_hours,
        coveragePercent=coverage_percent,
    )


def group_daily_metrics(
    observations: Sequence[HourlyObservation],
) -> list[DailyMetricSummary]:
    grouped: dict[date, list[HourlyObservation]] = defaultdict(list)
    for observation in observations:
        grouped[observation.start_time.date()].append(observation)

    return [
        DailyMetricSummary(date=delivery_date, metrics=compute_metrics(grouped[delivery_date]))
        for delivery_date in sorted(grouped)
    ]
