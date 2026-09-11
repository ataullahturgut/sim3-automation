# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.49
**Issue date:** 2026-09-11
**Repository:** `ataullahturgut/sim3-automation`  
**Canonical branch:** `gold-r4-direction-engine`  
**Default-branch scheduler:** `main`  
**Deployment mirror:** `gold-r4-direction-engine-ui-v122-final`  
**Project root:** `gold_axis_2026/`

---

## 1. Sole authority

This file is the only current Gold Control project manifest.

**Single-manifest rule:** `gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md` is the sole project-level authority for Gold Control forecasting, direction, risk, validation, readiness and future research governance. No second Gold Control project manifest may be created. Files whose names contain `manifest`, including run manifests, validation manifests or historical artifacts, are subordinate evidence artifacts only and are never competing project authority. Handover documents, checkpoints, contracts, preregistrations, design notes, reports and audit outputs are also subordinate to this file. If any subordinate artifact conflicts with this manifest, the copy of this file at the current canonical `gold-r4-direction-engine` HEAD wins.

Every new ChatGPT/Work/Codex Gold Control session must first re-read the current canonical branch HEAD and this exact manifest path/version before interpreting a handover, checkpoint, audit artifact or historical run manifest. A cached, copied or older manifest is not current authority.

GitHub is the authority for current code, frozen model/feature contracts, reproducibility and this manifest. Production Neon is the authority for mutable source observations, point-in-time lineage, append-only current runtime/context state and legitimately issued forecast/decision records.

Historical implementation detail belongs in Git history or immutable audit storage, not in current application/runtime views. Current views may summarize historical evidence but may not rewrite or destroy it.

Gold Control is a decision-support system, not an autonomous trading system. The application may not silently choose a model, average experts, tune thresholds, substitute providers, backdate evidence or manufacture an action.

Referenced current data/readiness contracts are subordinate implementation contracts and are binding only to the extent that they are consistent with this sole manifest:

- `GOLD_CONTROL_MODEL_DATA_READINESS_CONTRACT_V143_2026-09-07.md`
- `GOLD_CONTROL_LIVE_INTRAMONTH_RECOMPUTE_CONTRACT_V144_2026-09-07.md`
- `GOLD_CONTROL_HISTORICAL_PILOT_READINESS_CONTRACT_V145_2026-09-08.md`

Binding current operational implementations:

- canonical XAU reconciliation: `data_pipeline/twelve_xau_ny17.py`
- live intramonth append-only recompute: `data_pipeline/live_intramonth_recompute_v144.py`
- read-only current/live model-data readiness audit: `tools/audit_model_data_readiness_v143.py`
- strict post-write intramonth audit: `tools/audit_live_intramonth_postwrite_v144.py`
- `tools/audit_historical_pilot_readiness_v145.py`

The V1.45 historical-pilot auditor is implemented and test-proven read-only under the binding frozen contract. Its frozen baseline and gap evidence are preserved under `data_pipeline/audits/`. This implementation does not score performance and has no production-write authority.

`ACTIVE` means a governed identity is present on the current runtime surface. It is **not** by itself a source-freshness, historical-pilot-readiness or successful-recomputation certificate.

---

## 2. Governed architecture

The current architecture is:

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

The 12 governed identities are **not** a single homogeneous model-selection pool. They occupy different functional roles. Historical validation must therefore be role-specific and may not rank all 12 identities under one common forecasting metric.

V1.49 adds a research programme for improving monthly and short-horizon predictive power. That research programme does not itself add a thirteenth governed runtime identity, activate a selector/ensemble, or change production authority. A new research model or integration rule becomes runtime-governed only after separate evidence-based promotion and a later manifest version.

---

## 3. Governance locks

The following remain binding:

- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`
- `NOT_PROVEN_EXPERT_SELECTION_RULE`
- `NOT_PROVEN_POSITION_MAPPING`
- no automatic `BUY / SELL / HOLD / EXIT / REDUCE`
- no hindsight threshold tuning
- no random-split time-series validation
- no silent provider substitution
- no interpolation or forward-fill of missing canonical XAU session references
- no backdating of reconstruction/replay evidence
- no mutation of immutable historical forecast/runtime evidence
- no production forecast/decision authority write without explicit later authorization
- no stale derived context may be labelled fresh merely because the engine is `ACTIVE`
- no target-month observation may be inserted into a frozen target-month H=1 forecast after its origin
- no 2026 retrospective result may be used to alter architecture, features, thresholds, hyperparameters, source identity, model identity or validation rule inside the frozen pilot
- no historical reconstruction may be relabelled as prospective evidence
- no pilot-time deletion of a governed engine solely because one standalone performance metric is weak

Expert disagreement is displayed; it is not silently resolved.

Any post-pilot change to a governed engine, source, threshold, feature, hyperparameter, role or evaluation rule requires explicit versioned change control. That change control may be recorded directly in a new section of this sole manifest and may use subordinate implementation/evidence artifacts, but no subordinate file may become a second project manifest or supersede this file. The frozen pilot may not be rewritten.

---

## 4. Evidence and point-in-time semantics

Evidence classes are separate:

- `HISTORICAL_REPLAY`: reconstructed after the original origin from information bounded to that historical origin;
- `PROSPECTIVE_SHADOW`: issued after the governed mechanism is deployed and before the relevant future outcome is known;
- `LIVE_PRODUCTION`: only when separately authorized.

Current runtime inventory rows may use the governance wrapper class `RUNTIME_GOVERNANCE_AUDIT`; detailed context/reference evidence remains explicit in metadata. This wrapper does not convert a historical H=1 reference into prospective evidence.

For any historical forecast origin, every input must satisfy the point-in-time availability rule for that origin. Later target observations and later revisions are forbidden.

For reconstructed market histories whose raw values are retrieved after the original historical origin, the retrieval timestamp may not be falsified or backdated. Such rows may support `HISTORICAL_REPLAY` only when the governed source contract permits historical reconstruction and the replay procedure proves that no target/future information entered feature construction, parameter selection or scoring.

For current intramonth context, the relevant completed source observations may be consumed as they become available because FAST/SLOW/Emergency/GVZ are monitoring layers rather than the frozen H=1 monthly forecast.

---

## 5. Current September 2026 H=1 origin and frozen references

Target month: `2026-09`  
Frozen information boundary: `2026-08-31T21:00:00Z` = 31 Aug 2026 17:00 ET.

Current September H=1 reconstruction references:

| Identity | September reference | Evidence / role |
|---|---:|---|
| `VW_MIDAS_MSVR_SUCCESSOR_V1` | `4565.115907930242 USD/oz` | H=1 historical-origin reconstruction |
| `CAUSAL_PATCH` | `4452.046728838838 USD/oz` | H=1 historical-origin reconstruction |
| `MOMENTUM_3M` | `4345.814584037808 USD/oz` | source-bound R2 historical replay |
| `RANDOM_WALK` | `4397.305673870967 USD/oz` | mandatory source-bound R2 benchmark |

These values are frozen for September. September observations do not trigger their recomputation.

30 Sep 2026 is a later eligible prospective validation origin for October. It does not block the September references.

No selector/ensemble is authorized among the four experts.

---

## 6. Source-to-model binding

### `VW_MIDAS_MSVR_SUCCESSOR_V1`
Frozen four-metal MSVR with origin-local GPR PIT input. Historical replay success does not by itself prove prospective source readiness. Prospective four-metal inputs, GPR publication/vintage rule and target-anchor inputs remain separate gates.

### `CAUSAL_PATCH`
Frozen monthly H=1 expert. Completed-session/PIT safeguards remain part of the identity. Historical-replay and legitimately prospective Patch evidence remain distinct.

### `MOMENTUM_3M`
Current identity: `MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND`.

September persisted input set is restricted to `SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2`; target-month observations are forbidden.

### `RANDOM_WALK`
Current identity: `RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND`.

September persisted input set is restricted to the same governed R2 monthly-mean series and is origin-bounded.

### `MONTHLY_DIRECTION_3M`
Strategic monthly direction/prior. It is frozen at the target-month origin and is not a daily-refresh component.

### `FAST`
Source: `XAU_EOD_TWELVE_NY17` only.  
Rule: frozen R4.1 SMA20 + two completed-trade-date persistence rule.  
Freshness: latest FAST input must consume the newest eligible canonical XAU available to the current monitoring run.

### `SLOW`
Underlying source: `XAU_EOD_TWELVE_NY17` only.  
Rule: frozen R4.1 completed weekly close / SMA4 + two completed-week persistence rule.  
Incomplete weeks are excluded.

### `EMERGENCY_LEVEL` / `EMERGENCY_REVERSAL`
XAU source: accepted completed target-month `XAU_EOD_TWELVE_NY17` observations. The state is replayed chronologically from the beginning of the target month at each refresh so peak/trough memory is deterministic and recoverable.

The monthly reference remains explicit and immutable for the target month. For September 2026 the current Causal Patch reference is `HISTORICAL_REPLAY`; therefore the recomputed Emergency state may be described as **current-input / historical-reference context**, but it may not be relabelled as a prospective September forecast or prospective monthly reference.

### `GVZ_RISK`
Source: `GVZ_CBOE` only. Frozen R4.1 thresholds remain binding. It is risk context only and never predicts gold direction.

### `BOCPD_RETURN_SUCCESSOR_V1`
Regime/break context only; no price forecast, no direction vote, no automatic action.

### `MACRO_EVENT_SUCCESSOR_V2`
Release-aware event-risk context. Release timestamps and vintage semantics govern availability; revised macro values may not be inserted backward into earlier origins.

---

## 7. Canonical XAU ingestion contract

Canonical tactical XAU series:

`XAU_EOD_TWELVE_NY17`

Provider/input contract:

- provider: Twelve Data;
- symbol: `XAU/USD`;
- interval: `1min`;
- requested timezone: `America/New_York`;
- accepted bar: unique exact `16:59:00` source bar;
- accepted value: bar `close` after positive/range-valid OHLC checks;
- stored timestamp: corresponding `17:00 ET` session boundary converted to UTC;
- fallback: none;
- interpolation: forbidden;
- forward-fill: forbidden;
- silent provider substitution: forbidden;
- official CME/EBS settlement/fixing claim: forbidden.

CME/EBS regular-hours convention supplies the 17:00 ET trade-date-roll basis. The Twelve Data value is Gold Control's internal NY17 reference, not an official CME price.

### 7.1 Recent operational gap recovery

The production collector must perform bounded recent exact-bar reconciliation. It may recover a recent previously missed trade date only when Twelve Data later supplies the exact valid 16:59 bar.

Provider `404 / data not found` is treated as a no-bar result for that exact-date query. Authentication, permission, rate-limit, invalid-parameter, malformed-bar and server failures remain fail-closed.

`XAU_DAILY_XAUS` is an independent operational cross-check only. If its accepted trade date is newer than canonical NY17, intramonth recomputation is blocked until canonical NY17 catches up or the discrepancy is explicitly adjudicated. The cross-check never becomes silent model authority.

### 7.2 Historical NY17 reconstruction for GOLD_PILOT_V1

Historical pilot reconstruction is a separate governed lane from recent operational gap recovery.

Purpose: provide origin-safe historical NY17 observations needed to evaluate `MONTHLY_DIRECTION_3M`, `FAST`, `SLOW`, `EMERGENCY_LEVEL` and `EMERGENCY_REVERSAL` over the frozen pilot window.

Rules:

- source identity must remain Twelve Data `XAU/USD`;
- interval must remain `1min`;
- timezone must remain `America/New_York`;
- only the exact unique `16:59:00` bar may qualify;
- no 5-minute, hourly, daily or alternate-provider substitution is permitted for this lane;
- no interpolation, forward-fill or synthetic bar construction is permitted;
- retrieval timestamps must remain truthful and may not be backdated to the historical observation date;
- reconstructed rows are `HISTORICAL_REPLAY` evidence only and never become prospective proof merely because the observation date is historical;
- session eligibility must be adjudicated from provider evidence; weekday counting alone is insufficient;
- exact-date provider `404 / data not found` may establish `PROVIDER_NO_BAR` for that date; entitlement/auth/rate-limit/request failures remain separate blockers;
- historical reconstruction must not mutate legitimately issued prospective/runtime evidence;
- storage must be append-only or immutable-artifact based, with explicit source, retrieval, quality, lineage and fingerprint metadata;
- current production canonical semantics may not be silently rewritten to pretend reconstructed rows were available at the original historical origin.

Historical pilot readiness is established by the binding `GOLD_CONTROL_HISTORICAL_PILOT_READINESS_CONTRACT_V145_2026-09-08.md` plus its separately reviewed/frozen read-only auditor; it is not established by the V1.43 current/live readiness audit.

---

## 8. Append-only live intramonth recomputation — V1.44

Binding writer:

`data_pipeline/live_intramonth_recompute_v144.py`

The writer may append only:

- `FAST_STATE`
- `SLOW_STATE`
- `GVZ_VALUE`
- `GVZ_CAP`
- `GVZ_PANIC`
- `GVZ_REGIME`
- current runtime/context rows for `FAST`, `SLOW`, `GVZ_RISK`, `EMERGENCY_LEVEL`, `EMERGENCY_REVERSAL`

It may not write or mutate:

- monthly H=1 forecasts;
- `monthly_forecast_contracts`;
- `decision_signal_snapshots`;
- `decision_runs`;
- `decision_events`;
- selector/ensemble weights;
- position/action instructions.

Any failed prerequisite causes zero context writes.

### Idempotency

Each logical output receives a SHA-256 fingerprint over the exact governed inputs and contract version. A new append-only row is inserted only when that component's latest target-context fingerprint changes. Re-running identical inputs must therefore create no duplicate logical state.

### Provenance

Persisted context must record or carry:

- source series identity;
- selected source observation ID(s)/timestamps;
- `available_as_of` input cutoff;
- lineage IDs;
- input fingerprint;
- feature/model version;
- Git commit;
- target context;
- context issuance mode;
- `prospective_h1_claim=false`;
- `canonical_forecast_authority=false`;
- `AUTO_SELECTOR=OFF`;
- `AUTO_ENSEMBLE=OFF`;
- `decision_store_write=NONE`.

### Catch-up vs prospective-shadow

`catchup` is used when source observations were already available before deployment of this writer. It is historical/reconstruction context and is never relabelled prospective.

`prospective-shadow` is used only for later observations first consumed by the deployed scheduled writer. FAST/SLOW/GVZ may receive prospective-shadow context evidence. Emergency remains limited by the evidence class of its monthly reference.

---

## 9. Runtime and current-context selection

`current_engine_runtime_state_v1` must expose the latest complete target context containing all 12 governed engine identities.

Selection rule:

`LATEST_COMPLETE_12_ENGINE_TARGET_CONTEXT`

Expected inventory:

- 12 total
- 12 ACTIVE
- 0 WAITING
- 0 BLOCKED

This is inventory state, not a freshness or historical-pilot-readiness certificate.

`current_context_feature_state_v1` must expose the latest complete target context containing exactly:

- `MONTHLY_DIRECTION_3M`
- `FAST_STATE`
- `SLOW_STATE`
- `GVZ_VALUE`
- `GVZ_CAP`
- `GVZ_PANIC`
- `GVZ_REGIME`

Selection rule:

`LATEST_COMPLETE_7_FEATURE_TARGET_CONTEXT`

A partial future month may not displace the latest complete current context.

---

## 10. Readiness states and acceptance audits

Current/live readiness and historical-pilot readiness are separate governance dimensions.

### 10.1 Current/live readiness

The following remain distinct:

- `CURRENT_SURFACE_REGISTERED`
- `MONTHLY_REFERENCE_VALID`
- `INTRAMONTH_DATA_READY`
- `OPERATIONAL_MODEL_DATA_READY`

Current/live readiness audit:

`tools/audit_model_data_readiness_v143.py`

Strict V1.44 post-write audit:

`tools/audit_live_intramonth_postwrite_v144.py`

A V1.44 intramonth refresh is accepted only if both audits pass and authority stores remain zero.

The strict post-write audit must prove at least:

- canonical XAU is not behind the accepted cross-check;
- FAST/SLOW are bound to canonical XAU and are fresh relative to its latest availability;
- all four GVZ-derived features are bound to latest eligible `GVZ_CBOE`;
- FAST/SLOW/GVZ runtime rows carry the V1.44 refresh contract and input fingerprints;
- Emergency no longer exposes the stale month-open no-observation placeholder after target-month XAU exists;
- Emergency state is recomputed from current target-month XAU with explicit monthly-reference provenance;
- forecast/decision authority stores remain zero.

### 10.2 Historical-pilot readiness

Historical-pilot readiness is governed by:

`GOLD_CONTROL_HISTORICAL_PILOT_READINESS_CONTRACT_V145_2026-09-08.md`

The historical pilot uses 20 common **target-month readiness cells**, not one identical forecast-origin semantic for all engines:

- `2025-01..2025-12` = 12 retrospective validation target-month cells;
- `2026-01..2026-08` = 8 retrospective frozen OOS target-month cells.

The binding top-level readiness states are:

- `READY_PROVEN`
- `READY_TO_REPLAY`
- `PARTIAL`
- `BLOCKED_DATA`
- `BLOCKED_PIT`
- `BLOCKED_CONTRACT`
- `IMPLEMENTATION_FAIL`
- `CONTRACTUAL_EXCLUSION`

The planned V1.45 auditor must produce at minimum a `12 engines × 20 target-month cells = 240 rows` matrix and preserve each engine's role-specific evaluation clock.

For each engine/cell the audit must expose:

- governed engine/model version;
- role/evaluation-clock semantic;
- required source identities;
- required historical depth/prehistory;
- source coverage;
- point-in-time/reconstruction evidence class;
- source binding and lineage status;
- future-information/leakage status;
- deterministic/reproducibility evidence where applicable;
- specific replay-evidence reference where available;
- final readiness state and blocker/reason codes.

No model-performance score is permitted to convert a readiness failure into a pass.

---

## 11. GOLD_PILOT_V1 — frozen historical validation programme

### 11.1 Objective

`GOLD_PILOT_V1` does **not** attempt to optimize all 12 engines or choose a universal winner. Its objective is to establish whether each governed component is technically valid, origin-safe and useful in its declared role, and whether the 12-component information architecture provides complementary decision-support information.

### 11.2 Frozen sequence

The governed project sequence is:

`FREEZE`

→ `HISTORICAL READINESS MATRIX`

→ `DATA RECONSTRUCTION / GAP RESOLUTION`

→ `COMPONENT VERIFICATION`

→ `ROLE-SPECIFIC VALIDATION`

→ `INCREMENTAL CONTRIBUTION TEST`

→ `2025 RETROSPECTIVE VALIDATION`

→ `2026 JAN-AUG FROZEN OOS`

→ `ARCHITECTURE REVIEW`

→ `PROSPECTIVE SHADOW`

The sequence may not be reordered to inspect frozen OOS outcomes before validation rules are fixed.

### 11.3 Evaluation windows

- `2025-01..2025-12` = `RETROSPECTIVE_VALIDATION_WINDOW`
- `2026-01..2026-08` = `RETROSPECTIVE_FROZEN_OOS_TEST`
- first later issuance generated after the governed mechanism is deployed and before outcome is known = `PROSPECTIVE_SHADOW`

The 2026 Jan-Aug window is retrospective frozen OOS evidence, not prospective evidence and not an untouched future holdout once its outcomes are already known.

### 11.4 Component verification gate

Before role performance is interpreted, every component must prove as applicable:

- frozen-contract implementation identity;
- governed source binding;
- required historical coverage;
- origin-safe cutoff;
- zero future-target information;
- explicit reconstruction/vintage semantics;
- deterministic rerun/reconciliation evidence where defined by the component contract.

A component that cannot satisfy its required technical/data gate remains explicitly blocked/not proven under the V1.45 readiness contract. It is not repaired or tuned inside the frozen pilot.

### 11.5 Role-specific validation

The 12 identities are evaluated according to their declared role.

#### Monthly H=1 price experts

- `CAUSAL_PATCH`
- `VW_MIDAS_MSVR_SUCCESSOR_V1`
- `MOMENTUM_3M`
- `RANDOM_WALK`

These may be compared on common H=1 target origins using predeclared price-forecast metrics and the mandatory Random Walk benchmark. Accuracy, stability and incremental/encompassing information may be reported. No automatic expert selector or ensemble is authorized.

#### Strategic/tactical direction context

- `MONTHLY_DIRECTION_3M`
- `FAST`
- `SLOW`

These are evaluated on predeclared direction/context outcomes appropriate to their horizons. They may not be rejected merely because they do not minimize H=1 price MAPE.

#### Event/regime context

- `MACRO_EVENT_SUCCESSOR_V2`
- `BOCPD_RETURN_SUCCESSOR_V1`

These are evaluated on event/regime discrimination and incremental context value under their frozen contracts. They are not direction votes unless a later separately governed change authorizes such a role.

#### Emergency/risk context

- `EMERGENCY_LEVEL`
- `EMERGENCY_REVERSAL`
- `GVZ_RISK`

These are evaluated on tail-risk/context behavior, false-alert/reversal behavior and incremental risk information appropriate to their frozen definitions. They are not H=1 price forecasters.

### 11.6 Contribution and redundancy analysis

After component validity and role-specific validation, the pilot must evaluate whether each component contributes information not already explained by other components in the same or adjacent layer.

Permitted outputs include:

- incremental predictive/context information;
- forecast-error or state co-movement/correlation;
- forecast encompassing diagnostics for same-target H=1 experts;
- regime/event conditional behavior;
- redundancy/complementarity classification.

Permitted architecture classifications include:

- `VALIDATED_CORE`
- `VALIDATED_COMPLEMENTARY`
- `REDUNDANT_NOT_PROVEN`
- `BLOCKED_DATA`
- `IMPLEMENTATION_FAIL`
- `NOT_PROVEN`

These are evidence labels, not automatic deletion instructions. No governed engine is removed from the architecture until the full frozen pilot and a separately documented architecture review are complete.

### 11.7 No pilot-time optimization

During `GOLD_PILOT_V1` the following are forbidden in response to observed 2025/2026 outcomes:

- changing features;
- changing source identities;
- changing thresholds;
- changing hyperparameters outside an already frozen inner-selection rule;
- changing model architecture;
- changing role definitions;
- changing evaluation metrics/gates after inspecting frozen results;
- creating an automatic selector/ensemble;
- repairing a weak component and re-entering it into the same frozen pilot under the same identity.

Any substantive change requires a new challenger identity/change-control after the frozen pilot result is retained unchanged.

---

## 12. Historical data reconstruction priorities

The current first-order historical-pilot blockers are data-plane issues, not a mandate for new model development.

### Priority A — historical canonical NY17 sleeve

The project must first establish the exact missing historical NY17 dates required for `2025-01..2026-08` pilot target-month cells plus each component's necessary lookback.

The approved resolution order is:

1. run/freeze the V1.45 baseline readiness audit before backfill;
2. enumerate required session dates/cell windows;
3. query Twelve Data only for missing exact `XAU/USD`, `1min`, `16:59 America/New_York` bars;
4. classify each requested date using the binding V1.45 exact-date acquisition codes;
5. accept only exact valid bars or explicitly adjudicated provider no-bar dates;
6. persist/archive with truthful retrieval timestamps, lineage and historical-reconstruction evidence labels;
7. rerun the unchanged V1.45 historical-pilot readiness audit.

No broad intraday cache expansion is required when a minimal exact-bar reconstruction is sufficient.

### Priority B — historical GVZ sleeve

Historical `GVZ_CBOE` coverage required by the pilot must be completed from the governed Cboe official historical source, after the frozen baseline audit identifies the exact gap.

Historical GVZ retrieval may support historical replay but may not be represented as if Gold Control had prospectively stored the observation at the original historical date.

### Priority C — remaining frozen-origin closures

After Priority A/B:

- close the outstanding 2026-August Patch replay proof if not already covered by an existing frozen contract/evidence artifact;
- close the outstanding 2026-August BOCPD status under a separately explicit evaluation-only frozen-extension rule if permitted; otherwise retain `BLOCKED_CONTRACT`/`NOT_PROVEN`;
- run/verify the outstanding source-bound August RW/Momentum historical replays;
- verify the final retrospective VW target cell required by `GOLD_PILOT_V1`.

No result-driven model redesign is part of these closure tasks.

---

## 13. Scheduling authority and dependency order

GitHub scheduled workflows run from the repository default branch. Therefore:

- `main` owns cron/scheduling only;
- model/data implementation authority remains `gold-r4-direction-engine`;
- `main` calls reusable canonical workflows pinned to canonical authority;
- canonical reusable workflows do not own independent cron schedules.

Required intramonth dependency order:

`source ingestion succeeds`

→ `canonical NY17 reconciliation where applicable`

→ `V1.44 append-only intramonth recompute`

→ `current/live readiness + strict post-write audit`

→ `snapshot/UI refresh`

Historical-pilot reconstruction and audit are research/replay lanes and must not be wired into live authority-writing dependencies merely to make historical readiness appear current.

Derived recomputation must not be scheduled as if ingestion success were irrelevant.

The canonical `xau-ny17` lane must trigger recomputation only after successful NY17 reconciliation. A second recompute after the daily authority ingest/retry is required so newly released GVZ data is consumed without waiting for the next unrelated event.

---

## 14. Application/snapshot and deployment mirror

The application is read/presentation only. It consumes current runtime/context/source surfaces and may consume legitimately issued forecast/decision stores only if those stores are later authorized and populated.

The deployment mirror `gold-r4-direction-engine-ui-v122-final` must point to the exact governed canonical release HEAD after release validation. It carries no independent model semantics.

Current-view evidence labels must not hide the distinction between catch-up/historical context and prospective-shadow context. Historical pilot readiness must not be presented as live/prospective readiness.

If a database view sanitizes every derived context to a historical label, that observability defect must be corrected through a separately tested database migration before V1.44 is declared fully operational.

---

## 15. Current V1.44 live-operational release gate retained

V1.45 adds historical-pilot governance; it does **not** waive or retroactively satisfy the existing V1.44 live-operational release gate.

The V1.44 live lane remains accepted only after:

1. unit/frozen-rule tests for the writer pass;
2. read-only preflight proves correct fail-closed behavior against the current production state;
3. canonical NY17 bounded reconciliation is run before the first production catch-up;
4. append-only catch-up writes only authorized context/runtime tables;
5. both current/live readiness audits pass after the catch-up;
6. authority stores remain `0/0/0/0`;
7. September H=1 references remain numerically and evidentially unchanged;
8. main scheduler enforces ingestion → recompute → audit → snapshot ordering;
9. current-context database view exposes non-misleading evidence/freshness semantics;
10. application smoke passes and deployment mirror equals canonical release HEAD.

Until that live-operational gate is complete, the correct live statement remains:

`CURRENT_SURFACE_REGISTERED = TRUE`

but

`OPERATIONAL_MODEL_DATA_READY = NOT_YET_PROVEN`

unless and until V1.43/V1.44 audits prove otherwise at a later current state.

---

## 16. V1.45 historical-pilot stop point and next governed work

The project is not blocked on designing another model or selector.

Current V1.45 governance state:

- `HISTORICAL_PILOT_READINESS_CONTRACT = FROZEN`
- `HISTORICAL_PILOT_AUDITOR = IMPLEMENTED_READ_ONLY_AND_TESTED`
- `BASELINE_READINESS_MATRIX = PRESERVED_12_X_20`
- `HISTORICAL_DATA_BACKFILL = NOT_AUTHORIZED`
- `NY17_EXACT_WRITE_SET = NOT_PROVEN_ENTITLEMENT_BLOCKED`
- `GVZ_EXACT_WRITE_SET = PROVEN_295_OFFICIAL_CBOE_ROWS`

Implementation and evidence checkpoints:

- auditor and tests: `6df05a5f145a5797ff1a11b40f60adb77ede33b8`;
- frozen baseline evidence: `f2c96afed24356cd91775a5eeb6eb70be465940b`;
- gap inventory implementation/tests: `240b2f17f747661abf8286e49892399ce9bbc41f`;
- fail-closed exact-date probe implementation/tests: `dc38d86b229d3f7cbd6583c5a2c9f732ce64f7d0`;
- exact NY17/GVZ gap evidence: `ad7af6135a218839e668f56330cdf15bc434cd6e`;
- governed GitHub Actions probe: `82340f78d142f732c6b668d4847bd1f23a5d87d2`;
- blocked provider probe evidence and workflow path correction: `e310c8de1db6456412208fd2e6ed229a86ccc4ac`.

The next governed work is:

1. resolve the Twelve Data entitlement/quota blocker and complete exact-date NY17 probing; do not infer the production write count from blocked candidates;
2. prepare one explicit approval package only after the NY17 exact write set is proven, including the already proven 295-row official-Cboe GVZ set;
3. after explicit approval, resolve Priority A NY17 and Priority B GVZ gaps using only the frozen providers and exact recorded write sets;
4. close remaining frozen-origin evidence gaps without retuning;
5. rerun the unchanged V1.45 readiness audit;
6. freeze `GOLD_PILOT_V1` validation/contribution metrics before role-performance scoring;
7. execute role-specific validation and contribution analysis;
8. retain the architecture review as a post-pilot decision;
9. move later genuinely unseen issuances to `PROSPECTIVE_SHADOW`.

Until the historical-pilot gate is complete, the correct statement is:

`GOLD_PILOT_V1_HISTORICAL_READINESS = NOT_YET_PROVEN`.

---

## 17. V1.46 governed pilot execution state

This section supersedes Section 16 only for current execution state. The V1.45
historical contract, identities, clocks, prohibitions and evidence semantics
remain unchanged and binding.

* Exact NY17 adjudication: 684 candidate dates; 442 exact valid bars, 242
  explicit provider-no-bar dates, zero unresolved. The immutable historical
  artifact lane is authoritative; no production row was required or written.
* Official Cboe GVZ reconstruction: 295 rows for 2025-01-02..2026-03-09 in the
  immutable artifact lane; no duplicate production row was created.
* Post-gap readiness: 240/240 cells classified; 114 `READY_PROVEN`, 124
  `READY_TO_REPLAY`, one `BLOCKED_CONTRACT`, one `CONTRACTUAL_EXCLUSION`.
* Final component verification: 11 `PASS`, BOCPD `BLOCKED_DATA` for exact
  2026-08 CORE5 gold monthly input.
* Role validation: four `VALIDATED_CORE`, five `VALIDATED_COMPLEMENTARY`, two
  `NOT_PROVEN` Emergency roles, one blocked BOCPD role.
* Architecture review: no engine deletion; selector/ensemble and weight
  optimization remain off.
* 2025 retrospective validation is complete without tuning. The 2026 Jan-Aug
  report is explicitly partial: Jan-Jul are scoreable and August realized H=1
  target / BOCPD source coverage remains blocked.
* Prospective shadow preparation exists only as an observation/evaluation lane.
  Overall status is `BLOCKED_DATA`, not `PROSPECTIVE_SHADOW_READY`.

Current authority locks remain `AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`,
`NOT_PROVEN_POSITION_MAPPING`, and no automatic BUY/SELL/HOLD/EXIT/REDUCE.

---

## 18. V1.46 data-completion reconciliation — 2026-09-09

The exact World Bank Pink Sheet August Gold value (`4411 USD/troy ounce`) closes
the BOCPD evaluation-only and four H=1 realized-target data gaps through an
immutable historical reconstruction artifact. The frozen CORE5 payload remains
unchanged. BOCPD deterministic/prefix-invariance tests pass; no tuning occurred.

The official GPR 202609 vintage contains the required August observation and was
committed by the official source on 2026-09-01, before the 2026-09-30 origin.
The VW four-metal gate remains `WAITING_FOUR_METAL_SOURCE_DATA` because the pinned
upstream snapshot contains only 19 common August dates and no September dates.
No prospective forecast was issued.

Authorized V1.44 live catch-up run `34409095422` inserted one new exact NY17 row
and refreshed FAST, SLOW, both Emergency roles and GVZ_RISK. SLOW remains bound
to the last completed-week observation by contract. Final authority counts remain
zero and selector/ensemble remain OFF. Binding detail is recorded in
`data_pipeline/audits/data_completion_readiness_v146_20260909.md`.

---

## 19. V1.49 Gold forecasting research architecture — monthly + short-horizon predictive power — 2026-09-11

This section **replaces the former V1.48 HS-SDL-DMA short-horizon mathematical-core specification in full**. The V1.48 HS-SDL-DMA implementation/result is retained as historical negative evidence in Section 20, but it is no longer the current primary Gold forecasting architecture.

The primary research objective of Gold Control is now explicit:

> **maximize real out-of-sample predictive power for gold at both the next-month and short-horizon (1D/3D) levels, subject to strict point-in-time integrity, leakage prevention, reproducibility, benchmark discipline and evidence-based promotion.**

Methodological elegance is a constraint, not the optimization target. A model is not promoted because it is theoretically sophisticated; it must add reproducible OOS predictive information under the exact governed target and information boundary.

This section does not change the frozen September 2026 monthly references, does not activate automatic model selection or averaging, does not add a current runtime identity and grants no production/trading authority.

### 19.1 Binding research questions and status

Gold Control has two distinct forecasting programmes:

1. **MONTHLY H=1** — forecast the next calendar month's average XAU/USD price/return from the previous completed month-end origin.
2. **SHORT HORIZON** — forecast separately `NEXT_NY17_1D` and `NEXT_NY17_3D`, with probabilistic direction and, where supported, expected-return/magnitude outputs.

The two programmes may share data/context, but they must not be forced into one statistical model.

Binding current research status:

- `MONTHLY_RESEARCH_ARCHITECTURE = FROZEN_FOR_DIAGNOSTIC_STAGE`
- `MONTHLY_FINAL_INTEGRATION_RULE = NOT_YET_SELECTED`
- `MONTHLY_PRODUCTION_MODEL = NOT_YET_PROMOTED`
- `SHORT_HORIZON_RESEARCH_ARCHITECTURE = FROZEN_FOR_INCREMENTAL_VALUE_STAGE`
- `SHORT_HORIZON_FINAL_MODEL = NOT_YET_SELECTED`
- `HS_SDL_DMA_DIRECTION_FUSION_V1 = NOT_PROVEN_RETAINED_BASELINE`
- `NEXT_NY17_1D_PROBABILITY = NOT_PROVEN`
- `NEXT_NY17_3D_PROBABILITY = NOT_PROVEN`
- `TODAY_TO_NY17_PROBABILITY = BLOCKED_CONTRACT`
- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`
- `NOT_PROVEN_POSITION_MAPPING`
- `CORE_PRODUCTION_AUTHORITY = CLOSED`

