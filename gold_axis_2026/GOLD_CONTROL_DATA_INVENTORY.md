# GOLD CONTROL — DATA INVENTORY / HEALTH AUDIT

**Inventory version:** 2.0  
**Generated at (UTC):** `2026-09-02T18:20:05.173354+00:00`  
**Evidence:** direct read-only Neon query executed by protected GitHub Actions; transaction rolled back  
**Stage 1 status:** `PASS_AUDIT_COMPLETE_WITH_OPERATIONAL_BLOCKERS`  

---

## 1. Audit contract

This file is generated from the actual Neon data plane plus the database `source_registry`. It contains metadata only; observation values, provider payloads, secrets and quality-event messages are excluded.

Historical reconstruction remains governed by `observations_as_of(origin_ts)` / immutable snapshots. Current-state views never prove what was knowable at an old forecast origin.

## 2. Current database inventory

| Series | Semantic | Tier | Contract source | Actual latest source | Role | Display | Model/status | First obs | Last obs | First retrieval | Last retrieval | Rows | Pipeline health | PIT / blocker |
|---|---|---:|---|---|---|---|---|---|---|---|---|---:|---|---|
| `BARRICK_ABX_TSX_LEGACY` | BARRICK_TSX_PROXY | UNRE… | legacy Yahoo identity | — | legacy rebuild proxy | NOT_EXPLICITLY_FROZEN_F… | PINNED_LEGACY_ONLY | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS |
| `BARRICK_B_TWELVEDATA` | BARRICK_NYSE | B | Twelve Data | Twelve Data | current Barrick NYSE feature … | NO_RAW_DISPLAY | APPROVED_VENDOR_IDENTITY_VALIDATE… | 2016-01-04T00:00:00… | 2026-09-01T00:00:00… | 2026-08-31T14:09:09… | 2026-09-02T06:18:41… | 2681 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `DEXCHUS_ALFRED_PIT_ME` | Chinese yuan per US… | AUTH… | Federal Reserve Bank of St. L… | Federal Reserve Bank of St.… | GOLD_H1_SUCCESSOR_R1 macro fe… | NOT_EXPLICITLY_FROZEN_F… | APPROVED_HISTORICAL_PIT_RECONSTRU… | 2016-01-31T23:59:59… | 2026-08-31T23:59:59… | 2026-09-01T17:36:34… | 2026-09-01T17:36:34… | 128 | UNRESOLVED_NO_MAPPED_PIPELI… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `DEXCHUS_FRB_H10` | USDCNY | A | Board of Governors of the Fed… | Board of Governors of the F… | Patch macro feature candidate… | NOT_EXPLICITLY_FROZEN_F… | APPROVED_DIRECT_AUTHORITY | 2025-10-20T00:00:00… | 2026-08-28T00:00:00… | 2026-08-31T13:28:21… | 2026-09-01T08:22:56… | 216 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `DEXCHUS_FRED` | USDCNY | A | Federal Reserve Board H.10 vi… | — | Patch macro feature | NOT_EXPLICITLY_FROZEN_F… | APPROVED_WITH_AVAILABILITY_LAG | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS |
| `DFF_ALFRED_PIT_ME` | Effective federal f… | AUTH… | Federal Reserve Bank of St. L… | Federal Reserve Bank of St.… | GOLD_H1_SUCCESSOR_R1 macro fe… | NOT_EXPLICITLY_FROZEN_F… | APPROVED_HISTORICAL_PIT_RECONSTRU… | 2016-01-31T23:59:59… | 2026-08-31T23:59:59… | 2026-09-01T17:36:34… | 2026-09-01T17:36:34… | 128 | UNRESOLVED_NO_MAPPED_PIPELI… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `DFF_FRED` | FEDFUNDS | A | Federal Reserve Board H.15 vi… | — | Patch macro feature | NOT_EXPLICITLY_FROZEN_F… | APPROVED | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS |
| `DGS10_ALFRED_PIT_ME` | US 10Y Treasury con… | AUTH… | Federal Reserve Bank of St. L… | Federal Reserve Bank of St.… | GOLD_H1_SUCCESSOR_R1 macro fe… | NOT_EXPLICITLY_FROZEN_F… | APPROVED_HISTORICAL_PIT_RECONSTRU… | 2016-01-31T23:59:59… | 2026-08-31T23:59:59… | 2026-09-01T17:36:34… | 2026-09-01T17:36:34… | 128 | UNRESOLVED_NO_MAPPED_PIPELI… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `DGS10_FRB_H15` | US10Y | A | Board of Governors of the Fed… | Board of Governors of the F… | authority 10-year constant-ma… | NOT_EXPLICITLY_FROZEN_F… | APPROVED_DIRECT_AUTHORITY | 2025-10-24T00:00:00… | 2026-08-31T00:00:00… | 2026-08-31T13:28:21… | 2026-09-02T11:29:32… | 213 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `DGS10_FRED` | US10Y | A | Federal Reserve Board H.15 vi… | — | new reproducible 10Y feature;… | NOT_EXPLICITLY_FROZEN_F… | APPROVED | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS |
| `DJIA_FRED` | DJI | A | S&P Dow Jones Indices via FRED | FRED; underlying S&P Dow Jo… | forecast feature | NO_RAW_DISPLAY | APPROVED_PRIVATE_MODEL_USE_NO_PUB… | 2016-08-29T00:00:00… | 2026-09-01T00:00:00… | 2026-08-31T13:55:42… | 2026-09-02T05:51:31… | 2516 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `DTWEXBGS_FRB_H10` | USD_BROAD_INDEX | A | Board of Governors of the Fed… | Board of Governors of the F… | authority broad-dollar proxy … | NOT_EXPLICITLY_FROZEN_F… | APPROVED_PROXY_ONLY_DIRECT_AUTHOR… | 2025-10-20T00:00:00… | 2026-08-28T00:00:00… | 2026-08-31T13:28:21… | 2026-09-01T08:22:56… | 216 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `DTWEXBGS_FRED` | USD_BROAD_INDEX | A | Federal Reserve Board H.10 vi… | — | authority-grade dollar proxy … | NOT_EXPLICITLY_FROZEN_F… | APPROVED_PROXY_ONLY | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS |
| `DXY_ICE` | DXY | A | ICE Data Indices | — | exact DXY feature | NO_DISPLAY_BLOCKED | BLOCKED_LICENSE_OR_AUTHORIZED_VEN… | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS; BLOCKED_LICENSE_OR_AUTHORIZED… |
| `DZZ_TWELVEDATA` | DZZ | B | Twelve Data | Twelve Data | gold double-short ETN feature | NO_RAW_DISPLAY | APPROVED_VENDOR_IDENTITY_VALIDATE… | 2016-01-04T00:00:00… | 2026-09-01T00:00:00… | 2026-08-31T14:09:09… | 2026-09-02T06:18:41… | 2681 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `EFFR_NYFED` | FEDFUNDS | A | Federal Reserve Bank of New Y… | Federal Reserve Bank of New… | effective federal funds rate … | NOT_EXPLICITLY_FROZEN_F… | APPROVED_DIRECT_AUTHORITY | 2025-10-15T00:00:00… | 2026-08-31T00:00:00… | 2026-08-31T13:28:21… | 2026-09-02T11:29:32… | 221 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `GLL_TWELVEDATA` | GLL | B | Twelve Data | Twelve Data | gold inverse product feature | NO_RAW_DISPLAY | APPROVED_VENDOR_IDENTITY_VALIDATE… | 2016-01-04T00:00:00… | 2026-09-01T00:00:00… | 2026-08-31T14:09:09… | 2026-09-02T06:18:41… | 2681 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `GOLD_STAKTRAKR_LEGACY` | GOLD_DAILY_LEGACY | D | lbruton/StakTrakr archive | — | historical model continuity o… | NOT_EXPLICITLY_FROZEN_F… | KEEP_PINNED_DO_NOT_EXTEND_AS_AUTH… | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS |
| `GPRA_OFFICIAL` | GPRA | A | Caldara-Iacoviello official w… | Caldara-Iacoviello official… | forecast feature | NOT_EXPLICITLY_FROZEN_F… | APPROVED_REVISION_PRONE | 2023-08-01T00:00:00… | 2026-08-01T00:00:00… | 2026-08-31T12:58:31… | 2026-09-02T01:24:10… | 37 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `GPRT_OFFICIAL` | GPRT | A | Caldara-Iacoviello official w… | Caldara-Iacoviello official… | forecast feature | NOT_EXPLICITLY_FROZEN_F… | APPROVED_REVISION_PRONE | 2023-08-01T00:00:00… | 2026-08-01T00:00:00… | 2026-08-31T12:58:31… | 2026-09-02T01:24:10… | 37 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `GPR_OFFICIAL` | GPR | A | Caldara-Iacoviello official w… | Caldara-Iacoviello official… | forecast feature | NOT_EXPLICITLY_FROZEN_F… | APPROVED_REVISION_PRONE | 2023-08-01T00:00:00… | 2026-08-01T00:00:00… | 2026-08-31T12:58:31… | 2026-09-02T01:24:10… | 37 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `GVZ_CBOE` | GVZ | A | Cboe official historical pric… | Cboe | R4 risk cap | DISPLAY_OFFICIAL_CLOSE | APPROVED | 2026-03-10T00:00:00… | 2026-09-01T00:00:00… | 2026-08-31T12:58:31… | 2026-09-02T01:24:11… | 122 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `HL_PB_TWELVEDATA` | HL_PB | B | Twelve Data | Twelve Data | Hecla Series B preferred feat… | NO_RAW_DISPLAY | APPROVED_VENDOR_IDENTITY_VALIDATE… | 2016-01-04T00:00:00… | 2026-09-01T00:00:00… | 2026-08-31T14:09:09… | 2026-09-02T06:18:41… | 2681 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `LBMA_GOLD` | LBMA_GOLD_PRICE | A | ICE Benchmark Administration … | — | settlement-grade authority be… | NO_DISPLAY_BLOCKED | OPTIONAL_LICENSE_REQUIRED_FOR_MOD… | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS; OPTIONAL_LICENSE_REQUIRED_FOR… |
| `LBMA_PALLADIUM` | LBMA_PALLADIUM_PRICE | A | ICE Benchmark Administration … | — | exact authority PGM candidate | NO_DISPLAY_BLOCKED | BLOCKED_LICENSE_REQUIRED_FROM_202… | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS; BLOCKED_LICENSE_REQUIRED_FROM… |
| `LBMA_PLATINUM` | LBMA_PLATINUM_PRICE | A | ICE Benchmark Administration … | — | exact authority PGM candidate | NO_DISPLAY_BLOCKED | BLOCKED_LICENSE_REQUIRED_FROM_202… | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS; BLOCKED_LICENSE_REQUIRED_FROM… |
| `LBMA_SILVER` | LBMA_SILVER_PRICE | A | ICE Benchmark Administration … | — | authority benchmark | NO_DISPLAY_BLOCKED | OPTIONAL_LICENSE_REQUIRED_FOR_MOD… | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS; OPTIONAL_LICENSE_REQUIRED_FOR… |
| `NASDAQ100_ALFRED_PIT_ME` | NASDAQ-100 index: l… | AUTH… | Federal Reserve Bank of St. L… | Federal Reserve Bank of St.… | GOLD_H1_SUCCESSOR_R1 macro fe… | NOT_EXPLICITLY_FROZEN_F… | APPROVED_HISTORICAL_PIT_RECONSTRU… | 2016-01-31T23:59:59… | 2026-08-31T23:59:59… | 2026-09-01T17:36:34… | 2026-09-01T17:36:34… | 128 | UNRESOLVED_NO_MAPPED_PIPELI… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `NASDAQ100_FRED` | NDX | A | Nasdaq Inc. via FRED | FRED; underlying Nasdaq Inc. | Patch and forecast feature | NO_RAW_DISPLAY | APPROVED_PRIVATE_MODEL_USE_NO_PUB… | 1986-01-02T00:00:00… | 2026-09-01T00:00:00… | 2026-08-31T13:55:42… | 2026-09-02T05:51:31… | 10247 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `NEM_TWELVEDATA` | NEM | B | Twelve Data | Twelve Data | miner feature | NO_RAW_DISPLAY | APPROVED_VENDOR_IDENTITY_VALIDATE… | 2016-01-04T00:00:00… | 2026-09-01T00:00:00… | 2026-08-31T14:09:09… | 2026-09-02T06:18:41… | 2681 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `PALLADIUM_STAKTRAKR_LEGACY` | PALLADIUM_DAILY_LEG… | D | lbruton/StakTrakr archive | — | historical model continuity o… | NOT_EXPLICITLY_FROZEN_F… | KEEP_PINNED_DO_NOT_EXTEND_AS_AUTH… | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS |
| `PLATINUM_STAKTRAKR_LEGACY` | PLATINUM_DAILY_LEGA… | D | lbruton/StakTrakr archive | — | historical model continuity o… | NOT_EXPLICITLY_FROZEN_F… | KEEP_PINNED_DO_NOT_EXTEND_AS_AUTH… | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS |
| `SILVER_STAKTRAKR_LEGACY` | SILVER_DAILY_LEGACY | D | lbruton/StakTrakr archive | — | historical model continuity o… | NOT_EXPLICITLY_FROZEN_F… | KEEP_PINNED_DO_NOT_EXTEND_AS_AUTH… | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS |
| `SP500_FRED` | SP500 | A | S&P Dow Jones Indices via FRED | FRED; underlying S&P Dow Jo… | forecast feature | NO_RAW_DISPLAY | APPROVED_PRIVATE_MODEL_USE_NO_PUB… | 2016-08-29T00:00:00… | 2026-09-01T00:00:00… | 2026-08-31T13:55:42… | 2026-09-02T05:51:31… | 2516 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `TNX_LEGACY` | US10YT_LEGACY | UNRE… | legacy Yahoo identity | — | legacy VW rebuild exact ident… | NO_DISPLAY_BLOCKED | BLOCKED_AS_NEW_PRODUCTION_SOURCE;… | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS; BLOCKED_AS_NEW_PRODUCTION_SOU… |
| `VIX_CBOE` | VIX | A | Cboe official historical pric… | Cboe | forecast feature | SECONDARY_CONTEXT_IF_NE… | APPROVED | 2026-03-13T00:00:00… | 2026-09-01T00:00:00… | 2026-08-31T12:58:31… | 2026-09-02T01:24:11… | 122 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `XAG_INTRADAY_XAUS` | XAG_INTRADAY | C | XAUS /api/v1/intraday | — | research only | NOT_EXPLICITLY_FROZEN_F… | OPTIONAL | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS |
| `XAU_DAILY_XAUS` | XAU_DAILY | C | XAUS /api/v1/history; history… | yahoo finance (GC=F) | Piyasa daily history / last-c… | DISPLAY_OPERATIONAL_CRO… | CANDIDATE_NOT_BENCHMARK; APPROVED… | 2026-03-11T00:00:00… | 2026-09-02T00:00:00… | 2026-08-31T13:03:36… | 2026-09-02T11:29:43… | 122 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `XAU_EOD_CME_EBS` | XAU_USD_SPOT_EOD_DE… | A | CME Group / EBS Market on CME… | — | superseded authority/feed can… | NOT_EXPLICITLY_FROZEN_F… | SUPERSEDED_AS_OPERATIONAL_SOURCE_… | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS |
| `XAU_EOD_TWELVE_NY17` | XAU_USD_SPOT_EOD_DE… | B | Twelve Data | Twelve Data | canonical R4.1 EOD internal d… | NOT_EXPLICITLY_FROZEN_F… | APPROVED_CANONICAL_PIPELINE_SUCCE… | 2026-05-29T21:00:00… | 2026-08-31T21:00:00… | 2026-09-01T13:10:47… | 2026-09-01T13:49:02… | 46 | UNRESOLVED_NO_MAPPED_PIPELI… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `XAU_INTRADAY_XAUS` | XAU_INTRADAY | C | XAUS /api/v1/intraday | — | Emergency audit/research | NOT_EXPLICITLY_FROZEN_F… | APPROVED_INDICATIVE | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS |
| `XAU_MONTHLY_WB_PINKSHEET` | World Bank Pink She… | AUTH… | World Bank Pink Sheet | World Bank Pink Sheet | H1 historical target and real… | NOT_EXPLICITLY_FROZEN_F… | APPROVED_HISTORICAL_TARGET_FINAL_… | 2016-01-01T00:00:00… | 2026-07-01T00:00:00… | 2026-09-01T17:36:34… | 2026-09-01T17:36:34… | 127 | UNRESOLVED_NO_MAPPED_PIPELI… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT |
| `XAU_SPOT_GOLDAPI` | XAU_SPOT | C | Gold API (gold-api.com) | — | primary Gold Control Piyasa l… | NOT_EXPLICITLY_FROZEN_F… | APPROVED_INDICATIVE_PUBLIC_DISPLA… | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS |
| `XAU_SPOT_XAUS` | XAU_SPOT | C | XAUS public API | gold-api.com | Gold Control monitoring; Emer… | DISPLAY_INDICATIVE_NOT_… | APPROVED_INDICATIVE_NOT_SETTLEMENT | 2026-08-31T12:55:06… | 2026-09-02T14:28:54… | 2026-08-31T12:55:06… | 2026-09-02T14:28:54… | 24 | CURRENT_LAST_MAPPED_RUN_SUC… | ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT;… |
| `XPD_TWELVEDATA` | XPDUSD | B | Twelve Data Grow+ commodities | — | operational palladium alterna… | NO_DISPLAY_BLOCKED | PAID_GROW_REQUIRED; NOT_SILENT_PA… | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS; PAID_GROW_REQUIRED; NOT_SILEN… |
| `XPT_TWELVEDATA` | XPTUSD | B | Twelve Data Grow+ commodities | — | operational platinum alternat… | NO_DISPLAY_BLOCKED | PAID_GROW_REQUIRED; NOT_SILENT_PA… | — | — | — | — | 0 | NOT_PERSISTED_CURRENT_DB | NO_CURRENT_USABLE_ROWS; PAID_GROW_REQUIRED; NOT_SILEN… |

