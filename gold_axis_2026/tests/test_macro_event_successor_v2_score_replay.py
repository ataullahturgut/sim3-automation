from __future__ import annotations

import math
import sys
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parents[1] / "data_pipeline"
sys.path.insert(0, str(PIPELINE_DIR))

from macro_event_successor_v2_score_replay import (
    EventRow,
    classify,
    compute_scores,
    linear_quantile,
    robust_scale,
)


def row(month: str, nfp_surprise: float, unemp_surprise: float, ahe_surprise: float) -> EventRow:
    return EventRow(
        reference_month=month,
        nfp_actual=nfp_surprise,
        nfp_consensus=0.0,
        unemp_actual=unemp_surprise,
        unemp_consensus=0.0,
        ahe_actual=ahe_surprise,
        ahe_consensus=0.0,
    )


def month_seq(n: int) -> list[str]:
    out = []
    y, m = 2016, 1
    for _ in range(n):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y += 1
            m = 1
    return out


def test_classification_boundaries_unchanged_from_v1():
    assert classify(-1.0, 2, 1) == "GOLD_ADVERSE_MACRO_SHOCK"
    assert classify(1.0, 1, 2) == "GOLD_SUPPORTIVE_MACRO_SHOCK"
    assert classify(-0.999, 3, 0) == "MACRO_MIXED_OR_SMALL"
    assert classify(1.2, 2, 1) == "MACRO_MIXED_OR_SMALL"


def test_linear_quantile_frozen_interpolation():
    xs = [0.0, 10.0, 20.0, 30.0]
    assert math.isclose(linear_quantile(xs, 0.25), 7.5)
    assert math.isclose(linear_quantile(xs, 0.75), 22.5)


def test_mad_scale_is_not_exploded_by_single_extreme_prior_outlier():
    base = [float((i % 7) - 3) for i in range(24)]
    s1, method1 = robust_scale(base)
    contaminated = base + [10000.0]
    s2, method2 = robust_scale(contaminated)
    assert method1 == "MAD_1P4826"
    assert method2 == "MAD_1P4826"
    assert s1 is not None and s2 is not None
    assert s2 < s1 * 2.0


def test_iqr_fallback_when_mad_is_zero_but_iqr_positive():
    # Median absolute deviation is zero because more than half the sample is zero,
    # while the quartiles still span a non-zero range.
    values = [0.0] * 13 + [1.0] * 6 + [-1.0] * 5
    scale, method = robust_scale(values)
    assert method == "IQR_NORMAL_FALLBACK"
    assert scale is not None and scale > 0.0


def test_first_24_events_are_warmup_then_scoring_begins():
    months = month_seq(25)
    panel = [
        row(
            m,
            float((i % 7) - 3),
            float((i % 5) - 2) / 10.0,
            float((i % 6) - 3) / 10.0,
        )
        for i, m in enumerate(months)
    ]
    scores = compute_scores(panel)
    assert all(s.state == "INSUFFICIENT_HISTORY" for s in scores[:24])
    assert scores[24].score is not None


def test_current_extreme_event_does_not_enter_its_own_robust_scale():
    months = month_seq(25)
    panel = [
        row(
            m,
            float((i % 7) - 3),
            float((i % 5) - 2) / 10.0,
            float((i % 6) - 3) / 10.0,
        )
        for i, m in enumerate(months[:24])
    ]
    panel.append(row(months[24], 1000.0, 5.0, 5.0))
    score = compute_scores(panel)[-1]
    assert score.score is not None
    assert abs(score.score) > 10.0


def test_prefix_recompute_same_result():
    months = month_seq(40)
    panel = [
        row(
            m,
            float((i % 9) - 4),
            float((i % 7) - 3) / 10.0,
            float((i % 8) - 4) / 10.0,
        )
        for i, m in enumerate(months)
    ]
    full = compute_scores(panel)
    for i in range(len(panel)):
        prefix = compute_scores(panel[: i + 1])[-1]
        assert prefix.state == full[i].state
        assert prefix.method_nfp == full[i].method_nfp
        assert prefix.method_unemp == full[i].method_unemp
        assert prefix.method_ahe == full[i].method_ahe
        if prefix.score is None:
            assert full[i].score is None
        else:
            assert math.isclose(prefix.score, full[i].score, rel_tol=0.0, abs_tol=1e-12)
