# R23–R27 (2026-10-11 TRT) — REAL evidence of 2023↔2026 regime instability + fully source-audited but unpromoted adaptive H3 UP/DOWN routing
**Authoritative status:** actual Neon read-only SQL and real frozen-model computations completed for 5 consecutive preregistered research proposals. **Discoveries and validation must be distinguished:** R23 R24 R25 R26 R27 studies were generated sequentially AFTER prior 2025/26 model failures, hence 2025/26 are heavily opened. Quantified causal AS-OF differences are real retrospective effects, but no 2027 prospective and NO certified trading edge. R23–R27 prereg files written individually BEFORE their related market outcome SELECT. See exact files:
- `GOLD_R23_CAUSAL_RELATIVE_VOL_SHIFT_AND_DOWNSIDE_RANKING_PRE_REG_20261011.md`
- `GOLD_R24_ASOF_IMPLIED_STRESS_X_GOLD_TREND_INVERSION_CAUSAL_H3_PREREG_20261011.md`
- `GOLD_R25_H3_ASOF_STRESS_ANALOG_MATCHING_SAME_STATE_PATH_CBR_PREREG_20261011.md`
- `GOLD_R26_EXTREME_PUBLISHED_GVZ_ANALOG_SPECIALIST_VS_PRICE_ORIGIN_PREREG_20261011.md`
- `GOLD_R27_H3_PRIOR_20DAY_TREND_AND_GVZ_STRESS_SAFE_SOFT_ROUTER_PREREG_20261011.md`

## Data/source time contracts
2020–2025 historic `gold_research_evduka_xau15m_bidask_candidate`, 2026 native `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2` strictly `m1_matched=15`. Spot gold XAU BID/ASK M15 at TRT (UTC+3 year-round), 16 COMPLETE source M15 open-to-close BID features start 04:45..08:30 ending exactly 08:45 issue; entry quote open 09TR, outcome exit quote09TR on third following **Mon–Fri weekday**, no price forward-fill or shifted holidays, BID/ASK signed direction agreement. GVZ last **prior calendar date** dated US last NY close from `GOLD_EXECUTION_GVZ_FREE_CANDIDATE_2020_20261007.csv`, stale<=7caldays, no current-day NY GVZ or target-day news; 63 HISTORIC prior GVZ daily closes and 63 HISTORIC prior completed 4h gold RV bars for asof reference; last FIVE completed 09-to-09 gold moves computed from prior SIX09 opens only, no issue-day 09 return; last20 prior moves from previous21 quotes only. Reject quote gaps>7 calendar days. Original monthly 13D HMM latest month, original 2026 Aug/Sep precious metals, future GPR not used.
All model fits: 2023 train20–22 matured H3, 2024 train20–23 matured, both 2025 and2026 SAME frozen train2020–24 (H3 exit before Jan1 2025). Same scored dates within each comparative table; 2023/24/25/26 H3 n254/256/255/116 (R23–26), R27 stricter full prior20 quote history 254/256/255/101. Three-day targets overlap → IID interval tests invalid. Real BID/ASK quote endpoint ≠ bank transaction fills, so no backtest returns.

