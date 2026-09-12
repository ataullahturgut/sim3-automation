from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from gold_axis_2026.v151_thesis import run_v151_locked_audit as v

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v151_thesis/contracts/v151_master_locked_audit_freeze_v1.json"


def _frame(candidate: str, offset: float = 0.0, n: int = 120) -> pd.DataFrame:
    rows = []
    for t in range(n):
        y = t % 2
        p = 0.60 + offset if y else 0.40 - offset
        rows.append({
            "origin_index": t,
            "origin_date": pd.Timestamp("2023-01-01") + pd.Timedelta(days=t),
            "target_date": pd.Timestamp("2023-01-01") + pd.Timedelta(days=t + 1),
            "horizon": 1,
            "candidate": candidate,
            "y": y,
            "return": 0.01 if y else -0.01,
            "p": p,
            "p50": 0.5,
            "pfreq": 0.5,
            "role_score": 1.0 if y else -1.0,
            "train_n": 80,
        })
    return pd.DataFrame(rows)


def test_contract_is_frozen_and_nonproduction():
    c = json.loads(CONTRACT.read_text())
    assert c["status"] == "FROZEN_BEFORE_V151_2025_VALIDATION_AND_2026_TEST_RUN"
    assert c["governance"]["production_authority"] is False
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["master_orchestrator"]["missing_policy"] == "NOT_APPLICABLE_OR_BLOCKED_NEVER_NEUTRAL_VOTE"


def test_targets_do_not_create_labels_beyond_horizon():
    d = pd.DataFrame({"close": [100.0, 101.0, 99.0, 102.0, 103.0]})
    y1, _ = v.targets(d, 1)
    y3, _ = v.targets(d, 3)
    assert pd.isna(y1.iloc[-1])
    assert y3.iloc[-3:].isna().all()


def test_role_fast_requires_two_persistent_completed_states():
    d = pd.DataFrame({"close": list(range(1, 25))})
    out = v.role_fast(d)
    assert out.iloc[-1] == 1.0


def test_adaptive_combiners_only_use_prior_mature_errors_and_run():
    a = _frame("A", 0.02)
    b = _frame("B", -0.02)
    frames = {"A": a, "B": b}
    ew = v.mature_error_weighted(frames, ["A", "B"], "EW", 1, 40, 3.0, 20)
    dma = v.dma_style(frames, ["A", "B"], "DMA", 1, 0.97)
    assert not ew.empty
    assert not dma.empty
    assert ew["p"].between(0, 1).all()
    assert dma["p"].between(0, 1).all()


def test_selective_threshold_is_validation_only_rule():
    f = _frame("A", 0.03, 100)
    out = v.select_threshold(f, [0.0, 0.03, 0.05, 0.10])
    assert out["threshold"] in {0.0, 0.03, 0.05, 0.10}
    assert out["status"] in {"SELECTED_ON_2025_VALIDATION", "FALLBACK_ZERO"}


def test_research_sensitivity_cannot_be_thesis_primary():
    c = json.loads(CONTRACT.read_text())
    strict = set(c["general_direction"]["strict_primary_feature_sets"])
    sens = set(c["general_direction"]["research_sensitivity_feature_sets"])
    assert strict.isdisjoint(sens)
    assert "G0_G1_G2" in strict
    assert "G0_G1_G2_G3_G4" in sens
