# GOLD MONTHLY — ChHHO Error Severity V3 Authority

**Date:** 2026-09-30
**Status:** BINDING / SUPERSEDES V2 PRIMARY SEVERITY METRIC

## 1. Primary severity metric

Because the requested severity bands are explicitly percentage error bands, the primary alarm-severity metric is now **APE**:

APE = |forecast price - actual price| / actual price × 100.

Fixed bands:
- **NORMAL:** APE < 2.50%
- **MEDIUM:** 2.50% <= APE < 3.00%
- **HIGH:** APE >= 3.00%

## 2. Robustness metric

Absolute Gold log-return forecast error remains a required secondary robustness check with the same 2.50 / 3.00 percentage-point bands.

Any boundary disagreement between APE and return-error severity must be listed explicitly.

## 3. Model/economic evaluation

Unchanged:
- cumulative absolute USD error ΣAE remains the main economic/model-selection metric;
- direction accuracy remains co-primary;
- alarm severity is separate from model-selection scoring.

## 4. Input authority

Use the frozen row-level output from:
- workflow run 36702363530
- artifact 11090178105
- schema GOLD_MONTHLY_CHHHO_ERROR_SEVERITY_V2_2026-09-30

No model rerun and no alarm-rule retuning are allowed.

## 5. Required reporting

Report:
- APE NORMAL/MEDIUM/HIGH target lists;
- return-error band disagreements;
- A/B/C/D/H performance for APE HIGH;
- A/B/C/D/H performance for APE MEDIUM+HIGH;
- HIGH misses after A/B/C/D/H;
- MEDIUM targets and coverage.

No routing/model switching.
