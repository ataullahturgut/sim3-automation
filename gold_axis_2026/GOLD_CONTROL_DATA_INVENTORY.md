# GOLD CONTROL — DATA INVENTORY / HEALTH AUDIT

**Inventory version:** 1.0  
**Audit date:** 2026-09-01  
**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.0  
**Schema contract:** `GOLD_DATA_R2.6_2026-08-31`  
**Ingestion/data contract:** `GOLD_DATA_R2.7_2026-08-31`  
**Overall Stage 1 status:** `PARTIAL_COMPLETE_WITH_LIVE_DB_QUERY_BLOCKED`

---

## 0. PURPOSE AND EXIT RULE

This inventory is the canonical Stage 1 data-surface audit for Gold Control.

The Stage 1 exit criterion in the project manifest requires the **actual database** series inventory, including first/last observations, retrieval freshness, quality, lineage and display policy.

This document distinguishes four evidence levels:

| Evidence level | Meaning |
|---|---|
| `L1_LIVE_DB_QUERY` | Direct read-only query of current Neon rows during this audit |
| `L2_CI_DB_AUDIT` | Database/source state proven by a recorded CI persistence/audit run |
| `L3_FROZEN_ARCHITECTURE` | Explicitly verified and frozen in `GOLD_DATA_R2_ARCHITECTURE.md` |
| `L4_CONTRACT_ONLY` | Declared in source contracts, but current database row state not independently re-queried here |

### Current limitation

`L1_LIVE_DB_QUERY` could not be completed on 2026-09-01 because the available Neon connector exposed an argument-schema mismatch between its declared interface and runtime validator.

Status:

`BLOCKED_CONNECTOR_SCHEMA_MISMATCH`

This is **not evidence of a Neon outage, authentication failure, or missing database rows**. Therefore this audit does not invent current counts, current first/last timestamps, or current freshness values where they were not independently proven.

Stage 1 remains `PARTIAL_COMPLETE_WITH_LIVE_DB_QUERY_BLOCKED` until a direct read-only inventory query succeeds.

---

# 1. FROZEN DATA-PLANE PRINCIPLES

The following remain binding:

1. Provider lineage is part of series identity.
2. Similar economic meaning does not authorize silent provider substitution.
3. `observation_ts` is not automatically `available_as_of`.
4. Historical reconstruction must use `observations_as_of(origin_ts)` or an immutable forecast input snapshot.
5. `canonical_latest` and `usable_observations` are current-state surfaces, not historical backtest surfaces.
6. Backfilled history is not retrospectively knowable before first recorded retrieval unless publication/vintage timing is independently reconstructed.
7. Live/indicative XAU is not the frozen R4.1 EOD execution close.
8. Vendor same-day daily bars are not accepted as completed EOD bars while the relevant session may still be open.
9. Licensed/private raw data respects display and redistribution restrictions.
10. Blocked inputs do not receive invented proxies under the same identity.

---

# 2. CURRENT PRODUCTION-INGESTION INVENTORY

The frozen R2.7 architecture explicitly records the following 19 series as automatically collected and persisted to private Neon Postgres. The architecture states that source checks, persistence, deduplication and point-in-time database audits were verified by CI as of the 2026-08-31 freeze.

`Latest known eligible` below means the latest date **explicitly proven by the cited frozen audit**, not necessarily the current database latest on 2026-09-01.

