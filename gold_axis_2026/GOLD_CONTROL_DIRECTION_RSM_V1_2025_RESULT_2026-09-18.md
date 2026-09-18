# GOLD CONTROL — DIRECTION_RSM_V1_RESEARCH LOCKED 2025 TEST

**Date:** 2026-09-18  
**Identity:** `DIRECTION_RSM_V1_RESEARCH`  
**Status:** `LOCKED_2025_HISTORICAL_TEST_COMPLETE / NO_PROMOTION`  
**Specification checkpoint before 2025 price/return access:** `9cac26b21b81ddf0f403c86fc2bdb8935880c1ac`  
**Implementation:** `gold_axis_2026/tools/direction_rsm_v1_research.py`  
**Frozen forecast table:** `gold_axis_2026/GOLD_CONTROL_DIRECTION_RSM_V1_2025_WEEKLY_FORECASTS_2026-09-18.csv`

## 1. Frozen model used in 2025

No parameter or rule was changed after the pre-2025 checkpoint.

For weekly close `C_w`:

`r_w = ln(C_w / C_(w-1))`

`x_w = 1[r_w > 0]`

and

`p_up(w) = (1/52) * sum(x_(w-51), ..., x_w)`.

The forecast issued at week-w close targets the next represented calendar week:

- `UP` if `p_up >= 0.5`;
- `DOWN` otherwise.

Inputs are only the prior 52 weekly return signs from `XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`. No 2025 volatility-event labels, FAST, GVZ_RISK, BOCPD, Macro Event or Emergency outputs are inputs.

## 2. 2025 source audit

- selected research series: `XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`
- governed Monday-Friday New York-local rows in 2025: 255
- weekly construction: unchanged from preregistration
- no interpolation or forward-fill
- no provider substitution
- no 2025-driven threshold/window/source change
- complete target-week forecasts retained: 52

The weekly forecast table was written and frozen before the 19-event volatility overlay was applied.

## 3. Locked 2025 next-week direction results

- n = 52
- accuracy = 0.6923076923
- balanced accuracy = 0.5000000000
- Brier score = 0.2261606736
- log loss = 0.6453452357
- actual UP / DOWN = 36 / 16
- forecast UP / DOWN = 52 / 0
- exact `p_up=0.5` origins = 0
- always-UP accuracy = 0.6923076923
- previous-week-sign accuracy = 0.5576923077
- minimum `p_up` = 0.5192307692
- maximum `p_up` = 0.7115384615
- mean `p_up` = 0.6153846154

Confusion counts under UP as the positive class:
- TP = 36
- FP = 16
- TN = 0
- FN = 0

## 4. Interpretation

The raw 69.23% accuracy is not evidence of useful two-sided directional discrimination.

The model forecast UP in all 52 target weeks. The realized 2025 weekly class balance was 36 UP versus 16 DOWN, so an always-UP classifier also scores exactly 69.23%.

Therefore:

`RSM accuracy = always-UP accuracy = 69.23%`

and

`balanced accuracy = 50.00%`.

The model correctly followed the dominant bullish class but did not identify a single DOWN target week. This is classified as `WEAK_DIRECTIONAL_DISCRIMINATION`, not as a successful 69% direction predictor.

## 5. Independent verification

The locked 2025 metrics were independently reproduced with a separate PostgreSQL weekly/window-function calculation after the forecast table had been generated.

The independent SQL result matched exactly:
- n 52;
- accuracy 0.6923076923;
- balanced accuracy 0.5;
- Brier 0.2261606736;
- log loss 0.6453452357;
- 52 UP / 0 DOWN forecasts.

## 6. Promotion decision

Status:

`EVALUATED / NO_PROMOTION / WEAK_DIRECTIONAL_DISCRIMINATION`

No post-2025 rescue is authorized under this V1 identity. In particular, the 52-week lookback or 0.5 cutoff may not now be changed and retested on the same 2025 period as though it were untouched evidence.

Any scientifically justified RSM successor would require a separately named preregistration and a truthful evidence label.
