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
        "macro_event_state": "BLOCKED_NOT_FULLY_RECOVERED",
        "level_emergency": "BLOCKED_NO_PERSISTED_MONTHLY_PRICE_REFERENCE",
        "reversal_emergency": "BLOCKED_NO_PERSISTED_MONTHLY_PRICE_REFERENCE",
        "bocpd_context": "BLOCKED_EXACT_FORWARD_BOCPD_RULE_NOT_RECOVERED",
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


def test_all_governed_engines_are_always_present() -> None:
    rows = build_engine_inventory(_decision(), [], [])
    assert ENGINE_OBSERVABILITY_CONTRACT == "ALL_GOVERNED_FORECAST_DIRECTION_ENGINES_VISIBLE_V1"
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
    assert rows["VW_MIDAS_MSVR"]["status"] == "BLOCKED_NOT_PROVEN_EXECUTABLE"
    assert rows["MACRO_EVENT"]["status"] == "BLOCKED_NOT_FULLY_RECOVERED"
    assert rows["EMERGENCY_LEVEL"]["status"] == "BLOCKED_NO_PERSISTED_MONTHLY_PRICE_REFERENCE"
    assert rows["EMERGENCY_REVERSAL"]["status"] == "BLOCKED_NO_PERSISTED_MONTHLY_PRICE_REFERENCE"
    assert rows["BOCPD"]["status"] == "BLOCKED_EXACT_FORWARD_BOCPD_RULE_NOT_RECOVERED"

    forbidden = {"BUY", "SELL", "HOLD", "EXIT", "REDUCE"}
    joined = " ".join(str(value) for row in rows.values() for value in row.values()).upper()
    assert not any(term in joined for term in forbidden)
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
    assert counts["blocked"] == 5
    assert counts["waiting"] == 3
