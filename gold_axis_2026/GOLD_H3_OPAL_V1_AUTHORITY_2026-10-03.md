# OPAL-H3 V1 — OPTIONS POSITIONING ASYMMETRY LAYER AUTHORITY

**Date:** 2026-10-03
**Identity:** `OPAL_H3_V1_RESEARCH`
**Parent:** `AURORA_H3_V1_RESEARCH`
**Motivation ancestors:** `RIFT_H3_V1_RESEARCH`, `TURN_H3_V1_RESEARCH`, `VEGA_H3_V1_RESEARCH`
**Status:** PREREGISTERED / POST-HOC MECHANISM RESEARCH

## 1. Scientific question

AURORA's structural blind spot is H3 reversal after strong 12-hour momentum.

Realized-price reversal signals and directionless implied-volatility information were insufficient.

OPAL tests a new directional derivatives-market channel:

> do delta-adjusted options-only trader positions reveal asymmetric directional pressure that helps identify when current XAU momentum is vulnerable to reversal?

## 2. Official source

U.S. CFTC Disaggregated Commitments of Traders (COT), COMEX Gold contract code **088691**.

For each year 2021-2026:
- Disaggregated Futures Only annual compressed file:
  `fut_disagg_txt_<YEAR>.zip`
- Disaggregated Futures-and-Options Combined annual compressed file:
  `com_disagg_txt_<YEAR>.zip`

The CFTC combined report includes delta-adjusted options positions. Options-only trader exposure is reconstructed as:

`OPTIONS_ONLY_POSITION = COMBINED_POSITION - FUTURES_ONLY_POSITION`.

This reconstruction follows published commodity-options hedging-pressure research.

## 3. Availability / anti-leakage

COT positions are measured as of Tuesday and ordinarily released Friday at 15:30 ET.

For conservative historical availability, OPAL assigns:

`available_date = report_as_of_date + 7 calendar days`.

Thus an H3 origin may use only a COT report whose as-of date is at least 7 calendar days old.

This intentionally sacrifices freshness to avoid holiday/publication-time leakage.

## 4. Options-only state

For each report:

### Delta-adjusted options-only net exposures
Each divided by combined open interest:
- `opt_mm_net` = managed-money net options delta / OI
- `opt_prod_net` = producer/merchant net options delta / OI
- `opt_swap_net` = swap-dealer net options delta / OI
- `opt_other_net` = other-reportable net options delta / OI

where net = long - short.

### Weekly change
- one-report change in each normalized options-only net exposure.

### Rolling extremeness
Using previous 52 available reports only:
- `opt_mm_z52`
- `opt_prod_z52`
- `opt_swap_z52`
- `opt_other_z52`.

### Cross-cohort asymmetry
- `spec_hedger_gap = opt_mm_net - opt_prod_net`
- `spec_swap_gap = opt_mm_net - opt_swap_net`.

### Futures control
- `fut_mm_net` = managed-money futures-only net / futures-only OI
- `fut_prod_net` = producer futures-only net / futures-only OI.

## 5. Momentum-conditioned features

Same validated IRIS 1-hour XAU source:
- 16:00 America/New_York anchor;
- `trend_sign = sign(h_ret_12)`.

Fixed model feature set:

1. opt_mm_net
2. opt_prod_net
3. opt_swap_net
4. opt_other_net
5. d_opt_mm_net
6. d_opt_prod_net
7. opt_mm_z52
8. opt_prod_z52
9. opt_swap_z52
10. opt_other_z52
11. spec_hedger_gap
12. spec_swap_gap
13. fut_mm_net
14. fut_prod_net
15. trend_sign * opt_mm_net
16. trend_sign * opt_prod_net
17. trend_sign * spec_hedger_gap
18. trend_strength = abs(h_ret_12)/(h_rv_12+eps).

No feature search is permitted.

## 6. Reversal head

Target:
`REVERSAL = 1[sign(H3 return) != sign(h_ret_12)]`.

Model:
- StandardScaler
- LogisticRegression C=1.0
- class_weight=balanced
- monthly expanding refit
- target maturity enforced.

No hyperparameter search.

## 7. Fixed routing

AURORA remains default.

Only if:
- AURORA direction agrees with 12h momentum; and
- OPAL `p_reversal >= 0.70`

then flip AURORA.

Otherwise keep AURORA.

Threshold 0.70 is frozen before the run.

## 8. Evaluation

Architecture discovery is post-hoc after historical error inspection; therefore all 2022-2026 evidence is **RETROSPECTIVE_MECHANISM_VALIDATION**.

Report:
- 2022 H2
- 2023
- 2024
- 2025
- 2026
- 2023-2024
- 2025-2026.

Mechanism pass requires:
- 2023 accuracy >= AURORA -1 pp
- 2024 accuracy >= AURORA -1 pp
- 2023 Brier <= AURORA +0.003
- 2024 Brier <= AURORA +0.003
- 2023-2024 balanced accuracy >= AURORA
- 2023-2024 net rescue > 0.

## 9. Dependence-aware inference

If mechanism passes:
- paired circular moving-block bootstrap
- 10,000 replicates
- block lengths 5 and 10
- OPAL vs AURORA
- periods 2023-2024, 2025-2026, 2026.

## 10. Governance

No 2022-2026 result may change:
- CFTC report family
- 7-day availability lag
- options-only reconstruction
- feature set
- model class / C
- reversal threshold.

Frozen AURORA prospective validation remains untouched.
