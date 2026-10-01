# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 5 Forecast-Head Reconciliation Authority

**Date:** 2026-10-01  
**Status:** FROZEN PRE-RUN AUTHORITY  
**Parent:** `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_PROJECT_MANIFEST.md`

## 1. Mission

Reconcile the three frozen H3 forecast heads into one origin-level tactical forecast object without fitting a new predictive model and without optimizing trading P&L.

Frozen H3 heads:
- direction: CORE3 / XGB_CLASS
- point return: GOLD_ONLY / LGBM_REG
- distribution: GOLD_ONLY / LGBM_QUANT.

2025 remains forbidden for rule selection.

## 2. Authoritative prediction sources

Use only corrected Stage-2 H3 OOS predictions:
- run 36874561989
- artifact 11167744845.

No refit or regeneration is allowed in Stage 5.

## 3. Reconciliation inputs

For each DEV origin:

- `p_up` = frozen H3 XGB UP probability
- `ret_hat` = frozen H3 LightGBM point-return forecast
- `q10`, `q50`, `q90` = frozen H3 Quantile-LightGBM forecasts
- `sigma20` = origin-known Gold 20-observation volatility.

Volatility-normalized H3 scale:

`hvol = sigma20 * sqrt(3)`.

## 4. Fixed head votes

### Direction vote
- UP if `p_up >= 0.55`
- DOWN if `p_up <= 0.45`
- NEUTRAL otherwise.

### Point-return vote
Magnitude dead-band:
- `deadband = 0.25 * hvol`.

Then:
- UP if `ret_hat > +deadband`
- DOWN if `ret_hat < -deadband`
- NEUTRAL otherwise.

### Distribution-median vote
- UP if `q50 > +deadband`
- DOWN if `q50 < -deadband`
- NEUTRAL otherwise.

Thresholds are semantic and fixed before inspecting reconciliation outcomes.

No threshold search is allowed.

## 5. Directional consistency state

Exactly one state per origin:

### ALIGNED_UP
All three votes = UP.

### ALIGNED_DOWN
All three votes = DOWN.

### LOW_CONVICTION
At least two of three votes are NEUTRAL and there is no direct UP-vs-DOWN conflict among the non-neutral votes.

### MIXED
All remaining combinations, including explicit head disagreement.

## 6. Distribution risk flags

These are orthogonal to the directional state.

### HIGH_DOWNSIDE
`q10 <= -1.0 * hvol`.

### STRONG_UPSIDE
`q90 >= +1.0 * hvol`.

An origin may have:
- neither flag
- HIGH_DOWNSIDE only
- STRONG_UPSIDE only
- both.

## 7. Final display state

For one compact daily forecast object:

- `ALIGNED_UP_LOW_RISK` = ALIGNED_UP and not HIGH_DOWNSIDE
- `ALIGNED_UP_HIGH_RISK` = ALIGNED_UP and HIGH_DOWNSIDE
- `ALIGNED_DOWN` = ALIGNED_DOWN
- `LOW_CONVICTION` = LOW_CONVICTION
- `MIXED` = MIXED.

Risk flags remain separately visible even when the compact state does not encode them.

## 8. Supporting horizon context

H1 and H5 are not allowed to override the H3 state in Stage 5.

They may be displayed later as supporting context only.

The H5 TFT Q50 result remains supporting evidence and does not enter Stage-5 state construction.

## 9. Evaluation

DEV only:
- 2022-2024
- same 749 H3 origins.

For every directional/final state report:
- count / frequency
- realized H3 UP rate
- mean / median realized H3 return
- realized return standard deviation
- realized loss frequency
- severe-downside frequency
- strong-upside frequency.

Realized tail events use the same origin-known H3 scale:

- severe downside: `realized_r3 <= -1.0 * hvol`
- strong upside: `realized_r3 >= +1.0 * hvol`.

## 10. State usefulness gates

Stage 5 is a **usefulness audit**, not a model-selection competition.

### ALIGNED_UP usefulness PASS
Require:
- at least 30 DEV origins
- realized UP rate >= unconditional DEV UP rate + **7 percentage points**
- mean realized H3 return > 0
- each DEV year contains at least 5 ALIGNED_UP origins.

### ALIGNED_DOWN usefulness PASS
Require:
- at least 30 DEV origins
- realized DOWN rate >= unconditional DEV DOWN rate + **7 percentage points**
- mean realized H3 return < 0
- each DEV year contains at least 5 ALIGNED_DOWN origins.

### HIGH_DOWNSIDE flag usefulness PASS
Require:
- at least 30 flagged origins
- severe-downside frequency >= unconditional severe-downside frequency + **5 percentage points**.

### LOW_CONVICTION diagnostic
No promotion gate.
Report whether absolute realized return is lower than unconditional absolute realized return.

### MIXED diagnostic
No promotion gate.
Report whether outcomes are less directional / less reliable than aligned states.

## 11. Forecast-object promotion logic

The reconciliation architecture is **USEFUL PASS** if at least one of:
- ALIGNED_UP
- ALIGNED_DOWN
- HIGH_DOWNSIDE

passes its frozen usefulness gate.

If none pass:
- keep the three heads separate;
- do not manufacture a tactical state.

If pass:
- freeze the state architecture exactly as defined above;
- no threshold retuning.

## 12. Robustness

For ALIGNED_UP / ALIGNED_DOWN / HIGH_DOWNSIDE report:
- 2022
- 2023
- 2024
- LOW / MID / HIGH pre-frozen volatility buckets.

No post-hoc regime gate may be created.

## 13. No trading layer yet

Stage 5 does not optimize:
- entry
- exit
- holding period
- stop
- take profit
- transaction cost
- position size
- Sharpe / Sortino.

Those belong to Stage 6 only after the forecast object is frozen.

## 14. Required outputs

- origin-level reconciled forecast table
- state summary
- year summary
- volatility summary
- risk-flag summary
- usefulness decisions
- immutable hashes.

## 15. Exact next decision

If Stage 5 passes:
- freeze the daily H3 forecast object;
- proceed to Stage 6 tactical allocation / utility design.

If Stage 5 fails:
- keep separate H3 heads and design Stage 6 around raw head outputs without categorical state labels.
