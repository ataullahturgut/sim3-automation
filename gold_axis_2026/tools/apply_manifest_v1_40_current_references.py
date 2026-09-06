from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def replace_one(text: str, old: str, new: str, marker: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"{marker}:expected=1:found={n}")
    return text.replace(old, new, 1)


def patch_runtime() -> None:
    p = ROOT / "data_pipeline" / "data_evidence_spine_runtime_bootstrap.py"
    s = p.read_text(encoding="utf-8")
    repl = {
        '"CAUSAL_PATCH": ("WAITING", "WAITING_ELIGIBLE_MONTH_END_ORIGIN", "MONTHLY_H1_EXPERT", False),':
        '"CAUSAL_PATCH": ("ACTIVE", "ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE", "MONTHLY_H1_EXPERT", False),',
        '"MOMENTUM_3M": ("WAITING", "WAITING_ELIGIBLE_MONTH_END_ORIGIN", "MONTHLY_H1_EXPERT", False),':
        '"MOMENTUM_3M": ("ACTIVE", "ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE", "MONTHLY_H1_EXPERT", False),',
        '"RANDOM_WALK": ("WAITING", "WAITING_ELIGIBLE_MONTH_END_ORIGIN", "MONTHLY_H1_BENCHMARK", False),':
        '"RANDOM_WALK": ("ACTIVE", "ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE", "MONTHLY_H1_BENCHMARK", False),',
        '"EMERGENCY_LEVEL": ("WAITING", "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE", "EMERGENCY_CONTEXT", False),':
        '"EMERGENCY_LEVEL": ("ACTIVE", "ACTIVE_HISTORICAL_REPLAY_MONTH_OPEN_STATE_AVAILABLE", "EMERGENCY_CONTEXT", False),',
        '"EMERGENCY_REVERSAL": ("WAITING", "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE", "EMERGENCY_CONTEXT", False),':
        '"EMERGENCY_REVERSAL": ("ACTIVE", "ACTIVE_HISTORICAL_REPLAY_MONTH_OPEN_STATE_AVAILABLE", "EMERGENCY_CONTEXT", False),',
    }
    for old, new in repl.items():
        s = replace_one(s, old, new, "RUNTIME_STATUS_PATCH_MISMATCH")

    refs = '''CURRENT_MONTH_REFERENCES = {
    "CAUSAL_PATCH": {
        "reference_kind": "HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE",
        "evidence_class": "HISTORICAL_REPLAY",
        "target_month": "2026-09",
        "forecast_origin": "2026-08-31T21:00:00Z",
        "information_cutoff": "2026-08-31T21:00:00Z",
        "replay_executed_at": "2026-09-04T13:42:09.025554Z",
        "forecast_value": 4452.046728838838,
        "unit": "USD/oz",
        "input_fingerprint": "1d7669396dfda83062c4adfe9957b96eb76bd5a568a22c703fa841cff4791eb6",
        "canonical_authority": False,
        "prospective_claim": False,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
    },
    "VW_MIDAS_MSVR_SUCCESSOR_V1": {
        "reference_kind": "HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE",
        "evidence_class": "HISTORICAL_REPLAY",
        "target_month": "2026-09",
        "forecast_origin": "2026-08-31T21:00:00Z",
        "information_cutoff": "2026-08-31T21:00:00Z",
        "source_origin_boundary": "2026-08-31",
        "replay_executed_at": "2026-09-06T19:18:23Z",
        "forecast_value": 4565.115907930242,
        "unit": "USD/oz",
        "canonical_authority": False,
        "prospective_claim": False,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "selected_config": [1.0, 0.05, 0.5],
        "august_common_days": 26,
        "random_walk_same_origin": 4404.829230769231,
        "reconstruction_workflow_run_id": 34054462706,
        "reconstruction_head_sha": "24bede3ef96ba655ebb2108dc69ccf7dfc7e2f33",
        "reconstruction_artifact_id": 9995535377,
    },
    "MOMENTUM_3M": {
        "reference_kind": "HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE",
        "evidence_class": "HISTORICAL_REPLAY",
        "target_month": "2026-09",
        "forecast_origin": "2026-08-31T21:00:00Z",
        "information_cutoff": "2026-08-31T21:00:00Z",
        "replay_executed_at": "2026-09-03T19:21:35Z",
        "forecast_value": 4345.814584037808,
        "unit": "USD/oz",
        "input_fingerprint": "79a4665141f2209fc077c1f67ecf3fbb7145df0df41bcbb621bfa77382774c43",
        "canonical_authority": False,
        "prospective_claim": False,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "selector_status": "NOT_PROVEN_EXPERT_SELECTION_RULE",
    },
    "RANDOM_WALK": {
        "reference_kind": "HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE",
        "evidence_class": "HISTORICAL_REPLAY",
        "target_month": "2026-09",
        "forecast_origin": "2026-08-31T21:00:00Z",
        "information_cutoff": "2026-08-31T21:00:00Z",
        "replay_executed_at": "2026-09-03T19:21:35Z",
        "forecast_value": 4397.305673870967,
        "unit": "USD/oz",
        "input_fingerprint": "1ab3d6a747d191d44476cec1d772766eb2e801c566213223c8d95a88aaf6fca7",
        "canonical_authority": False,
        "prospective_claim": False,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "selector_status": "NOT_PROVEN_EXPERT_SELECTION_RULE",
    },
    "EMERGENCY_LEVEL": {
        "reference_kind": "HISTORICAL_REPLAY_MONTH_OPEN_STATE",
        "evidence_class": "HISTORICAL_REPLAY",
        "target_month": "2026-09",
        "forecast_origin": "2026-08-31T21:00:00Z",
        "information_cutoff": "2026-08-31T21:00:00Z",
        "replay_executed_at": "2026-09-04T13:42:09.025554Z",
        "state_value": "NEUTRAL",
        "monthly_reference": 4452.046728838838,
        "reason": "MONTH_OPEN_INITIALIZED_NO_SEPTEMBER_EOD_OBSERVATION",
        "canonical_authority": False,
        "prospective_claim": False,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
    },
    "EMERGENCY_REVERSAL": {
        "reference_kind": "HISTORICAL_REPLAY_MONTH_OPEN_STATE",
        "evidence_class": "HISTORICAL_REPLAY",
        "target_month": "2026-09",
        "forecast_origin": "2026-08-31T21:00:00Z",
        "information_cutoff": "2026-08-31T21:00:00Z",
        "replay_executed_at": "2026-09-04T13:42:09.025554Z",
        "state_value": "OFF",
        "monthly_reference": 4452.046728838838,
        "reason": "MONTH_OPEN_INITIALIZED_NO_SEPTEMBER_EOD_OBSERVATION",
        "canonical_authority": False,
        "prospective_claim": False,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
    },
}
'''
    s, n = re.subn(r"VW_SEPTEMBER_REFERENCE = \{.*?\n\}\n\n\ndef git_sha", refs + "\n\ndef git_sha", s, flags=re.S)
    if n != 1:
        raise RuntimeError(f"RUNTIME_REFERENCE_BLOCK_PATCH_FAILED:{n}")

    old = '''        if engine_id == "VW_MIDAS_MSVR_SUCCESSOR_V1":
            metadata.update(
                {
                    "model_status": "ACTIVE_RESEARCH_SHADOW_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE",
                    "current_month_reference": dict(VW_SEPTEMBER_REFERENCE),
                    "no_prospective_forecast_issued": True,
                    "later_prospective_validation_origin": "2026-09-30T21:00:00Z",
                    "later_prospective_validation_target": "2026-10",
                    "prospective_claim": False,
                    "canonical_forecast_authority": False,
                }
            )
        else:
            metadata["no_forecast_issued"] = True
'''
    new = '''        if engine_id in CURRENT_MONTH_REFERENCES:
            metadata.update(
                {
                    "model_status": "ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE",
                    "current_month_reference": dict(CURRENT_MONTH_REFERENCES[engine_id]),
                    "no_prospective_issuance": True,
                    "prospective_claim": False,
                    "canonical_forecast_authority": False,
                }
            )
            if engine_id == "VW_MIDAS_MSVR_SUCCESSOR_V1":
                metadata.update(
                    {
                        "later_prospective_validation_origin": "2026-09-30T21:00:00Z",
                        "later_prospective_validation_target": "2026-10",
                    }
                )
        else:
            metadata["no_forecast_issued"] = True
'''
    s = replace_one(s, old, new, "RUNTIME_METADATA_PATCH_MISMATCH")
    s = s.replace('{"active": 7, "waiting": 5, "blocked": 0}', '{"active": 12, "waiting": 0, "blocked": 0}')
    s = s.replace("RUNTIME_BOOTSTRAP_V139_COUNTS_INVALID", "RUNTIME_BOOTSTRAP_V140_COUNTS_INVALID")
    s = s.replace('counts.get("ACTIVE") != 7 or counts.get("WAITING") != 5 or counts.get("BLOCKED", 0) != 0',
                  'counts.get("ACTIVE") != 12 or counts.get("WAITING", 0) != 0 or counts.get("BLOCKED", 0) != 0')
    s = s.replace("DATA_EVIDENCE_SPINE_RUNTIME_BOOTSTRAP_V139_PASS", "DATA_EVIDENCE_SPINE_RUNTIME_BOOTSTRAP_V140_PASS")
    s = s.replace("CANONICAL_MANIFEST_RUNTIME_STATUS_V139", "CANONICAL_MANIFEST_RUNTIME_STATUS_V140")
    p.write_text(s, encoding="utf-8")


