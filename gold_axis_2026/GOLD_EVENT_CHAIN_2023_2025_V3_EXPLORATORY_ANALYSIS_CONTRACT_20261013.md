# GOLD EVENT CHAIN / ADVANCE CONDITIONS — V3 EXPLORATORY AUDIT CONTRACT
Date: 2026-10-13; branch gold-execution-channel-audit-20261006.
Purpose: Referee corrections accepted as *research questions*, NOT blindly promoted to fact or deployed signals.
PR #118 is open and independent; do not merge or overwrite its files.
WARNING: This is a written-before-V3-run exploratory analysis contract, **not untouched prospective preregistration**. Entire 2023–2025 and parts of 2026 have already influenced research, so no holdout status.

Data authority: Neon Gold Control / EV Trading Labs Dukascopy XAU 15-min bid+ask (midpoint); New York session rolls at 17:00 ET (TZ America/New_York). Only groups with >=70 quote bars count as daily observations. Check cross-source alignment and historical quality; no inferred night trading gaps. 2022 as warmup to compute lagged moving dispersion. An actionable as-of observation must be at or before decision timestamp. The following is retrospective event descriptive study, NOT execution backtest.

Event measurement PLAN:
(1) Daily simple return r1 = 100*(current NY17 close / previous close -1); trailing **60 previous completed** daily r1's sample std s60, min 40 observations (shifted, exclude current). Daily z1 = r1/s60.
(2) 5-trading-session simple return r5 = 100*(p_t/p_{t-5}-1); z5 = r5/(s60*sqrt(5)); exactly session lags, not 5 calendar days; display both fixed 3% and volatility-scaled |z5|>=2, |z1|>=2.5 (referee proposals). 2022 warmup enables first 2023 origins. Rolling-sigma estimator choice exploratory sensitivity, not optimal.
(3) Event threshold crossing timestamp is the **END of the 5-session window**. Its admissible antecedent observation interval begins at t-5 sessions and is NOT an inferred time of new information. Candidate triggers must distinguish when publication occurred relative to its local subevent and the window baseline. Do not equate cluster flagged date to true price-move inception.
(4) Event dedup: consecutive same-direction z5>=2 flagged days separated by <=3 eligible trading sessions merge into research clusters; sensitivity gap = 1,2,3,5. An overlap can contain genuine distinct economic triggers; retain marked subevents. Need both UP/DOWN controls and non-event days selected without future info.

Control/association plan:
- As-of "tension": previous 20 completed session return; report bins >=5%, >=8% (referee). These are exploratory thresholds selected with outcome exposure and must not be marketed as calibrated forecasts.
- Outcome: independent, nonoverlapping 10-session FUTURE first-pass >=3% UP and DOWN as event risk, noting overlapping horizons induce autocorrelation; also tabulate when both threshold directions are hit and temporal ordering. Note that post-decision outcome alone, not an investable trade.
- Compare event first-pass rates for tense/normal days, and **non-event comparators**. Provide counts and uncertainty; cluster dependence -> no naive Fisher significance claim.
- Cross-asset daily proxy CME continuous GC,SI,ZN,NQ,CL H1 series. These are roll-sensitive futures, not true spot DXY or real yields. Use matched NY17 completed sessions, report correlations/coverage and note roll discontinuities; ZN price direction inverse to Treasury yields. Do not use same-day cross-asset values to predict same day's completed move.
- Explore observations table for historical DXY, DFII10, CFTC, ETF, FedWatch and FOMC availability, with explicit observation_ts vs available_as_of. Report absent channels as absent rather than deriving from 2026 values.
- For news, first-publication as-of necessary; correction examples: WGC Oct 13 2025 statement includes BOTH tactical risks and that long/ETF accumulation remained relatively early; CFTC publication delayed as in CFTC official historical special notices https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalSpecialAnnouncements/index.htm ; historical report date != availability date.

Deliverables: machine-readable 2023–25 V3 daily controls + clusters; explicit data availability matrix; factual findings/counterexamples; updated manifest note (additive); no trained model, no trading rule. Facts from referee to cite as unverified if not independently reproduced.
