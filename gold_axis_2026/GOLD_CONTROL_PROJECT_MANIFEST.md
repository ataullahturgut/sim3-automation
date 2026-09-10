# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.48
**Issue date:** 2026-09-10
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

## 19. V1.48 frozen short-horizon mathematical core — HS-SDL-DMA — 2026-09-10

This section **replaces the former V1.47 open-ended mathematical/fusion research specification in full**. It is the sole current mathematical specification for the Gold Control short-horizon direction programme. Earlier chat proposals, exploratory names, density-first primary architectures, BPS-as-core proposals, DOW-as-core proposals, loss-discounted-pool-as-core proposals or other alternative primary formulations are not current authority. They may be studied only as challengers under Section 19.11 and may not be used to implement the core.

This section does not rewrite `GOLD_PILOT_V1`, does not change the four frozen September H=1 monthly references, does not add a thirteenth current governed runtime engine, and grants no production forecast, decision or trading authority.

### 19.1 Frozen core identity and status

The official short-horizon research core is:

`HS_SDL_DMA_DIRECTION_FUSION_V1`

Expanded name:

**Horizon-Specific Shrinkage Dynamic Logistic Regression + Small Dynamic Model Averaging + Inner-OOS Probability Recalibration + Abstention**.

Binding status:

- `SHORT_HORIZON_CORE_MODEL = HS_SDL_DMA_DIRECTION_FUSION_V1`
- `CORE_ARCHITECTURE = FROZEN_RESEARCH_SPECIFICATION`
- `CORE_IMPLEMENTATION = NOT_IMPLEMENTED`
- `CORE_RETROSPECTIVE_VALIDATION = NOT_RUN`
- `CORE_PROSPECTIVE_VALIDATION = NOT_RUN`
- `CORE_PRODUCTION_AUTHORITY = CLOSED`
- `TODAY_TO_NY17_PROBABILITY = BLOCKED_CONTRACT`
- `NEXT_NY17_1D_PROBABILITY = NOT_PROVEN`
- `NEXT_NY17_3D_PROBABILITY = NOT_PROVEN`
- `DASHBOARD_SHORT_HORIZON_PROBABILITY = NOT_PROVEN`
- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`
- `NOT_PROVEN_POSITION_MAPPING`

The word `DMA` inside this research-core identity does **not** activate the current/global `AUTO_ENSEMBLE`. It is an internal, offline/replay mathematical component of this named challenger only. It does not average the four governed monthly H=1 experts, does not create a production selector, and does not authorize automatic production weighting.

### 19.2 Forecast questions and exact primary targets

The short-horizon programme is a binary probabilistic direction problem, not a point-price model and not a trading-action model.

For each eligible completed NY17 anchor at time `t` and horizon `h`:

`r_(t,h) = log(P_(t+h) / P_t)`

`Y_(t,h) = 1{r_(t,h) > 0}`

and the model estimates:

`p_(t,h) = P(Y_(t,h)=1 | F_t)`.

`F_t` means only information proven available by the exact forecast origin/cutoff.

The primary frozen horizons are separate models:

- `NEXT_NY17_1D`: the next eligible completed NY17 reference versus the current completed NY17 anchor;
- `NEXT_NY17_3D`: the third subsequent eligible completed NY17 reference versus the current completed NY17 anchor.

There is **no single mathematical target named `1–3D`**. A user-facing “1–3 day outlook” may summarize the separately validated `1D` and `3D` outputs, but it may not be treated as a third target unless a later manifest version defines one.

`TODAY_TO_NY17` remains `BLOCKED_CONTRACT`: no intraday probability may be implemented until the exact intraday XAU source, issuance anchor, timestamp/session semantics, latency rule, stale-data rule, fallback policy and historical PIT availability are frozen. An arbitrary live quote may not be substituted.

The existing `MONTHLY_H1` target remains unchanged and separate: next calendar month's average XAU/USD under its existing month-origin contract. HS-SDL-DMA does not alter that target.

### 19.3 Role-preserving input architecture

The current Gold Control components are heterogeneous and must not be falsely treated as homogeneous votes or homogeneous predictive-density experts.

Direction-capable candidate inputs are represented conceptually by:

`D_t = [FAST_t, SLOW_t, MONTHLY_DIRECTION_3M_t]`.

Conditioning/context inputs are represented conceptually by:

`C_t = [BOCPD_t, GVZ_t, MACRO_EVENT_t, EMERGENCY_LEVEL_t, EMERGENCY_REVERSAL_t]`.

Binding role restrictions:

- `FAST` may provide short-horizon tactical direction information.
- `SLOW` may provide slower tactical/directional context.
- `MONTHLY_DIRECTION_3M` may provide strategic prior/context if its value was frozen and available at the short-horizon origin.
- `BOCPD_RETURN_SUCCESSOR_V1` remains regime/break context only. It may condition the reliability/effect of a direction-capable input; it is not itself an `UP`/`DOWN` vote.
- `GVZ_RISK` remains uncertainty/risk context only. It may condition the reliability/effect of a direction-capable input; it is not itself an `UP`/`DOWN` vote.
- `MACRO_EVENT_SUCCESSOR_V2` remains release-aware event context. Any directional incremental contribution must be learned origin-safely; the event state is not automatically assigned a sign.
- `EMERGENCY_LEVEL` / `EMERGENCY_REVERSAL` remain early-warning/abnormal-move/reversal context. They do not rewrite a previously issued monthly forecast.
- Market Shock research is non-canonical and is excluded from the initial core feature set unless separately recovered, frozen and admitted by a later manifest version.
- The four monthly H=1 price experts are **not automatically short-horizon features**. Any later use must prove origin compatibility and incremental value without target-month leakage.

No raw vote fraction may be interpreted as a probability. `5 of 7 signals UP` is not `P(UP)=71%`.

### 19.4 Exact core statistical form

For each horizon `h ∈ {1D, 3D}` and each pre-frozen candidate specification `M_k`:

`Y_(t,h) ~ Bernoulli(p_(k,t,h))`

with

`logit(p_(k,t,h)) = x_(k,t,h)' theta_(k,t,h)`

