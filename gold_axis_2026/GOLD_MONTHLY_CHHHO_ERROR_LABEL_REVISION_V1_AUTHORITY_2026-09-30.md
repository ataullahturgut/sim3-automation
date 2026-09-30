# GOLD MONTHLY — Alarm Error Label Revision V1 Authority

**Date:** 2026-09-30
**Status:** PRE-REGISTERED / BINDING ERROR-LABEL AUDIT
**Scope:** alarm research only; no router/model switching.

## 1. Problem

A fixed USD absolute-error threshold is not scale invariant. Gold at 1,800 USD and Gold at 4,500 USD should not be assigned the same model-failure label merely because absolute error crosses the same USD cutoff.

The project objective remains price forecasting and cumulative absolute USD error. This revision changes only the **alarm research target label**, not the model-selection objective.

## 2. Primary alarm error label

Primary:
**HIGH_RETURN_ERROR**

For target t:
- predicted Gold log return = model output;
- actual Gold log return = log(actual target price / origin Gold price);
- absolute return error in percentage points = |predicted - actual| × 100.

Frozen DEV threshold:
**HIGH_RETURN_ERROR if absolute return error > 3.00590 percentage points.**

This is the already-computed DEV Q3 threshold. No threshold search is allowed.

Reasons:
1. it is scale invariant across Gold price levels;
2. it is in the native output space of ChHHO;
3. it measures genuine forecast miss rather than nominal-price scaling.

## 3. Secondary labels

Robustness:
- HIGH_APE: APE > 2.96117% (frozen DEV Q3).

Economic reporting only:
- HIGH_AE: AE > 63.06 USD (frozen DEV Q3).

HIGH_AE is retained in reports because the project's main economic objective is ΣAE, but it is no longer the primary alarm/failure classification.

## 4. Required audit

Reclassify all scientifically usable ChHHO rows:
- valid pre-DEV 2021-11..2022-03;
- canonical DEV 2022-04..2024-12;
- 2025 transport;
- 2026 Jan-Aug.

Report:
- exact high-error target list under AE / APE / RETURN_ERROR;
- all disagreements among labels;
- A/B/C/D/H performance under RETURN_ERROR;
- E/G/GVZ/CFTC descriptors under RETURN_ERROR where available;
- return-error misses after A/B/C/D/H;
- comparison with the previous AE-based interpretation.

## 5. H definition

H remains frozen from the prior screen:
- abs monthly change in CFTC Managed-Money net/OI >= 0.1499821
  OR
- abs monthly open-interest percentage change >= 14.9766%.

No retuning.

## 6. Governance

- Do not modify A/B/C/D/E/G/H thresholds.
- Do not use 2025/2026 error labels to retune any candidate.
- No router/fallback testing.
- Any conclusion that changes only because AE and normalized labels disagree must be stated explicitly.
