# GOLD EXECUTION: 2022 WARM-UP + REALIZED / IMPLIED VOLATILITY — RESEARCH RESULT — 2026-10-08

**Status: REPRODUCED ARCHIVED-PERIOD PROBABILISTIC IMPROVEMENT / STRONG 2025 RETROSPECTIVE RESULT / NO UP-DOWN OR TRADE PROMOTION.**  
**Target:** XAU/USD `log(next-eligible 09:00 close / current-day 17:00 open)` under governed `Europe/Istanbul` clocks; exact XAU raw-bar calendar uses origin UTC 14:00 OPEN and next eligible 05:45 UTC bar CLOSE.  
**Forecast event:** `TAIL1=I(|overnight log-return|>=0.01)`, a magnitude event, **not direction**.  
**Decision info:** preceding matured overnight returns and previous-calendar-date official Cboe GVZ daily close, both available in principle after today's 09:00 source-price readiness. **09:15 issue time is not yet source-clock certified**, and the 17:00 return origin is not assumed bank-executable after consuming any contemporaneous 17:00 price.

## 1. Discovery: the missing 2022 historical warm-up was the avoidable bottleneck

Earlier risk work warmed the rolling 5/20/60-night features inside 2023 and then required another 120 scored observations before learning probabilities. The first 2023 probabilistic evaluation consisted of only 76 late-year days and was unstable. This architecture changed training population across the examined years and obscured early-year regime learning.

The existing repository **already contains 2022 15-minute raw spot prices** as `GOLD_XAUUSD_15M_UTC_2022_WITH_BUFFER.csv`. Combine with `GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv` (duplicate timestamps have deterministic precedence to the latter). Raw complete session anchors yield **exact 769/769 comparisons** against frozen 2023–2025 `M4_SIG_FPCA_MACRO` overnight target log returns, **max absolute discrepancy under 1e-9**. This proves forecast-label price identity without relying on a proxy target.

- 2022: 257 complete overnight labels; 199 eligible risk feature origins after 60-matured-return warm-up; **train/warm-up ONLY**.
- 2023: **256** evaluation days, **25** actual ≥1% overnight abs log-return events;
- 2024: **259** days, **24** events;
- 2025: **254** dates identified in the frozen M4 authority, **43** events; any extra raw target day outside the frozen authority is excluded, not added post hoc.
- Full evaluation: **769 forecasts**, not 76+259+254=589 from the previous late-2023 truncated evaluation.

## 2. Mechanistic innovation and hard information boundary

The research combines two genuinely different sources of risk information rather than stacking correlated direction models:

**Realized overnight multi-horizon memory** (fixed HAR-inspired score, **not** textbook estimated HAR-RV):
`RV_w(t)=sqrt(mean(r_{t-w}²...r_{t-1}²))`, `w∈{5,20,60}`;
`H(t)=sqrt(.5*RV5²+.3*RV20²+.2*RV60²)`.

**Implied-volatility expectation** from official Cboe `GVZCLS`: `GVZ_D-1` is the latest observation whose **source date < forecast issue date**. NEVER use same-date options close for a morning/17:00 issue unless actual historical publication-and-delivery timestamp is proven. GVZ is *expected volatility of the GLD ETF*, not an XAU-specific overnight implied-return prediction. Levels are distinct; fitted/log-standardized information is used, not naïvely equated to overnight variance.

**Probability head:** Ridge-penalized logistic regression `p=logistic(b0+b1*z(log H)+b2*z(log GVZ))`, L2 penalty 5 on slopes, intercept unpenalized. Target = ≥1% absolute *overnight log return*. The model computes probabilities, not buy/sell recommendations. No learned direction classifier is promoted.

Chronology:
1. 2022 risk-feature rows are matured historical training only;
2. 2023–2024 are **daily expanding, prequential** refits using only prior matured targets (n starts at 199);
3. 2025 is **parameter-frozen** to 2022–2024 rows (n=714). No 2025 label is fit or used to choose model parameters;
4. baseline = same-training-sample Laplace-smoothed historical ≥1% event rate `(1+N_event)/(2+N)`;
5. separate ablations: `HAR` only; `GVZ` only; `HAR+GVZ`, evaluated on exact same origins.