| Series ID | Semantic | Source / Tier | Production role | UI display policy | Contract / frozen status | Proven row coverage in this audit | Latest known eligible | Current row-level status |
|---|---|---|---|---|---|---|---|---|
| `XAU_SPOT_XAUS` | XAU live | XAUS public API / C | monitoring; Emergency candidate | `DISPLAY_INDICATIVE` | `APPROVED_INDICATIVE_NOT_SETTLEMENT` | `NOT_PROVEN_CURRENT_COUNT` | `NOT_PROVEN_CURRENT_LATEST` | `L3_FROZEN_ARCHITECTURE`; L1 blocked |
| `XAU_DAILY_XAUS` | XAU daily | XAUS history / C | operational cross-check | `DISPLAY_CHART_CROSSCHECK_ONLY` | `CANDIDATE_NOT_BENCHMARK` | `NOT_PROVEN_CURRENT_COUNT` | `NOT_PROVEN_CURRENT_LATEST` | `L3_FROZEN_ARCHITECTURE`; L1 blocked |
| `GVZ_CBOE` | GVZ | Cboe official / A | R4 risk cap | `DISPLAY` | `APPROVED` | `NOT_PROVEN_CURRENT_COUNT` | `NOT_PROVEN_CURRENT_LATEST` | `L3_FROZEN_ARCHITECTURE`; corrected PIT contract; L1 blocked |
| `VIX_CBOE` | VIX | Cboe official / A | forecast feature | `SECONDARY_CONTEXT_IF_NEEDED` | `APPROVED` | `NOT_PROVEN_CURRENT_COUNT` | `NOT_PROVEN_CURRENT_LATEST` | `L3_FROZEN_ARCHITECTURE`; corrected PIT contract; L1 blocked |
| `DGS10_FRB_H15` | US 10Y | Federal Reserve Board H.15 / A | authority feature candidate | `MODEL_OR_SECONDARY_CONTEXT` | `APPROVED_DIRECT_AUTHORITY` | `NOT_PROVEN_CURRENT_COUNT` | `NOT_PROVEN_CURRENT_LATEST` | `L3_FROZEN_ARCHITECTURE`; L1 blocked |
| `DEXCHUS_FRB_H10` | USD/CNY | Federal Reserve Board H.10 / A | Patch macro feature candidate | `MODEL_OR_SECONDARY_CONTEXT` | `APPROVED_DIRECT_AUTHORITY` | `NOT_PROVEN_CURRENT_COUNT` | `NOT_PROVEN_CURRENT_LATEST` | `L3_FROZEN_ARCHITECTURE`; L1 blocked |
| `DTWEXBGS_FRB_H10` | broad USD | Federal Reserve Board H.10 / A | USD proxy challenger | `MODEL_OR_SECONDARY_CONTEXT` | `APPROVED_PROXY_ONLY_DIRECT_AUTHORITY` | `NOT_PROVEN_CURRENT_COUNT` | `NOT_PROVEN_CURRENT_LATEST` | explicitly **not DXY**; L1 blocked |
| `EFFR_NYFED` | Fed Funds | New York Fed / A | Patch macro feature candidate | `MODEL_OR_SECONDARY_CONTEXT` | `APPROVED_DIRECT_AUTHORITY` | `NOT_PROVEN_CURRENT_COUNT` | `NOT_PROVEN_CURRENT_LATEST` | `L3_FROZEN_ARCHITECTURE`; L1 blocked |
| `GPR_OFFICIAL` | GPR | Caldara-Iacoviello official workbook / A | forecast feature | `MODEL_OR_SECONDARY_CONTEXT` | `APPROVED_REVISION_PRONE` | `NOT_PROVEN_CURRENT_COUNT` | `NOT_PROVEN_CURRENT_LATEST` | vintage-preserved; L1 blocked |
| `GPRT_OFFICIAL` | GPRT | Caldara-Iacoviello official workbook / A | forecast feature | `MODEL_OR_SECONDARY_CONTEXT` | `APPROVED_REVISION_PRONE` | `NOT_PROVEN_CURRENT_COUNT` | `NOT_PROVEN_CURRENT_LATEST` | vintage-preserved; L1 blocked |
| `GPRA_OFFICIAL` | GPRA | Caldara-Iacoviello official workbook / A | forecast feature | `MODEL_OR_SECONDARY_CONTEXT` | `APPROVED_REVISION_PRONE` | `NOT_PROVEN_CURRENT_COUNT` | `NOT_PROVEN_CURRENT_LATEST` | vintage-preserved; L1 blocked |
| `SP500_FRED` | S&P 500 | FRED API; underlying S&P DJI / A | forecast feature | `MODEL_ONLY_RAW_NONDISPLAY` | `APPROVED_PRIVATE_MODEL_USE_NO_PUBLIC_RAW_REDISTRIBUTION` | total current count `NOT_PROVEN`; first production load documented as 750 observations | `NOT_PROVEN_CURRENT_LATEST` | private model use; L1 blocked |
| `DJIA_FRED` | DJIA | FRED API; underlying S&P DJI / A | forecast feature | `MODEL_ONLY_RAW_NONDISPLAY` | `APPROVED_PRIVATE_MODEL_USE_NO_PUBLIC_RAW_REDISTRIBUTION` | total current count `NOT_PROVEN`; part of documented private-index load | `NOT_PROVEN_CURRENT_LATEST` | private model use; L1 blocked |
| `NASDAQ100_FRED` | Nasdaq-100 | FRED API; underlying Nasdaq / A | Patch/forecast feature | `MODEL_ONLY_RAW_NONDISPLAY` | `APPROVED_PRIVATE_MODEL_USE_NO_PUBLIC_RAW_REDISTRIBUTION` | total current count `NOT_PROVEN`; part of documented private-index load | `NOT_PROVEN_CURRENT_LATEST` | private model use; L1 blocked |
| `NEM_TWELVEDATA` | Newmont | Twelve Data / B | miner feature | `INTERNAL_NON_DISPLAY` | `APPROVED_VENDOR_IDENTITY_VALIDATED_INTERNAL_NON_DISPLAY` | **2,679 usable daily observations** in verified R2.7 seed | **2026-08-28** at seed verification | `L3_FROZEN_ARCHITECTURE`; L1 blocked |
| `BARRICK_B_TWELVEDATA` | Barrick NYSE | Twelve Data / B | Barrick feature | `INTERNAL_NON_DISPLAY` | `APPROVED_VENDOR_IDENTITY_VALIDATED_INTERNAL_NON_DISPLAY` | **2,679 usable daily observations** in verified R2.7 seed | **2026-08-28** at seed verification | `L3_FROZEN_ARCHITECTURE`; L1 blocked |
| `GLL_TWELVEDATA` | GLL | Twelve Data / B | inverse-gold feature | `INTERNAL_NON_DISPLAY` | `APPROVED_VENDOR_IDENTITY_VALIDATED_INTERNAL_NON_DISPLAY` | **2,679 usable daily observations** in verified R2.7 seed | **2026-08-28** at seed verification | `L3_FROZEN_ARCHITECTURE`; L1 blocked |
| `DZZ_TWELVEDATA` | DZZ | Twelve Data / B | double-short-gold feature | `INTERNAL_NON_DISPLAY` | `APPROVED_VENDOR_IDENTITY_VALIDATED_INTERNAL_NON_DISPLAY` | **2,679 usable daily observations** in verified R2.7 seed | **2026-08-28** at seed verification | `L3_FROZEN_ARCHITECTURE`; L1 blocked |
| `HL_PB_TWELVEDATA` | Hecla Series B preferred | Twelve Data / B | Hecla preferred feature | `INTERNAL_NON_DISPLAY` | `APPROVED_VENDOR_IDENTITY_VALIDATED_INTERNAL_NON_DISPLAY` | **2,679 usable daily observations** in verified R2.7 seed | **2026-08-28** at seed verification | `L3_FROZEN_ARCHITECTURE`; L1 blocked |

