from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "gold_axis_2026" / "GOLD_CONTROL_PROJECT_MANIFEST.md"
ENGINE = ROOT / "gold_axis_2026" / "apps" / "engine_observability_contract.py"
TEST = ROOT / "gold_axis_2026" / "apps" / "test_engine_observability_contract.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one occurrence, found {count}")
    return text.replace(old, new, 1)


def patch_manifest() -> None:
    text = MANIFEST.read_text(encoding="utf-8")
    text = replace_once(text, "**Manifest version:** 1.34", "**Manifest version:** 1.35", "manifest version")
    text = replace_once(text, "this v1.34 manifest governs", "this v1.35 manifest governs", "manifest authority wording")

    text = replace_once(
        text,
        "- `BOCPD_RETURN_SUCCESSOR_V1` — active regime/break context only; no direction vote.\n",
        "- `BOCPD_RETURN_SUCCESSOR_V1` — active regime/break context only; no direction vote.\n"
        "- `MACRO_EVENT_SUCCESSOR_V2` — active labor-event risk/context only; no direction vote and no H=1 price forecast.\n",
        "direction/context Macro successor bullet",
    )

    macro_section = """# 9A. MACRO EVENT GOVERNANCE — v1.35 RUNTIME REPLACEMENT

Archived engine identity:

`MACRO_EVENT`

remains historically traceable with the recovery limitation:

`BLOCKED_EXACT_MACRO_SCORE_CONSENSUS_AND_VINTAGE_CONTRACT_NOT_RECOVERED`

The archived identity is **not** repaired or renamed. Its partially recovered historical rule remains audit evidence only. It is removed from the current governed application runtime slot and replaced by the separately preregistered and validated successor identity:

`MACRO_EVENT_SUCCESSOR_V2`

Current operational target status after the v1.35 runtime deployment:

`ACTIVE_MACRO_EVENT_SUCCESSOR_V2_EVENT_RISK_CONTEXT`

Role:

`EVENT_RISK_CONTEXT`

Binding locks remain:

- direction vote = false;
- no H=1 monthly-average XAU/USD price forecast;
- no automatic action;
- no selector/ensemble role;
- no position mapping;
- no post-result retuning of the frozen V2 robust-score rule;
- no silent consensus-provider substitution;
- source lineage remains bound to the governed research source run `6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a` for the validated historical evidence.

Validation basis frozen before this promotion:

- robust-score replay: `PASS_V2_ROBUST_PREREG_REPLAY_REPRODUCIBLE`;
- event-reaction validation: `PASS_EVENT_REACTION_EVIDENCE`;
- frozen VAL+LOCK strong-shock events: `8`;
- directional hits in the preregistered 15-minute primary window: `7/8` = `87.5%`;
- exact one-sided sign-test p-value: `0.03515625`;
- median signed R15: `+0.9590818647119803%`.

Latest governed event-context reference from the frozen panel is the August 2026 Employment Situation released 2026-09-04:

- robust composite score = `-0.414773053241`;
- state = `MACRO_MIXED_OR_SMALL`.

This current September state remains `HISTORICAL_REPLAY` evidence because it was reconstructed later from historical/PIT research data. The **runtime promotion itself** is effective only at the true 2026-09-05 deployment time and must not be backdated to 2026-09-04.

The validation supports the narrow intended use of immediate event-risk/context classification. It does **not** establish H=1 monthly forecast skill, trading profitability, automatic action authority, selector/ensemble eligibility, or position mapping.

---

"""
    text = replace_once(text, "# 10. EMERGENCY GOVERNANCE\n", macro_section + "# 10. EMERGENCY GOVERNANCE\n", "insert Macro successor governance")

    text = replace_once(
        text,
        "# 11. CURRENT PRODUCTION RUNTIME AUTHORITY — v1.34 TARGET STATE",
        "# 11. CURRENT PRODUCTION RUNTIME AUTHORITY — v1.35 TARGET STATE",
        "runtime authority heading",
    )
    text = replace_once(
        text,
        "- `ACTIVE = 5`\n- `WAITING = 5`\n- `BLOCKED = 2`\n- direction-vote permitted = `3`\n- total current governed application motors = `12`",
        "- `ACTIVE = 6`\n- `WAITING = 5`\n- `BLOCKED = 1`\n- direction-vote permitted = `3`\n- total current governed application motors = `12`",
        "runtime counts",
    )
    text = replace_once(
        text,
        "Current BLOCKED application identities:\n\n- `VW_MIDAS_MSVR` — `BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN`\n- `MACRO_EVENT` — `BLOCKED_EXACT_MACRO_SCORE_CONSENSUS_AND_VINTAGE_CONTRACT_NOT_RECOVERED`\n\nCurrent active BOCPD replacement:",
        "Current BLOCKED application identity:\n\n- `VW_MIDAS_MSVR` — `BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN`\n\nCurrent active replacements:\n\n- `MACRO_EVENT_SUCCESSOR_V2` — `ACTIVE_MACRO_EVENT_SUCCESSOR_V2_EVENT_RISK_CONTEXT`\n\nCurrent active BOCPD replacement:",
        "blocked/current replacement inventory",
    )
    text = replace_once(
        text,
        "The archived `BOCPD` ledger identity remains queryable for audit/history but is no longer part of the 12-motor current application registry. Its latest archival runtime record may remain `BLOCKED` with explicit `replaced_by = BOCPD_RETURN_SUCCESSOR_V1` metadata; this does not increase the current application blocked count.\n",
        "The archived `BOCPD` ledger identity remains queryable for audit/history but is no longer part of the 12-motor current application registry. Its latest archival runtime record may remain `BLOCKED` with explicit `replaced_by = BOCPD_RETURN_SUCCESSOR_V1` metadata; this does not increase the current application blocked count.\n\n"
        "The archived `MACRO_EVENT` ledger identity likewise remains queryable for audit/history but is no longer part of the 12-motor current application registry. Its latest archival runtime record may remain `BLOCKED` with explicit `replaced_by = MACRO_EVENT_SUCCESSOR_V2` metadata; this also does not increase the current application blocked count.\n",
        "archived Macro ledger wording",
    )
    text = replace_once(
        text,
        "The BOCPD successor runtime replacement is explicitly authorized to update only the append-only engine runtime ledger/schema required to introduce the new engine identity.",
        "The BOCPD and Macro Event successor runtime replacements are explicitly authorized to update only the append-only engine runtime ledger/schema required to introduce their separately validated successor identities.",
        "authority-store runtime authorization",
    )
    text = replace_once(text, "# 13. UI CONTRACT — v1.34", "# 13. UI CONTRACT — v1.35", "UI heading")
    text = replace_once(
        text,
        "The archived `BOCPD` identity remains visible only in audit/history surfaces where its recovery-blocked lineage is relevant.\n",
        "The archived `BOCPD` identity remains visible only in audit/history surfaces where its recovery-blocked lineage is relevant.\n\n"
        "`MACRO_EVENT_SUCCESSOR_V2` replaces the archived `MACRO_EVENT` card in the current 12-motor application inventory and must display:\n\n"
        "- operational runtime status: `ACTIVE`;\n"
        "- role: `EVENT_RISK_CONTEXT`;\n"
        "- current September event-context reference: `MACRO_MIXED_OR_SMALL`;\n"
        "- reference evidence: `HISTORICAL_REPLAY`;\n"
        "- direction vote: `false`.\n\n"
        "The archived `MACRO_EVENT` identity remains visible only in audit/history surfaces where its recovery-blocked lineage is relevant.\n",
        "Macro UI contract",
    )
    MANIFEST.write_text(text, encoding="utf-8")


