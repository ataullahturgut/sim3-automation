import pandas as pd

from gold_axis_2026.v170_research.run_v170_public_positioning_context import SHUTDOWN_RELEASES, attach_public, load_contract


def test_contract_is_frozen_and_governance_off():
    c = load_contract()
    assert c["status"] == "FROZEN_BEFORE_ANY_V170_SCORING"
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False
    assert "same_day_GVZ" in c["forbidden_in_v170"]
    assert "2025_2026_based_selection" in c["forbidden_in_v170"]


def test_shutdown_release_mapping_is_delayed():
    assert SHUTDOWN_RELEASES["2025-09-30"] == "2025-11-19"
    assert SHUTDOWN_RELEASES["2025-12-30"] == "2026-01-13"
    for report, release in SHUTDOWN_RELEASES.items():
        assert pd.Timestamp(release) > pd.Timestamp(report)


def test_attach_public_uses_strictly_prior_information():
    panel = pd.DataFrame({
        "origin_date": pd.to_datetime(["2024-01-10", "2024-01-11"]),
        "target_date": pd.to_datetime(["2024-01-11", "2024-01-12"]),
        "y": [1, 0],
        "horizon": [1, 1],
    })
    gvz = pd.DataFrame({
        "gvz_date": pd.to_datetime(["2024-01-09", "2024-01-10", "2024-01-11"]),
        "pub_gvz_level_lag": [10.0, 20.0, 30.0],
        "pub_gvz_ret1_lag": [0.0, 0.1, 0.2],
        "pub_gvz_chg5_lag": [0.0, 0.1, 0.2],
        "pub_gvz_z20_lag": [0.0, 0.1, 0.2],
    })
    cot = pd.DataFrame({
        "report_date": pd.to_datetime(["2024-01-02", "2024-01-09"]),
        "available_date": pd.to_datetime(["2024-01-09", "2024-01-16"]),
        "pub_cot_mm_net_oi": [0.1, 0.2],
        "pub_cot_prod_net_oi": [-0.1, -0.2],
        "pub_cot_swap_net_oi": [0.05, 0.06],
        "pub_cot_mm_net_change_1w_oi": [0.01, 0.02],
        "pub_cot_oi_change_1w": [0.03, 0.04],
    })
    z = attach_public(panel, gvz, cot)
    assert float(z.loc[0, "pub_gvz_level_lag"]) == 10.0
    assert float(z.loc[1, "pub_gvz_level_lag"]) == 20.0
    assert pd.Timestamp(z.loc[0, "gvz_date"]) < pd.Timestamp(z.loc[0, "origin_date"])
    assert pd.Timestamp(z.loc[0, "available_date"]) < pd.Timestamp(z.loc[0, "origin_date"])
    assert float(z.loc[0, "pub_cot_mm_net_oi"]) == 0.1