## First solid finding: WHY 2023 and 2026 differ, not a retrospective invented state
R23 original market-source asof values on matched origins:
| Ex-ante input / retrospective outcome | 2023 | 2024 | 2025 | 2026 |
| --- | ---: | ---: | ---: | ---: |
| Median last published GVZ | about **14.6** |16.3|18.4|**26.6**|
| Median 04:45–08:45 complete-bar sqrt volatility |**0.179%**|0.221%|0.298%|**0.455%**|
| Actual three-day severe <=−1.5% downside frequency |**21/254=8.3%**|35/256=13.7%|29/255=11.4%|**36/116=31.0%**|
| **Post-outcome difference of preceding 5-day signed trend: (mean preissue trend among future severe declines) minus (mean among all other dates)** |**−0.00819 log**|+0.00114|+0.00986|**+0.01968 log**|
The GVZ median **1.8×**, same morning realized-vol median **2.55×**, downside tail class prevalence **3.75×** higher in2026 than2023. Crucially the **empirical trend-risk association reverses sign**. On quiet 2023 days, a negative recent5-day gold trend was more common before subsequent severe H3 declines (continuation); on turbulent 2026, relatively **positive** prior gold 5day trajectory was more common before sudden declines (reversal). This is a discovered conditional statistical association, **not proof of causal mechanism, not necessarily an independent usable predictor**.
R24 genuine source-available stress proxy from PREYEAR-TRAIN only median prior GVZ, no hindsight calendar-year labeling: cutoff2023 GVZ **18.08**, cutoff2024 **17.07**, frozen2025/26 **16.78**. Preissue 2023 origins above stress 27/254, 2024 87/256, 2025 180/255, and **2026 116/116**. Clearly 2025 bullish high-vol and 2026 bear/violent high-vol **both labeled stress**; a single GVZ threshold CANNOT distinguish them. Condition realized severity:
- 2023 normal GVZ, preissue Trend5 negative: future >=1.5% downside **15/121 (12.4%)**, normal GVZ positive Trend5 **5/106 (4.7%)**.
- 2026 high GVZ, Trend5 positive **19/55 (34.5%)** severe decline; high GVZ, Trend5 negative **17/61 (27.9%)** severe decline.
- 2025 high GVZ, Trend5 positive **19/124 (15.3%)**; high GVZ, negative **6/56 (10.7%)**.
The preregistered origin GPR/HMM monthly labels were NOT used; GVZ and past gold prices are timestamp-safe proxies only.

## R23 relative regime features actual downside logit proper scores (Brier, lower better)
Risk endpoint realized XAU 3weekday return <= -0.015, fixed alpha30 standardized ridge logistic:
| Model |2023 n254|2024 n256|2025 n255|2026 n116|
|---|---:|---:|---:|---:|
| OLD absolute RV+GVZ |**.077354**|.116241|.095959|.215909|
| +previous5 gold trend/min |.079425|.116088|**.093860**|.215147|
| +online RV/GVZ Z63 |.077420|.116238|.096386|.214762|
| +Z63 and trend |.079543|.116090|.094364|.213641|
| +prior downside shock × Z63 (predeclared) |.079546|**.115976**|.094593|**.208347**|
2026 favorable score .208347 but 2023 baseline was better .077354 and 2025 trend-only better .093860. No all-year winner. R23 2026 median raw GVZ high but **local** Z63 GVZ median **−0.593**, so high absolute implied volatility can be ordinary *relative to its own previous quarter*. Do not substitute a local z score for systemic regime level.

## R24 stress×gold trend logit causal-prior exante test
Frozen logistic y H3 severe-down and y H3 signed UP separately. Risk Brier:
| model | 2023 |2024|2025|2026|
|---|---:|---:|---:|---:|
|BASE RV/GVZ|**.077354**|.116241|.095959|.215909|
|+Trend5+MinDown5|.079425|.116088|.093860|.215147|
|+Trend5×training-median stress|.079891|.116524|**.093513**|**.214221**|
|+Trend5×rolling GVZ-Z63|.085978|.116412|.093411|.215849|
2026 stress interaction risk quintile top **11/23** downside vs bottom **4/23**, versus baseline **8/23 vs6/23**, but 2023/24 scores worsen.
Actual THREE-DAY **signed UP/DOWN BALANCED accuracy**, same sample n254/256/255/116:
| model|2023|2024|2025|2026|
|---|---:|---:|---:|---:|
|CBR price-only 41NN|50.19|49.46|**54.07**|46.93|
|RV/GVZ + prior5 trend/min|47.55|49.85|53.86|46.34|
| + binary extreme-stress × trend|49.93|48.40|54.34|**52.68**|
2026 signed stress model higher BA but 2023/24 and 2025 not durable, 2026 DOWN recall only25.35%; reject directional promotion.

