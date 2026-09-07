# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.43  
**Issue date:** 2026-09-07  
**Repository:** `ataullahturgut/sim3-automation`  
**Canonical branch:** `gold-r4-direction-engine`  
**Default-branch scheduler:** `main`  
**Deployment mirror:** `gold-r4-direction-engine-ui-v122-final`  
**Project root:** `gold_axis_2026/`

---

## 1. Sole authority

This file is the only current Gold Control project manifest.

GitHub is the authority for current code, model contracts, reproducibility and this manifest. Production Neon is the authority for mutable source observations, point-in-time lineage, current runtime/context state and legitimately issued forecast/decision records.

Superseded implementation detail belongs in Git history or immutable audit storage, not in current application/runtime views. Historical rows may remain immutable; current views must hide superseded identities and stale contracts.

The application is read/presentation only. It may not silently choose a model, average experts, tune thresholds, substitute providers, backdate reconstructed evidence or manufacture an action.

**V1.43 adds a separate data-readiness authority:** an engine can be registered `ACTIVE` while its live input chain is stale. `ACTIVE` therefore proves current governed identity presence, not source freshness or successful live recomputation.

Binding data-readiness contract:

`GOLD_CONTROL_MODEL_DATA_READINESS_CONTRACT_V143_2026-09-07.md`

Read-only production auditor:

`tools/audit_model_data_readiness_v143.py`

---

## 2. Product definition

Gold Control is an auditable XAU/USD decision-support system, not an autonomous trading system.

The system has four separate responsibilities:

1. estimate the next calendar month's average XAU/USD level;
2. maintain strategic and tactical direction context at different time scales;
3. detect intramonth shock, reversal, event and regime conditions;
4. expose volatility/risk context and immutable evidence provenance.

A price forecast is not a tactical direction signal. A risk/regime context is not a price forecast. No single context is an automatic position instruction.

---

## 3. Current governed architecture

`Monthly H=1 expert layer`

→ `Monthly Direction / Prior`

→ `FAST tactical context`

→ `SLOW tactical context`

→ `Macro Event context`

→ `BOCPD regime/break context`

→ `Emergency Level / Reversal`

→ `GVZ risk context`

→ `Decision-support presentation`

Current governed identities are exactly:

### Monthly H=1 price experts
- `CAUSAL_PATCH`
- `VW_MIDAS_MSVR_SUCCESSOR_V1`
- `MOMENTUM_3M`
- `RANDOM_WALK`

### Direction / event / regime / emergency / risk contexts
- `MONTHLY_DIRECTION_3M`
- `FAST`
- `SLOW`
- `MACRO_EVENT_SUCCESSOR_V2`
- `BOCPD_RETURN_SUCCESSOR_V1`
- `EMERGENCY_LEVEL`
- `EMERGENCY_REVERSAL`
- `GVZ_RISK`

No other identity belongs to the current governed runtime inventory.

---

## 4. Governance locks

The following remain binding:

- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`
- `NOT_PROVEN_EXPERT_SELECTION_RULE`
- `NOT_PROVEN_POSITION_MAPPING`
- no automatic `BUY / SELL / HOLD / EXIT / REDUCE`
- no hindsight threshold tuning
- no random-split time-series validation
- no silent provider substitution
- no interpolation or forward-fill of a missing canonical XAU session reference
- no backdating of reconstruction/replay evidence
- no mutation of immutable historical forecast/runtime evidence
- no production forecast/decision authority write without explicit later manifest authorization
- no relabelling of a stale derived context as live-fresh merely because its runtime identity is `ACTIVE`

Expert disagreement is displayed; it is not silently resolved.

---

## 5. Monthly origin and evidence contract

For target calendar month `M`, the H=1 origin is the completed month-end boundary immediately before `M`.

`origin(M) = completed month-end boundary of M-1`

The target is the next calendar month's average XAU/USD price.

Current September 2026 information boundary:

`2026-08-31T21:00:00Z` = 31 Aug 2026 17:00 ET.

A month-open snapshot is immutable. Later intramonth observations may update tactical, emergency, event and risk context, but may not rewrite the month-open snapshot.

Evidence classes remain explicit:

- `HISTORICAL_REPLAY`: reconstructed later from a frozen historical information boundary;
- `PROSPECTIVE_SHADOW`: issued at a real future origin before target realization;
- `LIVE_PRODUCTION`: only when separately authorized and legitimately issued.

Reconstruction may never be relabelled as prospective evidence.

Time-series evaluation and tuning remain forecasting-origin / point-in-time safe: observations or revisions not available at an origin may not enter that origin's training, tuning or forecast input set.

---

## 6. September 2026 current references and freshness interpretation

The following values were reconstructed from the completed 31-Aug information boundary. They are current September references, but not backdated prospective issuance evidence.

| Identity | Current September reference | Semantics | V1.43 interpretation |
|---|---:|---|---|
| `VW_MIDAS_MSVR_SUCCESSOR_V1` | `4565.115907930242 USD/oz` | H=1 price reference | frozen Aug-31 replay reference; do not refresh from September data |
| `CAUSAL_PATCH` | `4452.046728838838 USD/oz` | H=1 price reference | frozen Aug-31 replay reference; do not refresh from September data |
| `MOMENTUM_3M` | `4345.814584037808 USD/oz` | H=1 price reference | source-bound R2 historical replay; do not refresh from September data |
| `RANDOM_WALK` | `4397.305673870967 USD/oz` | H=1 benchmark | source-bound R2 historical replay; do not refresh from September data |
| `MONTHLY_DIRECTION_3M` | `DOWN` | strategic monthly context | month-origin context; not a live daily freshness claim |
| `FAST` | `ROBUST_UP` | tactical short-horizon context | current persisted value may be stale until V1.43 readiness passes |
| `SLOW` | `ROBUST_UP` | tactical slower context | current persisted value may be stale until V1.43 readiness passes |
| `MACRO_EVENT_SUCCESSOR_V2` | `MACRO_MIXED_OR_SMALL` | intramonth event-risk context | release/PIT semantics remain separate |
| `BOCPD_RETURN_SUCCESSOR_V1` | `NO_ADVERSE_BREAK_CANDIDATE` | regime/break context | current context, not a price/direction forecast |
| `EMERGENCY_LEVEL` | `NEUTRAL` | month-open emergency state | replay month-open state; not live-fresh after target-month observations arrive |
| `EMERGENCY_REVERSAL` | `OFF` | month-open emergency state | replay month-open state; not live-fresh after target-month observations arrive |
| `GVZ_RISK` | current persisted risk context | risk only | current persisted value may be stale until latest eligible GVZ is consumed |

The four H=1 expert values must not be averaged, weighted or winner-selected while the selector lock remains in force.

30 Sep 2026 is a later eligible prospective validation origin for October; it does not block the September reference.

**Production audit finding on 7 Sep 2026:** the governed inventory is complete, but the intramonth data path is not yet entitled to a global `READY` claim. During the audit, canonical `XAU_EOD_TWELVE_NY17` was at trade date 2026-09-03 while the approved independent daily XAU cross-check had 2026-09-04; FAST/SLOW and GVZ derived contexts predated newer eligible source availability; Emergency still carried a month-open no-September-EOD reason despite accepted September XAU observations. These are freshness/readiness blockers, not reasons to rewrite the frozen H=1 monthly references.

---

## 7. Motor semantics and governed model input binding

### `VW_MIDAS_MSVR_SUCCESSOR_V1`
Current VW/MSVR model identity. Frozen 8-feature four-metal MSVR with origin-local GPR point-in-time input. Historical replay window is 2023-01..2026-07, N=43. Historical replay MAPE is `2.69106498%` versus Random Walk `3.30232202%`. Historical replay performance is evidence, not proof of future superiority.

Historical replay input availability does not establish prospective runtime readiness. The four-metal prospective source refresh, GPR vintage/publication-lag rule and XAU target-anchor bridge remain separate gates. A replay reference may not be promoted to prospective merely because the model code is reproducible.

### `CAUSAL_PATCH`
Current monthly H=1 expert. Completed-session/PIT safeguards remain part of its executable identity. No selector or action authority. Historical replay and a legitimately persisted prospective Patch expert are separate evidence classes.

### `MOMENTUM_3M`
Current monthly H=1 expert. Distinct from `MONTHLY_DIRECTION_3M`.

Current source-bound identity:

`MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND`

Its persisted September replay input set is restricted to:

`SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2`

No target-month observation may enter the September H=1 input set.

### `RANDOM_WALK`
Mandatory same-origin naive benchmark.

Current source-bound identity:

`RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND`

Its persisted September replay input set is restricted to:

`SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2`

### `MONTHLY_DIRECTION_3M`
Strategic monthly direction/prior context; not an H=1 price forecast. It is origin-frozen for the target month and is not refreshed merely because new target-month daily bars arrive.

### `FAST`
Short-horizon tactical context from completed daily XAU observations and frozen SMA20/persistence logic. Governed daily XAU input is `XAU_EOD_TWELVE_NY17`. A FAST value whose input cutoff precedes a newer eligible canonical XAU availability is `STALE_RELATIVE_TO_SOURCE`, even if its runtime identity is ACTIVE.

### `SLOW`
Slower tactical confirmation context from completed weekly observations and frozen SMA4/persistence logic. Governed underlying input is `XAU_EOD_TWELVE_NY17`. Incomplete weeks may not be treated as completed weeks. Source freshness and completed-week semantics are separate checks.

### `MACRO_EVENT_SUCCESSOR_V2`
Timestamp-safe labor-event risk/context. Intramonth event information may not be inserted retroactively into the month-open snapshot. Scheduled/revision-prone macro inputs are freshness-checked by release/availability/vintage semantics, not by observation date alone.

### `BOCPD_RETURN_SUCCESSOR_V1`
Regime/break context only. No H=1 price forecast, no direction vote, no automatic action.

### `EMERGENCY_LEVEL`
Intramonth abnormal-level detector evaluated from accepted completed target-month observations against an explicitly permitted frozen monthly reference.

A month-open `NO_*OBSERVATION` state becomes stale after the first eligible target-month canonical XAU observation exists. It must not be silently reused as a live state.

### `EMERGENCY_REVERSAL`
Intramonth peak/trough reversal detector. Alert/context only. Same stale month-open rule as `EMERGENCY_LEVEL`.

The existing Patch Emergency bridge requires an eligible persisted Patch expert reference with the permitted prospective evidence class before a live Emergency reference is claimed. A September historical-replay Patch reference is not silently upgraded to that class.

### `GVZ_RISK`
Volatility/risk context only. It never predicts gold direction. A GVZ-derived context is stale when its input cutoff precedes the latest eligible `GVZ_CBOE` availability.

---

## 8. Current source surface and data-ingestion contract

The current database source surface is `current_source_registry_v1`.

It must include only:

- observation-backed source identities that are not `BLOCKED`, `OPTIONAL` or `PAID`-required placeholders; and
- explicitly approved non-persisted live display identity `XAU_SPOT_GOLDAPI`.

The raw `source_registry` remains historical/audit storage and is not itself a current surface.

### Canonical tactical XAU source

Current operational completed-daily XAU decision reference:

`XAU_EOD_TWELVE_NY17`

Semantics: Twelve Data `XAU/USD`, intraday `1min`, `America/New_York`; unique exact 16:59 bar close is stored at the 17:00 ET session boundary. CME/EBS regular hours are authority for the 17:00 ET trade-date-roll convention; the Twelve Data value remains an **internal NY17 decision reference**, not an official CME/EBS settlement or fixing.

Required rules:

- exact unique `16:59:00` source bar only;
- positive/range-valid OHLC;
- no interpolation;
- no forward fill;
- no silent fallback or provider substitution;
- no official-settlement claim;
- vendor raw data remains private unless rights are separately approved;
- production ingestion performs bounded recent exact-bar reconciliation so a previously missed recent date can be recovered later if the provider supplies the exact validated bar;
- provider `404 / data not found` may be retained as a no-bar date; authentication, permission, rate-limit, parameter and server failures remain fail-closed;
- a newer accepted `XAU_DAILY_XAUS` cross-check date than canonical NY17 means the tactical data plane is not ready until reconciled or explicitly adjudicated. The cross-check never becomes silent model authority.

### Macro/revision-prone sources

Wall-clock age is not used as a universal freshness test.

- completed-session market data are assessed against eligible completed sessions;
- scheduled macro data are assessed against release/availability timestamps;
- revision-prone macro replay uses point-in-time vintage evidence where available (for example ALFRED/FRED real-time periods) and never injects current revisions into historical origins;
- monthly GPR continues to obey its frozen publication-lag/vintage rule.

Research-only source identities may remain visible through the current source surface when they are observation-backed and required for reproducibility. Blocked/license placeholders and empty future candidates are not current.

---

## 9. Current runtime, context selection and data readiness

### Runtime inventory

The application/runtime authority view is `current_engine_runtime_state_v1`.

It must select the **latest complete target context containing all 12 governed engine identities**, then select the latest row for each engine inside that target context.

Selection rule:

`LATEST_COMPLETE_12_ENGINE_TARGET_CONTEXT`

Expected current inventory state:

- `ACTIVE = 12`
- `WAITING = 0`
- `BLOCKED = 0`
- total = `12`

This prevents a partially-created future month from replacing the current complete production context.

**This inventory state is not a freshness certificate.**

### Context-feature inventory

The current derived-context view is `current_context_feature_state_v1`.

It must select the **latest complete target context containing all 7 governed context features**:

- `MONTHLY_DIRECTION_3M`
- `FAST_STATE`
- `SLOW_STATE`
- `GVZ_VALUE`
- `GVZ_CAP`
- `GVZ_PANIC`
- `GVZ_REGIME`

Selection rule:

`LATEST_COMPLETE_7_FEATURE_TARGET_CONTEXT`

This prevents September + October rows from being simultaneously exposed as current during rollover and prevents a partial future context from taking authority.

### V1.43 model-data readiness

Four states are now distinct:

- `CURRENT_SURFACE_REGISTERED`
- `MONTHLY_REFERENCE_VALID`
- `INTRAMONTH_DATA_READY`
- `OPERATIONAL_MODEL_DATA_READY`

The read-only readiness workflow is:

`.github/workflows/gold-control-model-data-readiness-v143.yml`

A stale intramonth context must fail the readiness audit while preserving the current/historical evidence row. The audit never repairs data by writing a forecast, decision or authority row.

---

## 10. Provenance and point-in-time rule

Current views must not invent missing input fingerprints.

When a governed runtime row has no `input_fingerprint`, current metadata must expose:

`REFERENCE_METADATA_BOUND_INPUT_FINGERPRINT_NOT_AVAILABLE`

When present, it must expose:

`INPUT_FINGERPRINT_PRESENT`

Missing provenance is reported, not fabricated.

For an output to be described as current/fresh, its lineage must be traceable directly or through immutable input sets to the relevant source identity, observation timestamp, `available_as_of`, `retrieved_at`, quality status, lineage/snapshot member IDs, input fingerprint, model/feature version, Git commit and target/origin semantics.

For historical replay, each selected input must satisfy the frozen origin's point-in-time availability rule. Future target observations and later revisions are forbidden.

---

## 11. Application and snapshot contract

The current application reads only:

- `current_engine_runtime_state_v1`;
- `current_context_feature_state_v1`;
- `current_source_registry_v1` for current-source audit/health;
- current market display data;
- canonical forecast/decision stores only if later legitimately populated.

The committed fallback snapshot contract is:

`GOLD_CONTROL_CURRENT_PRODUCTION_DISPLAY_SNAPSHOT_V142`

The current surface contract is:

`GOLD_CONTROL_CURRENT_SURFACE_V142`

A valid V142 snapshot proves inventory and authority-lock consistency:

- exact 12 governed engines, all ACTIVE;
- one common complete target context;
- exact 7 current context features from the same target context;
- zero blocked/optional/paid rows in the current source surface;
- zero unauthorized forecast/decision authority rows;
- no forbidden action/selector payload.

**It does not by itself prove source freshness or live recomputation.** V1.43 model-data readiness is an additional required operational gate.

---

## 12. Scheduling authority

GitHub scheduled workflows run from the repository default branch. Therefore:

- `main` is the **default-branch scheduling surface**;
- canonical implementation remains `gold-r4-direction-engine`;
- scheduled jobs on `main` call reusable workflows pinned to `gold-r4-direction-engine`;
- reusable canonical writer/refresh workflows must not own independent `schedule:` triggers;
- snapshot refresh must be dispatched by the default-branch scheduler, not rely on a non-default-branch cron;
- model-data readiness is a read-only lane and must run after source-ingestion windows often enough to detect stale production context;
- a failing readiness lane must not be bypassed by relabelling an old context current.

This separation is operational only; `main` does not become model/code authority.

---

## 13. Deployment mirror

`gold-r4-direction-engine-ui-v122-final` is a deployment mirror only.

After a governed canonical release passes current-surface and application smoke tests, the deployment mirror must point to the exact canonical release HEAD. It must not carry independent model, manifest or runtime semantics.

---

## 14. V1.43 model-data gate

V1.43 preserves the clean current surface and adds an independent operational-readiness gate.

Required invariant set:

1. `current_source_registry_v1` contains no blocked/optional/paid placeholder and no empty source except the explicit non-persisted live display source;
2. `current_engine_runtime_state_v1` exposes exactly one latest complete 12-engine target context;
3. `current_context_feature_state_v1` exposes exactly one latest complete 7-feature target context;
4. current runtime inventory is `12 ACTIVE / 0 WAITING / 0 BLOCKED`;
5. missing fingerprints are reported, never synthesized;
6. production authority stores remain `0/0/0/0` unless later explicitly authorized;
7. current V142 snapshot continues to validate inventory/authority locks;
8. canonical app smoke passes against production current views;
9. default-branch scheduler owns cron and dispatches reusable canonical workflows;
10. deployment mirror equals the intended canonical release HEAD when deployed;
11. canonical NY17 XAU is not behind an accepted later daily XAU cross-check, or the discrepancy is explicitly adjudicated without silent substitution;
12. FAST/SLOW lineage is `XAU_EOD_TWELVE_NY17` and their input cutoffs are not stale relative to the latest eligible canonical XAU availability;
13. GVZ-derived context is not stale relative to the latest eligible `GVZ_CBOE` availability;
14. Emergency no-observation month-open placeholders are not described as live after target-month XAU exists;
15. September H=1 references remain frozen to the Aug-31 origin and retain `HISTORICAL_REPLAY`, `prospective_claim=false`, `canonical_authority=false`, selector OFF and ensemble OFF;
16. current RW/Momentum identities and immutable September input sets remain source-bound R2 with no post-origin input;
17. historical VW replay and prospective VW readiness remain separate; no prospective claim is issued until its prospective input gates pass.

Until checks 11–17 pass, the correct statement is:

`CURRENT_SURFACE_REGISTERED = TRUE`

but

`OPERATIONAL_MODEL_DATA_READY = FALSE`

for the affected live intramonth path.

The next governed implementation target is the **append-only live intramonth recomputation chain** with replay-equivalence, idempotency, explicit lineage and fail-closed tests:

`canonical XAU / eligible risk-event sources → FAST/SLOW → permitted Emergency bridge → GVZ / regime-event contexts → current presentation`

No decision/forecast authority write is authorized by this manifest merely to complete that chain.