def patch_engine() -> None:
    text = ENGINE.read_text(encoding="utf-8")
    text = replace_once(
        text,
        'ENGINE_OBSERVABILITY_CONTRACT = "ALL_GOVERNED_FORECAST_DIRECTION_ENGINES_VISIBLE_V3_BOCPD_SUCCESSOR_PROMOTED"',
        'ENGINE_OBSERVABILITY_CONTRACT = "ALL_GOVERNED_FORECAST_DIRECTION_ENGINES_VISIBLE_V4_BOCPD_AND_MACRO_SUCCESSORS_PROMOTED"',
        "engine observability contract",
    )
    text = replace_once(text, '    "MACRO_EVENT",\n', '    "MACRO_EVENT_SUCCESSOR_V2",\n', "display order Macro replacement")
    old_block = '''    "MACRO_EVENT": {\n        "label": "Macro Event",\n        "category": "EVENT_RISK",\n        "role": "Timestamp-safe event-risk state only",\n        "version": "MACRO_EVENT_PARTIAL_RULE_RECOVERED_SOURCE_CONTRACT_BLOCKED",\n        "default_status": "BLOCKED_EXACT_MACRO_SCORE_CONSENSUS_AND_VINTAGE_CONTRACT_NOT_RECOVERED",\n        "direction_vote": False,\n        "decision_key": "macro_event_state",\n    },\n'''
    new_block = '''    "MACRO_EVENT_SUCCESSOR_V2": {\n        "label": "Macro Event · Successor V2",\n        "category": "EVENT_RISK",\n        "role": "Active timestamp-safe labor-event risk/context; successor to archived MACRO_EVENT",\n        "version": "MACRO_EVENT_SUCCESSOR_V2",\n        "default_status": "WAITING_RUNTIME_PROMOTION_RECORD",\n        "direction_vote": False,\n        "decision_key": "macro_event_successor_context",\n    },\n'''
    text = replace_once(text, old_block, new_block, "registry Macro replacement")

    old_func = '''def _successor_context_reference(engine_id: str, runtime: dict[str, Any] | None) -> dict[str, Any] | None:\n    if engine_id != "BOCPD_RETURN_SUCCESSOR_V1" or not runtime:\n        return None\n    metadata = runtime.get("metadata")\n    if not isinstance(metadata, dict):\n        return None\n    if _text(metadata.get("successor_id")) != "BOCPD_RETURN_SUCCESSOR_V1":\n        return None\n    state = metadata.get("current_state")\n    if not _available(state):\n        return None\n    if runtime.get("direction_vote_permitted") is not False:\n        return None\n    return {\n        "state": _text(state),\n        "evidence_class": _text(metadata.get("current_state_evidence_class")) or _text(runtime.get("evidence_class")),\n        "state_as_of": metadata.get("current_state_as_of") or runtime.get("as_of"),\n        "information_cutoff": metadata.get("information_cutoff"),\n        "reference_kind": metadata.get("reference_kind") or "RUNTIME_SUCCESSOR_CONTEXT_REFERENCE",\n    }\n'''
    new_func = '''def _successor_context_reference(engine_id: str, runtime: dict[str, Any] | None) -> dict[str, Any] | None:\n    governed_successors = {"BOCPD_RETURN_SUCCESSOR_V1", "MACRO_EVENT_SUCCESSOR_V2"}\n    if engine_id not in governed_successors or not runtime:\n        return None\n    metadata = runtime.get("metadata")\n    if not isinstance(metadata, dict):\n        return None\n    if _text(metadata.get("successor_id")) != engine_id:\n        return None\n    state = metadata.get("current_state")\n    if not _available(state):\n        return None\n    if runtime.get("direction_vote_permitted") is not False:\n        return None\n    return {\n        "state": _text(state),\n        "evidence_class": _text(metadata.get("current_state_evidence_class")) or _text(runtime.get("evidence_class")),\n        "state_as_of": metadata.get("current_state_as_of") or runtime.get("as_of"),\n        "information_cutoff": metadata.get("information_cutoff"),\n        "reference_kind": metadata.get("reference_kind") or "RUNTIME_SUCCESSOR_CONTEXT_REFERENCE",\n    }\n'''
    text = replace_once(text, old_func, new_func, "generic successor context reference")
    ENGINE.write_text(text, encoding="utf-8")


