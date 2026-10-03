# RTE-H3 V1 — REVERSAL TRANSITION ENGINE PREREGISTRATION

**Date:** 2026-10-03  
**Identity:** `RTE_H3_V1`  
**Branch:** `gold-h3-rte-v1-20261003`  
**Role:** V5 rescue specialist for latent trend-break transition, not a generic UP/DOWN forecaster.  
**Status:** **PREREGISTERED BEFORE RTE RESULTS**

## 1. Research question

RTE-H3 does not ask “is the next H3 UP or DOWN?”

It asks:

> When HELIOS V5-DCE is making a continuation-style call in the same direction as 12h momentum, is that continuation state beginning to transition into a reversal?

The target is therefore conditioned on the exact failure mode we need to solve.

## 2. Evaluation universe

For each H3 origin:
- `v5_pred = 1[p_helios_v5_dce >= 0.5]`
- `momentum_up = 1[h_ret_12 >= 0]`
- eligible if `v5_pred == momentum_up`

Within this eligible universe:
- `rescue_target = 1[v5_pred != y_up]`
- `rescue_target=1` is a V5 missed reversal
- `rescue_target=0` is a V5-correct continuation

RTE never trains on origins where V5 already disagrees with momentum.

## 3. Source clock

Canonical H3 feature cutoff is the existing frozen project cutoff.

CME daily source:
- anonymous FTP: `ftp.cmegroup.com/daily_volume`
- workbook: `daily_volume_YYYYMMDD.xlsx`
- sheet: `CME Group Vol and OI by Product`

Rows used:
- `GC / GOLD FUTURES / F` — Total Volume only
- `OG / GOLD CALL / O` — Total Volume only
- `OG / GOLD PUT / O` — Total Volume only

Open Interest is deliberately excluded from RTE-H3 V1 because the current CME preliminary product workbook stops exposing the expected OI field after 2026-03-19. RTE V1 is designed for full 2026 source coverage.

Origin-safe rule:
> use only the latest source row with `trade_date < feature_cutoff_date`.

Same-day CME volume is forbidden. No lag search is allowed.

## 4. Transition-state inputs

### 4.1 Existing frozen intraday/path state

From `GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv`:
- `h_ret_12`
- `trend_strength`
- `opposite_semivar_share`
- `deceleration_6h`
- `path_consistency`
- `trend_close_location`
- `opposite_extreme_recency`
- `jump_concentration`
- `trend_to_range`
- `adverse_excursion`

From V5:
- `p_helios_v5_dce`
- `v5_confidence = 2*abs(p_helios_v5_dce-0.5)`

### 4.2 CME participation features

From prior-trade-date Gold futures volume:
- `gc_dlog_volume_1`
- `gc_volume_z20`
- `gc_volume_accel_5`

### 4.3 Gold options positioning-pressure proxy

This is **not CVOL skew** and must never be named or interpreted as implied-volatility skew.

Define:
- `call_vol` = OG GOLD CALL Total Volume
- `put_vol` = OG GOLD PUT Total Volume
- `opt_vol_imbalance = (call_vol-put_vol)/(call_vol+put_vol)`
- `d_opt_vol_imbalance_1`
- `opt_total_volume = call_vol+put_vol`
- `opt_total_z20`

Let `s = +1` for upward 12h momentum and `-1` for downward 12h momentum.

Reversal-oriented pressure:
- `signed_opt_pressure = -s * opt_vol_imbalance`
- `signed_d_opt_pressure = -s * d_opt_vol_imbalance_1`

Higher values mean options flow is leaning against the prevailing price momentum.

## 5. Counterfactual continuation twins

The central innovation is to compare each eligible origin with matured historical V5-correct continuations that looked structurally similar before the outcome.

Matching coordinates:
1. momentum direction must be identical
2. `abs(h_ret_12)`
3. `trend_strength`
4. `path_consistency`
5. `v5_confidence`

All continuous coordinates are standardized using the matured training set only.

For each test origin:
- find the **7 nearest matured rescue_target=0 continuations**
- use only rows whose `target_end_date_h3` is already matured before the current monthly test block
- no current/future row may enter the twin pool

For each reversal-pressure variable, compute current value minus the median of the seven continuation twins.

