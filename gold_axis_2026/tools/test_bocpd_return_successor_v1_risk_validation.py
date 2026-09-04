from __future__ import annotations

import numpy as np
import pandas as pd

from bocpd_return_successor_v1 import build_replay, load_core_monthly
from bocpd_return_successor_v1_risk_validation import (
    add_forward_outcomes,
    build_risk_validation,
    period_summary,
)


def test_forward_outcomes_start_after_signal_month():
    idx = pd.date_range("2020-01-01", periods=5, freq="MS")
    rows = pd.DataFrame(
        {
            "state": ["NO_ADVERSE_BREAK_CANDIDATE"] * 5,
            "period": ["VAL"] * 5,
        },
        index=idx,
    )
    price = pd.Series([100.0, 110.0, 99.0, 90.0, 95.0], index=idx)
    out = add_forward_outcomes(rows, price)
    assert np.isclose(out.loc[pd.Timestamp("2020-01-01"), "fwd_1m"], 0.10)
    assert np.isclose(out.loc[pd.Timestamp("2020-01-01"), "fwd_2m"], -0.01)
    assert np.isclose(out.loc[pd.Timestamp("2020-01-01"), "fwd_3m"], -0.10)
    assert out.loc[pd.Timestamp("2020-01-01"), "tail_2m"] == 0.0
    assert out.loc[pd.Timestamp("2020-01-01"), "tail_3m"] == 1.0


def test_risk_validation_does_not_change_frozen_state_output():
    replay = build_replay()
    frame, _ = build_risk_validation()
    assert list(frame.index) == list(replay.rows.index)
    assert frame["state"].tolist() == replay.rows["state"].tolist()
    assert frame["map_run"].tolist() == replay.rows["map_run"].tolist()
    assert np.allclose(frame["reset_fraction"], replay.rows["reset_fraction"], rtol=0.0, atol=0.0)


def test_validation_contract_roles_and_hard_gates():
    _, summary = build_risk_validation()
    assert summary["validation_status"] == "VALIDATION_RISK_DIAGNOSTIC_COMPLETE"
    assert summary["interpretation"] == "DESCRIPTIVE_ONLY"
    assert summary["primary_risk_horizon"] == "2-3M"
    assert summary["tail_definition"] == "CUMULATIVE_FORWARD_GOLD_RETURN_LE_MINUS_3PCT"
    assert summary["locked_role"] == "DIAGNOSTIC_ONLY"
    assert summary["direction_vote_permitted"] is False
    assert summary["position_mapping_permitted"] is False
    assert summary["automatic_action_approved"] is False
    assert summary["database_writes"] == "NONE"
    assert summary["prospective_claim"] is False
    assert summary["promotion_authorized"] is False
    assert all(summary["hard_gates"].values())


def test_validation_and_locked_candidate_counts_reconcile_engineering_output():
    frame, summary = build_risk_validation()
    val = frame[frame["period"].eq("VAL")]
    lock = frame[frame["period"].eq("LOCK")]
    assert summary["validation"]["candidate"]["n_state_rows"] == int(
        (val["state"] == "ADVERSE_BREAK_CANDIDATE").sum()
    )
    assert summary["locked"]["candidate"]["n_state_rows"] == int(
        (lock["state"] == "ADVERSE_BREAK_CANDIDATE").sum()
    )


def test_full_validation_horizons_available_but_locked_tail_is_horizon_specific():
    frame, summary = build_risk_validation()
    val = frame[frame["period"].eq("VAL")]
    assert val[["fwd_1m", "fwd_2m", "fwd_3m"]].notna().all().all()
    lock = summary["locked"]["candidate"]
    assert lock["n_tail_2m"] <= lock["n_state_rows"]
    assert lock["n_tail_3m"] <= lock["n_state_rows"]
