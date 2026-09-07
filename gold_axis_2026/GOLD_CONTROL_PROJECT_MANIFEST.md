# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.42  
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
- no backdating of reconstruction/replay evidence
- no mutation of immutable historical forecast/runtime evidence
- no production forecast/decision authority write without explicit later manifest authorization

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

---

## 6. September 2026 current references

The following values were reconstructed from the completed 31-Aug information boundary. They are current September references, but not backdated prospective issuance evidence.

| Identity | Current September reference | Semantics |
|---|---:|---|
| `VW_MIDAS_MSVR_SUCCESSOR_V1` | `4565.115907930242 USD/oz` | H=1 price reference |
| `CAUSAL_PATCH` | `4452.046728838838 USD/oz` | H=1 price reference |
| `MOMENTUM_3M` | `4345.814584037808 USD/oz` | H=1 price reference |
| `RANDOM_WALK` | `4397.305673870967 USD/oz` | H=1 benchmark |
| `MONTHLY_DIRECTION_3M` | `DOWN` | strategic monthly context |
| `FAST` | `ROBUST_UP` | tactical short-horizon context |
| `SLOW` | `ROBUST_UP` | tactical slower context |
| `MACRO_EVENT_SUCCESSOR_V2` | `MACRO_MIXED_OR_SMALL` | intramonth event-risk context |
| `BOCPD_RETURN_SUCCESSOR_V1` | `NO_ADVERSE_BREAK_CANDIDATE` | regime/break context |
| `EMERGENCY_LEVEL` | `NEUTRAL` | month-open emergency state |
| `EMERGENCY_REVERSAL` | `OFF` | month-open emergency state |
| `GVZ_RISK` | current persisted risk context | risk only |

The four H=1 expert values must not be averaged, weighted or winner-selected while the selector lock remains in force.

30 Sep 2026 is a later eligible prospective validation origin for October; it does not block the September reference.

---

## 7. Motor semantics

### `VW_MIDAS_MSVR_SUCCESSOR_V1`
Current VW/MSVR model identity. Frozen 8-feature four-metal MSVR with origin-local GPR point-in-time input. Historical replay window is 2023-01..2026-07, N=43. Historical replay MAPE is `2.69106498%` versus Random Walk `3.30232202%`. Historical replay performance is evidence, not proof of future superiority.

### `CAUSAL_PATCH`
Current monthly H=1 expert. Completed-session/PIT safeguards remain part of its executable identity. No selector or action authority.

### `MOMENTUM_3M`
Current monthly H=1 expert. Distinct from `MONTHLY_DIRECTION_3M`.

### `RANDOM_WALK`
Mandatory same-origin naive benchmark.

### `MONTHLY_DIRECTION_3M`
Strategic monthly direction/prior context; not an H=1 price forecast.

### `FAST`
Short-horizon tactical context from completed daily XAU observations and frozen SMA20/persistence logic.

### `SLOW`
Slower tactical confirmation context from completed weekly observations and frozen SMA4/persistence logic.

### `MACRO_EVENT_SUCCESSOR_V2`
Timestamp-safe labor-event risk/context. Intramonth event information may not be inserted retroactively into the month-open snapshot.

### `BOCPD_RETURN_SUCCESSOR_V1`
Regime/break context only. No H=1 price forecast, no direction vote, no automatic action.

### `EMERGENCY_LEVEL`
Intramonth abnormal-level detector evaluated from completed target-month observations against the frozen monthly reference.

### `EMERGENCY_REVERSAL`
Intramonth peak/trough reversal detector. Alert/context only.

### `GVZ_RISK`
Volatility/risk context only. It never predicts gold direction.

---

## 8. Current source surface

The current database source surface is `current_source_registry_v1`.

It must include only:

- observation-backed source identities that are not `BLOCKED`, `OPTIONAL` or `PAID`-required placeholders; and
- explicitly approved non-persisted live display identity `XAU_SPOT_GOLDAPI`.

The raw `source_registry` remains historical/audit storage and is not itself a current surface.

Current operational completed-daily XAU decision reference:

`XAU_EOD_TWELVE_NY17`

Semantics: Twelve Data `XAU/USD`, 1-minute source, New York time, internal 17:00 ET reference derived from the 16:59 bar. It is not labelled an official settlement.

Research-only source identities may remain visible through the current source surface when they are observation-backed and required for reproducibility. Blocked/license placeholders and empty future candidates are not current.

---

## 9. Current runtime and context selection

### Runtime

The application/runtime authority view is `current_engine_runtime_state_v1`.

It must select the **latest complete target context containing all 12 governed engine identities**, then select the latest row for each engine inside that target context.

Selection rule:

`LATEST_COMPLETE_12_ENGINE_TARGET_CONTEXT`

Expected current state:

- `ACTIVE = 12`
- `WAITING = 0`
- `BLOCKED = 0`
- total = `12`

This prevents a partially-created future month from replacing the current complete production context.

### Context features

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

---

## 10. Provenance rule

Current views must not invent missing input fingerprints.

When a governed runtime row has no `input_fingerprint`, current metadata must expose:

`REFERENCE_METADATA_BOUND_INPUT_FINGERPRINT_NOT_AVAILABLE`

When present, it must expose:

`INPUT_FINGERPRINT_PRESENT`

Missing provenance is reported, not fabricated.

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

A valid snapshot must prove:

- exact 12 governed engines, all ACTIVE;
- one common complete target context;
- exact 7 current context features from the same target context;
- zero blocked/optional/paid rows in the current source surface;
- zero unauthorized forecast/decision authority rows;
- no forbidden action/selector payload.

---

## 12. Scheduling authority

GitHub scheduled workflows run from the repository default branch. Therefore:

- `main` is the **default-branch scheduling surface**;
- canonical implementation remains `gold-r4-direction-engine`;
- scheduled jobs on `main` call reusable workflows pinned to `gold-r4-direction-engine`;
- reusable canonical writer/refresh workflows must not own independent `schedule:` triggers;
- snapshot refresh must be dispatched by the default-branch scheduler, not rely on a non-default-branch cron.

This separation is operational only; `main` does not become model/code authority.

---

## 13. Deployment mirror

`gold-r4-direction-engine-ui-v122-final` is a deployment mirror only.

After a governed canonical release passes current-surface and application smoke tests, the deployment mirror must point to the exact canonical release HEAD. It must not carry independent model, manifest or runtime semantics.

---

## 14. v1.42 clean-current-surface gate

Before v1.42 becomes canonical, prove all of the following:

1. `current_source_registry_v1` contains no blocked/optional/paid placeholder and no empty source except the explicit non-persisted live display source;
2. `current_engine_runtime_state_v1` exposes exactly one latest complete 12-engine target context;
3. `current_context_feature_state_v1` exposes exactly one latest complete 7-feature target context;
4. current runtime is `12 ACTIVE / 0 WAITING / 0 BLOCKED`;
5. missing fingerprints are reported, never synthesized;
6. production authority stores remain `0/0/0/0` unless later explicitly authorized;
7. current snapshot validates against V142;
8. canonical app smoke passes against production current views;
9. default-branch scheduler owns cron and dispatches reusable canonical workflows;
10. deployment mirror equals canonical release HEAD.

Only after this gate passes should work continue on the live intramonth refresh chain:

`XAU → FAST/SLOW → Emergency → GVZ → UI`.