## 3. Operational findings

- Persisted/current series in `usable_observations`: **25**.
- Registered series with no current usable rows: **21**.
- Degraded/stale mapped series: **0**.
- Explicit unresolved lineage/blocker notes: **1**.
- A provider failure is not repaired by silent substitution. A failed latest run remains visible as degraded health while unrelated provider jobs may continue independently.

### Latest source-job states

| Job | Status | Started | Finished | Read | Written |
|---|---|---|---|---:|---:|
| `daily:cboe` | `SUCCESS` | 2026-09-02T11:29:29.127251+00:00 | 2026-09-02T11:29:29.454269+00:00 | 240 | 0 |
| `daily:fed` | `SUCCESS` | 2026-09-02T11:29:32.501071+00:00 | 2026-09-02T11:29:33.522969+00:00 | 853 | 2 |
| `daily:fred_indices` | `SUCCESS` | 2026-09-02T16:47:16.557376+00:00 | 2026-09-02T16:47:17.346484+00:00 | 753 | 0 |
| `daily:gpr` | `SUCCESS` | 2026-09-02T11:29:28.958777+00:00 | 2026-09-02T11:29:29.363227+00:00 | 108 | 0 |
| `daily:twelve_market` | `SUCCESS` | 2026-09-02T16:52:58.117621+00:00 | 2026-09-02T16:52:59.939554+00:00 | 1297 | 0 |
| `daily:xau` | `SUCCESS` | 2026-09-02T11:29:43.599893+00:00 | 2026-09-02T11:29:44.315074+00:00 | 121 | 3 |
| `hourly:xau` | `SUCCESS` | 2026-09-02T14:28:54.542350+00:00 | 2026-09-02T14:28:54.750068+00:00 | 1 | 1 |

