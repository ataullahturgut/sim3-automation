from __future__ import annotations

import copy

import numpy as np
import pandas as pd

from gold_axis_2026.v161_thesis import run_v161_literature_short_horizon as v161


def test_contract_is_frozen_separate_line_and_has_no_production_authority():
    c = v161.load_contract()
    assert c["status"] == "FROZEN_BEFORE_V161_RETROSPECTIVE_SCORING"
    assert c["relationship_to_v160"].startswith("SEPARATE_SHORT_HORIZON_RESEARCH_LINE")
    assert c["targets"]["primary_horizon_sessions"] == 5
    assert c["targets"]["secondary_horizon_sessions"] == 3
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False
    assert c["governance"]["production_writes"] == "NONE"


def test_horizon_counts_eligible_weekday_origins_not_calendar_days():
    dates = pd.to_datetime(["2026-01-08", "2026-01-09", "2026-01-10", "2026-01-11", "2026-01-12", "2026-01-13", "2026-01-14"])
    d = pd.DataFrame({"date": dates, "close": [100, 101, 999, 999, 102, 103, 104]})
    z = v161.prepare_horizon(d, 3)
    assert z["date"].dt.weekday.max() < 5
    first = z.iloc[0]
    assert first["date"] == pd.Timestamp("2026-01-08")
    assert first["target_date"] == pd.Timestamp("2026-01-13")
    assert int(first["target_eligible_index"]) == 3


def test_primary_candidate_adds_realized_moments_but_ablation_does_not():
    c = v161.load_contract()
    base = v161.feature_list(c, "QB_BASE")
    primary = v161.feature_list(c, "QB_REALIZED")
    assert "rm_vol" not in base
    assert "rm_vol" in primary
    assert "rm_skew" in primary
    assert len(primary) > len(base)


def test_support_gate_rejects_one_class_or_low_coverage_result():
    c = v161.load_contract()
    bad = {
        "FORMATION_2024": {},
        "VALIDATION_2025": {
            "coverage": 0.50,
            "selective_balanced_accuracy": 0.75,
            "mcc": 0.40,
            "up_signals": 20,
            "down_signals": 0,
        },
        "TEST_2026_AVAILABLE": {
            "coverage": 0.10,
            "selective_balanced_accuracy": 0.70,
            "mcc": 0.30,
            "up_signals": 10,
            "down_signals": 5,
        },
    }
    gate = v161.support_gate(bad, c)
    assert gate["pass"] is False
    assert gate["checks"]["validation_both_directions"] is False
    assert gate["checks"]["test_coverage"] is False


def test_contract_does_not_claim_comex_futures_evidence():
    c = v161.load_contract()
    assert c["data"]["comex_gc_futures"] == "NOT_AVAILABLE_IN_GOVERNED_RESEARCH_STORE_FOR_THIS_FREEZE"
    assert c["data"]["futures_claim"] == "NONE; this is an XAU spot adaptation of futures-oriented literature, not a COMEX settlement/futures replication"


def test_forbidden_post_score_search_is_explicit():
    c = v161.load_contract()
    forbidden = set(c["forbidden_after_scoring"])
    assert "threshold_change" in forbidden
    assert "feature_search" in forbidden
    assert "model_search" in forbidden
    assert "hyperparameter_search" in forbidden
    assert "same_period_repair" in forbidden