A future final integration rule/model must be selected from evidence generated under this Section 19 sequence, not from chat preference or one favorable year.

### 19.2 Monthly research core — existing Gold Control models are retained

The monthly programme starts from the models already shown to contain useful information in Gold Control and in gold-specific literature. They are **research views**, not automatically equal-weight experts.

#### A. Mixed-frequency cross-metal view

`VW_MIDAS_MSVR_SUCCESSOR_V1`

Role: capture nonlinear, mixed-frequency and cross-precious-metal information from Gold/Silver/Platinum/Palladium with origin-safe GPR conditioning under its governed contract.

It remains a principal monthly research model. Its historical success and later instability are reasons to study complementarity/conditional performance, not reasons to delete or automatically promote it.

#### B. Dynamic macro-financial view family

- `DMA`
- `DMS`
- `IDMA` / separately governed adaptive-forgetting variants

Role: capture time-varying relevance of macro-financial predictors and model uncertainty.

The existing Gold Control CORE5 evidence (`GOLD`, `FEDFUNDS`, `NASDAQ`, `USD/CNY`, `GPR`) supports continued study of this family. DMA, DMS and IDMA must **not** be assumed to be three independent votes. Whether they should remain separate forecasts, be reduced to a parsimonious macro view, or enter an integration rule separately must be determined by the mandatory complementarity/encompassing audit in Section 19.4.

