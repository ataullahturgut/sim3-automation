from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "GOLD_CONTROL_PROJECT_MANIFEST.md"


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


def main() -> None:
    text = P.read_text(encoding="utf-8")
    text = once(text, "**Manifest version:** 1.12  ", "**Manifest version:** 1.13  ", "version")

    text = once(
        text,
        "Current database state on the 2026-09-01 audit:\n\n- forecast snapshot/contract tables exist;\n- their current row counts are zero;\n- no historical file-backed forecast may be backfilled and relabeled as if it had existed prospectively in Neon.\n\nThe first future `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` forecast must be stored before outcome realization with immutable inputs and provenance.",
        "Current forecast-state database reconciliation on 2026-09-01:\n\n- `forecast_input_snapshots`: **0 rows**;\n- `derived_feature_snapshots`: **1 row** — `MONTHLY_DIRECTION_3M`, quality `LATE_BOOTSTRAP_SHADOW_CONTEXT`;\n- `monthly_forecast_contracts`: **0 rows**;\n- append-only UPDATE/DELETE guard coverage: **3/3 tables**;\n- no historical file-backed forecast may be backfilled and relabeled as if it had existed prospectively in Neon.\n\nEvidence: read-only reconcile run `33518909613`, plus the guarded monthly-direction bootstrap issuance run `33516396253`. The first future H=1 `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` forecast must still be stored before outcome realization with immutable inputs and provenance.",
        "forecast_state_counts",
    )

    text = once(
        text,
        "**Piyasa / monitoring lane (current):**\n\n1. `XAU_SPOT_GOLDAPI` canonical live adapter activation/smoke is `PASS` by run `33519370028`, job `99894418747`; raw market value was not logged and no forecast/decision/DB write occurred.\n2. Current XAUS 1-year history adapter smoke is `PASS` by run `33519506662`, job `99894890585`; >=200 rows, >=300-day span, latest observation age <=7 days, no duplicate dates/null closes, no DB write.\n3. Keep Gold API live spot, XAUS display history, and Twelve NY17 canonical EOD as visibly separate provider/semantic lineages.\n4. Implement the canonical `Piyasa` screen using only proven data paths: live price + source/freshness, 1-year history/timeframe views supported by the adapter, GVZ latest/history, and the Decision Store strip.\n5. Keep `Canlı spot ≠ son EOD karar` visible and show `KANONİK KARAR YOK` whenever the Decision Store has no display-eligible forward state.\n6. Stage 5 is not PASS until UI-level source/freshness/error-state/mobile smoke is complete.",
        "**Piyasa / monitoring lane — CLOSED:**\n\n1. `XAU_SPOT_GOLDAPI` live adapter: PASS by run `33519370028`, job `99894418747`.\n2. XAUS 1-year operational display-history adapter: PASS by run `33519506662`, job `99894890585`.\n3. Canonical Piyasa UI + deterministic contract + Streamlit runtime smoke: PASS by run `33521193615`, job `99900581399`.\n4. Provider roles are explicit: Gold API live display, XAUS operational display history, Twelve NY17 internal canonical EOD decision reference.\n5. `Canlı spot ≠ son EOD karar` and `KANONİK KARAR YOK` fail-safe behavior are active.\n6. Stage 5 status is `PASS_PIYASA_SCREEN_CONTRACT`; later visual/mobile refinement belongs to Stage 10 and does not reopen Stage 5 data semantics.",
        "piyasa_lane",
    )

    text = once(
        text,
        "Current app UI architecture is transitional and must not be treated as final product architecture.\n\nKnown mismatch:\n\n- current app top-level tabs are still `Şimdi / Sinyaller / Model / Veri`\n- final information architecture is `Piyasa / Görünüm / Tahmin / Geçmiş`",
        "Current app information architecture now matches the canonical primary workflow:\n\n`Piyasa / Görünüm / Tahmin / Geçmiş`\n\nStage 5 data/display semantics are frozen and smoke-tested. Pixel-level design refinement and mobile interaction QA remain later Stage-10 work; they must not reintroduce fabricated metrics, action mapping, or provider ambiguity.",
        "app_architecture",
    )

    text = once(
        text,
        "Current live adapter contract after manifest v1.10:\n\n- XAU spot display primary: `XAU_SPOT_GOLDAPI` — indicative monitoring only, explicit source/freshness, never model/EOD/decision input;\n- XAU spot legacy/secondary: `XAU_SPOT_XAUS` — separate degraded lineage, no silent provider merge;\n- XAU history: current XAUS 1-year adapter remains transitional and must be independently healthy before Stage 5 is marked PASS;\n- canonical decision EOD history: `XAU_EOD_TWELVE_NY17` remains separate from the live display source;\n- GVZ: Cboe daily history / latest close.",
        "Current live/display adapter contract after manifest v1.13:\n\n- XAU spot display primary: `XAU_SPOT_GOLDAPI` — indicative monitoring only, explicit source/freshness, never model/EOD/decision input;\n- XAU spot legacy/secondary: `XAU_SPOT_XAUS` — separate degraded lineage, no silent provider merge;\n- XAU daily display history: `XAU_DAILY_XAUS` — explicitly labelled operational cross-check only; current-day row excluded from last-completed-daily comparison;\n- canonical decision EOD: `XAU_EOD_TWELVE_NY17` — internal model/decision reference, raw numeric value not rendered without separately proven Twelve display rights;\n- GVZ: Cboe daily history / latest close;\n- Stage 5 Piyasa UI contract: PASS by run `33521193615`, job `99900581399`.",
        "live_adapter_contract",
    )

    P.write_text(text, encoding="utf-8")
    print("MANIFEST_V1_13_RECONCILE_APPLIED")


if __name__ == "__main__":
    main()