## 2.1 Twelve Data seed audit — exact frozen evidence

The R2.7 architecture records the following verified one-time historical seed result:

- 13,395 completed-session observations collected across the five validated Twelve Data series;
- 12,098 new observations written after the existing daily seed;
- 0 revised observations in the backfill;
- dedupe replay: 13,395 read, 0 written;
- 0 quality errors;
- 2,679 usable daily observations per series;
- latest eligible observation at verification: 2026-08-28;
- zero point-in-time rows exposed before each series' first retrieval;
- zero same-exchange-day eligible rows.

These figures are historical audit evidence from the 2026-08-31 freeze. They are **not silently promoted to a 2026-09-01 live row count**.

## 2.2 Private index load — bounded evidence

The architecture records that the first authenticated FRED private-index production load wrote **750 observations** across `SP500_FRED`, `DJIA_FRED`, and `NASDAQ100_FRED`, and an immediate repeat wrote zero unchanged observations. A bounded historical seed was subsequently added.

Because this audit could not query current Neon rows, current per-series totals and current last-observation timestamps remain:

`NOT_PROVEN_CURRENT_COUNT` / `NOT_PROVEN_CURRENT_LATEST`.

---

# 3. DECLARED SERIES NOT PROVEN AS CURRENT PRODUCTION-INGESTION SURFACE