def patch_runtime_tests() -> None:
    p = ROOT / "data_pipeline" / "test_data_evidence_spine_runtime_bootstrap.py"
    s = p.read_text(encoding="utf-8")
    s = replace_one(s,
        "from data_evidence_spine_runtime_bootstrap import STATIC_VERSIONS, STATUS_SPECS, VW_SEPTEMBER_REFERENCE",
        "from data_evidence_spine_runtime_bootstrap import CURRENT_MONTH_REFERENCES, STATIC_VERSIONS, STATUS_SPECS",
        "RUNTIME_TEST_IMPORT_PATCH")
    s = s.replace("test_runtime_bootstrap_distribution_matches_v139_target", "test_runtime_bootstrap_distribution_matches_v140_target")
    s = replace_one(s, 'assert sum(v == "ACTIVE" for v in statuses.values()) == 1', 'assert sum(v == "ACTIVE" for v in statuses.values()) == 6', "RUNTIME_TEST_ACTIVE_COUNT")
    s = replace_one(s, 'assert sum(v == "WAITING" for v in statuses.values()) == 5', 'assert sum(v == "WAITING" for v in statuses.values()) == 0', "RUNTIME_TEST_WAITING_COUNT")
    s, n = re.subn(
        r"def test_runtime_bootstrap_exact_waiting_identities\(\):.*?\n\n\ndef test_runtime_bootstrap_vw_current_reference_is_active_and_nonprospective",
        'def test_runtime_bootstrap_exact_waiting_identities():\n    waiting = {engine_id for engine_id, spec in STATUS_SPECS.items() if spec[0] == "WAITING"}\n    assert waiting == set()\n\n\ndef test_runtime_bootstrap_vw_current_reference_is_active_and_nonprospective',
        s,
        flags=re.S,
    )
    if n != 1:
        raise RuntimeError(f"RUNTIME_TEST_WAITING_PATCH_FAILED:{n}")
    s = s.replace('VW_SEPTEMBER_REFERENCE[', 'CURRENT_MONTH_REFERENCES["VW_MIDAS_MSVR_SUCCESSOR_V1"][', )
    marker = "def test_runtime_bootstrap_emergency_status_codes_are_current():"
    insert = '''def test_runtime_bootstrap_all_aug31_september_references_are_active_and_nonprospective():
    assert set(CURRENT_MONTH_REFERENCES) == {
        "CAUSAL_PATCH",
        "VW_MIDAS_MSVR_SUCCESSOR_V1",
        "MOMENTUM_3M",
        "RANDOM_WALK",
        "EMERGENCY_LEVEL",
        "EMERGENCY_REVERSAL",
    }
    for engine_id, ref in CURRENT_MONTH_REFERENCES.items():
        assert STATUS_SPECS[engine_id][0] == "ACTIVE"
        assert ref["evidence_class"] == "HISTORICAL_REPLAY"
        assert ref["target_month"] == "2026-09"
        assert ref["forecast_origin"] == "2026-08-31T21:00:00Z"
        assert ref["prospective_claim"] is False
        assert ref["canonical_authority"] is False
        assert ref["auto_selector"] == "OFF"
        assert ref["auto_ensemble"] == "OFF"


'''
    s = replace_one(s, marker, insert + marker, "RUNTIME_TEST_MARKER")
    s = s.replace('assert STATUS_SPECS["EMERGENCY_LEVEL"][1] == "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE"',
                  'assert STATUS_SPECS["EMERGENCY_LEVEL"][1] == "ACTIVE_HISTORICAL_REPLAY_MONTH_OPEN_STATE_AVAILABLE"')
    s = s.replace('assert STATUS_SPECS["EMERGENCY_REVERSAL"][1] == "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE"',
                  'assert STATUS_SPECS["EMERGENCY_REVERSAL"][1] == "ACTIVE_HISTORICAL_REPLAY_MONTH_OPEN_STATE_AVAILABLE"')
    p.write_text(s, encoding="utf-8")


