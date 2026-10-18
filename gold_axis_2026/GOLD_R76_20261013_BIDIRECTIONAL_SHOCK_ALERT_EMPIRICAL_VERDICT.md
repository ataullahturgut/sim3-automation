# R76 — Gold intramonth two-sided shock risk, first empirically completed pilot (2026-10-13)

**RESEARCH STATUS: COMPLETED / NO ROBUST CONDITIONAL DIRECTION EDGE / NO BANK TRADING RULE.**
Experiment pre-registered *before observing outcome labels*: `GOLD_R76_20261013_TWO_SIDED_SHOCK_HAZARD_PREREG.md` commit `972152bd`; source data `data_r76/GOLD_R76_20261013_09TR_SHOCK_FIRST_TOUCH_3D_ORIGINS.csv` commit `747854fc`; Python script `tools/gold_r76_two_sided_shock_hazard.py`, controlled script input null-semivariance fix `a1bdbcb`. [Successful GitHub CI 38382297383](https://github.com/ataullahturgut/sim3-automation/actions/runs/38382297383). CSV forecast rows + JSON results downloadable CI artifact `r76-xau-3day-shock-pilot` id `11803652248`. No canonical project or original model modified.

## User's economic task (distinct from everyday UP/DOWN)
- Separate monthly trend/price forecast is the **primary allocation state** (monthly UP -> gold, monthly DOWN -> cash). R76 candidate is a short **unexpected adverse excursion/rebound** risk overlay: DOWN_FIRST risk during monthly UP -> watch for temporary cash; UP_FIRST during monthly DOWN -> potential temporary entry; HOLD/REENTER only after independent stabilized-risk evidence and bank spread. As-of monthly historical forecast series NOT presently demonstrated: `monthly_expert_forecasts` in Neon currently returns only two September 2026 HISTORICAL_REPLAY experts, not a verified prior-month-end point-in-time historical direction for all months. Hence NO monthly+R76 trade backtest or PnL claims.
- Same-hour decision origin: 09:00 TRT XAU BID/ASK midpoint OPEN. Outcome first upper +1.5% or first lower −1.5% barrier touched within three subsequent Mon–Fri 09:00 anchors, or neither; BOTH touched is recorded with order, not net 3d direction. This is different from R20–R29 signed 3d closing-endpoint >=1.5% severe-down research.
- 2020–25 EV/Dukascopy-derived BID/ASK15m; 2026 direct Dukascopy M1 matched15; >270 future M15 bars, >=85 first-day future bars, exactly 16 preissue 05→09 M15, last20 price anchors, 1540 quality-passed origins in 2020–26. Price source differs 2026; receipt time and actual Turkish bank order-fill bank bidask remain unverified. Three-day windows heavily OVERLAP; counts are predictions/windows not independent market events.
- Source bars forward highs/lows midpoint from average BID and ASK extrema at bar frequency; these are *research approximations* not executable midpoint ticks.

## Actual prevalence of early first-passage ±1.5% across 3d
| year | N windows | DOWN first | UP first | neither | both barriers eventually within window |
|---|---:|---:|---:|---:|---:|
| 2020 | 220 |68|95|57|6|
| 2021 |239|71|58|110|2|
| 2022 |236|80|80|76|7|
| 2023 |235|47|62|126|3|
| 2024 |234|55|93|86|8|
| 2025 |230|62|114|54|13|
| 2026 (Jan-Oct partial)|146|**82**|**61**|**3**|**24**|

In 2026 **143/146=97.9%** of the eligible origin windows touched a 1.5% barrier within3 source days, while only 109/235=46.4% did so in2023. A fixed 1.5% event has become too COMMON to meaningfully mean 'abnormal shock' in 2026; conditioning it on predicted *3-day* volatility rather than arbitrary retrospective threshold tuning is scientifically necessary. Predeclared secondary 1-session +/-1% ANY_SHOCK rate 2023 **85/235=36.2%**, 2024 107/234=45.7%, 2025 138/230=60.0%, 2026 **125/146=85.6%**.

## Chronological model and native same-date rolling baseline
Independent L2-regularized logistic pDOWN_FIRST, pUP_FIRST and pANY_TOUCH, features strictly known by issue: preceding20 complete 09 price returns (1/5/20, vol), completed04h signed return, 04h RV and downside/positive variance split. Training: 2023 on 2020–22 matured, 2024 on 2020–23 matured, 2025/26 model frozen 2020–24; both opened years previously investigated (not independent heldouts). Comparator is rolling-60 *matured* 3-day event prevalence available >=7 calendar days before issue. Correct-by-sign accuracy is NOT this project's primary metric.

| Outcome | Year | N | Base rolling60 Brier | New model Brier | Model AUC |
|---|---|---:|---:|---:|---:|
| DOWN first | 2023 |235|.1663|.1698|.554|
| DOWN first | 2024 |234|.1852|.1747|.662|
| DOWN first | 2025 |230|.2111|**.1880**|**.681**|
| DOWN first | 2026 |146|**.2655**|.2979|**.450**|
| UP first | 2023 |235|.2080|.1956|.536|
| UP first | 2024 |234|**.2509**|.2540|.474|
| UP first | 2025 |230|**.2592**|.2729|.507|
| UP first | 2026 |146|.2576|.2568|.587|
| ANY threshold touched | 2023 |235|.2655|.2543|.607|
| ANY threshold touched | 2024 |234|.2426|.2327|.583|
| ANY threshold touched | 2025 |230|.1982|**.1594**|.746|
| ANY threshold touched | 2026 |146|**.0231**|.0343|.483|

Definition: smaller Brier better; AUC >.5 better than random discrimination, class prevalence and differing source/year affect comparison. In 2026 the classifier *fails* at the exact DOWN risk needed for UP-month exit (AUC .45 and worse Brier than rolling); CANNOT trade from it.

The 2023–24 paired 5-session block bootstrap Brier gain CI versus mature60 includes zero for all: DOWN [-.00847,.01488], UP[-.00952,.01939], ANY[-.00665,.02876]. All 3 PREDECLARED support gates FAIL. No 2026-based threshold retuning, no signal flips or false extrapolated bank profit.

## Measured 2026 intrahorizon countertrend reality
24/146 windows eventually touched BOTH ±1.5% barriers (overlapping windows), including **14** DOWN_FIRST→UP later and **10** UP_FIRST→DOWN later. This is precisely why 'end 3d UP/DOWN' may fail to capture interim temporary corrections and rebounds. These are **descriptive realized paths**, NOT successful early warnings.
Example historical realized (09TR issue XAU midpoint): May01 $4604.98 DOWN_FIRST reached May04 10:15 UTC; May05 $4545.79 UP_FIRST reached May06 00:45 UTC. Note these are realized events, not model predictions.

## Decision / next predeclared family (not executed/proven here)
A true shock should be exceptional **relative to as-of expected variance over the SAME horizon**: predefine dynamic barriers max(real bank execution costs, k × 3d forecast standard deviation), with k and risk model fixed on development data. HAR-CAL currently predicts *08:45→16:45 same-day integrated RV*; it is NOT automatically a valid 09→3d sigma predictor. Build separate 3d vol model then test competing first-passage hazards and subsequently independent recovery/re-entry hazard (calm after shock) in genuinely forward 2027 data. Include different entry/exit bank decision clocks (09 and last normal-spread before17), acquisition asof signals, competing costs of false exits/missed rebound; do not approve live orders until action-level bank evidence exists.

**Bottom line:** New target is closer to user's allocation objective and detects transient adverse movements, but first low-capacity source-clean model failed robust predictive gates. Do not confuse finding common shocks with predicting shock direction. Further repeated fitting on opened 2026 without independent signal/vintage adds overfit risk.
