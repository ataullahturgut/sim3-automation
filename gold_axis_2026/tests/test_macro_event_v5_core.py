from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS_DIR))

from macro_event_v5_core import (
    RawEvent,
    fit_ols,
    linear_quantile,
    loo_sign_accuracy,
    score_family,
    severity,
    severity_thresholds,
)


def test_opposite_large_surprises_do_not_cancel_intensity():
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    events = []
    for i in range(24):
        events.append(RawEvent("X", start + timedelta(days=i), {"a": float((i % 5) - 2), "b": float((i % 7) - 3)}))
    events.append(RawEvent("X", start + timedelta(days=24), {"a": 10.0, "b": -10.0}))
    s = score_family(events)[-1]
    assert s.status == "SCORED"
    assert s.shock_intensity is not None and s.shock_intensity > 1.0


def test_current_event_not_in_own_scale():
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    events = [RawEvent("X", start + timedelta(days=i), {"a": float((i % 7) - 3)}) for i in range(24)]
    events.append(RawEvent("X", start + timedelta(days=24), {"a": 1000.0}))
    s = score_family(events)[-1]
    assert s.status == "SCORED"
    assert abs(s.z["a"]) > 100.0


def test_severity_quantiles_are_frozen_distributional_tiers():
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    events = [RawEvent("X", start + timedelta(days=i), {"a": float(i % 9)}) for i in range(40)]
    scored = score_family(events)
    th = severity_thresholds(scored)
    assert th["q90"] >= th["q75"]
    assert severity(th["q90"], th) == "HIGH"
    assert severity(th["q75"], th) in {"ELEVATED", "HIGH"}


def test_ols_and_loo_direction():
    xs = [[-2.0], [-1.0], [1.0], [2.0], [3.0]]
    ys = [-2.0, -1.0, 1.0, 2.0, 3.0]
    model = fit_ols(xs, ys)
    assert abs(model["coefficients"][0] - 1.0) < 1e-10
    assert loo_sign_accuracy(xs, ys) == 1.0


def test_quantile_determinism():
    assert linear_quantile([0.0, 10.0, 20.0, 30.0], 0.25) == 7.5
