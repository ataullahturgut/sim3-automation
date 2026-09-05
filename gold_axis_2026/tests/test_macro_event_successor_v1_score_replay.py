from __future__ import annotations

import math
import sys
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parents[1] / "data_pipeline"
sys.path.insert(0, str(PIPELINE_DIR))

from macro_event_successor_v1_score_replay import EventRow, classify, compute_scores


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


def test_classification_boundaries():
    assert classify(-1.0, 2, 1) == "GOLD_ADVERSE_MACRO_SHOCK"
    assert classify(1.0, 1, 2) == "GOLD_SUPPORTIVE_MACRO_SHOCK"
    assert classify(-0.999, 3, 0) == "MACRO_MIXED_OR_SMALL"
    assert classify(1.2, 2, 1) == "MACRO_MIXED_OR_SMALL"


def test_first_24_events_are_insufficient_history():
    months = month_seq(25)
    panel = [row(m, float(i % 3), float((i + 1) % 4) / 10.0, float((i + 2) % 5) / 10.0) for i, m in enumerate(months)]
    scores = compute_scores(panel)
    assert all(s.state == "INSUFFICIENT_HISTORY" for s in scores[:24])
    assert scores[24].state != "INSUFFICIENT_HISTORY"


def test_current_event_not_in_its_own_sigma():
    months = month_seq(25)
    panel = []
    for i, m in enumerate(months[:24]):
        panel.append(row(m, float(i % 4), float((i % 3) - 1) / 10.0, float((i % 5) - 2) / 10.0))
    panel.append(row(months[24], 1000.0, 5.0, 5.0))
    score = compute_scores(panel)[-1]
    assert score.score is not None
    # If the huge current surprise leaked into its own sigma, magnitude would be heavily damped.
    assert abs(score.score) > 10.0


def test_prefix_recompute_same_result():
    months = month_seq(35)
    panel = [row(m, float((i % 7) - 3), float((i % 5) - 2) / 10.0, float((i % 6) - 3) / 10.0) for i, m in enumerate(months)]
    full = compute_scores(panel)
    for i in range(len(panel)):
        prefix = compute_scores(panel[: i + 1])[-1]
        assert prefix.state == full[i].state
        if prefix.score is None:
            assert full[i].score is None
        else:
            assert math.isclose(prefix.score, full[i].score, rel_tol=0.0, abs_tol=1e-12)
