from __future__ import annotations

from pathlib import Path

P = Path(__file__).resolve().parents[1] / "GOLD_CONTROL_PROJECT_MANIFEST.md"
text = P.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global text
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"EXPECTED_ONE_MATCH:{n}:{old[:100]!r}")
    text = text.replace(old, new, 1)


replace_once("**Manifest version:** 1.14", "**Manifest version:** 1.15")

replace_once(
    "- `gold_axis_2026/data_pipeline/source_contracts_twelve_validated.json`\n- `gold_axis_2026/GOLD_CONTROL_DATA_INVENTORY.md`",
    "- `gold_axis_2026/data_pipeline/source_contracts_twelve_validated.json`\n- `gold_axis_2026/data_pipeline/source_contracts_successor.json`\n- `gold_axis_2026/GOLD_CONTROL_DATA_INVENTORY.md`",
)

replace_once(
    "Canonical target:\n\n> **Next calendar month's average XAU/USD price**",
    "Canonical target:\n\n> **Next calendar month's average XAU/USD price**\n\nSuccessor R2 historical target/outcome lineage: `XAU_MONTHLY_WB_PINKSHEET` (World Bank Pink Sheet monthly Gold average, legacy-CORE5 compatible). The daily R4 decision-reference lineage remains `XAU_EOD_TWELVE_NY17`; the two roles are intentionally separate and may not be relabelled as one another.",
)

replace_once(
    "Canonical validation contract: `gold_axis_2026/GOLD_CONTROL_H1_SUCCESSOR_VALIDATION_CONTRACT_R1.md`.",
    "Canonical R1 validation contract (superseded for the first scored successor replay): `gold_axis_2026/GOLD_CONTROL_H1_SUCCESSOR_VALIDATION_CONTRACT_R1.md`.\nCanonical active successor validation contract: `gold_axis_2026/GOLD_CONTROL_H1_SUCCESSOR_VALIDATION_CONTRACT_R2.md`.",
)

replace_once(
    "| 4B | `IN_PROGRESS_SUCCESSOR_VALIDATION_REQUIRED` | VW/Patch executable identity recovery rejected by evidence; `GOLD_H1_SUCCESSOR_R1` validation contract frozen; historical target/input readiness must pass before any comparative model score; forecast snapshot/contract not issued |",
    "| 4B | `IN_PROGRESS_SUCCESSOR_R2_HISTORICAL_REPLAY_AUTHORIZED` | Legacy VW/Patch recovery rejected; World Bank/CORE5 target identity proven; 127 target rows + four 128-row ALFRED PIT reconstruction series persisted to Neon; R2 contract frozen before scoring; comparative replay is the next gate; forecast snapshot/contract not issued |",
)

replace_once(
    "## `STAGE 4B — SUCCESSOR INPUT READINESS: PROVE A SOURCE-CONSISTENT HISTORICAL NY17 TARGET BEFORE ANY MODEL SCORE RUN`\n\nStage 5 remains closed as `PASS_PIYASA_SCREEN_CONTRACT`. Stage 6 remains blocked until a display-eligible stored Decision Store state exists. The legacy VW/Patch executable-recovery route is now rejected by evidence; Stage 4B proceeds only through the new `GOLD_H1_SUCCESSOR_R1` validation contract. No September H=1 row may be backdated and no successor may inherit a legacy model identity.",
    "## `STAGE 4B — RUN THE FROZEN SUCCESSOR R2 HISTORICAL REPLAY AND APPLY THE PRE-FROZEN RW GATES`\n\nStage 5 remains closed as `PASS_PIYASA_SCREEN_CONTRACT`. Stage 6 remains blocked until a display-eligible stored Decision Store state exists. Successor input readiness is now sufficient for the first controlled R2 score run. The historical monthly forecast outcome is the separately named World Bank/CORE5-compatible target; Twelve NY17 remains the daily decision reference. No September H=1 row may be backdated, no reconstructed historical observation may be called prospective, and no successor may inherit a legacy VW/Patch identity.",
)

replace_once(
    "1. `SUCCESSOR_HISTORICAL_TARGET_NOT_PROVEN`\n   - a sufficiently deep source-consistent historical NY17 target must be proven before comparative model scores are allowed;\n2. `GOLD_H1_SUCCESSOR_R1_NOT_VALIDATED`\n   - candidate set and acceptance gates are frozen, but no successor model has passed them;",
    "1. `SUCCESSOR_HISTORICAL_TARGET_AND_MINIMAL_MACRO_PIT_READINESS = CLOSED_FOR_R2_HISTORICAL_REPLAY`\n   - archived CORE5 target identity is materially matched by World Bank Pink Sheet over 127/127 months; 127 target rows and four complete 128-row ALFRED month-end PIT reconstruction series are persisted in Neon with explicit historical-reconstruction lineage;\n2. `GOLD_H1_SUCCESSOR_R2_NOT_VALIDATED`\n   - R2 candidate definitions and acceptance gates are frozen before scoring, but no successor model has yet passed them;",
)