Frozen counterfactual-gap variables:
- `cf_deceleration_gap`
- `cf_opposite_semivar_gap`
- `cf_adverse_excursion_gap`
- `cf_signed_opt_pressure_gap`
- `cf_signed_d_opt_pressure_gap`
- `cf_gc_dlog_volume_gap`
- `cf_opt_total_z20_gap`

The model therefore learns “what differs from a continuation that otherwise looks like this trend?” rather than merely “what does a reversal look like globally?”

## 6. Instant transition estimator

Low-capacity estimator:
- StandardScaler
- LogisticRegression
- C = 0.25
- solver = lbfgs
- class_weight = balanced
- seed = 20261003

This estimator is only a weight-estimation component inside RTE; the RTE architecture is defined by conditional V5 rescue targeting, counterfactual twins, and sequential transition memory.

Frozen model features:
- `v5_confidence`
- `trend_strength`
- `opposite_semivar_share`
- `deceleration_6h`
- `path_consistency`
- `trend_close_location`
- `opposite_extreme_recency`
- `adverse_excursion`
- `gc_dlog_volume_1`
- `gc_volume_z20`
- `gc_volume_accel_5`
- `signed_opt_pressure`
- `signed_d_opt_pressure`
- `opt_total_z20`
- all 7 counterfactual-gap variables above

Monthly expanding-origin refit.
Minimum matured training rows = 100.

## 7. Sequential transition memory

For each eligible origin, let:
- `p_inst` be the instant transition probability
- `base_rate` be the rescue-target prevalence in the matured training set
- `innovation = logit(p_inst) - logit(base_rate)`

Latent tension:
- if previous origin is eligible, momentum direction is unchanged, and feature-cutoff gap <= 5 calendar days:
  `T_t = 0.65*T_(t-1) + innovation_t`
- otherwise:
  `T_t = innovation_t`

Final transition probability:
`p_rte = logistic(logit(base_rate) + T_t)`

The decay coefficient 0.65 is frozen before results.

No decay search is permitted.

## 8. Period roles

- formation / warm-up: 2022
- DEV threshold selection: 2023-01-01 through 2024-12-31
- untouched confirmation: 2025
- final holdout: 2026, opened only if 2025 confirmation passes

## 9. Rescue threshold selection

Frozen grid:
`[0.55, 0.60, 0.65, 0.70, 0.75, 0.80]`

For a threshold `q`:
- RTE candidate if `p_rte >= q`
- candidate action = flip V5 direction

On 2023-2024 DEV:
- rescued = V5 wrong, RTE flip correct
- broken = V5 correct, RTE flip wrong
- net rescue = rescued - broken
- rescue precision = rescued / (rescued + broken)
- candidate rate = candidates / eligible origins

Eligibility constraints:
- rescue precision >= 0.55
- candidate rate <= 0.25
- net rescue > 0

Primary objective:
1. maximize net rescue
2. then maximize rescued count
3. then maximize rescue precision
4. then lower candidate rate
5. then higher threshold

If no threshold is eligible:
`NO_ELIGIBLE_RTE_THRESHOLD`

## 10. 2025 confirmation gate

All must hold:
- net rescue >= +2
- rescue precision >= 0.55
- candidate rate <= 0.25
- RTE-flipped accuracy > V5 accuracy on the same eligible universe

Failure => 2026 remains formally unopened.

## 11. 2026 final holdout

Only after 2025 confirmation PASS:
- eligible origin count
- candidate count/rate
- rescued / broken / net rescue
- rescue precision
- V5 accuracy vs RTE-assisted accuracy on eligible universe
- whole-clean-2026 V5 correct count plus net rescue
- resulting whole-clean-2026 accuracy
- coverage of the previously diagnosed V5 missed-reversal / OPAL-no-candidate set
- overlap with OPAL candidate events

No threshold or feature may change after 2026 is opened.

## 12. Governance

- No random split.
- No same-day CME volume.
- No target or future H3 information in features.
- No 2026 outcome may alter source, features, twin metric, K=7, C, decay, threshold grid or confirmation rule.
- If RTE fails, the result is retained as a negative mechanism test.
- HELIOS V5-DCE remains binding until a separate promotion decision.