and

`logit(p) = log(p/(1-p))`.

The design vector `x_(k,t,h)` may contain only:

1. an intercept;
2. origin-safe encodings of approved direction-capable inputs from `D_t`;
3. pre-frozen role-preserving interaction terms of the form `direction_input × context_input`.

Context-only main effects that would silently convert BOCPD, GVZ or Emergency into independent direction votes are forbidden in the initial core. Macro Event may not receive an unconditional directional sign by construction.

The initial candidate set must be **small and nested** and may contain at most four non-baseline specifications. Before the first outer test is run, the exact canonical field names, categorical/continuous encodings, missing-state handling and permitted interactions must be recovered from current code/evidence and frozen. Until that inventory is complete:

`CORE_FEATURE_SCHEMA = BLOCKED_INVENTORY`.

No programmer may guess state encodings such as `-1/0/+1`, invent a strength score, map labels to numbers without a frozen rule, or manufacture continuous values from categorical engine states.

### 19.5 Shrinkage dynamic logistic state evolution

Within each candidate model, coefficients may evolve over time:

`theta_(k,t,h) = theta_(k,t-1,h) + omega_(k,t,h)`

with a state-evolution uncertainty controlled by a pre-frozen discount/shrinkage rule.

The core requirement is **shrinkage toward stability**: when the data do not support time variation, the effective parameter evolution must be driven toward the static-model limit rather than forced to drift. A static regularized logistic model is therefore not an unrelated alternative; it is the mandatory stability benchmark and limiting case against which dynamic complexity must justify itself.

The exact coefficient regularization strength and state discount/forgetting hyperparameters must be selected only inside the inner rolling/expanding-origin procedure from a small pre-frozen admissible set. They may not be hand-tuned from outer results, 2026 Jan–Aug outcomes, dashboard behavior or prospective outcomes.

A more elaborate TVP process-variance shrinkage prior may be researched later, but it is not silently part of V1.48 unless explicitly implemented, tested and promoted by a later manifest version.

### 19.6 Small Dynamic Model Averaging layer

Model uncertainty is handled across the small pre-frozen candidate set, not across an uncontrolled universe.

Let `pi_(k,t|t-1,h)` be the pre-outcome weight of candidate `k` at origin `t`. The DMA transition uses a forgetting factor `alpha_h` under the frozen implementation:

`pi_(k,t|t-1,h) ∝ pi_(k,t-1|t-1,h) ^ alpha_h`,

normalized across the admitted candidate set.

After the relevant target has matured, the model probability is updated using that candidate's Bernoulli predictive likelihood. The next raw probability is:

`p_raw_(t,h) = Σ_k pi_(k,t|t-1,h) * p_(k,t,h)`.

Rules:

- initial candidate weights must be explicit and reproducible;
- `alpha_h` is horizon-specific and must be selected only inside inner rolling origins from a pre-frozen admissible set;
- no weight may be updated using an outcome that has not yet matured;
- the `3D` model may not consume the `t→t+3` outcome before the third subsequent eligible NY17 observation exists;
- no future overlap outcome may leak into preprocessing, coefficient state, weight update, calibration or model selection;
- a small candidate set is mandatory; uncontrolled combinatorial model search is forbidden in the core.

