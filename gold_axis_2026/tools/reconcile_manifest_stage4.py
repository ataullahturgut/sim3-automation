from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "GOLD_CONTROL_PROJECT_MANIFEST.md"
STAGE3 = ROOT / "GOLD_CONTROL_STAGE3_STATUS_2026-09-01.md"
STAGE4 = ROOT / "GOLD_CONTROL_STAGE4_STATUS_2026-09-01.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"EXPECTED_TEXT_NOT_FOUND:{label}")
    return text.replace(old, new, 1)


def main() -> int:
    manifest = MANIFEST.read_text(encoding="utf-8")
    stage3 = STAGE3.read_text(encoding="utf-8")

    manifest = replace_once(
        manifest,
        "**Manifest version:** 1.2",
        "**Manifest version:** 1.3",
        "manifest_version",
    )

    old_rows = "\n".join([
        "| 3 | `IN_PROGRESS_PRODUCTION_SCHEMA_PASS` | Isolated rehearsal PASS; guarded production migration PASS; Neon resource tree confirms Decision Store objects; production writer/reader not activated |",
        "| 4 | `PREPARATION_TESTS_PASS; NOT_COMPLETE_AHEAD_OF_STAGE3` | Deterministic R4.1 tests are prepared but Stage 3 writer/reader activation remains open |",
        "| 5–12 | `NOT_STARTED / NOT_COMPLETE` | Cannot be promoted ahead of Stage 3/4 |",
    ])
    new_rows = "\n".join([
        "| 3 | `PASS_DECISION_STORE_AND_READ_PATH` | Production schema PASS; emitted-state bridge rollback PASS; app Decision Store reader PASS; file-only latest-state dependency removed; evidence isolation/action guard enforced |",
        "| 4 | `IN_PROGRESS_BLOCKED_INPUT_CONTRACTS` | Deterministic engine/bridge tests PASS, but readiness audit is BLOCKED: forecast contract missing, immutable forecast input snapshot missing, latest daily XAU run not SUCCESS, and no approved canonical XAU EOD decision source |",
        "| 5–12 | `NOT_STARTED / NOT_COMPLETE` | Cannot be promoted ahead of Stage 4 |",
    ])
    manifest = replace_once(manifest, old_rows, new_rows, "roadmap_rows")

    start = manifest.index("# 24. IMMEDIATE NEXT WORK")
    marker = "### Operational work that continues independently"
    end = manifest.index(marker, start)
    section_lines = [
        "# 24. IMMEDIATE NEXT WORK",
        "",
        "The next canonical task is now:",
        "",
        "## `STAGE 4 — DETERMINISTIC R4.1 ISSUER: CLOSE INPUT CONTRACT BLOCKERS BEFORE ANY PROSPECTIVE WRITE`",
        "",
        "Stage 3 is closed as:",
        "",
        "`PASS_DECISION_STORE_AND_READ_PATH`",
        "",
        "Stage 3 closure evidence:",
        "",
        "- production Decision Store migration: run `33496843121`, job `99820886297`, `SUCCESS`;",
        "- guarded emitted-state → store → reader bridge: run `33498177345`, job `99825081623`, `R4_1_DECISION_BRIDGE_SMOKE_PASS`;",
        "- transitional app now reads Decision Store instead of `latest_signal.json`;",
        "- app read-only evidence-isolation smoke: run `33498603322`, job `99826433286`, `GOLD_CONTROL_DECISION_STORE_APP_READER_PASS`;",
        "- `HISTORICAL_REPLAY` is excluded from the current-state app reader;",
        "- `action_state` remains null under `NOT_PROVEN_POSITION_MAPPING`;",
        "- production Decision Store remains empty because no valid prospective issuer has been authorized.",
        "",
        "A canonical continuously scheduled live/EOD R4.1 producer is still:",
        "",
        "`NOT_FOUND_CANONICAL_LIVE_R4_1_EMITTER`",
        "",
        "The older R4 LONG/CASH / AL/SAT workflow is not an acceptable substitute because that would violate `NOT_PROVEN_POSITION_MAPPING`.",
        "",
        "### Stage 4 readiness audit",
        "",
        "Read-only production audit:",
        "",
        "- run: `33499509482`;",
        "- job: `99829327414`;",
        "- commit: `37fed93cbef76f394e8dee8b334f89617d94b3ef`;",
        "- result: `SUCCESS` audit execution, `readiness=BLOCKED`;",
        "- raw market values logged: `NO`.",
        "",
        "Confirmed blockers:",
        "",
        "1. `FORECAST_CONTRACT_NOT_ISSUED`",
        "2. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`",
        "3. `LATEST_DAILY_XAU_PIPELINE_NOT_SUCCESS`",
        "4. `NO_APPROVED_CANONICAL_XAU_EOD_DECISION_SOURCE`",
        "",
        "Important source interpretation:",
        "",
        "- `XAU_DAILY_XAUS` is transported through the frozen XAUS history endpoint and the registry already documents the upstream Yahoo lineage; upstream disclosure alone is not treated as silent substitution;",
        "- nevertheless this series is explicitly `operational cross-check only` / `CANDIDATE_NOT_BENCHMARK`, so it is not authorized as the R4.1 canonical EOD decision source;",
        "- `XAU_SPOT_XAUS` is indicative/non-settlement monitoring and likewise is not the frozen EOD decision close;",
        "- Cboe GVZ is available and the latest audited daily Cboe run is successful.",
        "",
        "Required next gates, in order:",
        "",
        "1. define and approve a canonical XAU EOD decision-price source/lineage under change control; do not silently promote the current cross-check or indicative spot series;",
        "2. restore a successful daily XAU ingestion path for the approved source;",
        "3. create the first genuine immutable H=1 forecast input snapshot and monthly forecast contract from the executable frozen forecasting path before outcome realization;",
        "4. only then build/schedule the canonical R4.1 EOD issuer using the frozen engine and complete provenance;",
        "5. the first real forward state must begin as `PROSPECTIVE_SHADOW`; `LIVE_PRODUCTION` remains disabled until Stage 12 graduation;",
        "6. do not backfill historical rows and relabel them as prospective.",
        "",
        "No `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` decision row may be written while any of the four readiness blockers remains open.",
        "",
    ]
    manifest = manifest[:start] + "\n".join(section_lines) + "\n" + manifest[end:]

    old_dep = "\n".join([
        "Current latest-state dependency:",
        "",
        "- `gold_axis_2026/r4_1/output/latest_signal.json`",
        "",
        "This is transitional. The roadmap requires database-backed decision state.",
    ])
    new_dep = "\n".join([
        "Current latest-state dependency:",
        "",
        "- `gold_axis_2026/apps/decision_source.py` reads the production Neon Decision Store;",
        "- display priority is `LIVE_PRODUCTION`, then explicitly labelled `PROSPECTIVE_SHADOW`;",
        "- `HISTORICAL_REPLAY` is never surfaced as the current decision;",
        "- if neither prospective class exists, the app shows `KANONİK KARAR YOK` rather than deriving a decision from live spot.",
        "",
        "The previous file-only `gold_axis_2026/r4_1/output/latest_signal.json` dependency has been removed from the app path.",
    ])
    manifest = replace_once(manifest, old_dep, new_dep, "app_dependency")

    stage3 = replace_once(
        stage3,
        "**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.2",
        "**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.3",
        "stage3_manifest_version",
    )
    stage3 = replace_once(
        stage3,
        "**Current status:** `PRODUCTION_SCHEMA_APPLIED_AND_VERIFIED; WRITER_READER_NOT_ACTIVATED`",
        "**Current status:** `PASS_DECISION_STORE_AND_READ_PATH`",
        "stage3_status",
    )
    sec = stage3.find("## 5. Production migration evidence and remaining Stage 3 work")
    if sec == -1:
        raise RuntimeError("EXPECTED_STAGE3_SECTION5_NOT_FOUND")
    closure = "\n".join([
        "## 5. Stage 3 closure",
        "",
        "Stage 3 is complete.",
        "",
        "Closure evidence:",
        "",
        "- production schema migration: run `33496843121`, job `99820886297`, `SUCCESS`;",
        "- production schema independently visible in Neon resource tree;",
        "- guarded R4.1 emitted-state bridge: run `33498177345`, job `99825081623`, `R4_1_DECISION_BRIDGE_SMOKE_PASS`;",
        "- bridge verification covered state-shape guard, forbidden action guard, drift guard, frozen engine/config identity, store-reader roundtrip, idempotency and rollback;",
        "- app Decision Store reader integration: canonical commit `50ab446b2b97634a2a812a3b6de655c358f9829b`;",
        "- app smoke: run `33498603322`, job `99826433286`, `GOLD_CONTROL_DECISION_STORE_APP_READER_PASS`;",
        "- app no longer depends on `latest_signal.json` for current decision state;",
        "- reader excludes `HISTORICAL_REPLAY` and refuses non-null action mapping;",
        "- no synthetic decision row survived rollback tests;",
        "- production Decision Store remains empty because prospective issuance prerequisites are not yet satisfied.",
        "",
        "Final Stage 3 status:",
        "",
        "`PASS_DECISION_STORE_AND_READ_PATH`",
        "",
        "The absence of a real prospective row is now a Stage 4/11 issuance prerequisite, not unfinished Decision Store infrastructure.",
        "",
    ])
    stage3 = stage3[:sec] + closure

    stage4 = "\n".join([
        "# GOLD CONTROL — STAGE 4 DETERMINISTIC R4.1 STATUS",
        "",
        "**Status date:** 2026-09-01",
        "**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.3",
        "**Stage:** 4 — Deterministic R4.1 Decision Engine / Issuer",
        "**Current status:** `IN_PROGRESS_BLOCKED_INPUT_CONTRACTS`",
        "",
        "## 1. What is verified",
        "",
        "- Frozen R4.1 engine tests are deterministic under the audited test contract.",
        "- R4.1 descriptive emitted state can be mapped to Decision Store without recomputing signals.",
        "- Persistence bridge refuses action/exposure fields and unreviewed emitted-state shape drift.",
        "- Store-reader roundtrip, idempotency and rollback are verified.",
        "- `LIVE_PRODUCTION` has an additional disabled-by-default write gate.",
        "- A current app reader exists but there are no display-eligible decision rows.",
        "",
        "## 2. Canonical live emitter audit",
        "",
        "Status:",
        "",
        "`NOT_FOUND_CANONICAL_LIVE_R4_1_EMITTER`",
        "",
        "`replay_daily.py` is a sequential replay CLI, not a prospective scheduled issuer.",
        "",
        "The older R4 workflow that emits LONG/CASH and AL/SAT cannot be promoted into R4.1 because the current contract is `NOT_PROVEN_POSITION_MAPPING`.",
        "",
        "## 3. Read-only production readiness audit",
        "",
        "Run `33499509482`, job `99829327414`, conclusion `SUCCESS`.",
        "",
        "The audit itself passed but readiness is:",
        "",
        "`BLOCKED`",
        "",
        "Blockers:",
        "",
        "1. `FORECAST_CONTRACT_NOT_ISSUED`",
        "2. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`",
        "3. `LATEST_DAILY_XAU_PIPELINE_NOT_SUCCESS`",
        "4. `NO_APPROVED_CANONICAL_XAU_EOD_DECISION_SOURCE`",
        "",
        "Decision Store row counts at audit time were zero. Forecast input/derived/contract table row counts were also zero.",
        "",
        "## 4. XAU source interpretation",
        "",
        "`XAU_DAILY_XAUS` remains an XAUS-transported daily cross-check whose upstream Yahoo lineage is disclosed in the registry. It is `CANDIDATE_NOT_BENCHMARK` and is not authorized as the canonical EOD decision close.",
        "",
        "`XAU_SPOT_XAUS` is `APPROVED_INDICATIVE_NOT_SETTLEMENT` monitoring. It is not the frozen EOD execution close.",
        "",
        "Therefore there is currently no approved canonical XAU EOD decision source in the live data plane.",
        "",
        "## 5. Next work",
        "",
        "1. resolve canonical XAU EOD decision-price authority/lineage under change control;",
        "2. restore successful daily ingestion for that approved source;",
        "3. implement genuine prospective H=1 forecast issuance with immutable input snapshot + monthly forecast contract;",
        "4. construct the canonical EOD R4.1 issuer only after those prerequisites pass;",
        "5. begin with `PROSPECTIVE_SHADOW`, not `LIVE_PRODUCTION`;",
        "6. preserve `NOT_PROVEN_POSITION_MAPPING`.",
        "",
        "No historical or file-backed result may be relabelled as prospective merely to populate the ledger.",
        "",
    ])

    MANIFEST.write_text(manifest, encoding="utf-8")
    STAGE3.write_text(stage3, encoding="utf-8")
    STAGE4.write_text(stage4, encoding="utf-8")
    print("GOLD_CONTROL_MANIFEST_STAGE4_RECONCILE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