#### C. Existing independent monthly views

- `CAUSAL_PATCH`
- `MOMENTUM_3M`

They remain independent research forecasts/context views and may contribute only if their OOS errors/information are not redundant with VW or the macro-dynamic family.

#### D. Mandatory benchmark / defensive anchor

`RANDOM_WALK`

RW is never removed from monthly evaluation. It is both the mandatory same-horizon benchmark and a candidate defensive anchor if later research proves that model edge is unstable and benchmark anchoring improves genuine OOS performance.

#### E. Additional challengers

No additional model is admitted merely because a paper reports low error. A challenger requires exact H=1 target parity, PIT-safe inputs, reproducible implementation and preregistration before outer scoring.

Potentially serious later challengers include PIT-safe implementations of data-rich regularized/tree models and gold-specific temporal architectures such as Patch/DPformer-family methods. They are not current winners and are not allowed to displace the existing monthly core before the existing-model complementarity audit is complete.

### 19.3 Monthly evidence already established — interpretation boundary

Existing evidence motivates the research programme but does not preselect the final integration rule.

Gold Control has previously observed:

- `VW_MIDAS_MSVR` historical/common-window MAPE below the Random Walk benchmark;
- 2025 governed validation in which VW materially outperformed RW on MAE;
- 2026 Jan-Jul frozen OOS in which VW no longer retained that advantage and Momentum performed better;
- CORE5 DMA/DMS/IDMA historical replay in which dynamic macro-family forecasts improved H=1 MAPE versus RW.

