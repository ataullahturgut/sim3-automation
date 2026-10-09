# R6 | XAU/USD Istanbul DAY 09→17 — Why did 2026 CPI/NFP DAY forecast seem 78.57% accurate?
**2026-10-09. GPT-6 actually executed read-only Neon SQL for source-qualified 2023/24/25 and 2026 native.** Status: **TRUE DIAGNOSTIC RESULT + EXPLORATORY CALENDAR RISK IMPROVEMENT, ZERO VALIDATED HIGH-ACCURACY SIGNED TRADE**.

## 0. Scientific governance / prior studies
- R5 original result 2026 11/14 right (78.57% accuracy) on CPI/NFP days; immediately selected for follow-up, **not an uninspected dataset**.
- R6 original decomposition formula prereg BEFORE the specific subinterval queries: `GOLD_R6_20261009_CPI_NFP_INTRADAY_RETURN_ATTRIBUTION_PREREG.md`.
- R6C month/weekday negative-control prereg before computing randomization outcomes: `GOLD_R6_20261009_EVENT_FIRST15_MONTH_WEEKDAY_MATCHED_PLACEBO_AUDIT_PREREG.md`.
- R6D late-entry **explicit POSTHOC hypothesis** documented before cross-year and no-event evaluation: `GOLD_R6D_20261009_POST_RELEASE_15MIN_SIGN_CONTINUATION_RETRO_HYPOTHESIS_PREREG.md`. This rule was inspired by already-inspected 2026 event first15/post positive outcomes and must not be called independently pre-registered discovery.
- Source: 2023–25 `gold_research_evduka_xau_session_target_candidate_v1` plus original same-source BID/ASK `gold_research_evduka_xau15m_bidask_candidate`; 2026 `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2`, require `m1_matched=15`; same Dukascopy upstream, separately retrieved, **not independent vendor**. Official BLS historical CPI/NFP release clock 08:30 ET; calendar https://www.bls.gov/schedule/2026/home.htm; 2023–25 exact UTC first-prints from `GOLD_EXECUTION_PRAMV_OFFICIAL_2025_MACRO_SOURCE_GOVERNED_V2_20261008.csv`; each historic UTC time independently matched America/New_York local 08:30, no mismatch. No surprise, price, actual or consensus released AFTER issue ever used in `B4` or `DIR4` pre08:45 inputs.
- Times: entry quote closed 09:00TR, event pre-close 08:30 ET=15:30TR summer/16:30TR winter, first post-event 15min close at 15:45/16:45TR, day exit quote17:00TR. Source MID=(BID close+ASK close)/2; ret log ratio; event “post” includes first 15minute instant reaction; later-only remainder excludes it.
- Gate: 17 contiguous fully completed origin M15 bars and all 09/event-/event+15/17 anchors. Event dates absent vendor source are **NOT** categorized no-event. Annual available full-source original-day counts 2023 256,2024 259,2025 258,2026 147 (2026 source date rows148, one not full; original scheduled CPI+NFP 2026 Jan-Oct=19, only14 source complete). All 2023–25 original source midpoint direction versus source-governed labels **0 mismatches** on scored days. No source filling.

## 1. First major causal timing diagnosis — fixed SAME DIR4 model, different subinterval labels
**ORIGINAL target is 09→17. Other rows below are diagnostic alternative targets and cannot be substituted as the claimed original model's accuracy.**
|Year|CPI/NFP source-qualified N|Forecast correct 09→news pre|Correct news→17 INCLUDING initial jump|Correct first15m news shock|Correct subsequent news+15→17|Correct 09→17 whole day|
|---|---:|---:|---:|---:|---:|---:|
|2023|23|11/23 (47.83%)|12/23 (52.17%)|12/23 (52.17%)|13/23 (56.52%)|10/23 (43.48%)|
|2024|24|9/24 (37.50%)|12/24 (50.00%)|12/24 (50.00%)|9/24 (37.50%)|12/24 (50.00%)|
|2025|22|13/22 (59.09%)|11/22 (50.00%)|13/22 (59.09%)|11/22 (50.00%)|10/22 (45.45%)|
|2026|**14**|**5/14 (35.71%)**|**12/14 (85.71%)**|**11/14 (78.57%)**|**8/14 (57.14%)**|**11/14 (78.57%)**|

All subinterval labels computed from original-source prices after outcome. **2026 forward event shock is where apparent predictive correctness resides, not in 09-to-news drift.** 2026 post-split agrees signed entire day 13/14, while pre-split agrees with entire day only6/14; 2026 pre and post have opposite signed moves on 9/14 dates. In 2023–25 annual post-news 08:45 fixed forecast is roughly50% despite 2026 12/14. 2026 native forecast on CPI/NFP event dates is BIT-IDENTICAL to simpler B4, so **no specialized predictive macro algorithm was involved**; cannot attribute 2026 to a newly learned news-sign relationship.
**Base-rate caveat:** 2026 14 event first15 reactions have 11 UP and3 DOWN; always-UP yields11/14 raw hits equal to DIR4 first15 11/14, though DIR4 captures three downside reactions and has BA86.36% in this tiny selected sample. Whole 2026 post has10 UP and4 DOWN; always-UP is10/14 whereas preorigin DIR4 post12/14, only +2 raw hits. Calendar selection and 2026 underlying price trend may explain much of the anomaly.

