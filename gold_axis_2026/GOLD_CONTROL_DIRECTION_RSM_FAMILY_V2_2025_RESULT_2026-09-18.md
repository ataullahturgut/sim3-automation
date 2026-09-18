# GOLD CONTROL — DIRECTION_RSM_FAMILY_V2_RESEARCH LOCKED 2025 FAMILY REPLAY

**Date:** 2026-09-18  
**Identity:** `DIRECTION_RSM_FAMILY_V2_RESEARCH`  
**Status:** `LOCKED_2025_FAMILY_REPLAY_COMPLETE / EVENT_OVERLAY_NOT_YET_APPLIED`  
**Pre-2025 frozen checkpoint:** `62ff5d2e4b96bc5af5bc0d6830ed8d3bad73fe57`  
**Frozen RSM table:** `GOLD_CONTROL_DIRECTION_RSM_FAMILY_V2_2025_RSM_FORECASTS_2026-09-18.csv`  
**Frozen ERSM table:** `GOLD_CONTROL_DIRECTION_RSM_FAMILY_V2_2025_ERSM_FORECASTS_2026-09-18.csv`

## 1. Frozen source-family rules

No family rule was changed after the pre-2025 checkpoint.

Evaluated variants:
- RSM-26, RSM-52, RSM-104;
- ERSM-26, ERSM-52, ERSM-104.

Weekly return construction follows the source text:
- daily simple percentage return `C_d/C_(d-1)-1`;
- Monday-start weekly return = sum of governed daily percentage returns;
- weekly sign = UP iff weekly summed return > 0.

ERSM uses:
- `alpha=2/(k+1)`;
- `w_i=alpha*(1-alpha)^(t-i)`;
- finite weights are not renormalized;
- UP iff `P>=0.5`.

No 2025-driven k, alpha, normalization or threshold choice was made.

## 2. Important construction correction relative to RSM V1

Pre-2025, source-text weekly-summed daily return signs and the earlier weekly-close log-return signs agreed on all 148 comparable weeks.

In 2025, one week differs:

- target week 2025-07-21;
- source-text weekly summed daily simple return = +0.0000292442 -> UP;
- weekly-close log return = -0.0002180709 -> DOWN.

Therefore the corrected V2 2025 target distribution is:
- 37 UP;
- 15 DOWN.

The earlier narrow RSM V1 used 36 UP / 16 DOWN because it used the weekly-close return construction. V2 supersedes that construction for source-family replication.

## 3. Locked 2025 results

| Variant | Accuracy | Balanced accuracy | Forecast UP / DOWN | UP sensitivity | DOWN sensitivity | Brier | Log loss |
|---|---:|---:|---:|---:|---:|---:|---:|
| RSM-26 | 0.7115385 | 0.5000000 | 52 / 0 | 1.0000000 | 0.0000000 | 0.2255064 | 0.6458076 |
| RSM-52 | 0.7115385 | 0.5000000 | 52 / 0 | 1.0000000 | 0.0000000 | **0.2209903** | **0.6348947** |
| RSM-104 | 0.7115385 | 0.5000000 | 52 / 0 | 1.0000000 | 0.0000000 | 0.2264949 | 0.6456877 |
| ERSM-26 | 0.6153846 | 0.4324324 | 47 / 5 | 0.8648649 | 0.0000000 | 0.2424496 | 0.6785664 |
| ERSM-52 | 0.6346154 | 0.4459459 | 48 / 4 | 0.8918919 | 0.0000000 | 0.2413689 | 0.6759268 |
| ERSM-104 | 0.5961538 | 0.4189189 | 46 / 6 | 0.8378378 | 0.0000000 | 0.2458296 | 0.6847942 |

All variants:
- n = 52;
- actual UP / DOWN = 37 / 15;
- previous-week-sign accuracy = 0.5576923;
- corrected always-UP accuracy = 37/52 = 0.7115385.

Confusion structure:
- RSM-26/52/104: TP=37, TN=0, FP=15, FN=0.
- ERSM-26: TP=32, TN=0, FP=15, FN=5.
- ERSM-52: TP=33, TN=0, FP=15, FN=4.
- ERSM-104: TP=31, TN=0, FP=15, FN=6.

## 4. Interpretation

The complete source-feasible family does not rescue standalone weekly Gold direction discrimination.

All three RSM variants collapse to the always-UP classifier in 2025. Their 71.15% raw accuracy exactly equals the corrected always-UP baseline.

ERSM does generate some DOWN calls, unlike RSM. However, every ERSM DOWN call in 2025 occurs on an actually-UP target week. Consequently:
- ERSM-26 captures 0/15 realized DOWN weeks;
- ERSM-52 captures 0/15;
- ERSM-104 captures 0/15.

Thus all six variants have 0% DOWN sensitivity.

RSM-52 has the best Brier score and log loss in 2025, but this is probability-quality evidence only. It does not establish directional discrimination because its categorical output remains 52/52 UP.

The source-family conclusion is therefore not based on a single RSM-52 test anymore: the complete same-source feasible RSM/ERSM family has been evaluated, and no variant establishes a robust standalone two-sided direction edge.

The frozen 19-event volatility overlay is a subsequent diagnostic and is not used to alter this conclusion.