def patch_multi_expert() -> None:
    p = ROOT / "data_pipeline" / "multi_expert_forecast.py"
    s = replace_one(p.read_text(encoding="utf-8"), 'MANIFEST_VERSION = "1.39"', 'MANIFEST_VERSION = "1.40"', "MULTI_MANIFEST_VERSION")
    p.write_text(s, encoding="utf-8")
    p = ROOT / "data_pipeline" / "test_multi_expert_forecast.py"
    s = p.read_text(encoding="utf-8").replace("test_manifest_v139_expert_set_is_exact_and_ordered", "test_manifest_v140_expert_set_is_exact_and_ordered", 1)
    p.write_text(s, encoding="utf-8")


def patch_observability() -> None:
    p = ROOT / "apps" / "engine_observability_contract.py"
    s = p.read_text(encoding="utf-8")
    s = s.replace(
        "ALL_GOVERNED_FORECAST_DIRECTION_ENGINES_VISIBLE_V6_VW_MSVR_SUCCESSOR_V1_SEPTEMBER_REFERENCE_ACTIVE",
        "ALL_GOVERNED_FORECAST_DIRECTION_ENGINES_VISIBLE_V7_ALL_AUG31_SEPTEMBER_REFERENCES_ACTIVE",
        1,
    )
    repl = {
        '"default_status": "WAITING_ELIGIBLE_MONTH_END_ORIGIN",\n        "direction_vote": False,\n        "expert_id": "CAUSAL_PATCH",':
        '"default_status": "ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE",\n        "direction_vote": False,\n        "expert_id": "CAUSAL_PATCH",',
        '"default_status": "WAITING_ELIGIBLE_MONTH_END_ORIGIN",\n        "direction_vote": False,\n        "expert_id": "MOMENTUM_3M",':
        '"default_status": "ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE",\n        "direction_vote": False,\n        "expert_id": "MOMENTUM_3M",',
        '"default_status": "WAITING_ELIGIBLE_MONTH_END_ORIGIN",\n        "direction_vote": False,\n        "expert_id": "RANDOM_WALK",':
        '"default_status": "ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE",\n        "direction_vote": False,\n        "expert_id": "RANDOM_WALK",',
        '"default_status": "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE",\n        "direction_vote": False,\n        "decision_key": "level_emergency",':
        '"default_status": "ACTIVE_HISTORICAL_REPLAY_MONTH_OPEN_STATE_AVAILABLE",\n        "direction_vote": False,\n        "decision_key": "level_emergency",',
        '"default_status": "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE",\n        "direction_vote": False,\n        "decision_key": "reversal_emergency",':
        '"default_status": "ACTIVE_HISTORICAL_REPLAY_MONTH_OPEN_STATE_AVAILABLE",\n        "direction_vote": False,\n        "decision_key": "reversal_emergency",',
    }
    for old, new in repl.items():
        s = replace_one(s, old, new, "OBSERVABILITY_DEFAULT_PATCH")
    s = replace_one(s, 'if ref.get("forecast_value") is None:\n        return None', 'if ref.get("forecast_value") is None and ref.get("state_value") is None:\n        return None', "OBSERVABILITY_REF_VALUE")
    s = replace_one(s, 'row["output"] = ref.get("forecast_value")', 'row["output"] = ref.get("forecast_value") if ref.get("forecast_value") is not None else ref.get("state_value")', "OBSERVABILITY_OUTPUT")
    p.write_text(s, encoding="utf-8")


