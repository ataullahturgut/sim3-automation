# RIFT-H3 V1 — REVERSAL IMBALANCE & FAT-TAIL TRIGGER AUTHORITY

**Date:** 2026-10-02
**Identity:** `RIFT_H3_V1_RESEARCH`
**Parent:** `AURORA_H3_V1_RESEARCH`
**Status:** PREREGISTERED / POST-HOC MECHANISM RESEARCH

## 1. Problem discovered

AURORA is structurally strong when the most recent 12-hour XAU momentum continues, and structurally weak when the next H3 outcome reverses that momentum.

Observed retrospective anatomy:
- 2023 continuation accuracy ~93%, reversal accuracy ~28%
- 2024 continuation accuracy ~92%, reversal accuracy ~33%
- 2025 continuation accuracy ~91%, reversal accuracy ~18%
- 2026 continuation accuracy ~95%, reversal accuracy ~16%.

This architecture was motivated after inspecting historical errors including 2026. Therefore **none of 2022-2026 is claimed as a pristine untouched lockbox for the architecture**. All results are retrospective mechanistic evidence. Only future frozen origins can provide prospective proof.

## 2. Scientific hypothesis

Commodity momentum reversals contain nonlinear information in:
- realized upside/downside semivariance imbalance;
- trend deceleration;
- adverse-session pressure;
- jump concentration;
- path consistency;
- location within the recent range.

This follows evidence that realized semivariance helps identify time-series momentum reversals in commodity futures and that realized moments/jumps contain predictive information for gold futures.

RIFT does not re-predict UP/DOWN directly. It predicts:

`REVERSAL = 1[ sign(H3 return) != sign(last 12h return) ]`.

## 3. Information set

Same validated IRIS 1-hour XAU source and 16:00 America/New_York anchor.

Only origin-time features are used.

Derived fixed features:

1. `trend_strength = |h_ret_12| / (h_rv_12 + eps)`
2. `opposite_semivar_share`
   - if h_ret_12 >= 0: downside semivariance share
   - if h_ret_12 < 0: upside semivariance share
3. `deceleration_6h = -sign(h_ret_12) * (2*h_ret_6 - h_ret_12) / (h_rv_12 + eps)`
4. `session_against_trend = -sign(h_ret_12) * h_session_ret / (h_rv_12 + eps)`
5. `path_consistency = sign(h_ret_12) * (2*h_upfrac_24 - 1)`
6. `trend_close_location`
   - up trend: h_close_location_24
   - down trend: 1 - h_close_location_24
7. `opposite_extreme_recency`
   - up trend: 1/(1+h_age_max_neg_24)
   - down trend: 1/(1+h_age_max_pos_24)
8. `h_jump_concentration_24`
9. `trend_to_range = |h_ret_12|/(h_range_24+eps)`
10. `adverse_excursion`
   - up trend: -h_max_drawdown_24/(h_range_24+eps)
   - down trend: h_recovery_24/(h_range_24+eps)

No feature search is permitted in V1.

## 4. Reversal head

Model:
- StandardScaler
- LogisticRegression C=1.0
- class_weight=balanced
- monthly expanding refit
- training rows must have `target_end_date_h3 <= first test feature cutoff`.

No random split.

## 5. Fixed correction rule

AURORA remains default.

At each origin:
- compute `p_reversal`.
- if AURORA direction already opposes the 12h momentum: **do not override**.
- if AURORA follows 12h momentum and `p_reversal >= 0.70`: flip the direction.
- otherwise retain AURORA.

Probability for a flipped call:
- if 12h momentum is UP: `p_up = 1 - p_reversal`
- if 12h momentum is DOWN: `p_up = p_reversal`.

The threshold 0.70 is fixed before the run. It is not searched.

## 6. Evaluation

Because architecture discovery used later historical errors, all years are labeled **RETROSPECTIVE_MECHANISM_VALIDATION**.

Report separately:
- 2022 H2
- 2023
- 2024
- 2025
- 2026
- 2023-2024
- 2025-2026.

A mechanism pass requires:
- 2023 accuracy >= AURORA -1 pp
- 2024 accuracy >= AURORA -1 pp
- 2023 Brier <= AURORA +0.003
- 2024 Brier <= AURORA +0.003
- aggregate 2023-2024 balanced accuracy >= AURORA
- aggregate 2023-2024 net rescue > 0.

If passed, 2025/2026 are descriptive stress evidence only, not clean transport proof.

## 7. Dependence-aware audit

If mechanism passes:
- circular moving-block bootstrap
- 10,000 replicates
- block lengths 5 and 10
- paired RIFT vs AURORA
- 2023-2024, 2025-2026, 2026.

## 8. Prospective governance

The existing frozen AURORA prospective ledger is not modified.

If RIFT passes retrospectively:
- create a separate frozen challenger identity;
- only new origins after that freeze count as prospective RIFT evidence.
