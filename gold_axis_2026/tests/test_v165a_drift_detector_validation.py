from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from gold_axis_2026.v165a_research import run_v165a_drift_detector_validation as v165a

ROOT = Path(__file__).resolve().parents[1]
R0 = ROOT / "v165a_research/contracts/v165a_drift_detector_validation_freeze_v1.json"
R1 = ROOT / "v165a_research/contracts/v165a_r1_synthetic_drift_detector_freeze_v1.json"


def test_r0_was_superseded_before_detector_scoring():
    c = json.loads(R0.read_text(encoding="utf-8"))
    assert c["status"] == "SUPERSEDED_BEFORE_DETECTOR_SCORING_INSUFFICIENT_FORMATION_SUPPORT"
    assert c["superseded_before_detector_scoring"] is True


def test_r1_is_frozen_and_governance_locked():
    c = json.loads(R1.read_text(encoding="utf-8"))
    assert c["status"] == "FROZEN_BEFORE_ANY_V165A_R1_DETECTOR_SCORING"
    assert c["evaluation_lock"]["2025_2026_used_for_detector_selection"] is False
    assert c["evaluation_lock"]["triggered_adaptation_in_v165a_r1"] == "FORBIDDEN"
    assert c["evaluation_lock"]["selector_scoring_in_v165a_r1"] == "FORBIDDEN"
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False


def test_candidate_grid_is_compact_and_predeclared():
    c = json.loads(R1.read_text(encoding="utf-8"))
    x = v165a.detector_candidates(c)
    ids = [z.candidate_id for z in x]
    assert len(ids) == 9
    assert len(set(ids)) == 9
    assert sum(z.family == "ADWIN" for z in x) == 3
    assert sum(z.family == "PAGE_HINKLEY" for z in x) == 6


def test_ar1_generator_is_deterministic_and_finite():
    a = v165a.generate_ar1_loss_stream(np.random.default_rng(7), 100, 0.6, "STUDENT_T5")
    b = v165a.generate_ar1_loss_stream(np.random.default_rng(7), 100, 0.6, "STUDENT_T5")
    assert len(a) == 100
    assert np.all(np.isfinite(a))
    assert np.allclose(a, b)


def test_drift_injection_preserves_pre_drift_segment():
    x = np.zeros(60, dtype=float)
    abrupt = v165a.inject_drift(x, 30, "ABRUPT", 1.0)
    gradual = v165a.inject_drift(x, 30, "GRADUAL_30", 1.0)
    assert np.allclose(abrupt[:30], 0.0)
    assert np.allclose(abrupt[30:], 1.0)
    assert np.allclose(gradual[:30], 0.0)
    assert gradual[30] > 0.0
    assert gradual[-1] == 1.0
    assert np.all(np.diff(gradual[30:]) >= -1e-12)


def test_source_selects_synthetically_before_actual_timeline_and_never_adapts():
    source = (ROOT / "v165a_research/run_v165a_drift_detector_validation.py").read_text(encoding="utf-8")
    assert 'selection = select_candidate(summary)' in source
    assert 'actual_timeline = None' in source
    assert source.index('selection = select_candidate(summary)') < source.index('actual_timeline = None')
    assert '"2025_2026_used_for_detector_selection": False' in source
    assert '"triggered_adaptation_performed": False' in source
