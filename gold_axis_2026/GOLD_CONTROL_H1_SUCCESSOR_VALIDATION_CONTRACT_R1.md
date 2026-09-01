# GOLD CONTROL — H=1 SUCCESSOR VALIDATION CONTRACT R1

**Freeze date:** 2026-09-01  
**Reserved model family identity:** `GOLD_H1_SUCCESSOR_R1`  
**Reserved engine lane:** `R4.2-SHADOW-CANDIDATE`  
**Evidence status:** `VALIDATION_CONTRACT_FROZEN; NO_MODEL_APPROVED`

## 1. Objective

Select, if evidence supports it, a reproducible successor for the missing/non-reproducible VW/Patch production path without inheriting either legacy model identity.

The successor must forecast:

> **the next calendar month's average XAU/USD price**

from information genuinely available at:

> **the end of the previous completed calendar month**.

No September 2026 forecast created after 2026-08-31 can satisfy this prospective contract.

## 2. Evidence classes

All historical development/evaluation performed now is:

`HISTORICAL_REPLAY`

It must not be described as genuinely unseen prospective evidence, even if rolling-origin rules are used correctly.

The first possible future evidence class is:

`PROSPECTIVE_SHADOW`

at a real future origin before the target outcome is known.

## 3. Target-data contract

### 3.1 Future operational target definition

Preferred target definition for the successor lane:

`XAU_MONTHLY_AVG_NY17`

Definition:

- arithmetic mean of valid completed trade-date `XAU_EOD_TWELVE_NY17` internal decision-reference observations belonging to the target calendar month;
- no forward fill for a missing exact NY17 observation;
- no use of live Gold API or XAUS display history as target/model input;
- source lineage and retrieval availability retained for every observation.

This target definition is a successor-lane contract and does not rewrite historical R4.1/VW artifacts.

### 3.2 Historical target readiness gate

Before model scoring begins, prove one of the following:

1. sufficiently deep historical `XAU_EOD_TWELVE_NY17` observations can be reconstructed from authorized Twelve Data intraday history under a frozen timestamp/bar mapping; or
2. a separately named historical research lineage is approved under change control and its semantic difference from the future NY17 target is quantified.

Option 1 is preferred.

If neither is proven:

`BLOCKED_SUCCESSOR_HISTORICAL_TARGET_NOT_PROVEN`

No model comparison may be promoted beyond exploratory research.

### 3.3 Historical mapping preference

The production mapping remains exact Twelve `1min` `16:59:00 America/New_York` close.

For deeper history, a coarser Twelve intraday interval may be considered only after an overlap audit proves its derived 17:00 ET reference is semantically compatible with the 1-minute production mapping. It receives its own lineage/version; it is never silently relabeled as the exact 1-minute source.

## 4. Feature-source contract

Initial successor development should prefer the smallest reproducible authority-grade feature surface.

Approved candidate feature domains, subject to source history/availability audit:

- target lags and lagged returns from the frozen successor target lineage;
- Federal Reserve/FRED/ALFRED: `DGS10`, `DFF`, `DEXCHUS`, `DTWEXBGS`;
- FRED index series already approved in the source contract where licensing permits private/internal model use: `SP500`, `DJIA`, `NASDAQ100`;
- Cboe official `VIX` / `GVZ` where relevant;
- official Caldara-Iacoviello GPR/GPRT/GPRA with publication/vintage controls.

Twelve equity/ETF auxiliary features may enter only if their historical coverage and point-in-time contract pass before the candidate score run.

The following are not silently recreated:

- exact ICE DXY;
- legacy `^TNX` identity;
- missing VW `GPY`, `long_term_trend`, `volatility`, `g_volatility` definitions;
- legacy processed proprietary inputs.

## 5. Candidate-set freeze

The following families form `SUCCESSOR_CANDIDATE_SET_R1` once the input-readiness gate passes. All use the same causal target/origin contract.

### Baselines / controls

- `RW_R1` — mandatory naive benchmark; not silently promoted as primary simply because other candidates fail;
- `DRIFT_R1` — simple time-series control;
- `MOM3_R1` — 3-month momentum price challenger/context control.

### Reproducible statistical candidates

- `DAMPED_TREND_R1` — damped trend/ETS-type candidate using target history only;
- `RIDGE_MACRO_R1` — regularized linear model on frozen lag/macro feature set;
- `HUBER_MACRO_R1` — robust linear candidate on the same frozen feature set;
- `SVR_RBF_MACRO_R1` — RBF SVR on the same frozen feature set.

### Conditional architecture candidate

