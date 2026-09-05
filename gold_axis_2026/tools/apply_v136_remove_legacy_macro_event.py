from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "gold_axis_2026" / "GOLD_CONTROL_PROJECT_MANIFEST.md"
ENGINE = ROOT / "gold_axis_2026" / "apps" / "engine_observability_contract.py"
DECISION = ROOT / "gold_axis_2026" / "apps" / "decision_source.py"
MOBILE = ROOT / "gold_axis_2026" / "apps" / "gold_control_mobile_v1.py"
ENGINE_TEST = ROOT / "gold_axis_2026" / "apps" / "test_engine_observability_contract.py"

LEGACY_ENGINE_TOKEN = re.compile(r"(?<![A-Z0-9_])MACRO_EVENT(?![A-Z0-9_])")
LEGACY_BLOCKER = "BLOCKED_EXACT_MACRO_SCORE_CONSENSUS_AND_VINTAGE_CONTRACT_NOT_RECOVERED"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one occurrence, found {count}")
    return text.replace(old, new, 1)


def clear_legacy_token(text: str) -> str:
    return LEGACY_ENGINE_TOKEN.sub("MACRO_EVENT_SUCCESSOR_V2", text)


def patch_manifest() -> None:
    text = MANIFEST.read_text(encoding="utf-8")
    text = replace_once(text, "**Manifest version:** 1.35", "**Manifest version:** 1.36", "manifest version")
    text = text.replace("this v1.35 manifest governs", "this v1.36 manifest governs")

    start = text.index("# 9A. MACRO EVENT GOVERNANCE")
    end = text.index("\n---\n\n# 10. EMERGENCY GOVERNANCE", start)
    section = """# 9A. MACRO EVENT SUCCESSOR V2 GOVERNANCE — v1.36

Current governed engine identity:

`MACRO_EVENT_SUCCESSOR_V2`

Operational status:

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
- source lineage remains bound to governed research source run `6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a` for the validated historical evidence.

Validation basis frozen before promotion:

- robust-score replay: `PASS_V2_ROBUST_PREREG_REPLAY_REPRODUCIBLE`;
- event-reaction validation: `PASS_EVENT_REACTION_EVIDENCE`;
- frozen VAL+LOCK strong-shock events: `8`;
- directional hits in the preregistered 15-minute primary window: `7/8` = `87.5%`;
- exact one-sided sign-test p-value: `0.03515625`;
- median signed R15: `+0.9590818647119803%`.

Latest governed event-context reference from the frozen panel is the August 2026 Employment Situation released 2026-09-04:

- robust composite score = `-0.414773053241`;
- state = `MACRO_MIXED_OR_SMALL`.

This September state remains `HISTORICAL_REPLAY` evidence because it was reconstructed later from historical/PIT research data. Runtime activation is effective only at its true deployment time and is not backdated to the event release.

The validation supports only immediate event-risk/context classification. It does **not** establish H=1 monthly forecast skill, trading profitability, automatic action authority, selector/ensemble eligibility, or position mapping.
"""
    text = text[:start] + section + text[end:]

    text = text.replace("# 11. CURRENT PRODUCTION RUNTIME AUTHORITY — v1.35 TARGET STATE", "# 11. CURRENT PRODUCTION RUNTIME AUTHORITY — v1.36")
    text = text.replace("After the v1.35 code + production runtime migration is applied and verified, the current governed application inventory is:", "Under v1.36, the current governed application inventory is:")

    old_runtime_para = """The archived `MACRO_EVENT` ledger identity likewise remains queryable for audit/history but is no longer part of the 12-motor current application registry. Its latest archival runtime record may remain `BLOCKED` with explicit `replaced_by = MACRO_EVENT_SUCCESSOR_V2` metadata; this also does not increase the current application blocked count.\n\n"""
    text = text.replace(old_runtime_para, "")
    text = text.replace("# 13. UI CONTRACT — v1.35", "# 13. UI CONTRACT — v1.36")
    old_ui = "The archived `MACRO_EVENT` identity remains visible only in audit/history surfaces where its recovery-blocked lineage is relevant.\n\n"
    text = text.replace(old_ui, "")

    # Any remaining standalone old engine name in current-manifest prose is rewritten
    # to the only governed current identity. Historical Git commits remain untouched.
    text = clear_legacy_token(text)

    if LEGACY_BLOCKER in text:
        raise RuntimeError("manifest still contains legacy Macro blocker")
    if LEGACY_ENGINE_TOKEN.search(text):
        raise RuntimeError("manifest still contains standalone legacy Macro engine token")
    MANIFEST.write_text(text, encoding="utf-8")


