# R77 — volatility-standardized gold UP/DOWN abnormal shock hazard: actual retrospective result (2026-10-13)

**COMPLETED RESEARCH / PROMOTION = REJECT / DO NOT AUTOMATICALLY SWITCH GOLD ↔ CASH.**
Prereg **before** any R77 target outcomes: commit `9e53ae311`. Canonical R76 first-passage original remains untouched. Source-matched `data_r77/GOLD_R77_20261013_VOL_SCALED_FIRST_TOUCH_EVENTS.csv`, fixed R76 origin features and script `tools/gold_r77_vol_scaled_first_passage_hazard.py`. [CI run 38383194007](https://github.com/ataullahturgut/sim3-automation/actions/runs/38383194007), published 146* in 2026 and full 2020–26 1,540 row evidence in artifact ID `11804676909` (result JSON + scored ROW_FORECASTS.csv). No monthly signal merged; no real bank price fills.

## Different target from R76's fixed 1.5%, not tuned on 2026
At 09:00 TRT, threshold `max(1.5% in log units,1.5×sqrt(3)×std(last 20 PRE-ISSUE COMPLETED 09–09 gold logreturns))`. Label next 3 eligible business-day-source-09 clocks: DOWN_FIRST, UP_FIRST, NONE at future 15minute mid high-low, first threshold reached. Tied same bar explicitly ambiguous.
**2026 sample after 20-source-anchor warmup is primarily 2026 February–October 7, not a full 2026 January dataset.** 2020–25 EV Dukascopy-derived, 2026 native direct M1 verified; provider delivery PIT and bank bidask unverified; research only. 3-day windows overlap.

### Dynamic shock event frequency (different from ordinary 1.5% movement)
| Year | Sources eligible | Median adaptive threshold | DOWN first | UP first | NONE | Any shock |
|---|---:|---:|---:|---:|---:|---:|
| 2023 |235|2.07%|21|40|174|61/235=26.0%|
| 2024 |234|2.29%|33|52|149|85/234=36.3%|
| 2025 |230|2.16%|22|62|146|84/230=36.5%|
| 2026 Feb–Oct |146|4.08%|19|18|109|37/146=25.3%|

R76 fixed1.5% ANY in 2026 was143/146=97.9%; **redefined relative extremity** avoids incorrectly labelling ordinary high-vol swings 'constant shocks'. **But meaningful bank-loss opportunity can occur below R77 extreme threshold**, e.g. May27 2026 downward max ~2.9% remained 'NONE' since preissue adaptive risk barrier ~3.19%; do not equate R77 NONE with safe to hold gold.

### Same frozen-origin 7-feature logistic vs prior-60 matured event frequency, Brier lower and rank AUC higher
| risk/year | Brier challenger | Brier rolling60 | AUC | Observed events |
|---|---:|---:|---:|---:|
|DOWN 2023|.0845|.0870|.689|21/235|
|DOWN 2024|.1182|.1278|.631|33/234|
|DOWN 2025|.0825|.0922|.699|22/230|
|DOWN 2026|.1123|.1238|.676|19/146|
|UP 2023|.1462|.1513|.495|40/235|
|UP 2024|.1725|.1884|.605|52/234|
|UP 2025|.1906|.2122|.690|62/230|
|UP 2026|.1047|.1121|.665|18/146|
|ANY 2023|.2007|.2056|.588|61/235|
|ANY 2024|.2223|.2479|.636|85/234|
|ANY 2025|.1959|.2454|.742|84/230|
|ANY 2026|.1796|.2004|.712|37/146|

**Good descriptive discovery:** All 12 year×risk Brier losses improved vs simple matured rolling60. 2026 DOWN AUC .676, UP .665, ANY .712; not classification hit rates. This is materially more promising than R76 static shock whose 2026 DOWN AUC .45 and ANY AUC .48.

### Why model cannot yet safely exit/enter
- Preregistered paired 5-session block bootstrap DEV Brier advantage excludes zero for **UP only**, but UP fails 2023 AUC>.50 (.495). DOWN DEV 95% CI [-.00284,+.01674] and ANY [-.00503,+.03357] include zero. **0 of 3 originally required support gates PASS**, even though Brier numerically better annually.
- Frozen score thresholds chosen only from DEV (80th percentile model p): DOWN `p≥.19846`, UP `p≥.23845`. Actual 2026 **DOWN alarms only 4, 1 hit**, **UP alarms only 1, 1 hit** out of **19 DOWN and18 UP** realized exceptional shock windows. Most relevant: in **2026 May+June**, there were **13 DOWN_FIRST exceptional events (5+8)** and the frozen DOWN alarm fired **zero** times in those two months. An AUC .676 rank signal did NOT translate into usable timely exit coverage.
- Model probabilities are not estimated historical same day live-reception forecasts; source firstprint and historical month decision archives absent. Absolute 3day high/low labels may include movement overnight when Turkish bank spread would be wide; event does not guarantee you can execute before shock.
- From Neon `monthly_expert_forecasts` current coverage only two Sep2026 `HISTORICAL_REPLAY` rows (RW/Momentum); **no valid archived monthly prediction series** to time-month condition 2020–26. A monthly+shock portfolio simulation built by using observed month direction would be severe hindsight leakage. No such backtest attempted.

### Research architecture proposed (not validated strategy)
**Two parallel risk heads, separate from monthly price forecast**:
- Monthly UP gold allocation -> EXCEPTIONAL_DOWN risk elevated? potential watch/temporary exit only if validated after-bank-cost avoided drawdown > false-exit fee + missed rally; no automatic switch.
- Monthly DOWN cash -> EXCEPTIONAL_UP risk elevated? potential short entry only if benefit > spread and forecast risk remains.
- Stabilization/re-entry requires a NEW as-of hazard: future 09/16:30 next1d adverse barrier probability, decaying already-matured realized drawdown/variance and reentry cooldown, not hindsight end-window return. Need bank ASK/BID timestamps and realistic execution costs 10/25/50bp scenarios.
- Non-exceptional yet financially costly declines should be separate 'ordinary-but-actionable correction' class. This avoid mistakenly treating R77 NONE as ZERO DOWNSIDE.

Next controlled scientific test: an actual monthly-as-of conditioned **multi-state** competing risk hazard (ordinary correction, standardized extraordinary shock, recovery) with reference spreads and independently prospective data; do not mine more 2026 barriers or pretend HAR-CAL DAY 08:45→16:45 forecasts 3d RV. HAR-CAL can seed distinct *3d calibrated* vol model in a future study.
