from __future__ import annotations

from engine_observability_contract import (
    ENGINE_DISPLAY_ORDER,
    ENGINE_OBSERVABILITY_CONTRACT,
    build_engine_inventory,
    engine_inventory_counts,
)


def _ref(value=None, state=None) -> dict:
    ref = {
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
    if state is not None:
        ref["state_value"] = state
    return ref


def _runtime_rows() -> list[dict]:
    rows = []
    price_refs = {
        "VW_MIDAS_MSVR_SUCCESSOR_V1": 4565.115907930242,
        "CAUSAL_PATCH": 4452.046728838838,
        "MOMENTUM_3M": 4345.814584037808,
        "RANDOM_WALK": 4397.305673870967,
    }
    for engine_id in ENGINE_DISPLAY_ORDER:
        metadata: dict = {"current_registry": True}
        display_output = None
        display_evidence = None
        vote = engine_id in {"MONTHLY_DIRECTION_3M", "FAST", "SLOW"}
        if engine_id in price_refs:
            metadata["current_month_reference"] = _ref(value=price_refs[engine_id])
        elif engine_id == "EMERGENCY_LEVEL":
            metadata["current_month_reference"] = _ref(state="NEUTRAL")
        elif engine_id == "EMERGENCY_REVERSAL":
            metadata["current_month_reference"] = _ref(state="OFF")
        elif engine_id == "BOCPD_RETURN_SUCCESSOR_V1":
            metadata.update({
                "current_state": "NO_ADVERSE_BREAK_CANDIDATE",
                "current_state_evidence_class": "HISTORICAL_REPLAY",
                "current_state_as_of": "2026-09-04T13:42:09Z",
                "information_cutoff": "2026-08-31T21:00:00Z",
            })
        elif engine_id == "MACRO_EVENT_SUCCESSOR_V2":
            metadata.update({
                "current_state": "MACRO_MIXED_OR_SMALL",
                "current_state_evidence_class": "HISTORICAL_REPLAY",
                "current_state_as_of": "2026-09-04T12:30:00Z",
                "information_cutoff": "2026-09-04T12:30:00Z",
            })
        elif engine_id == "MONTHLY_DIRECTION_3M":
            display_output, display_evidence = "DOWN", "LATE_BOOTSTRAP_SHADOW_CONTEXT"
        elif engine_id == "FAST":
            display_output, display_evidence = "ROBUST_UP", "LATE_BOOTSTRAP_SHADOW_CONTEXT"
        elif engine_id == "SLOW":
            display_output, display_evidence = "ROBUST_UP", "LATE_BOOTSTRAP_SHADOW_CONTEXT"
        elif engine_id == "GVZ_RISK":
            display_output, display_evidence = "GVZ=26.14 · REGIME=ELEVATED · CAP=0.5 · PANIC=false", "LATE_BOOTSTRAP_SHADOW_CONTEXT"
        row = {
            "engine_id": engine_id,
            "engine_version": f"current::{engine_id}",
            "engine_role": "CURRENT_ROLE",
            "as_of": "2026-09-06T19:35:41Z",
            "target_context": "2026-09",
            "evidence_class": "RUNTIME_GOVERNANCE_AUDIT",
            "runtime_status": "ACTIVE",
            "status_code": "ACTIVE_CURRENT_CONTEXT_AVAILABLE",
            "direction_vote_permitted": vote,
            "git_commit": "test-sha",
            "metadata": metadata,
        }
        if display_output is not None:
            row.update({
                "display_output": display_output,
                "display_evidence_class": display_evidence,
                "display_as_of": "2026-09-03T10:14:35Z",
                "display_input_cutoff": "2026-09-03T01:26:55Z",
            })
        rows.append(row)
    return rows


def test_current_contract_and_exact_inventory() -> None:
    rows = build_engine_inventory(None, None, None, _runtime_rows())
    assert ENGINE_OBSERVABILITY_CONTRACT == "GOLD_CONTROL_CURRENT_ENGINE_OBSERVABILITY_V141"
    assert tuple(row["engine_id"] for row in rows) == ENGINE_DISPLAY_ORDER
    assert len(rows) == 12
    assert len({row["engine_id"] for row in rows}) == 12
    assert all(row["runtime_status"] == "ACTIVE" for row in rows)
    assert engine_inventory_counts(rows) == {
        "total": 12,
        "active": 12,
        "waiting": 0,
        "blocked": 0,
        "missing": 0,
        "other": 0,
    }


def test_current_references_and_context_are_separate() -> None:
    rows = {row["engine_id"]: row for row in build_engine_inventory(None, None, None, _runtime_rows())}
    assert rows["VW_MIDAS_MSVR_SUCCESSOR_V1"]["output"] == 4565.115907930242
    assert rows["CAUSAL_PATCH"]["output"] == 4452.046728838838
    assert rows["MOMENTUM_3M"]["output"] == 4345.814584037808
    assert rows["RANDOM_WALK"]["output"] == 4397.305673870967
    assert rows["MONTHLY_DIRECTION_3M"]["output"] == "DOWN"
    assert rows["FAST"]["output"] == "ROBUST_UP"
    assert rows["SLOW"]["output"] == "ROBUST_UP"
    assert rows["EMERGENCY_LEVEL"]["output"] == "NEUTRAL"
    assert rows["EMERGENCY_REVERSAL"]["output"] == "OFF"
    assert rows["BOCPD_RETURN_SUCCESSOR_V1"]["output"] == "NO_ADVERSE_BREAK_CANDIDATE"
    assert rows["MACRO_EVENT_SUCCESSOR_V2"]["output"] == "MACRO_MIXED_OR_SMALL"
    assert "REGIME=ELEVATED" in rows["GVZ_RISK"]["output"]


def test_only_three_direction_votes_can_be_permitted() -> None:
    runtime = _runtime_rows()
    for row in runtime:
        row["direction_vote_permitted"] = True
    rows = {row["engine_id"]: row for row in build_engine_inventory(None, None, None, runtime)}
    permitted = {engine_id for engine_id, row in rows.items() if row["direction_vote"]}
    assert permitted == {"MONTHLY_DIRECTION_3M", "FAST", "SLOW"}