Correct inference:

`RELATIVE_MODEL_PERFORMANCE_IS_TIME_VARYING = SUPPORTED`

Not yet proven:

- that any one model universally dominates;
- that models are sufficiently complementary to justify combination;
- that regime/context variables can predict which model will be best at the next origin;
- that any particular weighting/selector/ensemble improves future OOS performance.

Therefore no monthly integration method may be selected before Section 19.4 is executed.

### 19.4 Mandatory monthly forecast complementarity / encompassing audit

Before any new selector, ensemble or final monthly model is implemented, Work must construct a **same-target, same-origin, PIT-compatible monthly forecast panel** containing all legitimately reconstructible H=1 forecasts for:

- VW-MIDAS-MSVR;
- DMA;
- DMS;
- IDMA where valid;
- Causal Patch;
- Momentum 3M;
- Random Walk.

For every common origin, retain forecast, target, error, absolute error/loss, origin cutoff, source/vintage lineage and evidence class.

The audit must answer, at minimum:

1. **Forecast/error dependence** — pairwise forecast, error and loss-differential correlation/covariance; rolling versions where sample size permits.
2. **Forecast encompassing** — whether one forecast contains the useful predictive information of another under the common H=1 target.
3. **Unconditional predictive accuracy** — Diebold-Mariano or an assumption-appropriate equivalent on preregistered losses.
4. **Conditional predictive ability** — Giacomini-White-style analysis or an assumption-appropriate equivalent asking whether relative forecast performance is predictable from information available at the origin.
5. **Multiple-model uncertainty** — Model Confidence Set / superior-set analysis where sample size and dependence assumptions permit; do not force a unique winner if the data do not identify one.
6. **Disagreement information** — test whether cross-model dispersion/disagreement predicts subsequent forecast error, absolute error or regime failure.
7. **Time/regime stability** — characterize whether relative loss changes systematically with pre-origin macro/risk/regime states, without treating post-outcome explanations as predictors.
8. **Redundancy classification** — identify models/views that are `NON_REDUNDANT`, `PARTIALLY_REDUNDANT`, `ENCOMPASSED/REDUNDANT_NOT_PROVEN`, or `BLOCKED`.

