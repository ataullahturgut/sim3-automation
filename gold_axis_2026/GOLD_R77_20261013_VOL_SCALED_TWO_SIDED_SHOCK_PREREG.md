# R77 prereg: volatility-scaled exceptional downside/upside first-passage shocks (2026-10-13)
Written **before calculating ANY R77 dynamic-barrier event counts or fitting R77 models**. R76 fixed±1.5% first-touch revealed 2026 143/146 (98%) event frequency: the threshold ceased to denote "shock." This justifies volatility-scale redesign, not retuning R76 posthoc to maximize 2026.

User wants **monthly gold/cash core allocation** + short-term alert to switch to cash during exceptional decline in UP-month and temporarily enter gold during a DOWN-month exceptional rebound, then re-enter/exit after calm. R77 is a *research event model*, not a trade model.

## Binding NEW target
Frozen issue 09:00 Europe/Istanbul, same-source M15 BID+ASK midpoint OPEN. From that point until same 09:00 on **third subsequent eligible weekday-source date**; strict forward M15 high/low. Threshold is PREISSUE adaptive:

`B(t)=max(0.015, 1.50*sqrt(3)*s20(t))` (absolute log barrier). `s20` = sample std of previous 20 **completed** 09→09 log returns, excluding the return whose ending 09 equals decision origin; extra lag is conservative asof safe. Up first touched if `log(mid_high/entry)>=B(t)`, down if `log(mid_low/entry)<=-B(t)`. Tied same-bar dual touch = ambiguous. If neither, NONE. Daily R76 09 pre4h feature and 1/5/20 09 returns could include same 09 quote (available at start); s20 is lagged daily volatility, not future realization. Compute +/- with log thresholds rather than applying +/- percentage inconsistently.
This **redefines label**, not just a model feature. Chosen k=1.5 by theoretical standardized extremity (~1.5σ of 3day daily-change variance), not 2026 optimization. 1.5% absolute min roughly beyond unknown bank spread scenario; no bank cost claim.

## Source/clock/eligibility
Same as R76: 2020–25 uniform EV Dukascopy derived, 2026 direct M1-confirmed Dukascopy, 16 complete last4h bars, >=270 future M15, next day >=85, valid 09 anchor, no crossing data provider. Preserve same 1540 origins and full source rows, no selection on shocks, no target-period feature leakage. Source quote high/low average approximate; no actual bank ASK/BID. 3-day outcomes overlap.
Train exactly same low-capacity R76 independent L2 C=.2 logistic features `r1,r5,r20,sd20,ret4,sqrt(rv4),asym4` with training standardization, labels DOWN_FIRST, UP_FIRST, ANY_SHOCK. Matured asof 2023 train 2020–22, 2024 train 2020–23; freeze 2025/26 train 2020–24. Compare same matured rolling60-class frequency, dev Brier, AUC, AP, top20 precision / lift, bootstrap block5, both 2023 and2024 retained signs and 2025/26 descriptive transport. No rescue by selecting 2026-only threshold. Same support gate as R76.
Report year event counts, median threshold as % by year, shocks that cross BOTH standardized barriers, stabilization NOT implemented until prob model is viable. If no robust gain, preserve failed R76/R77 and only suggest orthogonal macro/prospective data.
No retro evaluation with hindsight monthly realized direction or monthly HMM. Require stored point-in-time asof monthly forecast before any combined trade-cost strategy.
