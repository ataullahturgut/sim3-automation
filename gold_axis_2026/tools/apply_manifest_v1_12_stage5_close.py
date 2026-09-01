from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "GOLD_CONTROL_PROJECT_MANIFEST.md"
CONTRACT = ROOT / "data_pipeline" / "source_contracts.json"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    manifest = MANIFEST.read_text(encoding="utf-8")
    manifest = replace_once(
        manifest,
        "**Manifest version:** 1.11  ",
        "**Manifest version:** 1.12  ",
        "manifest_version",
    )

    manifest = replace_once(
        manifest,
        "Series: `XAU_DAILY_XAUS`  \nContract source: XAUS history  \nRole: operational cross-check  \nStatus: `CANDIDATE_NOT_BENCHMARK`\n\nThe persisted operational lineage currently exposes an upstream/source label associated with Yahoo/GC=F. This remains an operational cross-check lineage and is not promoted to settlement/EOD authority.",
        "Series: `XAU_DAILY_XAUS`  \nContract source: XAUS history  \nRole: **Piyasa daily history / last-completed-daily display cross-check only**  \nStatus: `CANDIDATE_NOT_BENCHMARK; APPROVED_EXPLICITLY_LABELLED_OPERATIONAL_DISPLAY`\n\nThe persisted operational lineage currently exposes an upstream/source label associated with Yahoo/GC=F. This remains an operational cross-check lineage and is not promoted to settlement/EOD authority. Any Piyasa rendering must explicitly disclose that it is not canonical spot/EOD, settlement, benchmark, or model authority. The current-day row is not eligible for the `last completed daily close`; that comparison uses the newest positive daily row strictly before the current UTC date.",
        "xaus_daily_display_role",
    )

    manifest = replace_once(
        manifest,
        "- latest completed daily close\n- GVZ latest official close",
        "- latest completed daily close from the explicitly labelled operational display history (`XAU_DAILY_XAUS`), never from raw Twelve vendor data unless display rights are separately proven\n- GVZ latest official close",
        "piyasa_primary_content",
    )

    manifest = replace_once(
        manifest,
        "Current timeframe contract for the existing XAUS history adapter:\n\n`1A | 3A | 6A | 1Y`\n\nDo not expose `1G`, `1H`, or `Tümü` until a real intraday/longer-history adapter is connected and audited.",
        "Current timeframe contract for the existing XAUS history adapter:\n\n`1A | 3A | 6A | 1Y`\n\nDo not expose `1G`, `1H`, or `Tümü` until a real intraday/longer-history adapter is connected and audited. `XAU_EOD_TWELVE_NY17` remains the internal canonical R4.1 EOD decision-reference lineage; its raw numeric value is not a Piyasa display field unless Twelve external-display rights are separately proven and frozen.\n\nDisplay/licensing change-control: `gold_axis_2026/GOLD_CONTROL_PIYASA_DISPLAY_CONTRACT_CHANGE_CONTROL_2026-09-01.md`.",
        "piyasa_timeframe_display_policy",
    )

    manifest = replace_once(
        manifest,
        "| 5 | `IN_PROGRESS_DATA_PATHS_PROVEN_UI_CONTRACT_NOT_COMPLETE` | Gold API live adapter smoke `SUCCESS` (run `33519370028`); XAUS 1-year history adapter smoke `SUCCESS` (run `33519506662`); canonical Piyasa UI/information-architecture implementation remains |",
        "| 5 | `PASS_PIYASA_SCREEN_CONTRACT` | Canonical Piyasa implementation + deterministic/live Streamlit smoke `SUCCESS` (run `33521193615`, job `99900581399`); approved tabs, live/history sources, freshness/source disclosure, timeframe gate, no decision/forecast writes |",
        "stage5_status",
    )

    manifest = replace_once(
        manifest,
        "The immediate product task is now:\n\n## `STAGE 5 — PIYASA UI CONTRACT: BIND PROVEN LIVE/HISTORY DATA TO THE CANONICAL PIYASA SCREEN`\n\nStage 4B forecast-governance work continues in parallel and remains fail-closed until its four active blockers are resolved. Piyasa progress does not authorize a forecast, final decision, action mapping, or prospective evidence claim.",
        "The immediate canonical task is now:\n\n## `STAGE 4B — RESOLVE THE H=1 FORECAST ISSUER AND VW MONTHLY REFERENCE WITHOUT SILENT MODEL SUBSTITUTION`\n\nStage 5 is closed as `PASS_PIYASA_SCREEN_CONTRACT` by run `33521193615`, job `99900581399`. Stage 6 remains blocked until a display-eligible stored Decision Store state exists. Stage 4B forecast-governance therefore becomes the next dependency to resolve; no September H=1 row may be backdated and no missing VW/Patch identity may be guessed.",
        "immediate_next_work",
    )

    anchor = "Stage-5 runtime evidence added in manifest v1.11:\n\n- canonical live adapter smoke: run `33519370028`, job `99894418747`, `SUCCESS`; source series `XAU_SPOT_GOLDAPI`, freshness PASS, role `INDICATIVE_DISPLAY_ONLY_NO_MODEL_USE`, no raw-value logging or writes;\n- current 1-year XAU history adapter smoke: run `33519506662`, job `99894890585`, `SUCCESS`; row/span/freshness/duplicate/null gates PASS, no raw-value logging or writes."
    addition = anchor + "\n\nStage-5 closure evidence added in manifest v1.12:\n\n- Piyasa deterministic contract tests: 4/4 PASS;\n- canonical Streamlit tabs: `Piyasa | Görünüm | Tahmin | Geçmiş`;\n- live Gold API and operational XAUS history rendered with explicit distinct lineage labels;\n- raw Twelve NY17 numeric market value intentionally not rendered;\n- Decision Store absence renders `KANONİK KARAR YOK`;\n- no forecast or decision write performed;\n- run `33521193615`, job `99900581399`, `STAGE5_PIYASA_UI_SMOKE_PASS`."
    manifest = replace_once(manifest, anchor, addition, "stage5_closure_evidence")

    MANIFEST.write_text(manifest, encoding="utf-8")

    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    data["version"] = "GOLD_DATA_R2_2026-09-01_PIYASA_DISPLAY_V2"
    series = data["series"]["XAU_DAILY_XAUS"]
    series["role"] = "Piyasa daily history / last-completed-daily operational display cross-check only"
    series["status"] = "CANDIDATE_NOT_BENCHMARK; APPROVED_EXPLICITLY_LABELLED_OPERATIONAL_DISPLAY"
    series["display_policy"] = "DISPLAY_ALLOWED_ONLY_WITH_EXPLICIT_CROSS_CHECK_LABEL; NOT_CANONICAL_SPOT_EOD_SETTLEMENT_OR_MODEL_AUTHORITY"
    series["completed_daily_rule"] = "newest positive daily row strictly before current UTC date"
    CONTRACT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("MANIFEST_V1_12_STAGE5_CLOSE_APPLIED")


if __name__ == "__main__":
    main()
