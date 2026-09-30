# GOLD MONTHLY — Transition / Change Detector V1 Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / REGIME-ONLY TRANSITION DETECTION  
**Parents:** Market Regime Discovery V1; Walk-Forward V1; Anchored Comparison V1; Prototype Alignment V1

## 1. Scientific question

Can we identify, using only information available at the completed month t, that the incumbent HMM regime is losing validity **before or while** the semantic R0/R1/R2 label changes?

This stage does **not** predict the next regime.

Output layer:
- `STABLE`
- `TRANSITION`

The semantic regime output remains separately:
- R0 / R1 / R2 / BELIRSIZ.

Examples:
- R2 + STABLE
- R2 + TRANSITION
- BELIRSIZ + TRANSITION
- R1 + STABLE

## 2. Systems evaluated

Run the transition layer on both previously governed HMM schedules:

### A. EXPANDING_REFIT
At month t:
- fit scaler/PCA/HMM on data strictly before t;
- filter t once;
- evaluate departure from the raw latent state that was incumbent at t-1 inside that same fit.

### B. ANNUAL_ANCHORED
At year Y:
- fit once through prior December;
- freeze model parameters for year Y;
- filter months sequentially;
- evaluate departure from the previous filtered latent state.

2015 warm-up exception remains unchanged: 2015-07..12 anchored at 2015-06.

Prototype-aligned semantic labels from V1 are reported, but **transition logic uses only within-fit quantities and does not depend on R0/R1/R2 naming**.

## 3. Frozen transition signals

For each completed month t, calculate five origin-safe indicators.

### S1 — posterior erosion
Signal = TRUE if either:
- posterior probability of the incumbent latent state after observing t is < 0.70; or
- incumbent posterior falls by >= 0.20 versus t-1.

### S2 — incumbent emission anomaly
Signal = TRUE if the current observation's emission log-density under the incumbent latent state is at or below the **10th percentile** of the fit's historical training-month incumbent-state emission log densities.

Historical comparison pool:
- training months whose hard filtered state equals that incumbent latent state.
- minimum pool size 8; otherwise S2 is unavailable/False.

### S3 — global predictive surprise
Signal = TRUE if the one-step predictive log score for t is at or below the **10th percentile** of the fit's historical one-step predictive log scores computed sequentially on its training history.

### S4 — multivariate market-state jump
Signal = TRUE if the Euclidean norm of the month-to-month change in the fit's standardized 13-feature market-state vector is at or above the **90th percentile** of historical training month-to-month change norms.

### S5 — confident latent-state switch
Signal = TRUE if:
- current best latent state differs from the t-1 incumbent; and
- current best posterior >= 0.60.

## 4. Frozen transition rule

`TRANSITION` if:
- S5 is TRUE; **or**
- at least **2 of S1..S4** are TRUE.

Otherwise:
- `STABLE`.

No threshold or vote count may be changed after the first successful production result.

Also report:
- number of active signals;
- active signal names;
- incumbent posterior;
- posterior drop;
- incumbent emission percentile;
- predictive-score percentile;
- market-state-jump percentile;
- whether the latent state switched.

## 5. Data and governance

Inputs:
- the same frozen 13 market-state variables used by Market Regime Discovery V1.

Forbidden:
- ChHHO forecasts;
- ChHHO errors;
- alarm A/B/C/D/E/G/H/I/T flags;
- HIGH/MEDIUM/NORMAL labels;
- target-month future information;
- routing/model-switch outcomes.

This detector is completely independent of forecast-performance outcomes.

## 6. Evaluation reference

Discovery V1 semantic regime labels are used **only after detection** for descriptive transition evaluation.

A reference confident-state transition is defined as:
- a change from one confident reference R-state to a different confident R-state;
- reference BELIRSIZ months between them are treated as a bridge, not as a separate regime.

For each transition:
- `transition-zone start` = month immediately after the last confident month of the old state;
- `confirmation month` = first confident month of the new state.

Positive transition-zone months are all months from zone start through confirmation month, inclusive.

Examples:
- direct 2024 R1->R2: zone = 2024-04 only;
- 2026 R2->R1 with May/Jun BELIRSIZ and July confident R1: zone = 2026-05..2026-07.

## 7. Required metrics

For full replay 2015-07..2026-08, core 2022-01..2026-08, and 2025-01..2026-08:

- total months;
- TRANSITION flags;
- flag rate;
- transition-zone months;
- transition-zone recall;
- stable/non-zone months;
- false-transition count;
- false-transition rate among non-zone months;
- precision = flagged transition-zone months / all flags;
- event hit rate: number of reference transitions with >=1 flag inside the transition zone;
- event miss count.

For each reference transition:
- zone start;
- confirmation month;
- first flag inside zone;
- first flag relative to confirmation month:
  - negative = before confirmed new regime;
  - zero = at confirmation;
- if no in-zone flag: MISS.

## 8. Mandatory checkpoints

Report month-level diagnostics for:
- 2024-03..2024-06;
- 2026-04..2026-08.

The key scientific question is whether:
- 2024-04 is identified as transition without excessive prior false flags;
- 2026-05 and/or 2026-06 are identified as transition before the confident R1 confirmation in 2026-07.

## 9. Interpretation rule

This V1 is a fixed-rule diagnostic, not a threshold-optimization exercise.

A detector is not authorized for alarm weighting merely because it catches 2024/2026.

Required for a useful candidate:
- event-level transition hits are materially better than chance-like sparse firing;
- 2024 and 2026 are both detected in-zone;
- non-zone false-transition rate remains operationally tolerable;
- no forecast/alarm outcome information was used.

If both schedules are weak, the next study may calibrate a transition score using an earlier historical development window only; 2025/2026 must not be used for threshold fitting.

## 10. Stage boundary

This stage does not:
- change R0/R1/R2 definitions;
- create a fourth regime;
- test regime-extreme/within-regime stress;
- select/weight/suppress alarms;
- modify the gold forecast;
- route between forecast models.