### 19.7 Probability recalibration is mandatory before dashboard use

`p_raw` is a research probability, not automatically a user-display probability.

Using only inner rolling-origin out-of-sample predictions, the primary recalibration form is deliberately low-dimensional:

`z_(t,h) = logit(clip(p_raw_(t,h)))`

`p_cal_(t,h) = logistic(a_h + b_h * z_(t,h))`.

The clipping epsilon, calibration training window/minimum sample and any regularization must be frozen before outer scoring. Recalibration may not be fit on the outer target being evaluated.

If there are insufficient origin-safe inner predictions to estimate calibration reliably:

`CALIBRATION_STATUS = BLOCKED_INSUFFICIENT_SAMPLE`

and the dashboard may not display a calibrated percentage for that horizon.

Raw classifier scores, raw DMA probabilities, vote fractions or in-sample fitted probabilities may never be relabelled as calibrated user probabilities.

### 19.8 Direction mapping and abstention

The production-facing semantic output, if later validated, is deliberately three-state:

- `UP`
- `DOWN`
- `UNCERTAIN`

The system is not required to issue a direction on every origin.

`UP/DOWN` mapping must use `p_cal` plus a pre-registered abstention/risk-coverage rule. The exact abstention threshold/coverage trade-off is **not to be guessed during implementation**. It must be frozen before the first outer evaluation after historical sample size and feasible inner-origin count are audited, but before any outer outcome is inspected.

Until that rule is frozen and validated:

`ABSTENTION_RULE = NOT_YET_FROZEN`

and any dashboard direction probability remains research-only.

`CONFIDENCE` is not equal to `P_UP`. A later confidence state may use calibration quality, effective sample size, source freshness, model disagreement and regime/risk conditions, but its mapping requires its own pre-registered rule.

Expected percentage move, target price, P10/P50/P90 or full return density is **not part of the V1.48 core**. Those may be developed later as separate magnitude/distribution challengers after short-horizon direction is validated.

### 19.9 Validation design — mandatory nested pseudo-real-time evaluation

Long future waiting is not replaced by hindsight tuning. The development design is nested rolling/expanding-origin pseudo-real-time validation.

At each outer origin:

1. reconstruct only data and states genuinely available by that cutoff;
2. apply all preprocessing/encoding only from data available within that training origin;
3. choose candidate specification, coefficient regularization, state discount/forgetting factor, DMA forgetting factor and calibration parameters only through earlier inner origins;
4. issue and immutably retain the outer probability before reading the outer target;
5. score only after the target matures;
6. retain input fingerprints, exact source/vintage lineage, code commit, chosen hyperparameters, raw probability, calibrated probability and outcome.

Forbidden:

- random train/test split;
- whole-sample scaling/encoding before temporal folds;
- later-vintage macro backfill into earlier origins;
- result-driven feature creation;
- selecting a hyperparameter after looking at the outer month/day;
- repeatedly enlarging the candidate universe after inspecting the same outer sequence;
- claiming the already-observed 2026 Jan–Aug window is a pristine future test for this post-hoc challenger.

The 2026 Jan–Aug evidence remains valid for the prior frozen pilot only. New short-horizon challenger evidence must be labelled according to its actual reconstruction/evaluation status.

### 19.10 Primary metrics and mandatory baselines

The primary probabilistic score is **Brier score**:

`BS_h = mean((p_cal_(t,h) - Y_(t,h))^2)`.

Mandatory supporting evidence:

- log loss under a pre-frozen numerical clipping rule;
- calibration intercept and calibration slope;
- reliability/calibration diagnostics;
- directional accuracy and balanced accuracy as secondary diagnostics;
- sample count and effective/matured origin count;
- stability by time/regime/risk/event strata where sample size permits;
- worst-period behavior;
- source-freshness and missing-state sensitivity.

Mandatory baselines/challengers for the first frozen round:

- `P_UP = 0.50` naive probability;
- expanding historical UP-frequency probability;
- `FAST_ONLY` origin-safe probabilistic baseline where historically reconstructible;
- static regularized logistic baseline using the same admitted feature semantics;
- equal-weight average of the same admitted candidate probabilities as a simple combination benchmark.

The dynamic core must justify complexity against these simpler alternatives. A complex model is not promoted merely because it has the best point estimate on one period.

For multiple-model comparison, Model Confidence Set / SPA-style procedures may be used where sample size and assumptions support them. The system must not force one winner when the data support a statistically indistinguishable superior set.

