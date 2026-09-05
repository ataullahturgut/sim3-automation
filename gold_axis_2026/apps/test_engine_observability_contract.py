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
        "level_emergency": "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE",
        "reversal_emergency": "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE",
        # Historical archived field deliberately retained in the decision payload.
        # The promoted successor registry must not read this value as successor output.
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
        "CAUSAL_PATCH": ("WAITING", "WAITING_ELIGIBLE_MONTH_END_ORIGIN", False, {}),
        "VW_MIDAS_MSVR": ("BLOCKED", "BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN", False, {}),
        "MOMENTUM_3M": ("WAITING", "WAITING_ELIGIBLE_MONTH_END_ORIGIN", False, {}),
        "RANDOM_WALK": ("WAITING", "WAITING_ELIGIBLE_MONTH_END_ORIGIN", False, {}),
        "MONTHLY_DIRECTION_3M": ("ACTIVE", "VERIFIED_PERSISTED_CONTEXT_AVAILABLE", True, {}),
        "FAST": ("ACTIVE", "VERIFIED_PERSISTED_CONTEXT_AVAILABLE", True, {}),
        "SLOW": ("ACTIVE", "VERIFIED_PERSISTED_CONTEXT_AVAILABLE", True, {}),
        "MACRO_EVENT_SUCCESSOR_V2": (
            "ACTIVE",
            "ACTIVE_MACRO_EVENT_SUCCESSOR_V2_EVENT_RISK_CONTEXT",
            False,
            {
                "successor_id": "MACRO_EVENT_SUCCESSOR_V2",
                "current_state": "MACRO_MIXED_OR_SMALL",
                "current_state_evidence_class": "HISTORICAL_REPLAY",
                "current_state_as_of": "2026-09-04T12:30:00Z",
                "information_cutoff": "2026-09-04T12:30:00Z",
                "reference_kind": "HISTORICAL_REPLAY_SUCCESSOR_CONTEXT",
            },
        ),
        "EMERGENCY_LEVEL": ("WAITING", "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE", False, {}),
        "EMERGENCY_REVERSAL": ("WAITING", "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE", False, {}),
        "BOCPD_RETURN_SUCCESSOR_V1": (
            "ACTIVE",
            "ACTIVE_BOCPD_RETURN_SUCCESSOR_V1_REGIME_CONTEXT",
            False,
            {
                "successor_id": "BOCPD_RETURN_SUCCESSOR_V1",
                "current_state": "NO_ADVERSE_BREAK_CANDIDATE",
                "current_state_evidence_class": "HISTORICAL_REPLAY",
                "current_state_as_of": "2026-08-31T21:00:00Z",
                "information_cutoff": "2026-08-31T21:00:00Z",
                "reference_kind": "HISTORICAL_REPLAY_SUCCESSOR_CONTEXT",
            },
        ),
        "GVZ_RISK": ("ACTIVE", "VERIFIED_PERSISTED_CONTEXT_AVAILABLE", False, {}),
    }
    return [
        {
            "engine_id": engine_id,
            "engine_version": engine_id if engine_id in {"BOCPD_RETURN_SUCCESSOR_V1", "MACRO_EVENT_SUCCESSOR_V2"} else f"runtime::{engine_id}",
            "engine_role": ("REGIME_BREAK_CONTEXT" if engine_id == "BOCPD_RETURN_SUCCESSOR_V1" else "EVENT_RISK_CONTEXT" if engine_id == "MACRO_EVENT_SUCCESSOR_V2" else "TEST_RUNTIME_ROLE"),
            "as_of": "2026-09-05T14:30:00Z",
            "target_context": "2026-09",
            "evidence_class": "RUNTIME_GOVERNANCE_AUDIT",
            "runtime_status": values[0],
            "status_code": values[1],
            "direction_vote_permitted": values[2],
            "git_commit": "test-sha",
            "metadata": values[3],
        }
        for engine_id, values in status.items()
    ]


def test_all_governed_engines_are_always_present() -> None:
    rows = build_engine_inventory(_decision(), [], [])
    assert ENGINE_OBSERVABILITY_CONTRACT == "ALL_GOVERNED_FORECAST_DIRECTION_ENGINES_VISIBLE_V4_BOCPD_AND_MACRO_SUCCESSORS_PROMOTED"
    assert tuple(row["engine_id"] for row in rows) == ENGINE_DISPLAY_ORDER
    assert "BOCPD" not in ENGINE_DISPLAY_ORDER
    assert "BOCPD_RETURN_SUCCESSOR_V1" in ENGINE_DISPLAY_ORDER
    assert "MACRO_EVENT_SUCCESSOR_V2" in ENGINE_DISPLAY_ORDER
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