The source contract also declares additional series. Declaration alone is not proof that the series is currently persisted and healthy in the production data plane.

| Series ID | Contract status | Inventory treatment |
|---|---|---|
| `XAU_INTRADAY_XAUS` | `APPROVED_INDICATIVE` | `CONTRACT_DECLARED; PRODUCTION_PERSISTENCE_NOT_PROVEN`; do not expose intraday UI until adapter/storage audit passes |
| `XAG_INTRADAY_XAUS` | `OPTIONAL` | research only |
| `DGS10_FRED` | `APPROVED` | separate legacy/FRED lineage; direct production authority path is `DGS10_FRB_H15` |
| `DFF_FRED` | `APPROVED` | separate lineage; current production direct-rate path includes `EFFR_NYFED` |
| `DEXCHUS_FRED` | `APPROVED_WITH_AVAILABILITY_LAG` | separate lineage; direct production path includes `DEXCHUS_FRB_H10` |
| `DTWEXBGS_FRED` | `APPROVED_PROXY_ONLY` | separate lineage; direct production path includes `DTWEXBGS_FRB_H10` |
| legacy StakTrakr metal series | `KEEP_PINNED_DO_NOT_EXTEND_AS_AUTHORITY` | historical continuity only, never promoted to authority |
| `BARRICK_ABX_TSX_LEGACY` | `PINNED_LEGACY_ONLY` | no silent bridge to current Barrick `B` |

---

# 4. BLOCKED / LICENSED / UNRESOLVED INPUTS

| Input / identity | Status | Production consequence |
|---|---|---|
| Exact ICE DXY | `BLOCKED_LICENSE_OR_AUTHORIZED_VENDOR_ENTITLEMENT_REQUIRED` | broad USD proxy remains separately named; never label it DXY |
| Legacy `^TNX` as new production source | `BLOCKED_AS_NEW_PRODUCTION_SOURCE` | direct H.15 10Y remains separate lineage |
| LBMA Gold / Silver | `OPTIONAL_LICENSE_REQUIRED_FOR_MODEL_USE` | do not assume rights |
| LBMA Platinum / Palladium | `BLOCKED_LICENSE_REQUIRED_FROM_2026-07-01` | exact benchmark continuity unresolved without license |
| XPT/USD / XPD/USD Twelve | `PAID_GROW_REQUIRED; NOT_SILENT_PATCH_SUBSTITUTE` | new lineage/model validation required |
| Exact GPY | `BLOCKED_AMBIGUOUS_IDENTIFIER` | no invented substitute |
| Exact `long_term_trend` | `BLOCKED_DEFINITION_NOT_RECOVERED` | no invented feature |
| Exact `volatility` | `BLOCKED_DEFINITION_NOT_RECOVERED` | no invented feature |
| Exact archived VW executable runner | `BLOCKED_NOT_PROVEN` | audited output may remain reference; not falsely represented as fully reproducible |

---

# 5. POINT-IN-TIME ELIGIBILITY

## 5.1 Current state

Current-state convenience surfaces:

- `canonical_latest`
- `latest_series`
- `usable_observations`

