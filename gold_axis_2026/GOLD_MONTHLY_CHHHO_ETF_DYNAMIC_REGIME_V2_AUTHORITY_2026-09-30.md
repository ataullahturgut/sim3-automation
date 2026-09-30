# GOLD MONTHLY — Gold ETF Dynamic Regime Screen V2 Authority

**Date:** 2026-09-30
**Status:** PRE-REGISTERED EXPLORATORY / FOLLOWS V1 STATIC-ANOMALY REJECTION
**Scope:** origin-safe ETF dynamics only; no routing/model switching.

V1 showed that single-month Q10/Q90 GLD/IAU flow/churn/volume anomalies do not identify the four unexplained HIGH-APE core targets. V2 tests a distinct hypothesis: **flow transition and persistence**, not single-month extremity.

## Calibration
2010-01..2020-12 only.

## Dynamic features
From the same official daily GLD/IAU sources:

- COMBINED_FLOW = mean monthly GLD-tonnes % change and IAU-shares % change.
- FLOW_DELTA1 = COMBINED_FLOW - prior month's COMBINED_FLOW.
- FLOW_SUM3 = rolling 3-month sum of COMBINED_FLOW.
- FLOW_SUM6 = rolling 6-month sum.
- OUTFLOW_STREAK = consecutive months through the origin with COMBINED_FLOW < 0.
- BREADTH2_STREAK = consecutive months through the origin with both GLD and IAU monthly changes < 0.
- GLD_LEVEL_RATIO12 = GLD month-end tonnes / prior-12-month median.
- IAU_LEVEL_RATIO12 = IAU month-end shares / prior-12-month median.

## Frozen historical anomaly flags
Using only 2010-2020 quantiles:
- ETF_FLOW_DETERIORATION_Q10: FLOW_DELTA1 <= Q10.
- ETF_FLOW_SUM3_Q10: FLOW_SUM3 <= Q10.
- ETF_FLOW_SUM6_Q10: FLOW_SUM6 <= Q10.
- ETF_OUTFLOW_STREAK_Q90: OUTFLOW_STREAK >= Q90, with minimum streak 2.
- ETF_BREADTH2_STREAK_Q90: BREADTH2_STREAK >= Q90, with minimum streak 2.
- ETF_GLD_LEVEL_HIGH_Q90: GLD_LEVEL_RATIO12 >= Q90.
- ETF_IAU_LEVEL_HIGH_Q90: IAU_LEVEL_RATIO12 >= Q90.

No thresholds may be fitted to 2021+ model errors.

## Reporting
For the four core targets and all 2021-11..2026-08 rows, report all dynamic features and flags.

Do not create a post-hoc Boolean composite after inspecting results. Each mechanism is evaluated individually.

Monthly WGC aggregate reports are corroboration only, never predictor inputs.
