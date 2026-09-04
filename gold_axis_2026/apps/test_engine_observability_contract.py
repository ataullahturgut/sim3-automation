from __future__ import annotations

from engine_observability_contract import (
    ENGINE_DISPLAY_ORDER,
    ENGINE_OBSERVABILITY_CONTRACT,
    build_engine_inventory,
    engine_inventory_counts,
)


def _decision() -> dict:
    return {
        "evidence_class": "LATE_BOOTSTRAP_SHADOW_CONTEXT",
        "context_only": True,
        "target_month": "2026-09-01",
        "generated_at": "2026-09-03T10:14:35.790Z",
        "monthly_direction_3m": "DOWN",
        "fast_state": "ROBUST_UP",
        "slow_state": "ROBUST_UP",
        "macro_event_state": "BLOCKED_EXACT_MACRO_SCORE_CONSENSUS_AND_VINTAGE_CONTRACT_NOT_RECOVERED",
        "level_emergency": "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE",
        "reversal_emergency": "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE",
        "bocpd_context": "BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED",
        "gvz": 26.14,
        "gvz_cap": 0.5,
        "gvz_panic": False,
        "gvz_regime": "ELEVATED",
        "context_feature_versions": {
            "MONTHLY_DIRECTION_3M": "R4_1_3M_SIMPLE_RETURN_V1",
            "FAST_STATE": "R4_1_SMA20_2_MARKET_DAY_PERSISTENCE_V1",
            "SLOW_STATE": "R4_1_COMPLETED_WEEKLY_SMA4_2_WEEK_PERSISTENCE_V1",
            "GVZ_REGIME": "R4_1_GVZ_RISK_CAP_CONTEXT_V1",
        },
        "context_feature_updated_at": {
            "MONTHLY_DIRECTION_3M": "2026-09-01T13:56:22.357Z",
            "FAST_STATE": "2026-09-02T18:36:16.680Z",
            "SLOW_STATE": "2026-09-02T18:36:16.680Z",
            "GVZ_REGIME": "2026-09-03T10:14:35.790Z",
        },
        "context_feature_input_cutoff": {
            "MONTHLY_DIRECTION_3M": "2026-09-01T13:49:02.380Z",
            "FAST_STATE": "2026-09-01T13:49:02.380Z",
            "SLOW_STATE": "2026-09-01T13:49:02.380Z",
            "GVZ_REGIME": "2026-09-03T01:26:55.875Z",
        },
        "context_feature_evidence": {
            "MONTHLY_DIRECTION_3M": "LATE_BOOTSTRAP_SHADOW_CONTEXT",
            "FAST_STATE": "LATE_BOOTSTRAP_SHADOW_CONTEXT",
            "SLOW_STATE": "LATE_BOOTSTRAP_SHADOW_CONTEXT",
            "GVZ_REGIME": "LATE_BOOTSTRAP_SHADOW_CONTEXT",
        },
    }


def _runtime_rows() -> list[dict]:
    status = {
        "CAUSAL_PATCH": ("WAITING", "WAITING_ELIGIBLE_MONTH_END_ORIGIN", False),
        "VW_MIDAS_MSVR": ("BLOCKED", "BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN", False),
        "MOMENTUM_3M": ("WAITING", "WAITING_ELIGIBLE_MONTH_END_ORIGIN", False),
        "RANDOM_WALK": ("WAITING", "WAITING_ELIGIBLE_MONTH_END_ORIGIN", False),
        "MONTHLY_DIRECTION_3M": ("ACTIVE", "VERIFIED_PERSISTED_CONTEXT_AVAILABLE", True),
        "FAST": ("ACTIVE", "VERIFIED_PERSISTED_CONTEXT_AVAILABLE", True),
        "SLOW": ("ACTIVE", "VERIFIED_PERSISTED_CONTEXT_AVAILABLE", True),
        "MACRO_EVENT": ("BLOCKED", "BLOCKED_EXACT_MACRO_SCORE_CONSENSUS_AND_VINTAGE_CONTRACT_NOT_RECOVERED", False),
        "EMERGENCY_LEVEL": ("WAITING", "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE", False),
        "EMERGENCY_REVERSAL": ("WAITING", "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE", False),
        "BOCPD": ("BLOCKED", "BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED", False),
        "GVZ_RISK": ("ACTIVE", "VERIFIED_PERSISTED_CONTEXT_AVAILABLE", False),
    }
    return [
        {
            "engine_id": engine_id,
            "engine_version": f"runtime::{engine_id}",
            "engine_role": "TEST_RUNTIME_ROLE",
            "as_of": "2026-09-03T14:43:00Z",
            "target_context": "2026-09",
            "evidence_class": "RUNTIME_GOVERNANCE_AUDIT",
            "runtime_status": values[0],
            "status_code": values[1],
            "direction_vote_permitted": values[2],
            "git_commit": "3c7e2b1",
        }
        for engine_id, values in status.items()
    ]


def test_all_governed_engines_are_always_present() -> None:
    rows = build_engine_inventory(_decision(), [], [])
    assert ENGINE_OBSERVABILITY_CONTRACT == "ALL_GOVERNED_FORECAST_DIRECTION_ENGINES_VISIBLE_V2_DUAL_STATE_REFERENCE"
    assert tuple(row["engine_id"] for row in rows) == ENGINE_DISPLAY_ORDER
    assert len(rows) == 12
    assert len({row["engine_id"] for row in rows}) == 12


