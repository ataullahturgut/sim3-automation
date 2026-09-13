from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from gold_axis_2026.v165a_research import run_v165a_drift_detector_validation as v165a

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v165a_research/contracts/v165a_drift_detector_validation_freeze_v1.json"


def test_contract_is_frozen_and_future_visible_losses_cannot_select_detector():
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert c["status"] == "FROZEN_BEFORE_ANY_V165A_DETECTOR_SCORING"
    assert c["formation_only_end"] == "2024-12-31"
    assert c["evaluation_lock"]["2025_2026_loss_streams_used_for_detector_selection"] is False
    assert c["evaluation_lock"]["triggered_adaptation_in_v165a"] == "FORBIDDEN"
    assert c["evaluation_lock"]["selector_scoring_in_v165a"] == "FORBIDDEN"
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False


def test_candidate_grid_is_small_and_predeclared():
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    x = v165a.detector_candidates(c)
    ids = [z.candidate_id for z in x]
    assert len(ids) == 9
    assert len(set(ids)) == 9
    assert sum(z.family == "ADWIN" for z in x) == 3
    assert sum(z.family == "PAGE_HINKLEY" for z in x) == 6


def test_moving_block_bootstrap_has_requested_length_and_uses_source_values():
    rng = np.random.default_rng(123)
    base = np.arange(20, dtype=float)
    x = v165a.moving_block_bootstrap(base, 57, 5, rng)
    assert len(x) == 57
    assert set(np.unique(x)).issubset(set(base))


def test_injected_drift_only_changes_post_drift_segment():
    x = np.zeros(40, dtype=float)
    abrupt = v165a.inject_drift(x, 20, "ABRUPT", 0.2, (-1.0, 1.0))
    gradual = v165a.inject_drift(x, 20, "GRADUAL_20", 0.2, (-1.0, 1.0))
    assert np.allclose(abrupt[:20], 0.0)
    assert np.allclose(abrupt[20:], 0.2)
    assert np.allclose(gradual[:20], 0.0)
    assert gradual[20] > 0.0
    assert gradual[-1] == 0.2
    assert np.all(np.diff(gradual[20:]) >= -1e-12)


def test_source_keeps_adaptation_out_and_formation_end_hard_cut():
    source = (ROOT / "v165a_research/run_v165a_drift_detector_validation.py").read_text(encoding="utf-8")
    assert '"triggered_adaptation_performed": False' in source
    assert '"2025_2026_loss_streams_used_for_detector_selection": False' in source
    assert 'panel = panel[pd.to_datetime(panel["date"]) <= formation_end]' in source
