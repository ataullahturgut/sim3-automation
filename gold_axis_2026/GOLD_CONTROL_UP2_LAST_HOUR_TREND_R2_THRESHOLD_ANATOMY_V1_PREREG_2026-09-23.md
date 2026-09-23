# GOLD CONTROL — UP-2 LAST-HOUR TREND-R2 THRESHOLD ANATOMY V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `UP2_LAST_HOUR_TREND_R2_THRESHOLD_ANATOMY_V1_RESEARCH`  
**Purpose:** diagnostic threshold anatomy only; no model fitting, no promotion.

## 1. Exact question

Inside the frozen One-Sided UP-2 call set, does a simple veto of the form

`veto UP2 if last_hour_trend_r2 >= threshold`

remove a useful fraction of false-UP actual-DOWN cases while preserving most captured-UP cases?

This is the exact Stage-2 diagnostic requested after the direction mechanism-gap audit.

## 2. Population

Primary diagnostic:
- governed 2022–2024 frozen UP-2 calls only;
- expected n=11 =8 CAPTURED_UP +3 FALSE_UP_ACTUAL_DOWN.

Locked transport:
- governed 2025 frozen UP-2 calls only;
- expected n=25 =13 CAPTURED_UP +12 FALSE_UP_ACTUAL_DOWN.

Any mismatch blocks interpretation.

## 3. Feature

Only:
- `last_hour_trend_r2`

Definition is frozen exactly as in `DIRECTION_MECHANISM_GAP_AUDIT_V1_RESEARCH`.

No other feature is inspected in this stage.

## 4. Threshold scan

No threshold is fitted.

Evaluate the fixed grid:

`0.00, 0.05, 0.10, ..., 1.00`.

For each threshold t:
- veto call if `R2 >= t`;
- false-UP removed;
- captured-UP lost;
- false-UP removal rate;
- captured-UP retention rate;
- remaining precision among non-vetoed UP2 calls;
- remaining call count.

## 5. Frozen diagnostic regions

A threshold is labeled:

- `USEFUL_PRE2025_ZONE` if:
  - removes at least 2 of 3 pre-2025 false-UPs; and
  - retains at least 6 of 8 captured-UPs.

- `STRICT_PRE2025_ZONE` if:
  - removes all 3 pre-2025 false-UPs; and
  - retains at least 6 of 8 captured-UPs.

These are diagnostic labels only, not deployment rules.

## 6. Locked-2025 transport check

For every threshold that enters either pre-2025 diagnostic zone, report the unchanged 2025 consequences.

A threshold is called `TRANSPORT_CONSISTENT` only if in locked 2025 it:
- removes at least 25% of false-UPs; and
- retains at least 75% of captured-UPs.

2025 is not allowed to choose, tune, or move the threshold.

## 7. Interpretation

Possible outcomes:
- a stable scalar veto zone exists;
- a pre-2025-only zone exists but does not transport;
- no useful scalar veto zone exists.

No logistic model, ensemble, second feature, or downstream change is allowed in this stage.

## 8. Governance

- no random split;
- no model fitting;
- no result-dependent threshold insertion;
- no 2025 tuning;
- no 2026 use;
- no runtime/production promotion.