These do not establish what the system knew at a historical origin.

## 5.2 Historical state

Required historical surfaces:

- `observations_as_of(origin_ts)`
- `latest_series_as_of(origin_ts)`

Eligibility requires at minimum:

```text
retrieved_at <= origin_ts
AND available_as_of <= origin_ts
```

## 5.3 Historical publication timestamps

For direct-authority and other backfilled histories where exact historical publication timestamps have not been independently reconstructed:

`HISTORICAL_RELEASE_TIMESTAMP_RECONSTRUCTION = NOT_PROVEN`

The conservative availability rule is the first retrieval recorded by the Gold Data Plane. This prevents a historical backfill from manufacturing historical knowledge.

## 5.4 Cboe correction

Early R2 Cboe rows used an invalid availability assumption. Raw evidence is retained, but the corrected PIT function excludes invalid-availability records. The frozen R2.7 audit states that CI proved zero such legacy rows are exposed in the pre-correction PIT gap.

---

# 6. DATABASE OBJECT INVENTORY

Frozen database objects documented by the R2.7 architecture:

## Primary tables

- `source_registry`
- `retrieval_runs`
- `observations`
- `source_vintages`
- `quality_events`
- `forecast_input_snapshots`
- `derived_feature_snapshots`
- `monthly_forecast_contracts`
- `system_metadata`

## Current-state views

- `canonical_latest`
- `latest_series`
- `usable_observations`

## Point-in-time functions

- `observations_as_of(timestamptz)`
- `latest_series_as_of(timestamptz)`

Direct current schema introspection was not completed in this audit because of `BLOCKED_CONNECTOR_SCHEMA_MISMATCH`; therefore object existence on 2026-09-01 is supported here by frozen schema/architecture evidence, not a fresh catalog query.

---

# 7. SCHEDULING / INGESTION CONTRACT

Frozen scheduling policy:

- XAU monitoring snapshot: hourly at minute 17;
- daily authority ingestion: 23:45 UTC plus independent 06:25 UTC retry/verification;
- Twelve private-market ingestion: Tuesday–Saturday 01:35 UTC plus 12:45 UTC retry;
- private FRED indices: Tuesday–Saturday after the U.S. session plus independent retry;
- provider jobs remain isolated so one provider outage does not block unrelated sources.

Workflow definitions are present in the canonical branch for the data pipeline, including Neon ingest, FRED private indices, Twelve market ingestion, pipeline smoke checks and direct-Fed probing. Presence of a workflow definition is **not by itself proof of the latest run conclusion**.

---

# 8. DATA-QUALITY GATES

Before a current observation is model-eligible, the frozen contract requires:

- schema check;
- numeric/domain check;
- parseable source timestamp;
- provider identity match;
- `available_as_of` present;
- retrieval-floor availability not earlier than first retrieval;
- no provider substitution;
- no same-exchange-day Twelve `1day` EOD bar;
- latest mandatory ingestion run successful;
- dedupe replay writes zero unchanged observations;
- PIT leak probes pass.

Because the latest mandatory database rows and run ledger could not be queried directly in this audit, **current health is not promoted to `LIVE_PASS`**.

---

# 9. APP / DATA-PLANE GAP

Current Streamlit implementation uses external runtime adapters directly for:

- XAU spot;
- one-year XAU daily history;
- Cboe GVZ history/latest close.

The app does not yet prove a general Neon query path for the market/home screen.

Status:

`NOT_PROVEN_APP_NEON_QUERY`

This is acceptable as a transitional monitoring adapter, but the app must preserve the frozen distinctions:

- indicative live spot != EOD execution close;
- daily XAUS history != settlement benchmark;
- model-only/vendor raw series are not exposed merely because they exist in Neon.

---

# 10. UI CONSEQUENCES — STAGE 1

Based on currently proven display contracts, the first `Piyasa` screen may safely be designed around:

1. `XAU_SPOT_XAUS` — indicative live price, with source/as-of/freshness;
2. `XAU_DAILY_XAUS` — operational daily chart/cross-check, not benchmark;
3. `GVZ_CBOE` — official latest daily close and frozen risk-band interpretation;
4. latest **stored** EOD decision only after Stage 3 creates the canonical decision state store.

Current XAUS history adapter supports a one-year daily history, so the frozen home-chart selector remains:

`1A | 3A | 6A | 1Y`

Do not expose `1G`, `1H`, or `Tümü` as if the current audited adapter already supplied those histories.

Authority macro data may later be summarized as secondary context, but should not overload the market-first home screen. Raw private/vendor series remain non-display by default.

---

# 11. AUDIT FINDINGS

## Finding 1 — Data architecture is structurally mature

The project has a frozen provider-lineage contract, append/revision semantics, PIT functions, source-vintage storage, quality-event storage and immutable forecast-input concepts.

Status: `PASS_ARCHITECTURE`.

## Finding 2 — Production ingestion set is explicitly documented

Nineteen production-ingestion series are explicitly marked verified in the R2.7 architecture.

Status: `PASS_FROZEN_2026_08_31_EVIDENCE`.

## Finding 3 — Current DB row inventory is not yet independently re-proven

Current first/last observations, last retrieval times, row counts, quality statuses and freshness could not be read directly on 2026-09-01 because of the connector schema mismatch.

Status: `BLOCKED_CONNECTOR_SCHEMA_MISMATCH`.

This blocks **Stage 1 full exit**, not the entire project.

## Finding 4 — Display rights are not uniform

Some series are suitable for display; others are explicitly private/non-display or raw-redistribution restricted.

Status: `PASS_POLICY_SEPARATION`.

## Finding 5 — Data availability is not model migration approval

New direct-authority/FRED/Twelve histories do not retroactively prove archived VW/Patch feature identities. Source-bridge and leakage-safe ablation remain required before a frozen model is migrated to a different lineage.

Status: `PASS_NO_SILENT_MODEL_MIGRATION`.

## Finding 6 — Decision state remains outside the current data plane

The current app still relies on a file-style latest signal contract rather than a canonical database-backed immutable decision ledger.

Status: `OPEN_STAGE_3_DECISION_STORE`.

---

# 12. STAGE 1 CLOSURE DECISION

**Decision:** `PARTIAL_COMPLETE_WITH_LIVE_DB_QUERY_BLOCKED`

What is complete:

- canonical series universe identified;
- source/tier/role/status mapped;
- display/non-display policy mapped;
- PIT rules mapped;
- database object contract mapped;
- blocked/licensed inputs mapped;
- exact verified R2.7 Twelve historical-seed metrics preserved without upgrading them to current-live claims;
- app/data-plane gaps documented.

What remains before `STAGE_1 = PASS`:

A read-only Neon query must generate, for every production series:

- `series_id`
- `semantic_id`
- provider / lineage
- first observation
- last observation
- first retrieval
- last retrieval
- latest provider/as-of
- usable/current row count
- latest quality status
- freshness
- PIT eligibility note

and must also reconcile the latest mandatory ingestion-run status from `retrieval_runs`.

Until then, missing live row metadata remains explicitly `NOT_PROVEN`, not inferred.

---

# 13. NEXT NON-BLOCKED WORKSTREAM

The connector limitation does not require the entire project to stop. The next roadmap stage can proceed on versioned GitHub artifacts while Stage 1 live row audit remains blocked:

## `STAGE 2 — FORECAST CANONICALIZATION`

Stage 2 must reconcile and freeze one unambiguous forecast registry for:

- H=1 target/origin contract;
- executable Causal Patch R1 path;
- audited VW shadow/reference;
- Random Walk benchmark;
- 3M Momentum direction challenger;
- archived-vs-reproducible model version differences;
- model metrics tied to exact version and evaluation window;
- provenance and blocker states.

No metric from one model version may be silently assigned to another model version.