### 2026 event groups NOT all scheduled dates
Native full-price source14 of 19 known CPI/NFP dates; 2026 CPI8 source-qualified of9 official listed, NFP6 of10. The 6 source-qualified NFP dates are May–October 2026: frozen original DIR4 correctly calls all6, an impressive but especially high-variance + source-selection-confounded result. 2026 CPI original full-DAY forecast5/8. **Do not report 6/6 as a stand-alone high performance news model**. Missing 5 source-date failures/quarantine unchanged, cannot assume results for other 5.

## 2. Clock placebo — news impulse magnitude *does* increase in a repeatable way across years
Control: non-CPI/NFP original DAY date, same **08:30 ET (New York DST aware)** artificial 15minute market interval, same vendor source and original 17 completed preorigin bars. Other economic releases on control days are NOT screened, which biases this contrast toward the null if other announcements also move markets.

|Year|CPI/NFP dates|Median absolute first15 news move|Same-clock no-CPI/NFP days|Median absolute same-clock15m move|News first15 ≥25bp|No-news clock15m ≥25bp|
|---|---:|---:|---:|---:|---:|---:|
|2023|23|33.15bp|233|9.64bp|14/23 **60.87%**|33/233 **14.16%**|
|2024|24|43.15bp|235|8.89bp|19/24 **79.17%**|27/235 **11.49%**|
|2025|22|20.78bp|236|8.39bp|10/22 **45.45%**|23/236 **9.75%**|
|2026|14|43.03bp|133|13.45bp|10/14 **71.43%**|21/133 **15.79%**|

2023–25 pooled event first15 >=25bp **43/69 (62.32%)**, non-event **83/704 (11.79%)**, +50.53pp, 5.29x descriptive risk ratio. 2026 follows in the same risk direction **10/14 vs21/133, +55.64pp**, ~4.52x. **A release-calendar-aware large-event-move risk alert survives the yearwise contrast, whereas signed surprise prediction does not.** This is conditional risk at a KNOWN upcoming event time, not evidence of the direction or bank tradability of the quote jump. `25bp` binary threshold is exploratory and was not a virgin holdout preregistration.

## 3. Actual causal information-time check — can user capture event-first15 abnormal sign edge after seeing the announcement?
A new late-window signal: at 15:45TR summer or16:45TR winter, first post-news M15 closes; predict `sign(first15 news reaction)` for **remaining portion to bank17** and test using original source quote MID. Hypothesis was recognized POSTHOC from event reaction; cross-year was then honestly executed (no retuning):
|Year|CPI/NFP dates|First15 sign correct about subsequent remaining return|No-event same-clock continuation|
|---|---:|---:|---:|
|2023|23|12/23 **52.17%**|110/233 **47.21%**|
|2024|24|11/24 **45.83%**|124/235 **52.77%**|
|2025|22|12/22 **54.55%**|117/236 **49.58%**|
|2026|14|**7/14 50.00%**|58/133 **43.61%**|

**DECISIVE NEGATIVE FALSIFICATION:** The high 2026 signed news edge largely lives IN the first 15-minute reaction, not in a momentum continuation after a human can safely see that reaction. 2023–25 combined 35/69=50.72% and 2026 only7/14=50.00%; do NOT launch a first15-followup BUY/SELL strategy. In addition 2026 same14 dates original 08:45 DAY model DIR4 predicted only8/14=57.14% for remaining portion. For a winter CPI/NFP release at 16:30TR, an after-first15 decision at16:45 has only15 minutes to17. No bank quotes, widened spread or economically executable model proven. For a naively unlimited long/short sign(first15) on remaining segment, 2026 hypothetical MID signed sum+168.82bp over14 source-event days, but **June05 one single move contributed +183.09bp; subtracting that one favorable day leaves −14.27bp**, and 2023/24/25 total signed gross is respectively −87.25bp/−198.62bp/−23.43bp. This is a failed robust strategy even ignoring spread/cost.

