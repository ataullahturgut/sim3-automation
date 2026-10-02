# GOLD MONTHLY — ADPRR-v1 AUTHORITY

**Date:** 2026-10-02  
**Status:** FROZEN PRE-RUN  
**Model:** Asymmetric Direction-Preserving Reliability Router (`ADPRR-v1`)

## Research question

Can a monthly gold forecasting architecture preserve the side on which a strong price model already performs well, while selectively improving its weaker directional side without materially damaging price error?

The method is intentionally low-capacity because the authoritative DEV set contains only 33 origins.

## Forecast contract

- Target: next-calendar-month average XAU/USD
- Horizon: H=1 month
- Representation: CURRENT8
- Origin: previous completed calendar month
- Random split: none
- Database: READ_ONLY
- DEV: 2022-04..2024-12, n=33
- 2025: locked report-only
- 2026 Jan-Jul: quarantined stress report-only

## Base price anchor

`PLS1 V1` is used as the price-magnitude anchor because:
- it is a top price-error monthly model;
- it is fully reproducible under the CURRENT8 contract across long historical origins;
- it provides a clean model-agnostic anchor for testing directional correction.

The router changes **direction only**. Forecast magnitude is the absolute PLS1 predicted log-return.

## Direction experts

All experts use only origin-known CURRENT8 inputs and are fit chronologically.

### E1 — LONG_EN
Elastic-Net Logistic:
- all prior PIT feature rows
- StandardScaler
- C=0.30
- l1_ratio=0.50
- class_weight=balanced
- saga
- seed 20261001.

### E2 — RECENT60_L2
Recent-memory Logistic:
- last 60 prior PIT rows
- StandardScaler
- C=1.0
- L2
- class_weight=balanced
- lbfgs.

### E3 — LOCAL_ANALOG
Non-parametric analog probability:
- standardized CURRENT8 state
- 15 nearest historical states
- inverse-distance exponential weighting
- 10 pseudo-observation shrinkage toward the historical UP prior.

## Side-conditional reliability

For every forecast month and every expert, reliability is estimated from only the previous 36 already-realized expert forecasts.

Separate Beta-smoothed reliabilities are maintained for:
- expert predicts UP
- expert predicts DOWN.

Beta prior:
- alpha = 3
- beta = 3.

For the current expert vote:
- posterior reliability = (correct + 3) / (calls + 6)
- reliability edge = max(2 * reliability - 1, 0).

Expert contribution:
- signed confidence = 2*p_up - 1
- contribution = reliability edge × signed confidence.

The normalized sum forms the directional rescue score in [-1,1].

This explicitly allows an expert to be trusted when predicting one direction but ignored when its historical reliability is weak on the opposite direction.

## Direction-preservation layer

The PLS1 sign is preserved by default.

An override is allowed only when:
1. rescue-score sign is opposite to the PLS1 direction; and
2. absolute rescue score exceeds an origin-specific threshold.

Threshold grid is frozen:
- 0.02
- 0.05
- 0.08
- 0.12
- 0.16
- 0.20
- 0.25.

For each outer forecast, threshold is selected using only the preceding 36 historical forecast origins.

### Preservation-constrained threshold choice

Within that 36-month calibration window:

1. Compute PLS1 UP recall and DOWN recall.
2. Define the stronger side as the side with higher PLS1 recall.
3. Candidate threshold is eligible only if:
   - strong-side recall is no worse than PLS1 by more than 5 percentage points; and
   - cumulative absolute price error is no more than 2% worse than PLS1.
4. Among eligible thresholds:
   - maximize weak-side recall;
   - tie-break by higher balanced direction accuracy;
   - then lower cumulative absolute error;
   - then larger threshold (more conservative).
5. If no threshold is eligible, do not override PLS1.

Thus the algorithm directly encodes:
**preserve the strong side; improve the weak side; protect price error.**

## Final forecast

Let PLS1 predicted log-return be r_anchor.

- no override: r_final = r_anchor
- UP override: r_final = +abs(r_anchor)
- DOWN override: r_final = -abs(r_anchor)

No magnitude amplification is allowed in V1.

## Evaluation

Primary:
- DEV cumulative absolute price error ΣAE
- DEV Direction Accuracy

Directional diagnostics:
- balanced accuracy
- UP recall
- DOWN recall
- minimum of UP/DOWN recall
- number of direction overrides
- beneficial vs harmful overrides

Price diagnostics:
- MAE
- RMSE
- worst AE
- relative MAE vs random walk.

Required comparison:
- PLS1 anchor
- ChHHO-ANFIS frozen reference
- DE-ABC-RBFNN frozen reference
- FULL7 ANN
- REDUCED4 ANN.

## Anti-overfit rule

No threshold, expert, reliability prior, lookback length, K, safeguard tolerance, or tie-break may change after DEV results are observed.

Any modification is `ADPRR-v2`.

## Paper role

ADPRR-v1 is designed as a model-agnostic asymmetric reliability overlay. Its candidate contribution is not another black-box forecaster, but an interpretable method that:
- decomposes direction-specific reliability;
- preserves a strong base forecaster by default;
- only repairs the historically weak side under explicit price-risk constraints;
- remains fully chronological and origin-safe.