No integration weights may be optimized using the final outer observations of the same audit sequence.

### 19.5 Integration-family selection is conditional on the audit — no preselected ensemble

V1.49 deliberately does **not** declare one final ensemble formula.

The permitted research logic is diagnostic:

#### Case A — one forecast encompasses others

Prefer the more parsimonious forecast/view. Do not add dominated forecasts merely to create an ensemble.

#### Case B — forecasts contain complementary information but simple combination already captures it

An equal-weight/simple-average combination is the mandatory combination benchmark. More complex weighting must beat it OOS after estimation cost.

#### Case C — strong common-factor/high-correlation structure exists

A factor-adjusted / regularized combination family becomes eligible for preregistration. Its purpose is to avoid counting the same forecast information multiple times while preserving genuine residual predictive content.

#### Case D — complementary model edge exists but decays/changes over time

A benchmark-anchored or iterated combination family becomes eligible for preregistration, including a second-stage combination with Random Walk/no-change if the development evidence supports defensive shrinkage when model edge weakens.

#### Case E — pre-origin state variables genuinely predict relative model loss

Only then may a conditional/regime-adaptive weighting or selection rule be preregistered. BOCPD, GVZ, macro-event or other state variables may not be used as regime selectors merely because they are intuitively plausible.

All integration families selected for formal testing must be frozen from development/inner evidence **before** final outer comparison. Result-driven movement from one family to another on the same outer sample is forbidden.

### 19.6 Monthly target and evaluation contract

The canonical monthly target remains:

`NEXT_MONTH_MONTHLY_AVERAGE_XAU_USD`

Origin remains the previous completed calendar month-end under the existing governed source contract.

Primary monthly evaluation must include:

- MAE;
- RMSE / MSFE;
- relative MAE and/or relative MSFE versus same-origin RW;
- median absolute error;
- signed error / bias;
- MAPE/sMAPE as supporting scale-free diagnostics, not sole selection criteria;
- direction accuracy as secondary information only;
- worst-period error;
- rolling/time stability;
- model win/loss concentration by period;
- forecast disagreement and error correlation;
- DM/GW/MCS or assumption-appropriate statistical evidence.

A complex integration rule is not promoted unless it beats both RW and a simple-combination benchmark robustly enough under preregistered criteria.

### 19.7 Short-horizon research objective — direction plus magnitude, not state-vote fusion alone

The short-horizon programme remains two separate targets:

- `NEXT_NY17_1D`
- `NEXT_NY17_3D`

For eligible completed NY17 anchor `t`:

`r_(t,h) = log(P_(t+h) / P_t)`

`Y_(t,h) = 1{r_(t,h) > 0}`

Primary probabilistic output:

`P(Y_(t,h)=1 | F_t)`

The new research programme must also evaluate whether forecasting expected return/magnitude adds useful information:

`E[r_(t,h) | F_t]`

and, only if sample size and calibration support it, conditional quantiles/intervals may be researched later.

The failed V1.48 HS-SDL-DMA run proves that a narrow FAST/SLOW/MONTHLY_DIRECTION state-fusion architecture did not add sufficient predictive power. It does **not** prove that short-horizon gold is unpredictable using a richer PIT-safe market information set.

### 19.8 Short-horizon information blocks — incremental predictive-content design

Short-horizon research must proceed by predeclared **information blocks**, not by unconstrained feature search.

Candidate blocks are:

#### Block 0 — parsimonious gold-history baseline

Origin-safe own-history features such as lagged returns, momentum, range and realized-volatility/realized-moment features whose exact definitions are frozen before scoring.

#### Block 1 — cross-precious-metal information

Gold/Silver/Platinum/Palladium returns and origin-safe relative/dispersion information where exact PIT data are available.

#### Block 2 — FX and rates

USD/DXY-related variables, nominal/real yield or curve variables only when source/vintage/timestamp semantics are proven for each origin.

#### Block 3 — equity/risk/commodity cross-market information

Examples may include Nasdaq/S&P/global equity, VIX/GVZ/OVX and selected commodity signals, but only after exact source and time-boundary parity are frozen.

#### Block 4 — existing Gold Control direction/context states

- `FAST`
- `SLOW`
- `MONTHLY_DIRECTION_3M`
- `BOCPD_RETURN_SUCCESSOR_V1`
- `GVZ_RISK`
- `MACRO_EVENT_SUCCESSOR_V2`
- `EMERGENCY_LEVEL`
- `EMERGENCY_REVERSAL`

These components keep their declared semantic roles. GVZ, BOCPD, Macro Event and Emergency do not become unconditional UP/DOWN votes. Their value must be demonstrated as incremental/interaction/context information.

#### Block 5 — positioning/flow/news sleeves

CFTC positioning, ETF/flow variables or gold-related news/NLP features may be researched only when genuine historical timestamp/PIT availability is proven. If a source cannot be reconstructed origin-safely, the block remains `BLOCKED_PIT` and is not approximated with final/current data.

The required experiment is **incremental predictive-content testing**: begin with a parsimonious baseline and add pre-frozen blocks one at a time or in a preregistered sequence. A block remains only if it adds robust nested-OOS information after complexity/estimation cost.

### 19.9 Short-horizon model-family research

V1.49 does not preselect a final short-horizon estimator.

The first serious candidate family must include:

- regularized linear/logistic models as parsimonious mandatory baselines;
- LightGBM and/or equivalent gradient-boosted tree models when sample size supports them;
- XGBoost/GBRT-type nonlinear tabular challengers;
- HS-SDL-DMA V1 as a retained NOT_PROVEN historical benchmark, not the default core.

Deep-learning / CNN-LSTM / TCN / Transformer-family models may enter only after data volume, target parity and PIT-safe feature history are sufficient and only under the same frozen nested OOS test. They do not receive preference merely because of model capacity.

For probability outputs, calibration is mandatory before any user-facing percentage. Raw scores, raw vote fractions and in-sample fitted probabilities are not calibrated probabilities.

### 19.10 Mandatory nested pseudo-real-time validation for both programmes

All substantive model/integration/feature choices must be evaluated by nested rolling/expanding-origin pseudo-real-time procedures.

At each outer origin:

1. construct only data known by the origin cutoff;
2. fit scaling/encoding/decomposition/feature transforms within the training origin only;
3. select hyperparameters, feature blocks, integration family and calibration rules only from earlier inner origins;
4. freeze the outer forecast before target maturity;
5. score only after the target becomes available;
6. retain source/vintage lineage, fingerprints, code commit, specification and output.