def patch_engine() -> None:
    text = ENGINE.read_text(encoding="utf-8")
    text = text.replace(
        '"role": "Active timestamp-safe labor-event risk/context; successor to archived MACRO_EVENT",',
        '"role": "Active timestamp-safe labor-event risk/context",',
    )
    text = clear_legacy_token(text)
    if LEGACY_ENGINE_TOKEN.search(text):
        raise RuntimeError("engine registry still contains standalone legacy Macro engine token")
    ENGINE.write_text(text, encoding="utf-8")


def patch_decision_source() -> None:
    text = DECISION.read_text(encoding="utf-8")
    text = text.replace(f'MACRO_EVENT_CONTEXT_STATUS = "{LEGACY_BLOCKER}"\n', "")
    text = text.replace('        "macro_event_down": row.get("macro_event_down"),\n', "")
    text = text.replace('        "macro_event_state": row.get("macro_event_down"),\n', "")
    text = text.replace('        "macro_event_state": MACRO_EVENT_CONTEXT_STATUS,\n', "")
    text = text.replace('            s.macro_event_down,\n', "")
    text = text.replace('            "macro_event_down": row.get("macro_event_down"),\n', "")
    text = clear_legacy_token(text)
    if LEGACY_BLOCKER in text or "MACRO_EVENT_CONTEXT_STATUS" in text or "macro_event_down" in text or "macro_event_state" in text:
        raise RuntimeError("decision_source still contains legacy Macro compatibility fields")
    if LEGACY_ENGINE_TOKEN.search(text):
        raise RuntimeError("decision_source still contains standalone legacy Macro engine token")
    DECISION.write_text(text, encoding="utf-8")


def patch_mobile() -> None:
    text = MOBILE.read_text(encoding="utf-8")
    text = text.replace(
        f'MACRO_EVENT_STATUS = "{LEGACY_BLOCKER}"',
        'MACRO_EVENT_SUCCESSOR_STATUS = "MACRO_MIXED_OR_SMALL"',
    )
    text = text.replace("MACRO_EVENT_STATUS", "MACRO_EVENT_SUCCESSOR_STATUS")
    text = clear_legacy_token(text)
    if LEGACY_BLOCKER in text:
        raise RuntimeError("mobile UI still contains legacy Macro blocker")
    if LEGACY_ENGINE_TOKEN.search(text):
        raise RuntimeError("mobile UI still contains standalone legacy Macro engine token")
    MOBILE.write_text(text, encoding="utf-8")


def patch_engine_test() -> None:
    text = ENGINE_TEST.read_text(encoding="utf-8")
    text = text.replace(f'        "macro_event_state": "{LEGACY_BLOCKER}",\n', "")
    text = text.replace('    assert "MACRO_EVENT" not in ENGINE_DISPLAY_ORDER\n', "")
    text = text.replace('    assert "MACRO_EVENT" not in rows\n', "")
    text = text.replace("test_archived_successors_are_replaced_in_current_registry_without_losing_vw_blocker", "test_current_successors_are_present_without_losing_vw_blocker")
    text = clear_legacy_token(text)
    if LEGACY_BLOCKER in text or "macro_event_state" in text:
        raise RuntimeError("engine test still contains legacy Macro fields")
    if LEGACY_ENGINE_TOKEN.search(text):
        raise RuntimeError("engine test still contains standalone legacy Macro engine token")
    ENGINE_TEST.write_text(text, encoding="utf-8")


def main() -> None:
    patch_manifest()
    patch_engine()
    patch_decision_source()
    patch_mobile()
    patch_engine_test()
    print("V136_LEGACY_MACRO_EVENT_CURRENT_TREE_CLEANUP_APPLIED")


if __name__ == "__main__":
    main()