## 4. Forecast-state database audit

This section is metadata-only and is included because Stage 2 depends on proving whether immutable forecast-state objects actually contain issued records.

| Object | Exists | Row count | Columns / temporal evidence |
|---|---|---:|---|
| `decision_events` | `True` | 0 | event_id, run_id, snapshot_id, event_ts, previous_classification, classification, classif… |
| `decision_runs` | `True` | 0 | run_id, decision_as_of, generated_at, engine_version, config_version, config_hash, code_s… |
| `decision_signal_snapshots` | `True` | 0 | snapshot_id, run_id, decision_as_of, target_month, close_value, close_source_ref, vw_fore… |
| `derived_feature_snapshots` | `True` | 1 | id, feature_name, feature_version, calculation_ts, input_cutoff, value_num, value_text, g… |
| `forecast_input_snapshots` | `True` | 0 | id, forecast_origin, target_period, model_name, model_version, git_commit, series_id, sem… |
| `monthly_forecast_contracts` | `True` | 0 | id, target_month, forecast_origin, model_name, model_version, forecast_value, unit, model… |

## 5. Quality and point-in-time status

- Quality ERROR events recorded in the append-only ledger: **38**.
- Quality WARNING events: **0**.
- Historical backfills retain the first-retrieval floor unless historical publication/vintage timing is independently reconstructed.
- `canonical_latest` and `usable_observations` are current-state surfaces only.
- Licensed/vendor raw display restrictions remain binding even when the series is healthy in Neon.

## 6. Stage 1 closure

**Decision:** `PASS_AUDIT_COMPLETE_WITH_OPERATIONAL_BLOCKERS`

Stage 1 is considered audit-complete because the required current inventory fields are now produced from an actual read-only Neon query. Operational source failures or lineage discrepancies remain explicit blockers; they do not invalidate the inventory itself and are not hidden by proxy substitution.

The next roadmap work is Stage 2 reconciliation of the forecast-state store, followed only then by Stage 3 decision-state persistence.