replace_once(
    "**Stage-4B successor lane (continues fail-closed):**\n\n1. run `SUCCESSOR_INPUT_READINESS_AUDIT`, beginning with historical Twelve XAU/USD NY17 depth/mapping;\n2. do not run comparative model scoring until the historical target lineage is frozen and the Candidate Set R1 input surface passes PIT/source audit;\n3. run the frozen `GOLD_H1_SUCCESSOR_R1` historical replay contract; if no candidate passes every gate, return `REJECT_ALL_SUCCESSOR_CANDIDATES`;\n4. if a candidate passes, freeze a new model version and R4.2 generic `monthly_price_reference` snapshot contract; do not mutate historical R4.1 VW identity;\n5. revalidate Level Emergency geometry under the new monthly reference without tuning thresholds on 2026 outcomes;\n6. before a real eligible month-end origin, persist immutable forecast input snapshot + forecast contract;\n7. first forward forecast/decision evidence remains `PROSPECTIVE_SHADOW`, never retroactive and not `LIVE_PRODUCTION`.",
    "**Stage-4B successor lane (continues fail-closed for prospective issuance):**\n\n1. execute `GOLD_CONTROL_H1_SUCCESSOR_VALIDATION_CONTRACT_R2.md` on the frozen `2018-07→2026-07` common historical-replay window;\n2. compare `RW_R2_PIT`, `DRIFT_R2_PIT`, `MOM3_R2_PIT`, `DAMPED_TREND_R2_PIT`, `RIDGE_MACRO_R2`, `HUBER_MACRO_R2`, and `SVR_RBF_MACRO_R2` exactly as frozen before scores;\n3. if no candidate passes every RW/robustness gate, return `REJECT_ALL_SUCCESSOR_CANDIDATES_R2` without post-score feature/model changes;\n4. if a candidate passes, freeze the selected successor identity and validate the R4.2 generic `monthly_price_reference` bridge; do not mutate historical R4.1 VW identity;\n5. revalidate Level Emergency geometry under the new monthly reference without tuning thresholds on 2026 outcomes;\n6. before a real eligible month-end origin, persist immutable forecast input snapshot + forecast contract;\n7. first forward forecast/decision evidence remains `PROSPECTIVE_SHADOW`, never retroactive and not `LIVE_PRODUCTION`.",
)

anchor = "### Manifest v1.8 forecast/monthly-context dependency audit"
if anchor not in text:
    raise RuntimeError("ANCHOR_NOT_FOUND_FOR_V1_15_EVIDENCE")

addition = """### Manifest v1.15 successor target/input reconciliation\n\nPre-score evidence now frozen:\n\n- CORE5 ↔ World Bank monthly target identity audit: run `33535312896`, job `99948062874`, `SUCCESS`; 2016-01→2026-07 common months `127/127`, exact equality `123/127`, all `127/127` within USD 0.50, maximum absolute difference USD 0.33, level correlation `0.9999999987`.\n- successor macro PIT readiness audit: run `33534515351`, job `99945412291`, `SUCCESS`; 2016 as-of probes passed for DGS10, DFF, DEXCHUS and NASDAQ100; DTWEXBGS/SP500/DJIA were not admitted to the first R2 common surface; VIX/GVZ/GPR remain separate PIT/vintage gates.\n- governed Neon backfill: run `33538748716`, job `99959440836`, `SUCCESS`; retrieval run `1b4ccbe6-0372-411e-95d9-eb832d637a00`; observations read/written `639/639`, revisions `0`; `XAU_MONTHLY_WB_PINKSHEET=127` rows (2016-01→2026-07); each of `DGS10_ALFRED_PIT_ME`, `DFF_ALFRED_PIT_ME`, `DEXCHUS_ALFRED_PIT_ME`, `NASDAQ100_ALFRED_PIT_ME`=`128` rows (2016-01-31→2026-08-31), one lineage and one quality class per series.\n- historical reconstruction rows preserve the true 2026 `retrieved_at`; ALFRED historical month-end is carried as `provider_as_of`. They are `HISTORICAL_REPLAY_RECONSTRUCTION`, not evidence that Gold Control physically stored them at old origins.\n- forecast-state counts after this data write remained `forecast_input_snapshots=0`, `derived_feature_snapshots=1`, `monthly_forecast_contracts=0`; the backfill did not manufacture an issued forecast.\n- active successor contract before first comparative score: `GOLD_CONTROL_H1_SUCCESSOR_VALIDATION_CONTRACT_R2.md`.\n\nR2 deliberately defers nonessential unresolved inputs rather than blocking an acceptable first validation system. Deferred inputs require later versioned change-control before use.\n\n"""
text = text.replace(anchor, addition + anchor, 1)

P.write_text(text, encoding="utf-8")
print("MANIFEST_V1_15_SUCCESSOR_INPUT_RECONCILIATION_READY")
