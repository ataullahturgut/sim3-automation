# GOLD CONTROL — UP-2 REGIME-CONDITIONED R2 ANATOMY V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `UP2_REGIME_CONDITIONED_R2_ANATOMY_V1_RESEARCH`  
**Purpose:** Stage-3 diagnostic only; test whether the Stage-2 R2 failure pattern becomes more reliable inside specific origin-safe market regimes.

## 1. Frozen base rule

Use the Stage-2 diagnostic threshold:

`last_hour_trend_r2 >= 0.50`

This threshold is fixed from the pre-2025 strict diagnostic zone and is not changed here.

## 2. Population

Only frozen One-Sided UP-2 calls:
- governed 2022–2024: expected 11 =8 captured UP +3 false-UP actual-DOWN;
- locked 2025: expected 25 =13 captured UP +12 false-UP actual-DOWN.

## 3. Frozen regime axes

All regime variables are origin-safe:

1. `sqrt_score` — frozen normalized SQRT risk intensity.
2. `rv60_ratio` — origin-day RV divided by median RV of the previous 60 governed trading days.
3. `downside_share` — origin-day downside semivariance share.
4. `late_downside_intensity` — final-quarter downside RV divided by full-day RV.
5. `lag1_close_return` — previous-close to origin-close log return.

For each axis, define the cutpoint as the **median among pre-2025 UP-2 calls only**. This is label-agnostic and frozen before inspecting 2025.

For each axis test both:
- HIGH regime: value >= pre-2025 median;
- LOW regime: value < pre-2025 median.

## 4. Conditional veto rule

For each axis-side combination:

`veto iff last_hour_trend_r2 >= 0.50 AND regime_condition_is_true`.

No model is fitted.

## 5. Diagnostic criteria

A rule is **PRE2025_USEFUL** if:
- removes at least 2/3 false-UP actual-DOWN cases;
- retains at least 6/8 captured-UP cases.

A pre-2025 useful rule is **TRANSPORT_CONSISTENT** if unchanged in locked 2025 it:
- removes at least 3/12 false-UP cases (25%);
- retains at least 10/13 captured-UP cases.

2025 does not choose the regime axis, side, or cutpoint.

## 6. Outputs

For every axis and side:
- pre-2025 median cutpoint;
- regime counts;
- false-UP removed;
- captured-UP retained;
- remaining precision;
- locked-2025 unchanged results;
- PRE2025_USEFUL / TRANSPORT_CONSISTENT flags.

## 7. Interpretation

Possible conclusions:
- one or more origin-safe regime conditions stabilize the R2 veto;
- pre-2025 conditioning exists but does not transport;
- no regime condition improves the scalar veto sufficiently.

Diagnostic only. No rule is promoted.

## 8. Governance

- no random split;
- no predictive model;
- no threshold search;
- no 2025 tuning;
- no 2026 use;
- no runtime/production promotion.
