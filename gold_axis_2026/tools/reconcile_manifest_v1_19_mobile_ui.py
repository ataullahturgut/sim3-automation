from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "GOLD_CONTROL_PROJECT_MANIFEST.md"
SPEC = ROOT / "GOLD_CONTROL_MOBILE_UI_PRODUCT_SPEC_V1.md"


def replace_once(text: str, old: str, new: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"MANIFEST_REPLACE_COUNT:{n}:{old[:80]}")
    return text.replace(old, new, 1)


def replace_between(text: str, start: str, end: str, replacement: str) -> str:
    i = text.find(start)
    if i < 0:
        raise RuntimeError(f"MANIFEST_START_NOT_FOUND:{start}")
    j = text.find(end, i + len(start))
    if j < 0:
        raise RuntimeError(f"MANIFEST_END_NOT_FOUND:{end}")
    return text[:i] + replacement + text[j:]


def main() -> int:
    if not SPEC.exists():
        raise RuntimeError("MOBILE_UI_SPEC_NOT_FOUND")
    text = MANIFEST.read_text(encoding="utf-8")
    if "**Manifest version:** 1.18" not in text:
        raise RuntimeError("EXPECTED_MANIFEST_V1_18_NOT_FOUND")

    text = replace_once(text, "**Manifest version:** 1.18", "**Manifest version:** 1.19")

    text = replace_once(
        text,
        "- **Intended production point-forecast path:** `CAUSAL_PATCH_R1_REPRO_V1_3_XAU_ONLY_ORIGIN_SAFE` — the V4 XAU-only successor of the reproducible Patch path, retaining the frozen Patch architecture and `L=252`, `P=21`, `D=32`. V4 source and locked historical model-impact gates passed, but it is not yet a prospective/live production issuer. `CAUSAL_PATCH_R1_REPRO_V1` remains immutable predecessor evidence and the exact archived historical Patch executable identity remains separately unproven;",
        "- **Intended forward point-forecast issuer candidate:** `CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE` — Patch V7. It retains the frozen Patch Transformer geometry `L=252`, `P=21`, `D=32`, uses the V6 origin-safe daily-train/hourly-anchor monthly-level architecture, and adds the completed-session daily-feature rule `observation_date < origin_date`. V7 locked historical model-impact gates passed with zero same-origin daily-feature use, zero future-information violations, deterministic rerun equality, and performance better than RW on the frozen 43-month window. Evidence remains `HISTORICAL_REPLAY_MODEL_IMPACT`; no live/prospective performance claim is made until a real pre-outcome forecast is issued. `CAUSAL_PATCH_R1_REPRO_V1` remains immutable predecessor evidence and the exact archived historical Patch executable identity remains separately unproven;",
    )

    forecast_ledger_anchor = "Historical closure/replay artifacts keep their original evidence class. No forecast may be relabelled as `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` unless it was issued before outcome realization with an immutable input snapshot and contract."
    ledger_note = forecast_ledger_anchor + "\n\nManifest v1.19 operational update: forecast-writer schema audit `FORECAST_WRITER_SCHEMA_AUDIT_PASS` confirmed identity/PK/unique/immutable guards; read-only writer rehearsal `PATCH_V7_FORECAST_WRITER_REHEARSAL_PASS` validated insert plans with zero persistent rows and no identity consumption; first-shadow preflight `FIRST_SHADOW_ISSUER_PREFLIGHT_PASS_WAITING_FOR_ELIGIBLE_ORIGIN` confirmed the ledger remains empty and the earliest eligible target/origin is October 2026 / end-September. No forecast has yet been issued."
    text = replace_once(text, forecast_ledger_anchor, ledger_note)

    mobile_section = """## 17.6 Approved mobile product UI V1\n\nBinding presentation specification:\n\n`gold_axis_2026/GOLD_CONTROL_MOBILE_UI_PRODUCT_SPEC_V1.md`\n\nStatus: `APPROVED_MOBILE_PRODUCT_UI_CONTRACT_V1`.\n\nThe approved 2026-09-02 mobile mockup direction is binding for visual hierarchy, navy/gold/white palette, mobile card structure, hero treatment and bottom-navigation concept. Mockup sample numbers are not data authority. Manifest/data/ledger semantics override every placeholder inside a drawing.\n\nMobile bottom-navigation label `Bugün` is an approved user-facing alias for the canonical `Piyasa` screen; the underlying screen/data contract remains `Piyasa`.\n\nProduction UI must specifically remove or replace mockup elements that are not currently authorized:\n\n- no `POZİSYONU KORU`, BUY/SELL/HOLD/EXIT or exposure mapping while `NOT_PROVEN_POSITION_MAPPING` remains active;\n- no arbitrary `Güç %`, confidence label/percentage or forecast band;\n- no fabricated forecast/reference values;\n- no YBB/12M strategy return, drawdown, trade count or entry/exit performance until an audited execution/portfolio contract exists;\n- `Tahmin` renders a numeric value only from canonical `monthly_forecast_contracts`;\n- `Görünüm` renders a current state only from a display-eligible Decision Store row;\n- `Geçmiş` keeps `HISTORICAL_REPLAY`, `PROSPECTIVE_SHADOW`, and `LIVE_PRODUCTION` visibly separated.\n\nImplementation candidate: `gold_axis_2026/apps/gold_control_mobile_v1.py`; it is not yet a Stage-10 completion claim.\n\n"""
    text = replace_once(text, "---\n\n# 18. UI / DESIGN SYSTEM FREEZE", mobile_section + "---\n\n# 18. UI / DESIGN SYSTEM FREEZE")

    text = replace_once(
        text,
        "| 4B | `PATCH_V4_XAU_ONLY_SOURCE_AND_HISTORICAL_MODEL_IMPACT_PASS; PROSPECTIVE_ISSUER_NOT_YET_AUTHORIZED` | V4 XAU-only source gate PASS and locked 43-month model-impact PASS under frozen geometry; remaining gates are executable/input identity freeze, monthly-reference→Emergency bridge validation, immutable forecast snapshot/contract, and complete forward EngineSnapshot |",
        "| 4B | `PATCH_V7_MODEL_IMPACT_PASS; R4_2_BRIDGE_PASS; WRITER_PREFLIGHT_PASS; WAITING_ELIGIBLE_ORIGIN` | V7 completed-session PIT gate PASS; generic monthly-reference→Emergency bridge PASS; forecast schema + read-only writer rehearsal + first-shadow preflight PASS. Forecast/input ledgers remain empty until a real eligible origin; complete forward EngineSnapshot/Decision Store issuance remains outstanding. |",
    )

    old_task = "## `STAGE 4B — FREEZE PATCH V4 XAU-ONLY EXECUTABLE/INPUT IDENTITY; VALIDATE MONTHLY-REFERENCE → EMERGENCY BRIDGE; DO NOT REOPEN MODEL SEARCH`"
    new_task = "## `STAGE 4B — PATCH V7 FORWARD ISSUER PREPARED; COMPLETE ENGINE SNAPSHOT + REAL ELIGIBLE-ORIGIN ISSUANCE; DO NOT REOPEN MODEL SEARCH`"
    text = replace_once(text, old_task, new_task)

    start = "Remaining Stage-4B dependency gates:\n\n"
    end = "Stage 5 remains closed as `PASS_PIYASA_SCREEN_CONTRACT`."
    replacement = """Remaining Stage-4B dependency gates after v1.19 reconciliation:\n\n1. V7 completed-session Patch identity is the active forward issuer candidate: `CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE`; do not reopen broad model search or retune from locked outcomes;\n2. R4.2 generic monthly-price-reference → Emergency bridge is validated; do not relabel the generic reference as historical `monthly_vw_forecast`;\n3. forecast DB schema/identity/immutability audit and read-only writer rehearsal are PASS; no real forecast row is authorized before an eligible origin;\n4. first-shadow issuer preflight is PASS and correctly returns `SKIP_NOT_ELIGIBLE_ORIGIN` on 2026-09-02; September remains non-backfillable;\n5. first possible contract-compliant target remains October 2026 at the end-September origin, after the issuer's availability/time gates close;\n6. a complete versioned forward `EngineSnapshot` and subsequent Decision Store write still must be built from the actually persisted forecast contract/snapshot IDs;\n7. first real forward forecast/decision evidence remains `PROSPECTIVE_SHADOW`; `LIVE_PRODUCTION` requires later prospective graduation gates;\n8. operational scheduler/dispatcher must actually execute from the repository default-branch scheduling surface without moving model authority out of `gold-r4-direction-engine`.\n\n"""
    text = replace_between(text, start, end, replacement)

    current_candidate_old = "`CAUSAL_PATCH_R1_REPRO_V1_3_XAU_ONLY_ORIGIN_SAFE` is the active Patch issuer candidate after V4 source + historical model-impact PASS;"
    if current_candidate_old in text:
        text = text.replace(current_candidate_old, "`CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE` is the active Patch issuer candidate after V6 monthly-level source/model gates plus V7 completed-session PIT historical model-impact PASS;", 1)

    v119 = """### Manifest v1.19 Patch V7 / writer / mobile-UI reconciliation\n\nNew frozen evidence and product decisions on 2026-09-02:\n\n- V5 hourly full-history monthly-level bridge failed closed on provider history entitlement; model scoring was skipped and thresholds were not relaxed;\n- V6 daily-train/hourly-anchor monthly-level architecture passed source and locked model-impact gates without changing Patch geometry;\n- V7 froze the final completed-session daily-feature correction before results: `TWELVE_XAU_USD_1DAY_OBSERVATION_DATE_STRICTLY_BEFORE_ORIGIN_DATE`; 43/43 origins used only strictly pre-origin daily observations, same-origin use 0, future-information violations 0, deterministic max diff 0;\n- V7 candidate MAPE `3.212376055%` vs RW `3.302322023%`, MAE `104.214302424` vs RW `107.465116279`, worst APE `9.016478855%` vs RW `9.625880596%`; hard/performance/model-impact gates PASS; evidence remains `HISTORICAL_REPLAY_MODEL_IMPACT`;\n- active forward candidate identity: `CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE`;\n- R4.2 generic monthly reference → Emergency bridge passed 5/5 tests while frozen R4.1 config remained unchanged;\n- production forecast writer schema audit passed; `forecast_input_snapshots` and `monthly_forecast_contracts` remained 0 rows and immutable guards were verified;\n- read-only writer rehearsal passed with insert-plan validation, 0→0 persistent rows and no identity consumption;\n- first-shadow issuer preflight passed, September backfill remains forbidden, earliest eligible origin is 2026-09-30 after 17:20 America/New_York, first target October 2026; no forecast value has been issued yet;\n- mobile product presentation is frozen by `GOLD_CONTROL_MOBILE_UI_PRODUCT_SPEC_V1.md`; approved mockup aesthetics do not authorize fabricated metrics or action mapping;\n- mobile Streamlit implementation candidate begins at `gold_axis_2026/apps/gold_control_mobile_v1.py`, backed by canonical Decision Store/forecast-ledger readers and fail-closed empty states.\n\n"""
    text = replace_once(text, "### Manifest v1.18 V3/V4 input-continuation and model-impact reconciliation", v119 + "### Manifest v1.18 V3/V4 input-continuation and model-impact reconciliation")

    text = replace_once(
        text,
        "Current Streamlit paths:\n\n- `gold_axis_2026/apps/gold_control.py`\n- `gold_axis_2026/apps/live_sources.py`",
        "Current Streamlit paths:\n\n- `gold_axis_2026/apps/gold_control.py` — current canonical Stage-5 app;\n- `gold_axis_2026/apps/gold_control_mobile_v1.py` — manifest-aligned mobile UI V1 implementation candidate;\n- `gold_axis_2026/apps/live_sources.py`;\n- `gold_axis_2026/apps/forecast_source.py` — read-only canonical forecast-ledger display reader;\n- `gold_axis_2026/apps/mobile_ui_contract.py` — deterministic presentation-state contract.",
    )

    MANIFEST.write_text(text, encoding="utf-8")
    print("MANIFEST_V1_19_RECONCILE_PASS")
    print("MOBILE_UI_SPEC=APPROVED_MOBILE_PRODUCT_UI_CONTRACT_V1")
    print("ACTIVE_PATCH=CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
