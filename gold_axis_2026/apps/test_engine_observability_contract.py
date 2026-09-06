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
        # These stale placeholders deliberately prove that governed runtime
        # current-month references override old WAITING presentation text.
        "level_emergency": "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE",
        "reversal_emergency": "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE",
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


def _ref(value=None, state=None, kind="HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE") -> dict:
    ref = {
        "reference_kind": kind,
        "evidence_class": "HISTORICAL_REPLAY",
        "target_month": "2026-09",
        "forecast_origin": "2026-08-31T21:00:00Z",
        "information_cutoff": "2026-08-31T21:00:00Z",
        "replay_executed_at": "2026-09-06T19:18:23Z",
        "canonical_authority": False,
        "prospective_claim": False,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
    }
    if value is not None:
        ref["forecast_value"] = value
        ref["unit"] = "USD/oz"
    if state is not None:
        ref["state_value"] = state
    return ref


def _runtime_rows() -> list[dict]:
    status = {
        "CAUSAL_PATCH": (
            "ACTIVE", "ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE", False,
            {"current_month_reference": _ref(4452.046728838838)},
        ),
        "VW_MIDAS_MSVR_SUCCESSOR_V1": (
            "ACTIVE", "ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE", False,
            {"current_month_reference": _ref(4565.115907930242)},
        ),
        "MOMENTUM_3M": (
            "ACTIVE", "ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE", False,
            {"current_month_reference": _ref(4345.814584037808)},
        ),
        "RANDOM_WALK": (
            "ACTIVE", "ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE", False,
            {"current_month_reference": _ref(4397.305673870967)},
        ),
        "MONTHLY_DIRECTION_3M": ("ACTIVE", "VERIFIED_PERSISTED_CONTEXT_AVAILABLE", True, {}),
        "FAST": ("ACTIVE", "VERIFIED_PERSISTED_CONTEXT_AVAILABLE", True, {}),
        "SLOW": ("ACTIVE", "VERIFIED_PERSISTED_CONTEXT_AVAILABLE", True, {}),
        "MACRO_EVENT_SUCCESSOR_V2": (
            "ACTIVE", "ACTIVE_MACRO_EVENT_SUCCESSOR_V2_EVENT_RISK_CONTEXT", False,
            {
                "successor_id": "MACRO_EVENT_SUCCESSOR_V2",
                "current_state": "MACRO_MIXED_OR_SMALL",
                "current_state_evidence_class": "HISTORICAL_REPLAY",
                "current_state_as_of": "2026-09-04T12:30:00Z",
                "information_cutoff": "2026-09-04T12:30:00Z",
                "reference_kind": "HISTORICAL_REPLAY_SUCCESSOR_CONTEXT",
            },
        ),
        "EMERGENCY_LEVEL": (
            "ACTIVE", "ACTIVE_HISTORICAL_REPLAY_MONTH_OPEN_STATE_AVAILABLE", False,
            {"current_month_reference": _ref(state="NEUTRAL", kind="HISTORICAL_REPLAY_MONTH_OPEN_STATE")},
        ),
        "EMERGENCY_REVERSAL": (
            "ACTIVE", "ACTIVE_HISTORICAL_REPLAY_MONTH_OPEN_STATE_AVAILABLE", False,
            {"current_month_reference": _ref(state="OFF", kind="HISTORICAL_REPLAY_MONTH_OPEN_STATE")},
        ),
        "BOCPD_RETURN_SUCCESSOR_V1": (
            "ACTIVE", "ACTIVE_BOCPD_RETURN_SUCCESSOR_V1_REGIME_CONTEXT", False,
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
            "engine_version": f"runtime::{engine_id}",
            "engine_role": "TEST_RUNTIME_ROLE",
            "as_of": "2026-09-06T19:35:41Z",
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


def test_v140_all_governed_engines_are_present() -> None:
    rows = build_engine_inventory(_decision(), [], [], _runtime_rows())
    assert ENGINE_OBSERVABILITY_CONTRACT == "ALL_GOVERNED_FORECAST_DIRECTION_ENGINES_VISIBLE_V7_ALL_AUG31_SEPTEMBER_REFERENCES_ACTIVE"
    assert tuple(row["engine_id"] for row in rows) == ENGINE_DISPLAY_ORDER
    assert len(rows) == 12
    assert len({row["engine_id"] for row in rows}) == 12
    assert all(row["runtime_status"] == "ACTIVE" for row in rows)


def test_v140_september_price_references_surface_without_authority_promotion() -> None:
    rows = {row["engine_id"]: row for row in build_engine_inventory(_decision(), [], [], _runtime_rows())}
    expected = {
        "CAUSAL_PATCH": 4452.046728838838,
        "VW_MIDAS_MSVR_SUCCESSOR_V1": 4565.115907930242,
        "MOMENTUM_3M": 4345.814584037808,
        "RANDOM_WALK": 4397.305673870967,
    }
    for engine_id, value in expected.items():
        row = rows[engine_id]
        assert row["output"] == value
        assert row["evidence_class"] == "HISTORICAL_REPLAY"
        assert row["forecast_track"] == "HISTORICAL_REPLAY"
        assert row["canonical_authority"] is False
        assert row["direction_vote"] is False
        assert row["status"].startswith("ISSUED_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE")


def test_v140_emergency_month_open_replay_overrides_stale_waiting_placeholders() -> None:
    rows = {row["engine_id"]: row for row in build_engine_inventory(_decision(), [], [], _runtime_rows())}
    assert rows["EMERGENCY_LEVEL"]["output"] == "NEUTRAL"
    assert rows["EMERGENCY_REVERSAL"]["output"] == "OFF"
    for engine_id in ("EMERGENCY_LEVEL", "EMERGENCY_REVERSAL"):
        row = rows[engine_id]
        assert row["evidence_class"] == "HISTORICAL_REPLAY"
        assert row["canonical_authority"] is False
        assert row["direction_vote"] is False
        assert row["status"].startswith("ISSUED_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE")


def test_context_and_promoted_successors_remain_visible() -> None:
    rows = {row["engine_id"]: row for row in build_engine_inventory(_decision(), [], [], _runtime_rows())}
    assert rows["MONTHLY_DIRECTION_3M"]["output"] == "DOWN"
    assert rows["FAST"]["output"] == "ROBUST_UP"
    assert rows["SLOW"]["output"] == "ROBUST_UP"
    assert "REGIME=ELEVATED" in str(rows["GVZ_RISK"]["output"])
    assert rows["BOCPD_RETURN_SUCCESSOR_V1"]["output"] == "NO_ADVERSE_BREAK_CANDIDATE"
    assert rows["MACRO_EVENT_SUCCESSOR_V2"]["output"] == "MACRO_MIXED_OR_SMALL"
    assert rows["BOCPD_RETURN_SUCCESSOR_V1"]["direction_vote"] is False
    assert rows["MACRO_EVENT_SUCCESSOR_V2"]["direction_vote"] is False


def test_v140_inventory_counts_current_reference_surfaces_separately_from_context() -> None:
    rows = build_engine_inventory(_decision(), [], [], _runtime_rows())
    counts = engine_inventory_counts(rows)
    assert counts == {
        "total": 12,
        "active": 6,
        "issued": 6,
        "blocked": 0,
        "waiting": 0,
        "other": 0,
    }


def test_runtime_cannot_self_promote_non_direction_engine_to_direction_vote() -> None:
    runtime = _runtime_rows()
    for row in runtime:
        if row["engine_id"] == "GVZ_RISK":
            row["direction_vote_permitted"] = True
    rows = {row["engine_id"]: row for row in build_engine_inventory(_decision(), [], [], runtime)}
    assert rows["GVZ_RISK"]["direction_vote"] is False
