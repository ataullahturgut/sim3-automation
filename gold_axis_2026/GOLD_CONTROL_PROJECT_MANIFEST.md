# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.47
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

## 19. V1.47 single-manifest forecast architecture and multi-horizon direction-fusion programme — 2026-09-10

This section is the binding forward research/development plan for Gold Control. It does not rewrite the frozen V1.45 pilot, does not change the four September H=1 references, does not add a thirteenth current runtime engine, and grants no forecast, decision or trading authority. Where Sections 16–18 describe earlier stop points, this section controls only the forward methodology and document-governance plan; historical evidence remains immutable.

### 19.1 Objective: separate forecast, monitoring and early warning

Gold Control must answer separate questions rather than collapse them into one signal:

1. **Monthly price forecast:** What is the next calendar month's average XAU/USD level or distribution?
2. **Short-horizon direction:** What is the calibrated probability that XAU/USD will be higher at a specified next-session / multi-session horizon?
3. **Regime/event/risk state:** Has the information environment changed enough to reduce confidence in the base forecast?
4. **Early-warning state:** Has an abnormal move already started, or has a reversal condition appeared?

The conceptual analogy to earthquake systems is limited to architecture: a background forecast is kept separate from continuously updated sensors, regime/event monitoring and an early-warning layer. It is **not** a claim that gold prices and earthquakes have the same stochastic process, predictability or causal mechanism. Earthquake/CSEP practice is used only as inspiration for prospective testing discipline, immutable forecast issuance and separation of forecast from early warning.

### 19.2 Current governed inventory remains unchanged

The current governed runtime inventory remains exactly the 12 identities in Section 2. V1.47 does not promote any new model or context engine.

Research status is frozen as follows:

