# GOLD MONTHLY — ADPRR-v1 TECHNICAL CORRECTION

**Date:** 2026-10-02  
**Status:** FROZEN BEFORE SUCCESSFUL SCIENTIFIC RUN  
**Reason:** The first execution failed before producing any model result.

## Failure

Workflow `37018150849` stopped at the source-build stage with:

`PIT_FEATURE_TABLE_TOO_SMALL n=52`

The cause is not a model-performance result. The original implementation incorrectly assumed that an origin-specific GPR vintage exists for the entire 2010+ historical calibration span.

No DEV, 2025 or 2026 ADPRR result was produced or inspected.

## Corrected origin-safe interpretation

For every outer forecast target T:

1. Use exactly the GPR vintage available at T's origin month.
2. Reconstruct all historical CURRENT8 samples using that single outer-origin vintage, exactly as the governed monthly model family does for its training history.
3. Build a **nested historical calibration ledger inside the outer origin**:
   - previous 36 completed target months;
   - for each historical pseudo-target u, fit only on rows earlier than u;
   - PLS1 pseudo-forecast uses its own preceding 12-month component selection inside the outer-origin history;
   - directional experts are trained only on rows earlier than u.
4. Estimate side-specific expert reliabilities and choose the preservation threshold using this historical ledger only.
5. Fit the same experts on all matured rows and forecast T.
6. T's actual value is accessed only after the forecast is fixed for scoring.

This correction removes the false requirement for historical origin-vintage files while keeping the outer forecast origin-safe.

## Frozen V1 parameters after correction

- calibration ledger: 36 historical pseudo-targets
- expert reliability Beta prior: (3,3)
- LONG_EN: C=.30, l1_ratio=.50, balanced
- RECENT60_L2: last 60 observations, balanced
- LOCAL_ANALOG: K=15, pseudo-count=10
- threshold grid: 0.02, 0.05, 0.08, 0.12, 0.16, 0.20, 0.25
- strong-side recall tolerance: 5 percentage points
- price ΣAE tolerance: +2%
- final magnitude: absolute PLS1 predicted log-return
- only direction may be flipped

No parameter was changed in response to model performance because no model performance existed before this correction.
