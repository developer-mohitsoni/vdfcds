import hashlib
import json
from pathlib import Path

import pytest

from app.analytics import compute_metrics
from app.models import WindSnapshot

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = PROJECT_ROOT / "data" / "processed" / "january-2026.v1.json"
PROVENANCE_PATH = PROJECT_ROOT / "data" / "processed" / "january-2026.v1.provenance.json"


def test_january_reference_snapshot_matches_acceptance_baseline() -> None:
    snapshot_bytes = SNAPSHOT_PATH.read_bytes()
    snapshot = WindSnapshot.model_validate_json(snapshot_bytes)
    provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))

    assert hashlib.sha256(snapshot_bytes).hexdigest() == provenance["sha256"]
    assert len(snapshot.hours) == 744
    assert snapshot.coverage.expected_hours == 744
    assert snapshot.coverage.complete_hours == 744
    assert snapshot.coverage.coverage_percent == 100
    assert all(
        observation.forecast_publish_time is not None
        and observation.forecast_publish_time <= observation.decision_cutoff
        for observation in snapshot.hours
    )

    metrics = compute_metrics(snapshot.hours)
    assert metrics.mae_mw == pytest.approx(2122.8111559139785)
    assert metrics.rmse_mw == pytest.approx(2616.689226352927)
    assert metrics.mean_bias_mw == pytest.approx(1840.295941532258)
    assert metrics.wape_percent == pytest.approx(18.3305417821734)
    assert metrics.p90_absolute_error_mw == pytest.approx(4312.4)