For `3D`, overlapping targets induce dependence. Statistical inference and resampling must account for that dependence with an appropriate pre-frozen HAC/block-resampling design; ordinary independent-observation tests are not sufficient.

Numerical promotion thresholds are deliberately not invented here. They must be pre-registered after the exact historical origin count/feature availability audit and **before** outer performance is inspected. Until then:

`CORE_PROMOTION_THRESHOLDS = NOT_YET_FROZEN`.

### 19.11 Challenger hierarchy — core does not move when new papers appear

The HS-SDL-DMA architecture is the frozen primary core for the next implementation/validation round. New literature does not automatically replace it.

Permitted secondary challengers, only after exact target/PIT parity is established, include:

- standard `DMA` / `DMS` benchmark variants;
- `DOW-DMA`;
- `IDMA` / adaptive-forgetting variants;
- loss-discounted pooling;
- Dynamic Bayesian Predictive Synthesis / dynamic prediction pools;
- XGBoost or other calibrated nonlinear tabular classifier;
- distributional/quantile models;
- deep-learning/Transformer-family models when historical sample size and PIT-safe inputs justify them.

These are **not core** and must not be implemented as though V1.48 selected them. They compete against HS-SDL-DMA under the same frozen origins, target definition, information set and evaluation rules. Any later replacement of the core requires a new manifest version and explicit evidence that the challenger provides robust incremental value rather than one-period improvement.

### 19.12 Dashboard binding

The intended top-level short-horizon cards are:

- `TODAY / NY17` — remains `BLOCKED_CONTRACT` until the intraday anchor/source contract exists;
- `NEXT 1D` — driven only by validated `NEXT_NY17_1D` output;
- `NEXT 3D` — driven only by validated `NEXT_NY17_3D` output;
- `NEXT MONTH` — remains under the separate existing H=1 monthly expert governance.

For an eligible validated short-horizon card, the dashboard may eventually show:

- `UP / DOWN / UNCERTAIN`;
- calibrated `P_UP`;
- confidence only when its rule is validated;
- exact `AS_OF` cutoff;
- source/evidence freshness;
- explanatory `NEDEN?` context showing support/conflict without pretending all components are direction votes.

If calibration or the horizon model is not proven, display `NOT_PROVEN / Olasılık henüz kalibre edilmedi`. Do not invent a percentage for visual completeness.

A green/up indicator is not `BUY`; red/down is not `SELL`. Position sizing/action mapping remains unauthorized.

### 19.13 Immediate build order and hard stop points

The next implementation order is frozen as:

`CURRENT CANONICAL STATE REVERIFY`

→ `EXACT SHORT-HORIZON HISTORICAL INPUT/STATE INVENTORY`

→ `1D / 3D SOURCE + SESSION CLOCK VERIFICATION`

→ `EXACT FEATURE ENCODING + MISSING-STATE FREEZE`

→ `SMALL CANDIDATE SPECIFICATION FREEZE (K ≤ 4)`

→ `INNER HYPERPARAMETER / CALIBRATION RULE FREEZE`

→ `ABSTENTION + PROMOTION RULE PREREGISTRATION`

→ `DETERMINISTIC NESTED ROLLING/EXPANDING REPLAY`

→ `BASELINE + CALIBRATION + STABILITY TESTS`

→ `MCS / SPA / OVERLAP-AWARE INFERENCE WHERE APPLICABLE`

→ `CORE VS CHALLENGER REVIEW`

→ `DASHBOARD EVIDENCE CONTRACT TEST`

→ `LATER GENUINE PROSPECTIVE SHADOW`.

Hard stops:

- if exact feature/state encoding cannot be recovered: `BLOCKED_INVENTORY`;
- if PIT availability cannot be proven: `BLOCKED_PIT`;
- if a source/session clock is ambiguous: `BLOCKED_CONTRACT`;
- if calibration sample is insufficient: `BLOCKED_INSUFFICIENT_SAMPLE`;
- if leakage/prefix invariance fails: `IMPLEMENTATION_FAIL`;
- if baselines are not included: `VALIDATION_INVALID`;
- if promotion thresholds were set after outer results were viewed: `GOVERNANCE_FAIL`.

No blocked condition may be silently repaired by imputation, relabelling, alternate provider substitution or retrospective threshold tuning.

### 19.14 Academic authority basis for the frozen core

The V1.48 core is grounded in the following authority chain:

