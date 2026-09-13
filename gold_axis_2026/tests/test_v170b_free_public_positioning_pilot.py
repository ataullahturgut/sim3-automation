import json
from pathlib import Path

import pandas as pd

from gold_axis_2026.v170_research.run_v170b_free_public_positioning_pilot import build_cot_features, sha256_file


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v170_research/contracts/v170b_free_public_positioning_pilot_freeze_v1.json"
SNAPSHOT = ROOT / "v170_research/data/v170a_cftc_gold_weekly_compact.csv"


def test_v170b_contract_and_snapshot_are_frozen_before_scoring():
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert c["status"] == "FROZEN_BEFORE_ANY_V170B_FORECAST_SCORING"
    assert sha256_file(SNAPSHOT) == c["new_public_data"]["compact_snapshot_sha256"]
    assert c["new_public_data"]["rows"] == 183
    assert c["new_public_data"]["pit_available_rule"].startswith("Tuesday report positions become eligible only from report_date + 6 calendar days")
    assert c["model_lock"]["hyperparameter_search"] == "FORBIDDEN"
    assert c["incremental_hope_gate"]["eligible_candidates"] == ["BASE_PLUS_LEGACY", "BASE_PLUS_DISAGG"]
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False


def test_v170b_cot_features_use_predeclared_columns_and_conservative_clock():
    raw = pd.read_csv(SNAPSHOT)
    cot = build_cot_features()
    assert len(cot) == 183
    assert cot["report_date"].is_monotonic_increasing
    delta = pd.to_datetime(raw["available_date"]) - pd.to_datetime(raw["report_date"])
    assert (delta.dt.days == 6).all()
    expected = {
        "legacy_nc_net_share", "legacy_nc_net_change", "legacy_nc_z52", "legacy_comm_net_share", "legacy_oi_log_change",
        "mm_net_share", "mm_net_change", "mm_z52", "prodmerc_net_share", "disagg_oi_log_change",
    }
    assert expected.issubset(set(cot.columns))
    # 52-week z-score is explicitly past-only and therefore unavailable before 26 previous weekly observations.
    assert cot.loc[:25, "legacy_nc_z52"].isna().all()
    assert cot.loc[:25, "mm_z52"].isna().all()