## 4. Same-month + weekday alternative-days negative control on 2026 observed 14 event dates
10,000 fixed-seed 20261009 deterministic LCG replicates. For EACH of the 14 source-eligible event dates, draw with replacement one source-eligible non-event date from same month AND weekday, fallback same month only if pool empty (one 2026-10-02 Friday falls back October month4 rows). Include all 19 event dates in exclusion pool even if source-incomplete; do not treat known release as no-release.
|Endpoint|Actual fixed DIR4 correct on event dates|Matched no-event 14-date mean correct|Empirical tail frequency|
|---|---:|---:|---:|
|Before release|5/14|8.08/14|5.05% (≤5)|
|First15 news reaction|11/14|8.01/14|5.01% (≥11)|
|Entire post-release until17|12/14|7.50/14|**0.13%** (≥12)|
|Full 09→17|11/14|7.33/14|2.19% (≥11)|
|After first15 to17|8/14|8.33/14|71.83% (≥8)|

**CRITICAL INTERPRETATION:** 0.13% is NOT a confirmatory p-value because (i) the question and 14-event cohort were selected after seeing strong 2026 event outcome; (ii) dated news events cannot be randomized; (iii) 2026 already inspected repeatedly and 2023–25 contradict first15 signed edge; (iv) small pools and one month-only fallback. It confirms a descriptive 2026 anomaly under this particular weekday/month placebo, **not a statistically validated portable predictive signal**.

## 5. Actual additional predictability experiment: elementary frozen time-ordered *event risk* probability
Question: at 08:45, only the officially scheduled event class `E=known 08:30ET CPI/NFP` (yes/no) is available. Can a risk-head estimate `P(|XAU MID 08:30ET→08:45ET future 15min news-clock return| >= 25bp)` better than a **pooled constant prior** trained on exactly the same matured previous-year dates, with no 2025 or 2026 fitted data at each scoring year? Post-hoc model class/threshold exploration. **This is NOT a direction forecast**.

Train reference exact group counts using already-validated event/no-event magnitude classification:
- 2023+2024: event `33/47` crossed25bp; no-event `60/468`; pooled `93/515`.
- 2025: event `10/22`, no-event `23/236`, total n258.
- 2023+2024+2025: event `43/69`, no-event `83/704`, pooled `126/773`.
- Native2026: event `10/14`, no-event `21/133`, total n147.

Pre-origin binary risk probabilities use Beta(1,1) Laplace smoothing `(x+1)/(n+2)` learned only 2023–24 before predicting2025 and 2023–25 before predicting2026. Control is exact same training cohort **pooled** Beta(1,1) prior; both fixed for each scoring year. No 2025 test or2026 stress rows in their own fit; no extra predictor.
|Holdout/stress year|Event risk P from past|No-event risk P from past|Constant from same past|Event/no-event observed|Event-head Brier|Constant Brier|Relative Brier reduction|
|---|---:|---:|---:|---:|---:|---:|---:|
|**2025 inspected** (train23–24)|69.39%|12.98%|18.18%|45.45% /9.75%|**0.107441**|0.114453|**6.13%**|
|**2026 inspected native** (train23–25)|61.97%|11.90%|16.39%|71.43%/15.79%|**0.141959**|0.168622|**15.81%**|

This is a **real numerical gain on the proper (probabilistic extreme-move) objective in chronological retrospective validation**, and risk-class pattern persists each year. But 2025 and 2026 are repeatedly inspected, threshold25bp was chosen during exploratory diagnosis, official historical schedule publication vintage unproved, vendor remains same upstream, missing2026 event days and quote spikes make bank application unqualified. Do not call it untouched test or actionable bank execution or >70% XAU UP/DOWN direction. Brier improvement mostly comes from a clear known US release-calendar feature; it need not require RD-Agent or complex GNN. A fully preregistered forward calendar risk score and actual broker spread/quote metrics are required for independent confirmation.

## 6. Decision and next falsifiers
- **Signed DAY forecast new champion: NONE.** Original DAY2026 DIR4 BA56.30%, raw55.78% on147; OVN existing CBR BA60.31% N72 untouched by R6.
- **EXPLANATION from R6:** 2026 anomalous event-day 11/14 full-day directional correctness is driven by pre08:45 price sign coincidentally matching an unusually influential 08:30ET release response; pre-release drift only5/14. Pre-scheduled news day plus prior-price sign not robust signed across23–25. Significant *descriptive* late US-session volatility risk: known CPI/NFP day reliably elevates 15:30/16:30TR 15m >=25bp risk across 2023–26.
- **Explicit causal/tradability warning:** The 12/14 “post-news correct” includes an event-time move not known/tradable before its completion. The only observable reaction-followup experiment yields no signed accuracy benefit (7/14). No licensed bank instantaneous executable BID/ASK, slippage, timing uncertainty, short ability. If deployed merely as cautionary risk alarm, must consider open existing positions, user 09–17 trading restriction, volatility scale drift, and broker spread.
- **Further research hypothesis, not yet result:** improve risk forecasts combining known schedule, pre08:45 implied rate/yield/broad dollar, regime and event type; then study if *any* source-pure independent before-news directional signal exists, validated 2023–24→2025→inspected2026 before prospective frozen cohort. No back-fitting 2026 CPI/NFP event-specific gate into DAY sign.