## R25 state-matched historical 41NN preissue price paths
Distinct from R13 distance-adding regime: choose prior documented PREYEAR GVZ level and prior completed5d momentum sign groups before selecting path lookalikes (STATE2, STATE4), plus fractional soft neighbor weighting (STRESS+MOM both match 1; one .35; neither .10). All source-equal n254/256/255/116.
| H3 signed BA | 2023|2024|2025|2026|
|---|---:|---:|---:|---:|
| Original PATH CBR|50.19|49.46|**54.07**|46.93|
| same TRAIN GVZ stress STATE2|52.19|48.64|52.12|50.64|
| same stress+past5 trend STATE4|49.80|46.84|50.17|49.42|
| **SOFT 2-factor state**|**50.99**|**50.75**|51.45|**53.27**|
SOFT state rescues/breaks relative PATH 2023 +2;2024 +5;2025 **−7**;2026 **+9**. 2026 BA53.27 UP75.56%, DOWN30.99%, better but remains low. Fails 2025 transport and DOWN recall target.

## R26 did GVZ top 20% select correct year autonomously?
Source matched n254/256/255/116, preyear TRAIN threshold top20% previous GVZ: 2023 **21.04**,2024 20.06,2025 and2026 19.57. If GVZ≥training q80, use R25 SOFT otherwise preserve original PATH:
|year|activated|PATH BA|q80 gated BA|net rescued−broken|
|---|---:|---:|---:|---:|
|2023|2/254|50.19|50.19|0|
|2024|6/256|49.46|49.46|0|
|2025|**108/255**|54.07|**50.30**|**−10**|
|2026|**116/116**|46.93|**53.27**|**+9**|
R26 **proof of insufficiency**: entire 2026 meets high-GVZ condition but many bullish 2025 sessions ALSO do. 2025 signed UP source prevalence161/255=63.1% vs2026 45/116=38.8%. A GVZ-only switch cannot separate "high volatility bull" and "high volatility bear."

## R27 ONE predeclared extra preissue slow-drift state, 20 days to distinguish 2025 vs2026
Hypothesis formed AFTER seeing R26: only route to SOFT when GVZ≥training-only 80th percentile **AND** last TWENTY fully completed prior 09→09 gold log returns sum NEGATIVE (no current 09 quote, no lookahead). Eligible sample R27 n2023/24/25/26=254/256/255/**101** (2026 smaller than R26 owing20 step history validity). SAME eligible-dates recomputed PRICE and q80 comparator.
|year|source N|QVOL only activated|two-factor GVZ Q80+20d bearish activated|PATH BA|q80-only BA|**R27 2-factor BA**|paired R27 rescue/break/net|
|---|---:|---:|---:|---:|---:|---:|---|
|2023|254|2|0|50.19|50.19|50.19|0/0/0|
|2024|256|6|0|49.46|49.46|49.46|0/0/0|
|2025|255|108|**18**|**54.07**|50.30|52.61|0/4/−4|
|2026|101|101|**60**|44.09|52.80|**52.80**|**11/1/+10**|
The new slow-drift filter reduced the 2025 false activations108→18 (net loss shrinks −10→−4), while preserving the 2026 signed benefit on a valid n101 subset (net +10 correctly classified: 11 rescued versus1 broken); **concrete mechanism-level improvement relative R26 excessive gating**, but R27 BA still below original PATH in 2025, and 2026 DOWN recall only30%. No promotion, all prospective 2027 tests required. This is not a >70% bank trading success, and 2023–24 no improvement vs price-only despite reduced incorrect routing.

## Decision and safe research frontier
Discovered *observable* cause of invalid assumption "one universal gold regime": (1) GVZ level1.8x and 4h gold RV2.5x higher in2026 than2023; (2) severe 3d downside incidence3.75x and sign of trailing5d trend conditional on future deep-down flips; (3) GVZ-only stress fails to distinguish 2025 bullish-high-risk regime from 2026 bearish-high-risk, while past20d drift provides some observable separation. Model risk mapping changes as underlying regime shifts; monthly HMM retrospective t-month state is unavailable intramonth, and its delayed filtered state from prior month is not a substitute for true same-day proxy. R27 is a research **gate improvement vs the previous BAD gate**, not new champion vs frozen original price-only model in all years. False certainty from 2026 threshold hunting explicitly prohibited. Reserve this as pre-specified new candidate for genuinely unseen 2027 source timestamp-certified issue paper trail, with bank fills/spread and 3day overlapping-event purging. Do not alter production trading forecaster; continue evaluating a novel real-time orthogonal macro driver instead of trying endless transformations of the same XAU+GVZ observations.