Forbidden:

- random split;
- whole-sample normalization/decomposition;
- final-vintage substitution into earlier origins;
- target leakage;
- adding a new model/feature block after seeing the same final outer results;
- selecting an integration rule from the final outer sample;
- relabelling known 2025/2026 outcomes as pristine unseen prospective evidence.

The already observed 2025/2026 periods may be used only as correctly labelled retrospective research/diagnostic evidence for a newly designed V1.49 architecture. Genuine future proof begins only after a final candidate system is frozen and issued before the outcome.

### 19.11 Short-horizon evaluation

Primary probabilistic metrics:

- Brier score;
- log loss;
- calibration intercept/slope;
- reliability diagnostics.

Supporting metrics:

- balanced accuracy;
- directional accuracy;
- expected-return error/loss if magnitude is modeled;
- time/regime/risk stability;
- worst-period behavior;
- matured origin count/effective sample;
- missing/freshness sensitivity.

Mandatory probability baselines include:

- `P_UP = 0.50`;
- expanding historical UP frequency;
- parsimonious own-history model;
- retained HS-SDL-DMA V1 result where exact origin parity permits comparison.

For 3D overlapping targets, inference must account for dependence with a preregistered HAC/block-resampling design or an assumption-appropriate equivalent.

No model is promoted on raw accuracy alone.

### 19.12 Research sequence — binding order for Work

The next governed research order is:

`CURRENT CANONICAL STATE REVERIFY`

→ `MONTHLY SAME-ORIGIN FORECAST PANEL RECONSTRUCTION`

→ `MONTHLY COMPLEMENTARITY / ENCOMPASSING / ERROR-DEPENDENCE AUDIT`

→ `DM + CONDITIONAL PREDICTIVE ABILITY + MCS/SUPERIOR-SET ANALYSIS`

→ `MONTHLY INTEGRATION-FAMILY DIAGNOSIS`

→ `FREEZE LIMITED MONTHLY INTEGRATION CANDIDATES + SIMPLE/RW BASELINES`

→ `SHORT-HORIZON PIT DATA / SOURCE / CLOCK INVENTORY`

→ `SHORT-HORIZON INFORMATION-BLOCK DEFINITIONS`

→ `INCREMENTAL PREDICTIVE-CONTENT AUDIT`

→ `FREEZE LIMITED SHORT-HORIZON MODEL CANDIDATES`

→ `NESTED ROLLING/EXPANDING PSEUDO-REAL-TIME REPLAY`

→ `CALIBRATION + STABILITY + STATISTICAL COMPARISON`

→ `MONTHLY + SHORT-HORIZON ARCHITECTURE REVIEW`

→ `DASHBOARD EVIDENCE CONTRACT REVIEW`

→ `LATER GENUINE PROSPECTIVE SHADOW`.

The sequence may not be reordered to choose an ensemble/model before the diagnostics that justify it.

### 19.13 Hard-stop states

Use explicit fail-closed states:

- feature/source identity cannot be recovered: `BLOCKED_INVENTORY`;
- origin availability/vintage cannot be proven: `BLOCKED_PIT`;
- target/source/session clock ambiguous: `BLOCKED_CONTRACT`;
- insufficient common-origin sample for a claimed comparison: `BLOCKED_INSUFFICIENT_SAMPLE`;
- leakage/prefix/determinism failure: `IMPLEMENTATION_FAIL`;
- missing mandatory RW/simple baselines: `VALIDATION_INVALID`;
- model/feature/integration family selected after final outer outcomes were inspected: `GOVERNANCE_FAIL`;
- statistical evidence does not establish superiority/complementarity: `NOT_PROVEN`.

No blocked condition may be repaired through silent imputation, final-vintage substitution, alternate-provider substitution, backdating or hindsight retuning.

### 19.14 Academic authority basis for V1.49

The research design is grounded in an authority chain rather than one model paper:

- Aye, G.C., Gupta, R., Hammoudeh, S., Kim, W.J. (2015), “Forecasting the price of gold using dynamic model averaging,” *International Review of Financial Analysis*, 41, 257–266. DOI `10.1016/j.irfa.2015.03.010`. Direct gold evidence for time-varying model/predictor relevance and DMA/DMS forecasting.
- Baur, D.G., Beckmann, J., Czudaj, R. (2016), “A melting pot — Gold price forecasts under model and parameter uncertainty,” *International Review of Financial Analysis*, 48, 282–291. DOI `10.1016/j.irfa.2016.10.010`. Gold-specific evidence that DMA improves forecasts and predictor relevance changes over time.
- Chen/Yang/Lan (2026), “Three horizon-specific drivers of gold prices with Iterated Dynamic Model Averaging,” *Economics Letters*, 268, 113147. DOI `10.1016/j.econlet.2026.113147`. Supports horizon-dependent gold drivers and adaptive model/predictor weighting; Gold Control's CORE5 implementation is not claimed to be an exact replication.
- Wang et al. (2026), “What drives precious metals pricing? An explainable Mixed-frequency machine learning approach,” *Mineral Economics*. Supports mixed-frequency, cross-precious-metal nonlinear forecasting as the methodological family behind the VW-MIDAS-MSVR research view; exact archived Gold Control identity remains governed separately.
- Diebold, F.X., Mariano, R.S. (1995), “Comparing Predictive Accuracy,” *Journal of Business & Economic Statistics*. DOI `10.1080/07350015.1995.10524599`. Basis for pairwise predictive-accuracy comparison under explicit loss functions.
- Giacomini, R., White, H. (2006), “Tests of Conditional Predictive Ability,” *Econometrica*. DOI `10.1111/j.1468-0262.2006.00718.x`. Basis for asking whether relative forecast performance is predictable from information available at the origin.
- Hansen, P.R., Lunde, A., Nason, J.M. (2011), “The Model Confidence Set,” *Econometrica*, 79(2), 453–497. DOI `10.3982/ECTA5771`. Basis for retaining a statistically indistinguishable superior set rather than manufacturing a unique winner.
- Tashman, L.J. (2000), “Out-of-sample tests of forecasting accuracy: an analysis and review,” *International Journal of Forecasting*, 16(4), 437–450. DOI `10.1016/S0169-2070(00)00065-0`. Basis for rolling-origin/multiple-test-period evaluation.
- Hewamalage, H., Ackermann, K., Bergmeir, C. (2023), “Forecast evaluation for data scientists: common pitfalls and best practices,” *Data Mining and Knowledge Discovery*, 37, 788–832. DOI `10.1007/s10618-022-00894-5`. Basis for avoiding random split, whole-sample preprocessing/decomposition leakage and weak benchmark design.
- Gneiting, T., Balabdaoui, F., Raftery, A.E. (2007), “Probabilistic Forecasts, Calibration and Sharpness,” *JRSS Series B*, 69(2), 243–268. DOI `10.1111/j.1467-9868.2007.00587.x`. Basis for probability calibration/proper probabilistic evaluation.
- Lee, S., Lee, T.-H. (2026), “Improving the simple average combined forecast via factor-adjusted regularization,” *International Journal of Forecasting*. DOI `10.1016/j.ijforecast.2026.07.008`. This is a **conditional candidate family**, relevant only if the complementarity audit demonstrates a strong common-factor/high-correlation problem.
- “Raising the bar in commodity price forecasting: Evidence from iterated forecast combinations” (2026), *Economic Modelling*, article 107800. DOI `10.1016/j.econmod.2026.107800`. This is a **conditional candidate family**, relevant only if the audit demonstrates complementary but time-unstable model edge and benchmark anchoring is justified.
- Ha et al. (2026), “Machine learning-based portfolio optimization: comparative analysis with the all-weather portfolio strategy,” *Financial Innovation*, 12:112. DOI `10.1186/s40854-026-00927-8`, together with the 2023 *Chaos, Solitons & Fractals* gold ML study, PII `S0960077923009803`. These support regularized/tree-based data-rich short-horizon challengers; they do not prove Gold Control performance without the Section 19 nested PIT-safe test.
- 2024 *Finance Research Letters* 1-day-ahead gold-futures/news study, PII `S1544612324011450`. Supports a future news/NLP information sleeve only if Gold Control can prove historical timestamp/PIT availability.