def test_current_direction_context_is_visible_even_without_h1_expert_rows() -> None:
    rows = {row["engine_id"]: row for row in build_engine_inventory(_decision(), [], [])}

    assert rows["MOMENTUM_3M"]["output"] is None
    assert rows["MOMENTUM_3M"]["status"] == "WAITING_ELIGIBLE_MONTH_END_ORIGIN"
    assert rows["MOMENTUM_3M"]["version"] == "MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND"
    assert rows["RANDOM_WALK"]["output"] is None
    assert rows["RANDOM_WALK"]["status"] == "WAITING_ELIGIBLE_MONTH_END_ORIGIN"
    assert rows["RANDOM_WALK"]["version"] == "RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND"

    assert rows["MONTHLY_DIRECTION_3M"]["output"] == "DOWN"
    assert rows["MONTHLY_DIRECTION_3M"]["status"] == "STORED_CONTEXT_AVAILABLE"
    assert rows["MONTHLY_DIRECTION_3M"]["version"] == "R4_1_3M_SIMPLE_RETURN_V1"
    assert rows["FAST"]["output"] == "ROBUST_UP"
    assert rows["SLOW"]["output"] == "ROBUST_UP"


def test_blockers_remain_visible_and_no_action_or_selector_is_created() -> None:
    rows = {row["engine_id"]: row for row in build_engine_inventory(_decision(), [], [])}
    assert rows["VW_MIDAS_MSVR"]["status"] == "BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN"
    assert rows["MACRO_EVENT"]["status"] == "BLOCKED_EXACT_MACRO_SCORE_CONSENSUS_AND_VINTAGE_CONTRACT_NOT_RECOVERED"
    assert rows["EMERGENCY_LEVEL"]["status"] == "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE"
    assert rows["EMERGENCY_REVERSAL"]["status"] == "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE"
    assert rows["BOCPD"]["status"] == "BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED"

    import re
    forbidden = {"BUY", "SELL", "HOLD", "EXIT", "REDUCE"}
    joined = " ".join(str(value) for row in rows.values() for value in row.values()).upper()
    assert forbidden.isdisjoint(set(re.findall(r"[A-Z]+", joined)))
    assert all(row["canonical_authority"] is False for row in rows.values())


def test_gvz_is_visible_as_risk_not_direction() -> None:
    rows = {row["engine_id"]: row for row in build_engine_inventory(_decision(), [], [])}
    gvz = rows["GVZ_RISK"]
    assert gvz["status"] == "STORED_CONTEXT_AVAILABLE"
    assert "REGIME=ELEVATED" in str(gvz["output"])
    assert "CAP=0.5" in str(gvz["output"])
    assert gvz["direction_vote"] is False


def test_issued_expert_row_overrides_waiting_status_but_not_canonical_authority() -> None:
    month_end = [{
        "expert_id": "CAUSAL_PATCH",
        "model_version": "CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE",
        "forecast_track": "MONTH_END_EXPERT",
        "target_month": "2026-10-01",
        "as_of": "2026-09-30T21:00:00Z",
        "forecast_value": 3500.0,
        "evidence_class": "PROSPECTIVE_SHADOW",
        "canonical_authority": False,
    }]
    rows = {row["engine_id"]: row for row in build_engine_inventory(_decision(), month_end, [])}
    patch = rows["CAUSAL_PATCH"]
    assert patch["status"] == "ISSUED_MONTH_END_EXPERT"
    assert patch["output"] == 3500.0
    assert patch["evidence_class"] == "PROSPECTIVE_SHADOW"
    assert patch["canonical_authority"] is False


def test_inventory_counts_are_explicit() -> None:
    rows = build_engine_inventory(_decision(), [], [])
    counts = engine_inventory_counts(rows)
    assert counts["total"] == 12
    assert counts["active"] == 4
    assert counts["issued"] == 0
    assert counts["blocked"] == 3
    assert counts["waiting"] == 5


def test_runtime_ledger_is_status_authority_but_never_output_authority() -> None:
    decision = _decision()
    rows = {row["engine_id"]: row for row in build_engine_inventory(decision, [], [], _runtime_rows())}
    assert rows["MONTHLY_DIRECTION_3M"]["output"] == "DOWN"
    assert rows["MONTHLY_DIRECTION_3M"]["status"] == "STORED_CONTEXT_AVAILABLE"
    assert rows["MONTHLY_DIRECTION_3M"]["runtime_status"] == "ACTIVE"
    assert rows["MONTHLY_DIRECTION_3M"]["runtime_status_code"] == "VERIFIED_PERSISTED_CONTEXT_AVAILABLE"
    assert rows["MONTHLY_DIRECTION_3M"]["runtime_evidence_class"] == "RUNTIME_GOVERNANCE_AUDIT"
    assert rows["MONTHLY_DIRECTION_3M"]["direction_vote"] is True
    assert rows["GVZ_RISK"]["direction_vote"] is False
    assert rows["CAUSAL_PATCH"]["output"] is None
    assert rows["CAUSAL_PATCH"]["status"] == "WAITING_ELIGIBLE_MONTH_END_ORIGIN"
    assert rows["VW_MIDAS_MSVR"]["status"] == "BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN"
    assert all(row["canonical_authority"] is False for row in rows.values())


def test_runtime_cannot_self_promote_non_direction_engine_to_direction_vote() -> None:
    runtime = _runtime_rows()
    for row in runtime:
        if row["engine_id"] == "GVZ_RISK":
            row["direction_vote_permitted"] = True
    rows = {row["engine_id"]: row for row in build_engine_inventory(_decision(), [], [], runtime)}
    assert rows["GVZ_RISK"]["direction_vote"] is False