**Preregistration caveat:** this study's 2022 warm-up repair and source-combination choice arose during prior inspection of 2025 archives. No 2025 outcome entered the numerical 2025 fit, but the *research design* was not prospectively frozen. Thus 2025 is **retrospective transport, not untouched OOS**. Development ablations were also evaluated, so nominal statistical tests are exploratory.

## 3. Primary Brier and probabilistic results

Brier (lower is better), identical target dates within each year:

| Period | N / ≥1% nights | Historical incidence | HAR only | GVZ only | HAR + GVZ | Relative gain vs historical |
|---|---:|---:|---:|---:|---:|---:|
| 2023 chronological | 256 / 25 | 0.089595 | 0.088378 | 0.087299 | **0.087457** | **2.39%** |
| 2024 chronological | 259 / 24 | 0.084713 | **0.083772** | 0.084560 | 0.083812 | **1.06%** |
| 2025 retrospective frozen-parameter | 254 / 43 | 0.144108 | 0.136964 | 0.132209 | **0.131277** | **8.90%** |

2025 relative improvement to **HAR only** = (0.136964-0.131277)/0.136964=**4.15%**. GVZ-only is extremely competitive in 2025 (Brier 0.132209, AUC 0.7065), so do **not** claim unique incremental synergy on an unquestionable basis; the multi-input 2025 Brier advantage over GVZ-alone is only ~0.000932.

AUC for ranking ≥1% overnight events (2023 / 2024 / 2025):
- HAR + GVZ **0.5841 / 0.5888 / 0.6969**;
- HAR only **0.5560 / 0.6108 / 0.6585**;
- GVZ only **0.5823 / 0.5459 / 0.7065**.

All-year likelihood analysis matters: the simple GVZ and HAR variants alternate as strongest in 2023/24; the combined model avoids a negative Brier skill vs historical rate in every year but is not superior to every ablation in each year. 2025 mean combined probability = **15.46%**, realized event rate = **16.93%**, less underpredictive than the earlier 2023-only warm-up probability model.

Log-loss: 2023 combined **0.31402** vs historical **0.32664**; 2024 **0.30757** vs **0.31193**; 2025 **0.42276** vs **0.47028**.

## 4. Paired five-date block-bootstrap uncertainty / stress

Using the *already-recorded* held-out-per-origin predictions, circular 5-date moving blocks, 4,800 seeded resamples, percentile intervals for annual difference `Brier(historical) - Brier(HAR+GVZ)`:

| Year | Point Brier gain | Exploratory 95% block interval | Against HAR-only point gain |
|---|---:|---|---:|
| 2023 | +0.002138 | **[-0.000224, +0.004409]** | +0.000921 |
| 2024 | +0.000901 | **[-0.001601, +0.003648]** | -0.000040 |
| 2025 retrospective | **+0.012831** | **[+0.003816, +0.024097]** | **+0.005687** |

2025's annual difference vs HAR-only has exploratory interval approximately **[+0.001249, +0.011068]**. **No p-value or interval here is corrected for multiple hypothesis/model search, nonstationarity, opened-archive selection or program-selection effects.** 2023/2024 intervals include zero, so the two development-year gains are *not independently significant*.

Stress ablations on unmodified 2025 forecasts:
- H1: Brier **0.149663** vs baseline **0.165485**;
- H2: **0.114283** vs **0.124350**;
- remove three biggest absolute nights: combined **0.125682** vs base **0.136370**;
- remove seven biggest: combined **0.118432** vs base **0.125760**.

Thus 2025 Brier improvement is not just one or several explosive price events. But half-year and deletion checks are still **within** the already inspected 2025 archive.

## 5. Fixed-developer-quantile *diagnostic* risk-warning operating point

At the empirical 80th percentile of **2023–2024 probability forecasts**, set once, the combined probability threshold is **0.14184363080752652**. The historical coverage changes under an evolving risk regime:

| Period | Alarm dates / all | ≥1% actual events captured | ≥2% actual events captured |
|---|---:|---:|---:|
| 2023 | 67/256 | 8/25 | 0/2 |
| 2024 | 37/259 | 6/24 | 1/5 |
| 2025 retrospective | 113/254 | 30/43 | **7/7** |