- `PATCH_SUCCESSOR_R1` — may enter only if, **before any comparative score run**, its new approved input pipeline, model code, seeds, preprocessing and fold contract are fully frozen. It is a new model identity and may not inherit `PATCH_R1` production history.

The archived VW rebuilds and legacy `Repro SVR` remain research comparators unless separately admitted by change control before scoring. No auto-selector or auto-ensemble is in Candidate Set R1.

## 6. Leakage-safe historical replay

Rules:

- random split prohibited;
- every forecast origin uses only information available at or before that origin;
- scalers/transformers fit inside each training fold only;
- publication lags and vintages enforced per source;
- model/hyperparameter selection uses inner expanding/rolling origins strictly before the outer origin;
- target-month observations are never used in model fitting, feature construction, selection or weighting;
- no threshold/model-family changes after comparative outer scores are inspected without opening a new versioned change control.

Minimum-history requirements are fixed by the model family before scoring and may not be shortened because a candidate performs poorly.

## 7. Evaluation window

The intended common outer replay starts no later than `2016-01` and runs through `2026-07`, **if and only if** the frozen common input contract provides adequate point-in-time history.

If the common source history cannot support a `2016-01` start, the run must stop as:

`BLOCKED_COMMON_HISTORY_INSUFFICIENT_FOR_FROZEN_WINDOW`

rather than silently moving the evaluation start after seeing results. A revised evaluation window requires a new contract version before model scores are produced.

## 8. Metrics

Primary comparative loss:

- `Relative_MAE_vs_RW = sum(|e_candidate|) / sum(|e_RW|)`.

Report, but do not optimize separately after the fact:

- MAE;
- MAPE;
- sMAPE;
- median absolute error;
- RMSE;
- monthly win rate versus RW;
- directional accuracy as a secondary diagnostic only;
- calendar-year and major-regime breakdowns;
- paired loss-difference bootstrap interval as an uncertainty diagnostic, not a mandatory significance gate.

## 9. Historical shadow-eligibility gate

A candidate may become `HISTORICAL_REPLAY_SHADOW_ELIGIBLE` only if all of the following hold on the same frozen common window:

1. source/provenance/PIT audit = PASS;
2. deterministic rerun/reproduction = PASS;
3. `Relative_MAE_vs_RW < 1.00`;
4. candidate MAPE <= RW MAPE;
5. candidate median absolute error <= RW median absolute error;
6. candidate beats RW in at least half of the completed calendar-year buckets represented by the common replay;
7. no completed calendar-year bucket has candidate MAE > `1.50 ×` RW MAE for that same year;
8. no unresolved leakage, target-definition, or feature-availability exception.

These gates only permit prospective shadow consideration. They do **not** establish live-production superiority.

If no candidate passes, result is:

`REJECT_ALL_SUCCESSOR_CANDIDATES`

and the system remains forecast-blocked.

## 10. Model selection rule

Among candidates that pass every gate:

1. choose the lowest aggregate `Relative_MAE_vs_RW`;
2. tie-break by lower median absolute error;
3. second tie-break by simpler model class / fewer frozen degrees of freedom;
4. retain all other passing candidates as named shadows, not an auto-ensemble.

This ranking is frozen before the comparative score run.

## 11. R4.2 decision-engine bridge gate

Passing the forecast gate does not automatically authorize the successor as a decision reference.

Before an R4.2 prospective decision is written:

- replace the VW-specific snapshot field with generic `monthly_price_reference` + `monthly_price_reference_model_id` in a new versioned contract;
- quantify how the successor reference changes Level Emergency trigger geometry relative to historical R4.1 VW reference;
- do not retune the existing ±4% Level Emergency or Reversal thresholds on 2026 outcomes;
- if threshold semantics are no longer defensible under the new reference, open separate R4.2 threshold validation/change control;
- rerun deterministic engine/bridge tests under the new snapshot schema;
- preserve `NOT_PROVEN_POSITION_MAPPING` and null action state.

## 12. Prospective issuance gate

The first `GOLD_H1_SUCCESSOR_R1` issuance may be written only at a real month-end origin with:

- immutable input snapshot persisted before target realization;
- frozen model code/config SHA;
- frozen source/vintage lineage;
- point forecast and RW benchmark;
- model id/version;
- target definition;
- issued-at timestamp;
- evidence class `PROSPECTIVE_SHADOW`.

For October 2026, the real origin is end-September 2026. If the pipeline is not ready then, do not backfill later.

## 13. Current next gate

`SUCCESSOR_INPUT_READINESS_AUDIT`

The immediate technical question is whether authorized Twelve XAU/USD intraday history is sufficiently deep to construct a source-consistent NY17 historical target and whether a coarser historical interval can be proven compatible with the exact 1-minute production mapping.
