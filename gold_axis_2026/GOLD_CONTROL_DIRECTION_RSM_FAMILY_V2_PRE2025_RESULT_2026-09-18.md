# GOLD CONTROL — DIRECTION_RSM_FAMILY_V2_RESEARCH PRE-2025 CHECKPOINT

**Date:** 2026-09-18  
**Identity:** `DIRECTION_RSM_FAMILY_V2_RESEARCH`  
**Status:** `PRE2025_FAMILY_CHECKPOINT_COMPLETE / FROZEN_BEFORE_2025_REPLAY`  
**Preregistration:** `gold_axis_2026/GOLD_CONTROL_DIRECTION_RSM_FAMILY_V2_PREREG_2026-09-18.md`  
**Implementation:** `gold_axis_2026/tools/direction_rsm_family_v2_research.py`

## 1. Corrected source-family specification

This checkpoint corrects the earlier overly narrow treatment of the first direction motor.

Source-faithful family:
- RSM(26), RSM(52), RSM(104);
- ERSM(26), ERSM(52), ERSM(104).

The source paper also evaluates 156, 208, 260, 520 and 780 weeks, but these are not pre-2025 evaluable from the retained same-source March-2022 history. No older provider is spliced to manufacture those windows.

RSM:
`P=(1/k)sum x_i`.

ERSM:
`alpha=2/(k+1)`;
`w_i=alpha(1-alpha)^(t-i)`;
`P=sum w_i x_i`.

The finite ERSM weights are not renormalized.

Direction:
UP iff `P>=0.5`.

## 2. Corrected weekly return construction

The source paper calculates daily percentage returns and aggregates them into weekly returns.

V2 therefore uses:
`r_d=C_d/C_(d-1)-1`
and
`r_w=sum r_d`
inside Monday-start calendar weeks.

Pre-2025 construction audit:
- comparable weeks = 148;
- sign matches versus the previous weekly-close log-return construction = 148;
- mismatches = 0;
- concordance = 100%.

Thus the earlier weekly-close implementation happened to produce identical pre-2025 binary signs, but V2 retains the source-text-faithful daily-percentage aggregation.

## 3. Own-support results

| Variant | Period | n | Accuracy | Balanced acc. | UP sens. | DOWN sens. | Forecast UP/DOWN | Brier | Log loss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RSM-26 | 2023 | 52 | 0.5000000 | 0.4970238 | 0.5357143 | 0.4583333 | 28 / 24 | 0.2509672 | 0.6950592 |
| RSM-26 | 2024 | 53 | 0.5094340 | 0.5000000 | 1.0000000 | 0.0000000 | 53 / 0 | 0.2623925 | 0.7184658 |
| RSM-52 | 2023 | 44 | 0.5454545 | 0.5747368 | 0.3600000 | 0.7894737 | 13 / 31 | 0.2520676 | 0.6973116 |
| RSM-52 | 2024 | 53 | 0.5094340 | 0.5007123 | 0.9629630 | 0.0384615 | 51 / 2 | 0.2533563 | 0.6999508 |
| RSM-104 | 2024 | 45 | 0.4888889 | 0.4450000 | 0.8400000 | 0.0500000 | 40 / 5 | 0.2536530 | 0.7004721 |
| ERSM-26 | 2023 | 52 | 0.5000000 | 0.5238095 | 0.2142857 | 0.8333333 | 10 / 42 | 0.2647375 | 0.7241539 |
| ERSM-26 | 2024 | 53 | 0.3773585 | 0.3796296 | 0.2592593 | 0.5000000 | 20 / 33 | 0.2697213 | 0.7331154 |
| ERSM-52 | 2023 | 44 | 0.4545455 | 0.5200000 | 0.0400000 | 1.0000000 | 1 / 43 | 0.2690515 | 0.7322004 |
| ERSM-52 | 2024 | 53 | 0.3962264 | 0.3995726 | 0.2222222 | 0.5769231 | 17 / 36 | 0.2588254 | 0.7108836 |
| ERSM-104 | 2024 | 45 | 0.4222222 | 0.4750000 | 0.0000000 | 0.9500000 | 1 / 44 | 0.2606160 | 0.7144667 |

RSM-104 and ERSM-104 have no 2023 OOS block because 104 weeks of same-source warm-up are not yet available.

## 4. Fair 2024 common-support comparison

All six variants are simultaneously eligible beginning target week **2024-02-26**. The common-support set contains 45 target weeks with 25 UP and 20 DOWN outcomes.

| Variant | Accuracy | Balanced acc. | Forecast UP/DOWN | Brier | Log loss |
|---|---:|---:|---:|---:|---:|
| RSM-26 | 0.5555556 | 0.5000000 | 45 / 0 | 0.2537804 | 0.7008762 |
| RSM-52 | 0.5555556 | 0.5000000 | 45 / 0 | **0.2526134** | **0.6984772** |
| RSM-104 | 0.4888889 | 0.4450000 | 40 / 5 | 0.2536530 | 0.7004721 |
| ERSM-26 | 0.3777778 | 0.3900000 | 17 / 28 | 0.2668947 | 0.7273382 |
| ERSM-52 | 0.3777778 | 0.3950000 | 15 / 30 | 0.2600271 | 0.7132773 |
| ERSM-104 | 0.4222222 | 0.4750000 | 1 / 44 | 0.2606160 | 0.7144667 |

## 5. Interpretation before 2025

The corrected family evaluation does **not** establish a robust pre-2025 Gold direction edge.

- RSM-52 is the strongest-looking RSM member in 2023 and has the best Brier/log-loss among RSM variants on the fair 2024 common support, but both RSM-26 and RSM-52 collapse to all-UP on that common 2024 support.
- RSM-104 produces some DOWN calls but has balanced accuracy 0.445 on common support.
- All three source-form ERSM variants are weak in 2024. ERSM-104 is heavily DOWN-degenerate.
- No source-feasible variant shows stable two-sided discrimination across pre-2025 periods.

No Gold-specific winner is selected here. All six source-grounded variants are now frozen and will be replayed unchanged in 2025. The 2025 result cannot be used to choose k, RSM versus ERSM, alpha, normalization or threshold under V2.