**Warning:** 2025's 7/7 ≥2% event capture is at **113 alerts (~44.5% of dates)**; it must **not** be compared with a 95-alert/6-of-7 rule as if alert budgets were equal. The wider alert population increases sensitivity but lowers specificity. This is *absolute-move* early warning, not a 7/7 correct direction forecast. The research model still requires cost and false-alarm utility assessment to choose a tradeable operating point.

## 6. Failed direction hypotheses / what remains unsolved

Separate mechanism screen using 2023–2025 origin-safe completed 09:00–17:00 15-minute XAU paths (daily OHLC realized volatility, semivariance imbalance, day high/low close location, bipower jump proxy, intraday early/late returns), D-1 GVZ and D-1 DGS2:
- Built 780 complete daily price-path candidate days; on 2023–2025 frozen overnight cohort, 764 had complete **raw OHLC + target** including 2025 right-censoring at year-end.
- 2023–2024 prequential low-capacity logistic *direction* heads based on path geometry, afternoon pressure, historical GVZ/rates and their combinations generally lacked transportable balanced skill. Examples: path-shape model 2023 BA≈53.55%, 2024≈47.16%, 2025≈51.81% on its comparable full-date cohorts; full path + GVZ 48.28% / 49.27% / 48.94%.
- Continuation/reversal simplistic heuristics and online M4/PAIR error weighting had already failed in prior `GOLD_EXECUTION_TAIL1_PROBABILITY_RESEARCH_RESULT_2026-10-08.md`.
- Consequently **no new full-coverage UP/DOWN claim**, no action outside frozen PRAMV V1, and no transfer from magnitude probability to sign.

This negative result matters: the new probability gain is in the magnitude/risk task, not directional market timing. A genuinely independent *price discovery* signal such as properly aligned COMEX GC basis/volume or signed macro surprise requires new source audit on exact-comparable rows before direction enhancement can be claimed.

## 7. Reproducibility artifacts & promotion gate

- Forecast rows: `GOLD_OVN_2022_WARMUP_GVZ_TAIL1_PREDICTIONS_2026-10-08.csv` (769 rows)
- Summary: `GOLD_OVN_2022_WARMUP_GVZ_TAIL1_METRICS_2026-10-08.csv` (three years)
- Source-to-forecast executable audit: `tools/gold_execution_har_gvz_warmup2022_20261008.py` (expected per-row maximum probability difference under 1e-8 on independent execution; the paper's research values were also independently reconstructed in a JS audit). Its GitHub Actions run is **not yet available**; current numeric claims are from direct in-chat reconstruction and persisted evidence, not from a completed separate CI job.
- Immutable frozen direction control: `GOLD_EXECUTION_PRAMV_V1_PROSPECTIVE_FREEZE_2026-10-07.md`.

**Next scientific proof, before production:** independently execute the source-rebuild script in repo CI; verify literal feature timestamps/absence of vendor backfill revision; lock this single compact HAR+GVZ probability head; score a genuinely future, unseen run with timestamped probabilities, proper calibration and matched HAR/GVZ/simple incidence comparators, with block/SPA uncertainty and no further threshold selection. Then evaluate whether risk can reduce losses on real bank quotes with bid/ask, ready-time delay, long-only inventory and 09:00–17:00 user execution restrictions. *None of these prospective economic criteria are yet satisfied.*

## 8. Academic sources

- Corsi (2009), *A Simple Approximate Long-Memory Model of Realized Volatility*, Journal of Financial Econometrics 7, 174–196. DOI: 10.1093/jjfinec/nbp001.
- Cboe, *GVZ Index Dashboard / Methodology*, https://www.cboe.com/us/indices/dashboard/gvz/ : GVZ is a GLD-option-derived expected 30-day volatility index, not an overnight direction predictor.
- Sobti, Sehgal & Ilango (2021), *How do macroeconomic news surprises affect round-the-clock price discovery of gold?*, International Review of Financial Analysis 78, 101893. DOI: 10.1016/j.irfa.2021.101893. GC/New York price discovery is multi-venue, asymmetrically sensitive to announcements; this is mechanism authority, not proof of this Istanbul forecast.
