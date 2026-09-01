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
    text = once(text, "**Manifest version:** 1.13  ", "**Manifest version:** 1.14  ", "version")

    text = once(
        text,
        "## 7.1 Production role freeze\n\nUntil explicitly superseded by audited evidence:\n\n- **Audited shadow/reference:** VW-MIDAS-MSVR\n- **Executable point-forecast path:** reproducible Causal Patch R1 implementation / temporary executable path\n- **Direction challenger:** 3M Momentum\n- **Benchmark:** Random Walk\n- **Auto selector:** `OFF / REJECT_NOT_PROVEN`\n- **Auto ensemble for primary:** `OFF / REJECT_FOR_PRIMARY`\n- **Model disagreement:** visible to audit/UI where useful\n\nDo not claim the audited VW output is fully executable/reproducible until the exact provenance gap is closed.",
        "## 7.1 Archived role freeze and successor requirement\n\nHistorical production-closure evidence remains immutable:\n\n- **Archived audited analytical reference:** VW-MIDAS-MSVR Adapt V2 — historical reference only; executable identity recovery rejected as `BLOCKED_NOT_PROVEN`;\n- **Archived Patch role:** Causal Patch R1 — historical production-closure artifact only; retained runner does not reproduce the canonical August Patch artifact and therefore `PATCH_R1_EXECUTABLE_IDENTITY_NOT_PROVEN`;\n- **Direction challenger/context:** 3M Momentum — reproducible context role preserved;\n- **Benchmark:** Random Walk — mandatory naive benchmark and 43/43 identity-verified across legacy/canonical files;\n- **Auto selector:** `OFF / REJECT_NOT_PROVEN`;\n- **Auto ensemble for primary:** `OFF / REJECT_FOR_PRIMARY`.\n\nNo archived VW/Patch artifact may be presented as a current executable model. A new H=1 production path requires a new identity under `GOLD_H1_SUCCESSOR_R1`; reserved engine lane `R4.2-SHADOW-CANDIDATE`, status `VALIDATION_ONLY_NOT_APPROVED`.\n\nCanonical change-control: `gold_axis_2026/GOLD_CONTROL_STAGE4B_FORECAST_SUCCESSOR_CHANGE_CONTROL_2026-09-01.md`.\nCanonical validation contract: `gold_axis_2026/GOLD_CONTROL_H1_SUCCESSOR_VALIDATION_CONTRACT_R1.md`.",
        "forecast_role_freeze",
    )

    text = once(
        text,
        "| 4B | `IN_PROGRESS_BLOCKED_FORECAST_ISSUER` | Current H=1 issuer and VW monthly reference remain unresolved; forecast input snapshot/contract not issued |",
        "| 4B | `IN_PROGRESS_SUCCESSOR_VALIDATION_REQUIRED` | VW/Patch executable identity recovery rejected by evidence; `GOLD_H1_SUCCESSOR_R1` validation contract frozen; historical target/input readiness must pass before any comparative model score; forecast snapshot/contract not issued |",
        "stage4b_status",
    )

    text = once(
        text,
        "The immediate canonical task is now:\n\n## `STAGE 4B — RESOLVE THE H=1 FORECAST ISSUER AND VW MONTHLY REFERENCE WITHOUT SILENT MODEL SUBSTITUTION`\n\nStage 5 is closed as `PASS_PIYASA_SCREEN_CONTRACT` by run `33521193615`, job `99900581399`. Stage 6 remains blocked until a display-eligible stored Decision Store state exists. Stage 4B forecast-governance therefore becomes the next dependency to resolve; no September H=1 row may be backdated and no missing VW/Patch identity may be guessed.",
        "The immediate canonical task is now:\n\n## `STAGE 4B — SUCCESSOR INPUT READINESS: PROVE A SOURCE-CONSISTENT HISTORICAL NY17 TARGET BEFORE ANY MODEL SCORE RUN`\n\nStage 5 remains closed as `PASS_PIYASA_SCREEN_CONTRACT`. Stage 6 remains blocked until a display-eligible stored Decision Store state exists. The legacy VW/Patch executable-recovery route is now rejected by evidence; Stage 4B proceeds only through the new `GOLD_H1_SUCCESSOR_R1` validation contract. No September H=1 row may be backdated and no successor may inherit a legacy model identity.",
        "immediate_task",
    )

    text = once(
        text,
        "Confirmed active Stage-4B forecast blockers after manifest v1.10 reconciliation:\n\n1. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`\n2. `FORECAST_CONTRACT_NOT_ISSUED`\n3. `PATCH_R1_CURRENT_ISSUER_NOT_PROVEN`\n   - retained Patch code is proven only through its prior August horizon and may not be date-extended by assumption.\n4. `VW_CURRENT_MONTHLY_REFERENCE_NOT_ISSUED`\n   - `VW_EXECUTABLE_REPRODUCTION_BLOCKED_NOT_PROVEN`; the exact original VW-MIDAS-MSVR Adapt V2 runner/source chain is not retained.",
        "Confirmed active Stage-4B successor blockers after manifest v1.14 change-control:\n\n1. `SUCCESSOR_HISTORICAL_TARGET_NOT_PROVEN`\n   - a sufficiently deep source-consistent historical NY17 target must be proven before comparative model scores are allowed;\n2. `GOLD_H1_SUCCESSOR_R1_NOT_VALIDATED`\n   - candidate set and acceptance gates are frozen, but no successor model has passed them;\n3. `R4_2_MONTHLY_REFERENCE_BRIDGE_NOT_VALIDATED`\n   - a non-VW successor may not be inserted into the R4.1 `monthly_vw_forecast` field; a generic R4.2 monthly-reference contract and Emergency-geometry validation are required;\n4. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`\n5. `FORECAST_CONTRACT_NOT_ISSUED`\n\nLegacy-route statuses retained for audit:\n\n- `VW_EXECUTABLE_IDENTITY_RECOVERY = REJECTED_BLOCKED_NOT_PROVEN`;\n- `PATCH_R1_EXECUTABLE_IDENTITY = BLOCKED_NOT_PROVEN`.",
        "active_blockers",
    )

    marker = "Closed current-state/context gates:\n\n- `CANONICAL_XAU_HISTORY_BACKFILL_NOT_YET_SUCCESS` → `CLOSED_BY_RUN_33515654716`;"
    addition = "Stage-4B executable-identity audit evidence added in manifest v1.14:\n\n- legacy-vs-production identity audit: run `33522033593`, job `99903431886`, `SUCCESS`; VW exact equality `0/43`, Patch exact equality `0/43`, RW exact equality `43/43`; high correlation is explicitly not accepted as identity proof;\n- retained August Patch reproduction audit: run `33522158937`, job `99903852563`, `SUCCESS`; canonical-vs-reproduced absolute difference `33.825192815012 USD`, relative difference ~`0.8219%`, exact/1e-6 equality `FALSE`; input package ends 2026-07;\n- current 2026 model-risk authority reference: Federal Reserve SR 26-2 / interagency revised guidance; principles applied as governance reference, not a legal-applicability claim;\n- successor change-control frozen: `GOLD_CONTROL_STAGE4B_FORECAST_SUCCESSOR_CHANGE_CONTROL_2026-09-01.md`;\n- successor validation contract frozen before comparative scoring: `GOLD_CONTROL_H1_SUCCESSOR_VALIDATION_CONTRACT_R1.md`.\n\n" + marker
    text = once(text, marker, addition, "stage4b_evidence")

    text = once(
        text,
        "**Stage-4B forecast/decision lane (continues fail-closed):**\n\n1. resolve/freeze the current monthly VW reference without silent model substitution;\n2. resolve the current H=1 executable point issuer with leakage-safe change control rather than extending Patch constants;\n3. before the real end-September origin, issue the immutable forecast input snapshot + monthly forecast contract;\n4. build/schedule the canonical R4.1 issuer only when every mandatory EngineSnapshot field has valid evidence;\n5. first forward Decision Store state remains `PROSPECTIVE_SHADOW`, never retroactive and not `LIVE_PRODUCTION`.",
        "**Stage-4B successor lane (continues fail-closed):**\n\n1. run `SUCCESSOR_INPUT_READINESS_AUDIT`, beginning with historical Twelve XAU/USD NY17 depth/mapping;\n2. do not run comparative model scoring until the historical target lineage is frozen and the Candidate Set R1 input surface passes PIT/source audit;\n3. run the frozen `GOLD_H1_SUCCESSOR_R1` historical replay contract; if no candidate passes every gate, return `REJECT_ALL_SUCCESSOR_CANDIDATES`;\n4. if a candidate passes, freeze a new model version and R4.2 generic `monthly_price_reference` snapshot contract; do not mutate historical R4.1 VW identity;\n5. revalidate Level Emergency geometry under the new monthly reference without tuning thresholds on 2026 outcomes;\n6. before a real eligible month-end origin, persist immutable forecast input snapshot + forecast contract;\n7. first forward forecast/decision evidence remains `PROSPECTIVE_SHADOW`, never retroactive and not `LIVE_PRODUCTION`.",
        "stage4b_lane",
    )

    text = once(
        text,
        "No `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` **decision** row may be written while an active Stage-4B blocker prevents construction of the complete frozen EngineSnapshot. This does not block non-decision `Piyasa` monitoring.\nNo `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` decision row may be written while any active Stage-4 readiness blocker remains open.",
        "No `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` **decision** row may be written while an active Stage-4B successor blocker prevents construction of the complete versioned EngineSnapshot. This does not block non-decision `Piyasa` monitoring.",
        "duplicate_block_rule",
    )

    P.write_text(text, encoding="utf-8")
    print("MANIFEST_V1_14_SUCCESSOR_APPLIED")


if __name__ == "__main__":
    main()
