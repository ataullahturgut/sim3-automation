# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.41  
**Issue date:** 2026-09-06  
**Repository:** `ataullahturgut/sim3-automation`  
**Canonical branch:** `gold-r4-direction-engine`  
**Project root:** `gold_axis_2026/`

---

## 1. Sole authority

This file is the only current Gold Control project manifest.

The current working tree contains only current operational code, current contracts, current configuration, current tests and current evidence needed by an executable path. Superseded implementation detail belongs in Git history, not in the current application/runtime surface.

Production Neon is the authority for mutable source observations, point-in-time lineage, current runtime state and legitimately issued forecast/decision records. GitHub is the authority for code, model contracts, reproducibility and this manifest.

The application is read/presentation only. It may not silently choose a model, average experts, tune thresholds, substitute providers, backdate reconstructed evidence or manufacture an action.

---

## 2. Product definition

Gold Control is a mobile-first, auditable XAU/USD decision-support system. It is not an autonomous trading system.

The system has four distinct responsibilities:

1. estimate the next calendar month's average XAU/USD level;
2. maintain strategic and tactical direction context at different time scales;
3. detect intramonth shock, reversal, event and regime conditions;
4. expose volatility/risk context and immutable evidence provenance.

These responsibilities must remain separate. A price forecast is not a tactical direction signal; a risk or regime context is not a price forecast; no single context is an automatic position instruction.

---

## 3. Current architecture

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

No other identity belongs to the current governed application/runtime inventory.

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
- no backdating of reconstructed/replay evidence
- no mutation of immutable historical forecast/runtime evidence
- no production forecast/decision authority write without an explicit later manifest authorization

Expert disagreement is displayed; it is not silently resolved.

---

## 5. Monthly origin and target contract

For target calendar month `M`, the H=1 origin is the completed month-end boundary immediately before `M`.

`origin(M) = completed month-end boundary of M-1`

The target is the next calendar month's average XAU/USD price.

Current September 2026 information boundary:

`2026-08-31T21:00:00Z` = 31 Aug 2026 17:00 ET.

A month-open snapshot is immutable. Later intramonth observations may update tactical, emergency, event and risk context, but may not rewrite the month-open snapshot.

---

## 6. September 2026 current references

The following values were reconstructed from the completed 31-Aug information boundary. They are current September references, but they are not backdated prospective issuance evidence.

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

---

## 7. Current motor semantics

### `VW_MIDAS_MSVR_SUCCESSOR_V1`
Current VW/MSVR model identity. Frozen 8-feature four-metal MSVR with origin-local GPR point-in-time input. Historical replay window is 2023-01..2026-07, N=43. Historical replay MAPE is `2.69106498%` versus Random Walk `3.30232202%`. Historical replay success is evidence, not proof of future superiority.

The 31-Aug → September value is an origin reconstruction. A later genuinely prospective validation at the next eligible origin is a separate evidence milestone and does not block the September reference.

### `CAUSAL_PATCH`
Current monthly H=1 expert. Completed-session/PIT safeguards remain part of its executable model identity. It has no selector or action authority.

### `MOMENTUM_3M`
Current monthly H=1 expert. Its H=1 price output is distinct from `MONTHLY_DIRECTION_3M`.

### `RANDOM_WALK`
Mandatory same-origin naive benchmark.

### `MONTHLY_DIRECTION_3M`
Strategic monthly direction/prior context. Direction vote permitted only within the frozen direction-support semantics; it is not an H=1 price forecast.

### `FAST`
Short-horizon tactical context. Current frozen rule uses completed daily XAU observations and the SMA20/persistence logic. It is intended to detect early directional conflict/reversal relative to the slower monthly context.

### `SLOW`
Slower tactical confirmation context using completed weekly observations and the SMA4/persistence logic.

### `MACRO_EVENT_SUCCESSOR_V2`
Timestamp-safe labor-event risk/context. It is not an H=1 price forecast and has no automatic action authority. Event information that arrives after the month-open origin remains intramonth context and is never retroactively inserted into the month-open snapshot.

### `BOCPD_RETURN_SUCCESSOR_V1`
Regime/break context only. No H=1 price forecast, no direction vote and no automatic action.

### `EMERGENCY_LEVEL`
Intramonth abnormal-level detector. The month-open state is initialized from the frozen monthly reference and must later be evaluated only from completed target-month observations.

### `EMERGENCY_REVERSAL`
Intramonth peak/trough reversal detector. It is alert/context only and cannot automatically flip a position.

### `GVZ_RISK`
Volatility/risk context only. It never predicts gold direction.

---

## 8. Current source surface

Current operational market reference for completed daily XAU decision context:

`XAU_EOD_TWELVE_NY17`

Semantics: Twelve Data `XAU/USD`, 1-minute source, New York time, internal 17:00 ET reference derived from the 16:59 bar. It is not labelled an official settlement.

Current live display source remains separate from model authority. Research-only sources remain separate from operational source identities.

The current database surface must expose only current source-registry rows through `current_source_registry_v1`. Superseded zero-observation registry placeholders are not part of the current source surface.

---

## 9. Current production runtime surface

The application/runtime authority view is:

`current_engine_runtime_state_v1`

It must expose exactly the 12 current governed identities and no superseded identity.

Expected current count:

- `ACTIVE = 12`
- `WAITING = 0`
- `BLOCKED = 0`
- total = `12`

This count means the current runtime references are registered and observable. It does not by itself prove that every intramonth refresh schedule is fresh; data freshness is audited separately.

Immutable historical execution rows may remain in the underlying append-only audit ledger. They are not current application identities and must never be read through the current runtime view.

---

## 10. Current evidence semantics

Evidence classes must remain explicit:

- `HISTORICAL_REPLAY` / origin reconstruction: computed later from a frozen historical information boundary;
- `PROSPECTIVE_SHADOW`: issued at a real future origin before target realization;
- `LIVE_PRODUCTION`: only when separately authorized and legitimately issued.

Reconstruction may never be relabelled as prospective evidence.

---

## 11. Current application contract

The current application reads:

- current 12-motor runtime state;
- current derived direction/risk context;
- separately issued expert forecasts/references;
- current market display data;
- canonical forecast/decision stores only if later legitimately populated.

The application must not depend on date-specific replay modules, version-specific migration helpers or superseded snapshot contracts.

The only committed fallback snapshot contract is the current production display snapshot contract defined in `apps/production_display_snapshot.py`.

---

## 12. Clean-current-surface gate

Before this manifest becomes canonical, the v1.41 clean-current-surface audit must prove:

1. current application/runtime code contains no superseded engine identity;
2. no stale WAITING/NOT_ISSUED default remains for the current September state;
3. no superseded snapshot contract remains accepted by current code;
4. date-specific replay modules are absent from the current application path;
5. current source registry exposes no zero-dependency superseded placeholder rows;
6. current runtime view contains exactly 12 current identities;
7. production authority stores remain unchanged unless explicitly authorized;
8. current tests and observability tests pass;
9. the committed production display snapshot matches the current production surface.

Only after this gate passes should work continue on the live intramonth refresh chain (`XAU → FAST/SLOW → Emergency → GVZ → UI`).
