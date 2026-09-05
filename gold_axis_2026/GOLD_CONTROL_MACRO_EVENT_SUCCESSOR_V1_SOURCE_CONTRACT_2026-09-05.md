# Gold Control — Macro Event Successor V1 Source Contract

**Date:** 2026-09-05  
**Status:** PRE_SCORE_SOURCE_CONTRACT  
**Engine identity:** `MACRO_EVENT_SUCCESSOR_V1`  
**Parent context:** canonical `gold-r4-direction-engine` at `54ecda1eb7643aac6b7c114be7b3c61b468bc8e1`

## 1. Governance locks

- The archived `MACRO_EVENT` identity remains blocked and is not relabelled.
- This document creates a new successor identity only.
- No model score, threshold tuning, selector, ensemble, position mapping, or Decision Store authority is created here.
- No post-result formula tuning is allowed.
- Historical reconstruction must remain distinct from prospective issuance.
- `monthly_forecast_contracts`, `decision_signal_snapshots`, `decision_runs`, and `decision_events` must not be written by source-ingestion or source-audit jobs.

## 2. Functional objective

`MACRO_EVENT_SUCCESSOR_V1` is an event-context engine for U.S. Employment Situation releases. It is not a standalone monthly XAU/USD price forecaster and does not inherit the archived R4.1 macro-score formula.

Initial indicators in scope:

1. Nonfarm Payrolls (headline payroll employment change),
2. Unemployment Rate,
3. Average Hourly Earnings (AHE).

## 3. Source authority hierarchy

### 3.1 Actual / official release

Primary authority: U.S. Bureau of Labor Statistics (BLS), Employment Situation / BLS Public Data.

The contract must preserve:

- release event identity,
- reference month,
- published actual,
- official release timestamp / availability time,
- whether the value is first-print or revised.

### 3.2 Revision / historical point-in-time cross-check

ALFRED/FRED real-time-period data may be used where the exact series identity supports the required first-release reconstruction. The point-in-time view must be queried with historical real-time bounds; current-vintage values must never be backfilled as if they were known at the historical event time.

### 3.3 Consensus / market expectation

Preferred authority: Bloomberg median consensus when licensed historical point-in-time access is available.

Candidate fallback for research audit: Trading Economics Economic Calendar Point-in-Time.

The fallback is **not approved for model use** until an empirical audit proves that, for the chosen event identity and sample window:

- `Forecast` is the pre-release consensus available before the event,
- timestamps are chronologically valid,
- later revisions do not overwrite the historical forecast state,
- event/reference-month mapping is stable,
- actual/previous/revised fields can be distinguished.

Until that audit passes, consensus source status is `PENDING_PIT_CONSENSUS_AUDIT`.

## 4. Database architecture

The source pipeline must use the existing production data-plane tables rather than embedding external values in model code.

### 4.1 `source_registry`

Register one semantic series identity per governed field/provider. Candidate identities include:

- `MACRO_NFP_ACTUAL_FIRST_PRINT`
- `MACRO_UNEMP_ACTUAL_FIRST_PRINT`
- `MACRO_AHE_ACTUAL_FIRST_PRINT`
- `MACRO_NFP_CONSENSUS_PIT`
- `MACRO_UNEMP_CONSENSUS_PIT`
- `MACRO_AHE_CONSENSUS_PIT`

Consensus identities remain research-only until source audit approval.

### 4.2 `retrieval_runs`

Every ingestion/audit execution receives a unique `run_id`, code SHA, pipeline version, status, and observation counts.

### 4.3 `source_vintages`

When provider payload snapshots are available, persist content hash, provider-as-of, retrieval time, content type, and metadata. Never overwrite a prior vintage.

### 4.4 `observations`

Persist normalized point-in-time records with:

- `series_id`,
- `observation_ts`,
- `value`,
- `source`,
- `source_symbol`,
- `provider_as_of`,
- `available_as_of`,
- `first_seen_at`,
- `retrieved_at`,
- `frequency`,
- `unit`,
- `transform`,
- `quality_status`,
- `lineage_id`,
- `payload_hash`,
- metadata containing release/reference/event identifiers.

The model must read these governed database records. It must not make an unlogged live web/API call during scoring.

## 5. Point-in-time rule

For a historical event at time `t`, an input is eligible only if `available_as_of <= t` under its approved source contract.

Current-vintage data must never be substituted for historical first-print values. Consensus must be the last approved pre-release snapshot, never a post-release update.

## 6. Development sequence

1. Verify exact BLS indicator/event identities and release timestamps.
2. Audit structured first-print/vintage coverage.
3. Audit the historical consensus candidate against pre-release chronology.
4. Only after source coverage passes, freeze the surprise transformation and development/validation windows.
5. Implement deterministic database ingestion.
6. Implement database-only model input loader.
7. Run prefix/future-invariance and leakage tests.
8. Run untouched validation under a separately frozen scoring contract.
9. Only after validation may runtime promotion be considered.

## 7. Current decision

- Archived `MACRO_EVENT`: unchanged / blocked.
- `MACRO_EVENT_SUCCESSOR_V1`: `SOURCE_CONTRACT_OPEN_PIT_CONSENSUS_AUDIT_PENDING`.
- Production authority: `FALSE`.
- Direction vote: `FALSE`.
- Decision Store writes: `NONE`.
