from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from gold_axis_2026.v157_thesis import run_v157_breakaware_realized_moments as core
from gold_axis_2026.v157_thesis import run_v157_entry as entry

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v157_thesis/contracts/v157_breakaware_realized_moments_freeze_v1.json"


def contract():
    return json.loads(CONTRACT.read_text())


def test_contract_is_frozen_research_only_and_h10_primary():
    c = contract()
    assert c["status"] == "FROZEN_BEFORE_V157_2025_2026_SCORING"
    assert c["evidence_class"] == "RETROSPECTIVE_SUCCESSOR_DIAGNOSTIC"
    assert c["evaluation"]["primary_lane"] == "PRIMARY_H10"
    assert c["horizons"]["PRIMARY_H10"] == 10
    assert c["h1_policy"].startswith("NOT_RESCORED")
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False
    assert c["governance"]["production_writes"] == "NONE"
    assert c["break_aware_training"]["bocpd_is_context_not_direction_vote"] is True
    assert c["source"]["realized_moment_session"]["end"] == "13:29:00"


def test_target_and_mature_training_never_use_unmatured_labels():
    c = contract()
    n = 320
    z = pd.DataFrame({
        "date": pd.bdate_range("2023-01-02", periods=n),
        "close": np.exp(np.linspace(np.log(1800.0), np.log(2200.0), n)),
        "rm_valid": True,
        "bocpd_last_break_available": pd.NaT,
    })
    z = core.add_target(z, 10)
    train, mode, _ = core.training_indices(z, 180, 10, "ROLLING126", True, c)
    assert mode == "ROLLING126"
    assert train
    assert max(train) + 10 <= 180
    assert len(train) <= 126


def test_break_aware_training_uses_only_post_break_when_threshold_is_met():
    c = contract()
    n = 360
    dates = pd.bdate_range("2023-01-02", periods=n)
    z = pd.DataFrame({
        "date": dates,
        "close": np.exp(np.linspace(np.log(1800.0), np.log(2300.0), n)),
        "rm_valid": True,
        "bocpd_last_break_available": pd.NaT,
    })
    z = core.add_target(z, 10)
    t = 300
    break_date = dates[210]
    z.loc[t, "bocpd_last_break_available"] = break_date
    train, mode, used = core.training_indices(z, t, 10, "BREAK_AWARE", True, c)
    assert mode == "POST_BREAK"
    assert used == break_date.date().isoformat()
    assert len(train) >= c["break_aware_training"]["minimum_post_break_mature_targets"]
    assert all(z.loc[j, "date"] >= break_date for j in train)
    assert all(j + 10 <= t for j in train)


def test_selective_rule_is_no_signal_when_interval_crosses_zero_and_pt_rejects_degenerate_margin():
    f = pd.DataFrame({
        "target_return": [0.01, -0.02, 0.03, -0.01],
        "y": [1, 0, 1, 0],
        "q25": [-0.01, -0.03, 0.01, -0.02],
        "q50": [0.001, -0.01, 0.02, -0.005],
        "q75": [0.02, -0.001, 0.04, 0.02],
    })
    m = core.metrics(f)
    # Row 1 crosses zero => NO_SIGNAL; rows 2 and 3 are directional; row 4 crosses zero.
    assert m["selective_n"] == 2
    assert m["up_signals"] == 1
    assert m["down_signals"] == 1
    deg = core.pt_test(np.array([1, 0, 1, 0, 1]), np.ones(5, dtype=int))
    assert deg["status"] == "UNDEFINED_DEGENERATE_MARGIN"


def test_bocpd_daily_context_uses_only_completed_months():
    panel = pd.DataFrame({
        "date": pd.to_datetime(["2025-03-03", "2025-04-15", "2026-06-30"]),
        "close": [1.0, 1.0, 1.0],
    })
    out = core.build_bocpd_daily_context(panel)
    assert out["bocpd_month"].notna().all()
    assert all(out["bocpd_month"].dt.to_period("M") < out["date"].dt.to_period("M"))


def test_corrected_dm_hln_reports_positive_gain_for_better_challenger():
    n = 80
    y = np.sin(np.linspace(0.1, 8.0, n)) * 0.02
    base = pd.DataFrame({
        "origin_index": np.arange(n), "target_return": y,
        "q25": np.zeros(n) - 0.03, "q50": np.zeros(n), "q75": np.zeros(n) + 0.03,
    })
    ch = pd.DataFrame({
        "origin_index": np.arange(n),
        "q25": y - 0.003, "q50": y, "q75": y + 0.003,
    })
    d = entry.hac_dm_hln(base, ch, 10)
    assert d["status"] == "OK"
    assert d["mean_loss_gain"] > 0
    assert d["challenger_mean_pinball_aligned"] < d["base_mean_pinball_aligned"]