- McCormick, T.H., Raftery, A.E., Madigan, D., Burd, R.S. (2012), “Dynamic Logistic Regression and Dynamic Model Averaging for Binary Classification,” *Biometrics*, 68(1), 23–30. DOI `10.1111/j.1541-0420.2011.01645.x`. This is the direct methodological basis for online binary probability prediction under both time-varying coefficients and model uncertainty.
- Raftery, A.E., Kárný, M., Ettler, P. (2010), “Online Prediction Under Model Uncertainty via Dynamic Model Averaging,” *Technometrics*, 52(1), 52–66. DOI `10.1198/TECH.2009.08104`. This supplies the core DMA model-uncertainty/forgetting framework and supports using a small set of substantively motivated models.
- Bitto, A., Frühwirth-Schnatter, S. (2019), “Achieving shrinkage in a time-varying parameter model framework,” *Journal of Econometrics*, 210(1), 75–97. DOI `10.1016/j.jeconom.2018.11.006`. This supports the principle that time-varying parameters should shrink toward static behavior when time variation is not supported; V1.48 uses that principle conservatively and does not silently import the paper's full MCMC specification.
- Aye, G.C., Gupta, R., Hammoudeh, S., Kim, W.J. (2015), “Forecasting the price of gold using dynamic model averaging,” *International Review of Financial Analysis*, 41, 257–266. DOI `10.1016/j.irfa.2015.03.010`. This supplies direct gold-market evidence that model/predictor relevance can vary through time and that dynamic model selection/averaging is a serious gold-forecast benchmark.
- Gneiting, T., Balabdaoui, F., Raftery, A.E. (2007), “Probabilistic Forecasts, Calibration and Sharpness,” *JRSS Series B*, 69(2), 243–268. DOI `10.1111/j.1467-9868.2007.00587.x`. This is the probability-calibration/proper-scoring authority for not exposing uncalibrated model scores as probabilities.
- Tashman, L.J. (2000), “Out-of-sample tests of forecasting accuracy: an analysis and review,” *International Journal of Forecasting*, 16(4), 437–450. DOI `10.1016/S0169-2070(00)00065-0`. This supports explicit rolling-origin, updating/recalibration and multiple-test-period evaluation design.
- Hansen, P.R., Lunde, A., Nason, J.M. (2011), “The Model Confidence Set,” *Econometrica*, 79(2), 453–497. DOI `10.3982/ECTA5771`. This supports retaining a superior set instead of forcing a unique winner when statistical evidence does not distinguish candidates.

These sources justify the **architecture and evaluation discipline**. They do not prove that HS-SDL-DMA will outperform Gold Control baselines on the project's data. That empirical claim remains `NOT_PROVEN` until the frozen replay and subsequent evidence gates pass.

---

## 20. V1.48 HS-SDL-DMA implementation and first frozen replay state

The Section 19 build order was executed on a feature branch without changing the
frozen architecture. Exact inventory contains 400 retrospective NY17 origins.
FAST, SLOW and MONTHLY_DIRECTION use categorical one-hot contrasts; no numeric
vote encoding was invented. Context-only components lacking an exact daily PIT
join are excluded from the initial three nested candidates.

Candidate universe, inner grid, calibration and abstention/promotion rules were
committed before outer scoring. Deterministic nested replay subsequently produced
279 calibrated outer 1D and 273 calibrated outer 3D predictions. Evidence is
`RETROSPECTIVE_PSEUDO_REAL_TIME_VALIDATED`, never prospective.

Neither horizon passed the preregistered promotion gates. HS-SDL-DMA Brier was
`0.254468` (1D) and `0.255404` (3D), versus `0.25` for the mandatory constant
probability baseline. Calibration/stability gates also failed. Therefore:

- `CORE_IMPLEMENTATION = IMPLEMENTED_RESEARCH_ONLY`
- `CORE_RETROSPECTIVE_VALIDATION = VALID_RUN_PROMOTION_NOT_PROVEN`
- `NEXT_NY17_1D_PROBABILITY = NOT_PROVEN`
- `NEXT_NY17_3D_PROBABILITY = NOT_PROVEN`
- `DASHBOARD_SHORT_HORIZON_PROBABILITY = NOT_PROVEN`
- `LATER_GENUINE_PROSPECTIVE_SHADOW = BLOCKED_PROMOTION_NOT_PROVEN`
- `CORE_PRODUCTION_AUTHORITY = CLOSED`
- `TODAY_TO_NY17_PROBABILITY = BLOCKED_CONTRACT`
- `AUTO_SELECTOR = OFF`; `AUTO_ENSEMBLE = OFF`

Full evidence is in `HS_SDL_DMA_RETROSPECTIVE_VALIDATION_REPORT_V1_2026-09-10.md`
and `data_pipeline/audits/hs_sdl_dma_replay_v1/`.
