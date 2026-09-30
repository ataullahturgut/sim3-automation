# GOLD MONTHLY — Anchored vs Expanding Regime Detector Comparison V1 Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / REGIME-ONLY COMPARISON  
**Parent:** Market Regime Walk-Forward Detection V1  
**Purpose:** test whether repeatedly re-fitting the HMM each month causes state-definition drift and delayed transition recognition.

## 1. Systems compared

### A. EXPANDING-REFIT
At each completed month t:
- train on all market-state months strictly before t;
- re-fit StandardScaler, PCA and 3-state diagonal Gaussian HMM;
- then filter month t.

This must reproduce the already-completed Walk-Forward V1 run.

### B. ANNUAL-ANCHORED
At the start of each calendar year Y:
- train StandardScaler, PCA and the 3-state HMM once using data through Y-1 December;
- freeze those parameters for every month of year Y;
- technical warm-up exception for the first partial replay year only: because the effective panel begins 2010-07 and the minimum history is 60 months, the 2015 replay is anchored at **2015-06** and covers 2015-07..2015-12. This exception is determined solely by data availability and is fixed before successful execution;
- only the filtered posterior is updated month by month during Y.

Thus state definitions cannot drift intra-year.

### C. STRICT-2024-ANCHOR sensitivity
For 2025-01..2026-08 only:
- fit once through 2024-12;
- keep scaler/PCA/HMM fixed through the entire 20-month period;
- sequentially update posterior only.

This is a sensitivity check for the hypothesis that 2025 data used in a 2026 annual re-anchor could itself shift state definitions.

## 2. Frozen architecture

- K=3, inherited from Market Regime Discovery V1.
- 13 market-state features only.
- PCA target >=85% explained variance, min 2, max 6 components.
- 10 deterministic HMM seeds; highest training likelihood retained.
- posterior confidence <60% => BELIRSIZ.
- OOD: current maximum emission log-density below the training-history 5th percentile.

No model is allowed to use forecast errors, alarms, HIGH/MEDIUM/NORMAL labels, model forecasts or routing outputs.

## 3. Evaluation period

- full replay: 2015-07..2026-08;
- core recent: 2022-01..2026-08;
- 2025-01..2026-08 transport/inspection period.

2025/2026 is already opened for regime-detector evaluation and is not described as untouched.

## 4. Primary non-circular comparison metric

Because latent regime labels have no directly observed ground truth, the primary model comparison is **one-step-ahead predictive log score of the current market-state vector**, computed before observing month t:

log p(x_t | data through t-1, frozen/refitted model).

Higher average predictive log score is better.

Report:
- mean predictive log score;
- median predictive log score;
- total predictive log score;
- per-month paired score difference ANCHORED - EXPANDING;
- count/share of months where anchored is better.

## 5. Secondary descriptive diagnostics

Reference labels from Market Regime Discovery V1 may be used only after both detectors have produced their outputs.

Report for each detector:
- BELIRSIZ rate;
- OOD rate;
- exact agreement with reference labels;
- strict R-state accuracy on reference-confident months;
- per-regime recall;
- balanced accuracy;
- confusion matrix.

These label-agreement measures are **secondary** because the reference is itself HMM-derived and not independent ground truth.

## 6. Transition diagnostics

Mandatory:
- 2024-04 R1 -> R2 onset;
- 2026-05/06 ambiguity zone;
- 2026-07/08 R1 stabilization.

For each detector show:
- state;
- posterior confidence;
- BELIRSIZ status;
- predictive log score;
- OOD flag.

Also report confident-reference transition detection delays.

## 7. Interpretation rule

Do not select a detector from reference-label agreement alone.

Anchored HMM is supported as the next operational regime candidate only if:
- it does not materially worsen predictive log score versus expanding-refit in the core recent period;
- it preserves acceptable R2 transition behavior around 2024-04;
- and it improves or at least does not worsen the 2026 transition-zone behavior.

If evidence is mixed, retain both as research models and do not move to alarm weighting.

## 8. Governance

This study does not:
- select or suppress alarms;
- weight alarms;
- tune alarm thresholds;
- correct forecasts;
- route between forecasting models.

Alarm-conditioned work remains blocked until the regime detector is sufficiently stable.


## Technical amendment before successful execution

The first workflow attempt failed before producing any comparison result because a January-2015 annual anchor has only 54 complete months (2010-07..2014-12), below the pre-existing 60-month minimum-history gate. No model-comparison statistics were observed.

The implementation therefore applies the data-availability rule stated above: 2015-07..2015-12 is frozen from a 2015-06 anchor (60 months); 2016 onward uses the normal prior-December annual anchor. All other design and interpretation rules remain unchanged.
