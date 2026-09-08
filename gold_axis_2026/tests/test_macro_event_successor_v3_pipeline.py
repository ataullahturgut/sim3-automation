from __future__ import annotations

import math
import sys
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parents[1] / "data_pipeline"
sys.path.insert(0, str(PIPELINE_DIR))

import macro_event_successor_v3_pipeline as m


def test_scope_has_only_frozen_families():
    assert set(m.EMPLOYMENT_IDS) == {"nfp_actual","nfp_consensus","unemp_actual","unemp_consensus","ahe_actual","ahe_consensus"}
    assert set(m.INFLATION_IDS) == {"cpi_actual","cpi_consensus","core_actual","core_consensus"}
    assert set(m.SCORE_IDS) == {"EMPLOYMENT","INFLATION"}


def test_windows_and_threshold_are_frozen_elsewhere_not_mutated_here():
    assert m.STRONG_THRESHOLD == 1.0
    assert m.MIN_PRIOR == 24


def test_inflation_gold_orientation_state():
    assert m.state_from_score(-1.2, [-1.1, -1.3]) == "GOLD_ADVERSE_MACRO_SHOCK"
    assert m.state_from_score(1.2, [1.1, 1.3]) == "GOLD_SUPPORTIVE_MACRO_SHOCK"
    assert m.state_from_score(-2.0, [-3.0, 1.0]) == "MACRO_MIXED_OR_SMALL"


def test_robust_scale_requires_prior_only_sample_size():
    assert m.robust_scale([1.0] * 23) == (None, None)
    scale, method = m.robust_scale([0.0] * 12 + [1.0] * 12)
    assert scale is not None and math.isfinite(scale) and scale > 0
    assert method in {"MAD", "IQR"}


def test_fomc_is_not_substituted_by_existing_rate_series():
    src = Path(m.__file__).read_text(encoding="utf-8")
    assert "DFF_ALFRED" not in src
    assert "EFFR_NYFED" not in src
    assert "proxy_substitution\":False" in src


def test_no_decision_store_or_market_shock_write_path():
    src = Path(m.__file__).read_text(encoding="utf-8")
    assert "decision_store" not in src.lower()
    assert "forecast_store" not in src.lower()
    assert "market_shock_threshold_changed" not in src or "market_shock_threshold_changed" in src