- `MULTI_HORIZON_DIRECTION_FUSION = RESEARCH_CHALLENGER_NOT_IMPLEMENTED`
- `INTRADAY_TO_NY17_DIRECTION_PROBABILITY = NOT_PROVEN`
- `NEXT_NY17_1D_DIRECTION_PROBABILITY = NOT_PROVEN`
- `NEXT_NY17_1_3D_DIRECTION_PROBABILITY = NOT_PROVEN`
- `DASHBOARD_PROBABILITY_UI = SPECIFIED_NOT_IMPLEMENTED`
- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`
- `PRODUCTION_FORECAST_AUTHORITY = CLOSED`
- `PRODUCTION_DECISION_AUTHORITY = CLOSED`

Historical/research identities such as `TVP_AR`, `DMA`, `DMS`, `IDMA`, the Market Shock V3 research lane and Macro Event V3 research lane are not current governed engines. They may enter a future research candidate inventory only after their exact code, target, source, PIT semantics and historical evidence are recovered and frozen. `BYDZ` is currently `NOT_FOUND` as an exact governed/research identity and must not be guessed, renamed or mapped to another method without primary project evidence.

### 19.3 Horizon and target separation

The existing canonical monthly target remains unchanged:

- `MONTHLY_H1`: next calendar month's average XAU/USD; prior completed month-end information boundary as already governed.

The short-horizon programme introduces research targets, not production outputs:

| Research horizon | Primary research event | Status |
|---|---|---|
| `INTRADAY_TO_NY17` | XAU/USD is higher at the same eligible NY17 boundary than at the governed intraday issuance anchor | `BLOCKED_CONTRACT` until exact intraday anchor/source/session clock is frozen |
| `NEXT_NY17_1D` | next eligible completed NY17 reference is above the current completed NY17 anchor | `RESEARCH_TARGET_DEFINED` |
| `NEXT_NY17_1_3D` | third subsequent eligible completed NY17 reference is above the current completed NY17 anchor | `RESEARCH_TARGET_DEFINED` |
| `MONTHLY_H1` | existing next-month average XAU/USD target | `CURRENT_CANONICAL_TARGET` |

For the directional research targets, the primary event is `future_return > 0`. Material-move probabilities such as `P(return > +x%)` or `P(return < -x%)` require a separate pre-registered threshold and may not be chosen after viewing outer-test outcomes.

`INTRADAY_TO_NY17` may not be implemented from an arbitrary live quote. Before any historical or live run, the exact intraday price source, timestamp semantics, session calendar, latency, stale-data rule, fallback policy and output clock must be frozen in this manifest or in a subordinate implementation artifact explicitly referenced by a later version of this manifest. Until then the dashboard must show `NOT_PROVEN` rather than an intraday probability.

### 19.4 Sensor-role discipline for short-horizon research

Current components keep their original roles. Fusion research may consume their origin-safe states as candidate predictors/context only under the following restrictions:

- `FAST`: short-horizon tactical direction candidate input.
- `SLOW`: slower tactical/context candidate input.
- `MONTHLY_DIRECTION_3M`: strategic prior/context candidate input; never refreshed with target-month future information.
- `MACRO_EVENT_SUCCESSOR_V2`: release-aware event-risk context. It is not automatically converted into a direction vote. Any directional use requires separately demonstrated incremental value under an origin-safe research design.
- `BOCPD_RETURN_SUCCESSOR_V1`: regime/break conditioning only. It remains **not a direction vote** and cannot directly manufacture `UP` or `DOWN` probability.
- `GVZ_RISK`: risk/uncertainty conditioning only. It remains **not a gold-direction predictor** and cannot directly manufacture `UP` or `DOWN` probability.
- `EMERGENCY_LEVEL` / `EMERGENCY_REVERSAL`: early-warning / abnormal-move / reversal context. They may reduce or qualify confidence when legitimately known at issuance time, but they do not rewrite an already issued monthly H=1 forecast.
- Market Shock research: non-canonical research context only; no live or fusion use until exact identity and frozen validation are re-established.
- H=1 price experts: may supply background forecast/disagreement context when origin-compatible, but target-month observations may not leak backward into their frozen forecast.

No raw count of green/red engines is a probability model. `5 of 7 engines UP` may be displayed as descriptive disagreement evidence if useful, but it may not be relabelled `P(UP)=71%`.

### 19.5 Direction Fusion research output

A future validated Direction Fusion challenger may produce, separately for each eligible horizon:

- `P_UP`: calibrated probability that the horizon return is positive;
- `DIRECTION`: `UP`, `DOWN` or `UNCERTAIN`, only under pre-registered mapping rules;
- `CONFIDENCE`: a separately defined evidence-confidence state, not a synonym for `P_UP`;
- `AS_OF`: exact information cutoff;
- `SOURCE_FRESHNESS`: freshness state for every required input family;
- `REGIME_STATE`: conditioning context, if proven;
- `EVENT_RISK_STATE`: conditioning context, if proven;
- `TAIL_RISK_STATE`: conditioning context, if proven;
- `EARLY_WARNING_STATE`: current abnormal-move/reversal state, if applicable.

A displayed probability must come from out-of-sample/pseudo-real-time calibrated predictions. Raw model scores, vote fractions, uncalibrated classifier outputs or in-sample fitted probabilities may not be displayed as user probabilities.

`CONFIDENCE` must be separated from direction probability. Its future rule may consider at least calibration error, effective historical sample size, model disagreement, source freshness, regime instability and risk/event conditions. The thresholds for `HIGH / MEDIUM / LOW` or any equivalent labels must be frozen **before** the corresponding outer test is inspected. Until that rule is validated, confidence is `NOT_PROVEN`.

Expected percentage move or price magnitude may be shown only if a separately evaluated magnitude/return model supports it. Direction probability alone does not authorize an expected-return number.

### 19.6 Retrospective development when waiting for many future months is impractical

A lack of time for long prospective accumulation does not authorize hindsight tuning. The approved high-information retrospective design is **nested rolling/expanding-origin pseudo-real-time validation**.

For every outer origin:

1. reconstruct only information genuinely available by that origin, including publication lags and vintage rules;
2. fit preprocessing only on the training/inner data available by that origin;
3. if feature/model/calibration/hyperparameter selection is required, learn it only from earlier inner rolling origins;
4. issue the outer prediction without access to that outer target or any later observation;
5. score only after the frozen outer prediction exists;
6. retain the prediction, input fingerprint, source vintages, code commit and evaluation result immutably.

Random split is forbidden. Whole-sample preprocessing before fold construction is forbidden. Future revisions may not be inserted into historical origins unless the historical source contract proves that revision was actually available then.

The 2026 Jan–Aug outcomes are already known to the project. They remain valid evidence for the previously frozen V1.45 pilot, but they are **not an untouched future test set for a challenger designed after those outcomes were inspected**. New challenger work must label this reuse transparently and rely on a broader origin sequence, nested outer testing and later genuinely unseen evidence rather than pretending Jan–Aug is pristine.

Before new challenger scoring begins, the candidate universe must be frozen. Adding candidates repeatedly after seeing the same outer outcomes is data snooping and is not permitted inside one frozen evaluation round.

### 19.7 Evaluation metrics and model comparison

Metrics must match the target and role.

For monthly H=1 price forecasts, permitted core metrics include:

- MAE and RMSE;
- MAPE/APE where numerically meaningful;
- bias;
- skill/relative loss versus the mandatory same-horizon Random Walk benchmark;
- direction correctness as a secondary diagnostic;
- stability by year/regime/origin bucket;
- worst-period and tail-error diagnostics.

For binary direction probabilities, the core evidence must include:

- Brier score;
- log loss where probabilities are bounded/handled under a pre-registered numerical rule;
- calibration/reliability diagnostics;
- directional accuracy and balanced accuracy as secondary classification diagnostics;
- discrimination diagnostics where sample size supports them;
- sample count/effective sample size;
- performance by regime/risk/event state and by time bucket;
- stability and worst-period behavior.

For full predictive distributions, if later implemented, use proper scoring/coverage diagnostics such as CRPS, interval coverage and sharpness subject to calibration. Existing point forecasts may not be retroactively presented as P10/P50/P90 distributions without a separately validated probabilistic model.

Pairwise forecast-comparison tests such as Diebold–Mariano may be used when their assumptions and loss differential are appropriate. When many models are compared, multiple-comparison-aware procedures such as Hansen's SPA and Model Confidence Set may be used. The system must not force a unique winner when the data support a set of statistically indistinguishable superior models.

Forecast combination may be evaluated only as an offline research challenger. Equal-weight combination is a mandatory simple benchmark if combination is studied; more complex weights must be estimated only from inner-origin historical losses and must be compared against the simple benchmark. A successful research combination does **not** turn `AUTO_ENSEMBLE` on.

### 19.8 Dashboard presentation contract

The intended user-facing top layer is horizon-based rather than model-name-based. When evidence exists, the top cards are:

1. `TODAY / NY17`
2. `NEXT 1D`
3. `NEXT 1–3D`
4. `NEXT MONTH`

Each short-horizon card may display only evidence actually proven for that horizon:

- direction or `UNCERTAIN`;
- calibrated `P(UP)` if and only if calibration is validated;
- confidence if and only if the confidence rule is validated;
- exact `as_of` / last-update time;
- freshness/evidence status;
- expected move only if a magnitude model is separately validated.

If a probability is not proven, the dashboard must show `NOT_PROVEN` / `Olasılık henüz kalibre edilmedi`; it must never invent a percentage for visual completeness.

The `NEXT MONTH` card must preserve the current H=1 governance. While no expert selector/ensemble/probabilistic H=1 distribution is authorized, it may show the individual governed expert point forecasts, their disagreement/range and evidence class. It may **not** silently collapse them into a single P50, weighted average or winner. P10/P50/P90 may appear only after a probabilistic H=1 model or combination has separately passed its validation and authorization gates.

A secondary `WHY / NEDEN?` area may show which validated signals support, oppose or qualify the displayed horizon view. This is explanatory evidence, not a vote count. `BOCPD`, `GVZ`, Macro Event and Emergency must be labelled according to their actual role (regime, risk, event, early warning) rather than falsely displayed as price forecasters.

Colors/icons must communicate direction, uncertainty, freshness and alarm separately. A green/up indicator is not a BUY instruction; red/down is not a SELL instruction. No dashboard element may manufacture position sizing or action mapping while `NOT_PROVEN_POSITION_MAPPING` remains binding.

### 19.9 Promotion gates for multi-horizon Direction Fusion

`MULTI_HORIZON_DIRECTION_FUSION` remains research-only until all applicable gates pass:

1. exact horizon/target semantics are frozen;
2. exact source identities and time/session clocks are frozen;
3. historical coverage and PIT/vintage availability are proven;
4. candidate predictor/model universe is frozen before outer-test inspection;
5. deterministic nested rolling/expanding-origin replay passes with zero future-information violations;
6. fold-local preprocessing/calibration is proven;
7. probability calibration and proper scoring evidence pass pre-registered acceptance rules;
8. mandatory simple baselines are included;
9. stability/worst-regime diagnostics are acceptable under pre-registered criteria;
10. model-comparison/multiple-comparison evidence is reported without forcing a false unique winner;
11. dashboard representations are traceable to exact evidence and show `NOT_PROVEN` where evidence is absent;
12. no current 12-engine role is silently changed;
13. no monthly H=1 historical forecast is rewritten;
14. production Neon authority tables remain untouched unless a later explicit production authorization is issued;
15. `AUTO_SELECTOR` and `AUTO_ENSEMBLE` remain OFF until separately authorized after the research gates.

Passing retrospective nested pseudo-real-time validation permits the label `RETROSPECTIVE_PSEUDO_REAL_TIME_VALIDATED` only. It does not permit `PROSPECTIVE_VALIDATED`. Genuine pre-outcome issuance remains the only basis for prospective evidence.

### 19.10 Near-term governed work order

The next research/development order is:

`CURRENT STATE REVERIFY`

→ `EXACT HISTORICAL/RESEARCH ENGINE INVENTORY RECOVERY`

→ `HORIZON + SOURCE CLOCK FREEZE`

→ `CANDIDATE UNIVERSE FREEZE`

→ `NESTED ROLLING/EXPANDING PSEUDO-REAL-TIME REPLAY`

→ `PROBABILITY CALIBRATION + ROLE-SPECIFIC METRICS`

→ `DM / SPA / MODEL CONFIDENCE SET WHERE APPLICABLE`

→ `FUSION CHALLENGER COMPARISON`

→ `DASHBOARD EVIDENCE CONTRACT TEST`

→ `ARCHITECTURE / PROMOTION REVIEW`

→ `LATER GENUINE PROSPECTIVE SHADOW`

No result-driven threshold/model/source change may be inserted inside this sequence after the relevant evaluation round has been frozen. If a challenger fails, its failure is retained and a new versioned challenger round is required.

### 19.11 Academic basis for V1.47 methodology

The methodological design is grounded in established forecast-evaluation literature and uses earthquake testing only as a systems/testing analogy:

- Tashman, L.J. (2000), “Out-of-sample tests of forecasting accuracy: an analysis and review,” *International Journal of Forecasting*, 16(4), 437–450. DOI: `10.1016/S0169-2070(00)00065-0`. Supports explicit fixed/rolling-origin, updating/recalibration and multiple-test-period design choices.
- Gneiting, T., Balabdaoui, F., Raftery, A.E. (2007), “Probabilistic Forecasts, Calibration and Sharpness,” *Journal of the Royal Statistical Society: Series B*, 69(2), 243–268. DOI: `10.1111/j.1467-9868.2007.00587.x`. Supports calibration, sharpness and proper scoring of probabilistic forecasts.
- Timmermann, A. (2006), “Forecast Combinations,” *Handbook of Economic Forecasting*, Vol. 1, 135–196. DOI: `10.1016/S1574-0706(05)01004-9`. Supports evaluating simple forecast combinations as robust benchmarks rather than assuming optimized weights dominate.
- Hansen, P.R. (2005), “A Test for Superior Predictive Ability,” *Journal of Business & Economic Statistics*, 23, 365–380. DOI: `10.1198/073500105000000063`. Supports multiple-model predictive-ability testing/data-snooping control.
- Hansen, P.R., Lunde, A., Nason, J.M. (2011), “The Model Confidence Set,” *Econometrica*, 79(2), 453–497. DOI: `10.3982/ECTA5771`. Supports retaining a statistically defensible set of superior models when data do not justify a unique winner.
- Collaboratory for the Study of Earthquake Predictability (CSEP), official testing programme. Used here only as an analogy for rigorous, predeclared, prospective forecast-testing discipline and separation of forecast experiments from early-warning interpretation; it supplies no gold-price model and no statistical-equivalence claim.

These references justify the **evaluation architecture**, not automatic promotion of any specific Gold Control model. Every model/source/threshold still requires Gold Control-specific evidence under this manifest.