def patch_manifest() -> None:
    p = ROOT / "GOLD_CONTROL_PROJECT_MANIFEST.md"
    s = p.read_text(encoding="utf-8")
    s = replace_one(s, "**Manifest version:** 1.39", "**Manifest version:** 1.40", "MANIFEST_VERSION")
    s = replace_one(s, "this v1.39 manifest governs current product/runtime behavior", "this v1.40 manifest governs current product/runtime behavior", "MANIFEST_AUTH_VERSION")
    s = s.replace("# 6. H=1 FORECAST EXPERT INVENTORY — v1.39", "# 6. H=1 FORECAST EXPERT INVENTORY — v1.40", 1)
    s = s.replace("# 11. CURRENT PRODUCTION RUNTIME AUTHORITY — v1.39 TARGET STATE", "# 11. CURRENT PRODUCTION RUNTIME AUTHORITY — v1.40 TARGET STATE", 1)
    s = replace_one(s, '- `ACTIVE = 7`\n- `WAITING = 5`\n- `BLOCKED = 0`', '- `ACTIVE = 12`\n- `WAITING = 0`\n- `BLOCKED = 0`', "MANIFEST_COUNTS")
    old_active = '''- `MONTHLY_DIRECTION_3M`
- `FAST`
- `SLOW`
- `GVZ_RISK`
- `BOCPD_RETURN_SUCCESSOR_V1`
- `MACRO_EVENT_SUCCESSOR_V2`
- `VW_MIDAS_MSVR_SUCCESSOR_V1`

WAITING:

- `CAUSAL_PATCH`
- `MOMENTUM_3M`
- `RANDOM_WALK`
- `EMERGENCY_LEVEL`
- `EMERGENCY_REVERSAL`
'''
    new_active = '''- `MONTHLY_DIRECTION_3M`
- `FAST`
- `SLOW`
- `GVZ_RISK`
- `BOCPD_RETURN_SUCCESSOR_V1`
- `MACRO_EVENT_SUCCESSOR_V2`
- `VW_MIDAS_MSVR_SUCCESSOR_V1`
- `CAUSAL_PATCH`
- `MOMENTUM_3M`
- `RANDOM_WALK`
- `EMERGENCY_LEVEL`
- `EMERGENCY_REVERSAL`

WAITING:

- none in the current governed 12-motor inventory.
'''
    s = replace_one(s, old_active, new_active, "MANIFEST_ACTIVE_LIST")
    sec12 = '''# 12. v1.40 AUG31 -> SEPTEMBER CURRENT-REFERENCE ACTIVATION AUTHORIZATION

Binding authorization token:

`MANIFEST_V1_40_ALL_AUG31_SEPTEMBER_REFERENCE_ACTIVATION`

The user-directed current-month objective is to run and expose every already-proven 31-Aug -> September motor now. 30 September is not a blocker for these September references.

Authorized append-only current runtime changes:

- `CAUSAL_PATCH` -> ACTIVE historical-replay current-month reference `4452.046728838838 USD/oz`;
- `MOMENTUM_3M` -> ACTIVE historical-replay current-month reference `4345.814584037808 USD/oz`;
- `RANDOM_WALK` -> ACTIVE historical-replay current-month reference `4397.305673870967 USD/oz`;
- `EMERGENCY_LEVEL` -> ACTIVE historical-replay month-open state `NEUTRAL`;
- `EMERGENCY_REVERSAL` -> ACTIVE historical-replay month-open state `OFF`.

The already-active `VW_MIDAS_MSVR_SUCCESSOR_V1` September reference remains `4565.115907930242 USD/oz`.

For all six reconstructed/replayed September reference surfaces:

- information/origin boundary remains `2026-08-31T21:00:00Z`;
- actual reconstruction/replay execution timestamps are preserved;
- evidence remains `HISTORICAL_REPLAY` / origin reconstruction as applicable;
- `prospective_claim = false`;
- `canonical_authority = false`;
- `direction_vote_permitted = false` for these expert/reference outputs;
- `AUTO_SELECTOR = OFF`;
- `AUTO_ENSEMBLE = OFF`;
- no forecast-contract or Decision Store write is authorized.

Required post-write assertions:

- current governed runtime = `ACTIVE 12 / WAITING 0 / BLOCKED 0`;
- all four forecast/decision authority stores remain zero;
- no historical timestamp is rewritten;
- archived/superseded identities remain audit history and are not reactivated.

---

# 13.'''
    s, n = re.subn(r"# 12\. v1\.39 PRODUCTION RUNTIME ACTIVATION AUTHORIZATION.*?---\n\n# 13\.", sec12, s, flags=re.S)
    if n != 1:
        raise RuntimeError(f"MANIFEST_SEC12_PATCH_FAILED:{n}")
    s = s.replace("# 14. UI CONTRACT — v1.39", "# 14. UI CONTRACT — v1.40", 1)
    sec19 = '''# 19. NEXT LEGITIMATE STOP POINT

The 31-Aug -> September current-month reconstruction/replay layer is now the immediate operational target; it does not wait for 30 September.

After v1.40 activation, the current governed 12-motor inventory must have no WAITING or BLOCKED current identity. Historical blocked rows for superseded identities remain immutable audit evidence and must not be revived.

The next engineering step is therefore consistency verification across production Neon, runtime bootstrap, application observability and the production display snapshot. Only after that current-month reconciliation is complete does the separate later VW/MSVR prospective validation milestone remain:

`2026-09-30 origin -> 2026-10 target`

That later prospective test does not invalidate or postpone the September historical-replay current-month references.

---

# 20.'''
    s, n = re.subn(r"# 19\. NEXT LEGITIMATE STOP POINT.*?---\n\n# 20\.", sec19, s, flags=re.S)
    if n != 1:
        raise RuntimeError(f"MANIFEST_SEC19_PATCH_FAILED:{n}")
    s = replace_one(s,
        'Target v1.39 runtime inventory after September-reference activation:\n\n`ACTIVE 7 / WAITING 5 / BLOCKED 0 / TOTAL 12`',
        'Target v1.40 runtime inventory after Aug31-to-September current-reference activation:\n\n`ACTIVE 12 / WAITING 0 / BLOCKED 0 / TOTAL 12`',
        "MANIFEST_FINAL_COUNTS",
    )
    p.write_text(s, encoding="utf-8")


def main() -> int:
    patch_runtime()
    patch_runtime_tests()
    patch_multi_expert()
    patch_observability()
    patch_manifest()
    print("GOLD_CONTROL_V140_CURRENT_REFERENCE_PATCH_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
