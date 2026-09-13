from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from gold_axis_2026.v162_thesis import run_v162_crase_gold as v162

ROOT = Path(__file__).resolve().parents[1]


def test_contract_is_frozen_and_nonproduction():
    c = v162.load_contract()
    assert c["status"] == "FROZEN_BEFORE_V162_RETROSPECTIVE_SCORING"
    assert c["novelty_status"].startswith("PROTOTYPE_METHOD_NOT_YET_CLAIMED_NOVEL")
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False
    assert c["governance"]["production_writes"] == "NONE"


def test_effective_sample_size():
    assert abs(v162.effective_sample_size(np.ones(10)) - 10.0) < 1e-12
    assert v162.effective_sample_size(np.zeros(10)) == 0.0


def test_contract_maturity_and_degeneracy_are_binding():
    c = v162.load_contract()
    assert "already matured" in c["maturity"]["rule"]
    assert c["local_reliability"]["requires_both_realized_classes"] is True
    assert "min(weighted predicted UP share" in c["local_reliability"]["degeneracy_penalty"]
    assert c["aggregation"]["otherwise"] == "NO_SIGNAL"
    assert c["aggregation"]["no_post_score_threshold_change"] is True


def test_regime_features_and_experts_are_fixed():
    c = json.loads((ROOT / "v162_thesis/contracts/v162_crase_gold_freeze_v1.json").read_text())
    assert c["experts"] == ["H5_BASE_QB", "H5_PD_RM_QB", "TREND20", "GC_TREND3"]
    assert len(c["regime_features"]) == 11
    assert c["horizon"] == 5