def patch_test() -> None:
    text = TEST.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '        "MACRO_EVENT": ("BLOCKED", "BLOCKED_EXACT_MACRO_SCORE_CONSENSUS_AND_VINTAGE_CONTRACT_NOT_RECOVERED", False, {}),\n',
        '''        "MACRO_EVENT_SUCCESSOR_V2": (\n            "ACTIVE",\n            "ACTIVE_MACRO_EVENT_SUCCESSOR_V2_EVENT_RISK_CONTEXT",\n            False,\n            {\n                "successor_id": "MACRO_EVENT_SUCCESSOR_V2",\n                "current_state": "MACRO_MIXED_OR_SMALL",\n                "current_state_evidence_class": "HISTORICAL_REPLAY",\n                "current_state_as_of": "2026-09-04T12:30:00Z",\n                "information_cutoff": "2026-09-04T12:30:00Z",\n                "reference_kind": "HISTORICAL_REPLAY_SUCCESSOR_CONTEXT",\n            },\n        ),\n''',
        "test runtime Macro successor",
    )
    text = replace_once(
        text,
        '            "engine_version": "BOCPD_RETURN_SUCCESSOR_V1" if engine_id == "BOCPD_RETURN_SUCCESSOR_V1" else f"runtime::{engine_id}",\n            "engine_role": "REGIME_BREAK_CONTEXT" if engine_id == "BOCPD_RETURN_SUCCESSOR_V1" else "TEST_RUNTIME_ROLE",\n',
        '            "engine_version": engine_id if engine_id in {"BOCPD_RETURN_SUCCESSOR_V1", "MACRO_EVENT_SUCCESSOR_V2"} else f"runtime::{engine_id}",\n            "engine_role": ("REGIME_BREAK_CONTEXT" if engine_id == "BOCPD_RETURN_SUCCESSOR_V1" else "EVENT_RISK_CONTEXT" if engine_id == "MACRO_EVENT_SUCCESSOR_V2" else "TEST_RUNTIME_ROLE"),\n',
        "test runtime successor identities",
    )
    text = replace_once(
        text,
        '    assert ENGINE_OBSERVABILITY_CONTRACT == "ALL_GOVERNED_FORECAST_DIRECTION_ENGINES_VISIBLE_V3_BOCPD_SUCCESSOR_PROMOTED"\n    assert tuple(row["engine_id"] for row in rows) == ENGINE_DISPLAY_ORDER\n    assert "BOCPD" not in ENGINE_DISPLAY_ORDER\n    assert "BOCPD_RETURN_SUCCESSOR_V1" in ENGINE_DISPLAY_ORDER\n',
        '    assert ENGINE_OBSERVABILITY_CONTRACT == "ALL_GOVERNED_FORECAST_DIRECTION_ENGINES_VISIBLE_V4_BOCPD_AND_MACRO_SUCCESSORS_PROMOTED"\n    assert tuple(row["engine_id"] for row in rows) == ENGINE_DISPLAY_ORDER\n    assert "BOCPD" not in ENGINE_DISPLAY_ORDER\n    assert "MACRO_EVENT" not in ENGINE_DISPLAY_ORDER\n    assert "BOCPD_RETURN_SUCCESSOR_V1" in ENGINE_DISPLAY_ORDER\n    assert "MACRO_EVENT_SUCCESSOR_V2" in ENGINE_DISPLAY_ORDER\n',
        "test display order assertions",
    )
    old_test = '''def test_archived_bocpd_is_replaced_in_current_registry_without_losing_other_blockers() -> None:\n    rows = {row["engine_id"]: row for row in build_engine_inventory(_decision(), [], [])}\n    assert rows["VW_MIDAS_MSVR"]["status"] == "BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN"\n    assert rows["MACRO_EVENT"]["status"] == "BLOCKED_EXACT_MACRO_SCORE_CONSENSUS_AND_VINTAGE_CONTRACT_NOT_RECOVERED"\n    assert rows["EMERGENCY_LEVEL"]["status"] == "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE"\n    assert rows["EMERGENCY_REVERSAL"]["status"] == "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE"\n    assert "BOCPD" not in rows\n    assert rows["BOCPD_RETURN_SUCCESSOR_V1"]["status"] == "WAITING_RUNTIME_PROMOTION_RECORD"\n    assert rows["BOCPD_RETURN_SUCCESSOR_V1"]["direction_vote"] is False\n\n    import re\n    forbidden = {"BUY", "SELL", "HOLD", "EXIT", "REDUCE"}\n    joined = " ".join(str(value) for row in rows.values() for value in row.values()).upper()\n    assert forbidden.isdisjoint(set(re.findall(r"[A-Z]+", joined)))\n    assert all(row["canonical_authority"] is False for row in rows.values())\n'''
    new_test = '''def test_archived_successors_are_replaced_in_current_registry_without_losing_vw_blocker() -> None:\n    rows = {row["engine_id"]: row for row in build_engine_inventory(_decision(), [], [])}\n    assert rows["VW_MIDAS_MSVR"]["status"] == "BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN"\n    assert rows["EMERGENCY_LEVEL"]["status"] == "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE"\n    assert rows["EMERGENCY_REVERSAL"]["status"] == "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE"\n    assert "BOCPD" not in rows\n    assert "MACRO_EVENT" not in rows\n    assert rows["BOCPD_RETURN_SUCCESSOR_V1"]["status"] == "WAITING_RUNTIME_PROMOTION_RECORD"\n    assert rows["MACRO_EVENT_SUCCESSOR_V2"]["status"] == "WAITING_RUNTIME_PROMOTION_RECORD"\n    assert rows["BOCPD_RETURN_SUCCESSOR_V1"]["direction_vote"] is False\n    assert rows["MACRO_EVENT_SUCCESSOR_V2"]["direction_vote"] is False\n\n    import re\n    forbidden = {"BUY", "SELL", "HOLD", "EXIT", "REDUCE"}\n    joined = " ".join(str(value) for row in rows.values() for value in row.values()).upper()\n    assert forbidden.isdisjoint(set(re.findall(r"[A-Z]+", joined)))\n    assert all(row["canonical_authority"] is False for row in rows.values())\n'''
    text = replace_once(text, old_test, new_test, "archived successor test")

    marker = '''def test_gvz_is_visible_as_risk_not_direction() -> None:\n'''
    macro_test = '''def test_promoted_macro_successor_runtime_exposes_current_event_context_without_direction_vote() -> None:\n    rows = {row["engine_id"]: row for row in build_engine_inventory(_decision(), [], [], _runtime_rows())}\n    macro = rows["MACRO_EVENT_SUCCESSOR_V2"]\n    assert macro["runtime_status"] == "ACTIVE"\n    assert macro["runtime_status_code"] == "ACTIVE_MACRO_EVENT_SUCCESSOR_V2_EVENT_RISK_CONTEXT"\n    assert macro["status"] == "STORED_CONTEXT_AVAILABLE"\n    assert macro["output"] == "MACRO_MIXED_OR_SMALL"\n    assert macro["evidence_class"] == "HISTORICAL_REPLAY"\n    assert macro["as_of"] == "2026-09-04T12:30:00Z"\n    assert macro["reference_kind"] == "HISTORICAL_REPLAY_SUCCESSOR_CONTEXT"\n    assert macro["direction_vote"] is False\n    assert macro["canonical_authority"] is False\n\n\n'''
    text = replace_once(text, marker, macro_test + marker, "insert Macro successor runtime test")
    text = replace_once(
        text,
        '    assert fallback_counts["blocked"] == 2\n    assert fallback_counts["waiting"] == 6\n',
        '    assert fallback_counts["blocked"] == 1\n    assert fallback_counts["waiting"] == 7\n',
        "fallback counts",
    )
    text = replace_once(
        text,
        '    assert promoted_counts["active"] == 5\n    assert promoted_counts["issued"] == 0\n    assert promoted_counts["blocked"] == 2\n    assert promoted_counts["waiting"] == 5\n',
        '    assert promoted_counts["active"] == 6\n    assert promoted_counts["issued"] == 0\n    assert promoted_counts["blocked"] == 1\n    assert promoted_counts["waiting"] == 5\n',
        "promoted counts",
    )
    text = replace_once(
        text,
        '    assert rows["BOCPD_RETURN_SUCCESSOR_V1"]["direction_vote"] is False\n    assert all(row["canonical_authority"] is False for row in rows.values())\n',
        '    assert rows["BOCPD_RETURN_SUCCESSOR_V1"]["direction_vote"] is False\n    assert rows["MACRO_EVENT_SUCCESSOR_V2"]["direction_vote"] is False\n    assert all(row["canonical_authority"] is False for row in rows.values())\n',
        "runtime authority Macro direction lock",
    )
    TEST.write_text(text, encoding="utf-8")


def main() -> None:
    patch_manifest()
    patch_engine()
    patch_test()
    print("MACRO_EVENT_SUCCESSOR_V2_PROMOTION_PATCH_APPLIED")


if __name__ == "__main__":
    main()