def test_current_successors_are_present_without_losing_vw_blocker() -> None:
    rows = {row["engine_id"]: row for row in build_engine_inventory(_decision(), [], [])}
    assert rows["VW_MIDAS_MSVR"]["status"] == "BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN"
    assert rows["EMERGENCY_LEVEL"]["status"] == "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE"
    assert rows["EMERGENCY_REVERSAL"]["status"] == "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE"
    assert "BOCPD" not in rows
    assert rows["BOCPD_RETURN_SUCCESSOR_V1"]["status"] == "WAITING_RUNTIME_PROMOTION_RECORD"
    assert rows["MACRO_EVENT_SUCCESSOR_V2"]["status"] == "WAITING_RUNTIME_PROMOTION_RECORD"
    assert rows["BOCPD_RETURN_SUCCESSOR_V1"]["direction_vote"] is False
    assert rows["MACRO_EVENT_SUCCESSOR_V2"]["direction_vote"] is False

    import re
    forbidden = {"BUY", "SELL", "HOLD", "EXIT", "REDUCE"}
    joined = " ".join(str(value) for row in rows.values() for value in row.values()).upper()
    assert forbidden.isdisjoint(set(re.findall(r"[A-Z]+", joined)))
    assert all(row["canonical_authority"] is False for row in rows.values())


def test_promoted_bocpd_successor_runtime_exposes_aug31_context_without_direction_vote() -> None:
    rows = {row["engine_id"]: row for row in build_engine_inventory(_decision(), [], [], _runtime_rows())}
    bocpd = rows["BOCPD_RETURN_SUCCESSOR_V1"]
    assert bocpd["runtime_status"] == "ACTIVE"
    assert bocpd["runtime_status_code"] == "ACTIVE_BOCPD_RETURN_SUCCESSOR_V1_REGIME_CONTEXT"
    assert bocpd["status"] == "STORED_CONTEXT_AVAILABLE"
    assert bocpd["output"] == "NO_ADVERSE_BREAK_CANDIDATE"
    assert bocpd["evidence_class"] == "HISTORICAL_REPLAY"
    assert bocpd["as_of"] == "2026-08-31T21:00:00Z"
    assert bocpd["reference_kind"] == "HISTORICAL_REPLAY_SUCCESSOR_CONTEXT"
    assert bocpd["direction_vote"] is False
    assert bocpd["canonical_authority"] is False


def test_promoted_macro_successor_runtime_exposes_current_event_context_without_direction_vote() -> None:
    rows = {row["engine_id"]: row for row in build_engine_inventory(_decision(), [], [], _runtime_rows())}
    macro = rows["MACRO_EVENT_SUCCESSOR_V2"]
    assert macro["runtime_status"] == "ACTIVE"
    assert macro["runtime_status_code"] == "ACTIVE_MACRO_EVENT_SUCCESSOR_V2_EVENT_RISK_CONTEXT"
    assert macro["status"] == "STORED_CONTEXT_AVAILABLE"
    assert macro["output"] == "MACRO_MIXED_OR_SMALL"
    assert macro["evidence_class"] == "HISTORICAL_REPLAY"
    assert macro["as_of"] == "2026-09-04T12:30:00Z"
    assert macro["reference_kind"] == "HISTORICAL_REPLAY_SUCCESSOR_CONTEXT"
    assert macro["direction_vote"] is False
    assert macro["canonical_authority"] is False


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


def test_inventory_counts_are_explicit_before_and_after_runtime_promotion_record() -> None:
    fallback_rows = build_engine_inventory(_decision(), [], [])
    fallback_counts = engine_inventory_counts(fallback_rows)
    assert fallback_counts["total"] == 12
    assert fallback_counts["active"] == 4
    assert fallback_counts["issued"] == 0
    assert fallback_counts["blocked"] == 1
    assert fallback_counts["waiting"] == 7

    promoted_rows = build_engine_inventory(_decision(), [], [], _runtime_rows())
    promoted_counts = engine_inventory_counts(promoted_rows)
    assert promoted_counts["total"] == 12
    assert promoted_counts["active"] == 6
    assert promoted_counts["issued"] == 0
    assert promoted_counts["blocked"] == 1
    assert promoted_counts["waiting"] == 5


def test_runtime_ledger_is_status_authority_but_not_direction_vote_authority() -> None:
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
    assert rows["BOCPD_RETURN_SUCCESSOR_V1"]["direction_vote"] is False
    assert rows["MACRO_EVENT_SUCCESSOR_V2"]["direction_vote"] is False
    assert all(row["canonical_authority"] is False for row in rows.values())


def test_runtime_cannot_self_promote_non_direction_engine_to_direction_vote() -> None:
    runtime = _runtime_rows()
    for row in runtime:
        if row["engine_id"] == "GVZ_RISK":
            row["direction_vote_permitted"] = True
    rows = {row["engine_id"]: row for row in build_engine_inventory(_decision(), [], [], runtime)}
    assert rows["GVZ_RISK"]["direction_vote"] is False