These authorities justify the **research questions, candidate information channels, diagnostic sequence and evaluation discipline**. They do not predetermine the winning model or integration rule.

---

## 20. Retained V1.48 HS-SDL-DMA negative evidence — historical baseline only

This section preserves the V1.48 short-horizon experiment as immutable research evidence. It is **not** the current primary mathematical core after V1.49.

The former V1.48 build order was executed on a feature branch. Exact inventory contained 400 retrospective NY17 origins. FAST, SLOW and MONTHLY_DIRECTION used categorical one-hot contrasts; no numeric vote encoding was invented. Context-only components lacking an exact daily PIT join were excluded from the initial three nested candidates.

Candidate universe, inner grid, calibration and abstention/promotion rules were committed before outer scoring. Deterministic nested replay produced 279 calibrated outer 1D and 273 calibrated outer 3D predictions. Evidence class remains `RETROSPECTIVE_PSEUDO_REAL_TIME_VALIDATED`, never prospective.

Neither horizon passed the preregistered promotion gates. HS-SDL-DMA Brier was `0.254468` (1D) and `0.255404` (3D), versus `0.25` for the mandatory constant-probability baseline. Calibration/stability gates also failed.

Binding interpretation after V1.49:

- `HS_SDL_DMA_DIRECTION_FUSION_V1 = NOT_PROVEN_RETAINED_BASELINE`
- `HS_SDL_DMA_RETROSPECTIVE_VALIDATION = VALID_RUN_PROMOTION_NOT_PROVEN`
- `NEXT_NY17_1D_PROBABILITY = NOT_PROVEN`
- `NEXT_NY17_3D_PROBABILITY = NOT_PROVEN`
- `DASHBOARD_SHORT_HORIZON_PROBABILITY = NOT_PROVEN`
- `LATER_GENUINE_PROSPECTIVE_SHADOW = BLOCKED_PROMOTION_NOT_PROVEN`
- `CORE_PRODUCTION_AUTHORITY = CLOSED`
- `TODAY_TO_NY17_PROBABILITY = BLOCKED_CONTRACT`
- `AUTO_SELECTOR = OFF`; `AUTO_ENSEMBLE = OFF`

The result must not be deleted, relabelled or tuned away. It serves as a negative control and mandatory historical benchmark for the richer V1.49 short-horizon research programme where origin parity permits comparison.

Full evidence remains in `HS_SDL_DMA_RETROSPECTIVE_VALIDATION_REPORT_V1_2026-09-10.md` and `data_pipeline/audits/hs_sdl_dma_replay_v1/`.

---

## 21. V1.49 execution state — 2026-09-11 retrospective research checkpoint

This section records execution results under the frozen Section 19 architecture. It does not revise the Section 19 research design and does not create production authority.

### 21.1 Monthly programme

- Four frozen PIT-compatible views (VW, Patch, Momentum, RW) have 43 common target months from 2023-01 through 2026-07.
- The requested seven-view common PIT panel has zero valid origins. Available CORE5 material is `APPROVED_RESEARCH_ONLY_NOT_PIT`; DMA/DMS/IDMA remain `BLOCKED_PIT` and are excluded from candidate selection.
- Development diagnostics classify the four valid views as partially redundant. No DM or conditional-predictive-ability comparison established a 5% advantage. Formal MCS is `BLOCKED_INSUFFICIENT_SAMPLE`.
- The only pre-outer integration candidates were RW and `SIMPLE_EQUAL_4`; complex integration remains `NOT_PROVEN`.
- In the 2025-01 through 2026-07 retrospective outer window (N=19), VW had the best point MAE (132.561) and RMSE (176.076), versus RW 176.053 and 216.326. VW-versus-RW HAC squared-loss p-value was 0.0917. Monthly promotion remains `NOT_PROVEN`.

### 21.2 Short-horizon programme

- The exact historical reconstruction contains 400 chronological NY17 origins, with 399 mature 1D and 397 mature 3D targets.
- Block 0 and categorical Block 4 were executable. Blocks 1, 2, 3 and 5 remain `BLOCKED_CONTRACT` or `BLOCKED_PIT`; no substitution or backfill was used.
- Block 4 improved development Brier by 0.00215 for 1D and 0.00627 for 3D and was frozen before outer scoring.
- Frozen nested outer replay produced 159 1D and 157 overlapping 3D observations. V1.49 Brier was 0.261830 (1D) and 0.276739 (3D), both worse than the mandatory 0.25 benchmark. Both calibration gates failed.
- `NEXT_NY17_1D = NOT_PROVEN`; `NEXT_NY17_3D = NOT_PROVEN`; `HS_SDL_DMA_DIRECTION_FUSION_V1 = NOT_PROVEN_RETAINED_BASELINE`.

### 21.3 Governance disposition

- Evidence class: `RETROSPECTIVE_RESEARCH_DIAGNOSTIC_NOT_PROSPECTIVE`.
- Leakage accepted: none. Missing PIT proof remains explicit blocker evidence.
- Full-run determinism: PASS; three reruns produced identical monthly, 1D and 3D output hashes.
- `AUTO_SELECTOR = OFF`; `AUTO_ENSEMBLE = OFF`.
- Production forecast/decision authority: CLOSED. Production database writes: NONE.
- Dashboard short-horizon probability: CLOSED.
- `LATER_GENUINE_PROSPECTIVE_SHADOW = BLOCKED_PIT_AND_PROMOTION_NOT_PROVEN`.

Binding execution evidence is `GOLD_CONTROL_V149_RESEARCH_EXECUTION_REPORT_2026-09-11.md` and `data_pipeline/audits/v149_research/`.

---

## 22. V1.49 Phase-2 role-preserving direction checkpoint — 2026-09-11

This execution-state section does not alter the frozen Section 19 architecture and does not create a new model or production authority.

- A role-preserving event/regime direction is accepted only as a preregistered research hypothesis.
- The general `NEXT_NY17_1D` / `NEXT_NY17_3D` programme and the sparse Macro Event + Market Shock event study are separate evaluation lanes.
- The deterministic inventory panel contains 400 NY17 origins, 399 mature 1D targets and 397 mature 3D targets.
- Block 0 and the already-tested Block 4 state fields are ready for retrospective replay; they do not constitute new incremental evidence.
- `GVZ_RISK = BLOCKED_PIT_EXACT_RELEASE_CLOCK_NOT_PROVEN` for an exact NY17-origin join.
- `MACRO_EVENT_SUCCESSOR_V2 = BLOCKED_PANEL_DAILY_ASOF_JOIN_NOT_CANONICAL` for the proposed daily study.
- `BOCPD_RETURN_SUCCESSOR_V1 = BLOCKED_DATA_DAILY_ORIGIN_STATE_NOT_FOUND`.
- `MARKET_SHOCK_V3 = NOT_FOUND_CANONICAL`; numerical claims supplied outside canonical evidence are not admitted.
- Phase-2 model scoring is blocked until at least one genuinely incremental information lane proves exact source, clock and PIT availability.
- Evidence remains retrospective, `AUTO_SELECTOR = OFF`, `AUTO_ENSEMBLE = OFF`, and production authority remains closed.

Binding checkpoint evidence is `GOLD_CONTROL_V149_PHASE2_DIRECTION_AND_ACTION_CHECKPOINT_2026-09-11.md` and `data_pipeline/audits/v149_phase2/`.
