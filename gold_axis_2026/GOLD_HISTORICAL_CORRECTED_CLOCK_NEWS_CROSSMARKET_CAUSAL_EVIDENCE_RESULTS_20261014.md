# Gold historical event research — corrected price clock, actual macro timing, cross-market cause falsification
**14 October 2026 | 2023–2025 | EVIDENCE-BASED RETROSPECTIVE RESEARCH | NO TRADING, NO FORECASTING**

## Executive finding
Original historical gold-event source contained a verifiable New York 17:00 session-boundary defect. We reran actual archived 15-minute XAU BID/ASK mid bars, **exactly recovered all 42 original 3%-reversal ZigZag legs**, and recomputed the full ZigZag algorithm on corrected 17:00 New York session closes. **42 legs remained 42; 4 legs' extrema dates changed, all directions stayed the same.** The October–November 2025 **gold vs equity market signature CHANGED** for one corrected leg: an originally gold-and-equities-up rebound is actually **gold-up/equity-down** on the corrected time interval.

We separately compared **85 dated CPI/NFP/FOMC releases** to XAU M15 and CME oil/Nasdaq/10Y-note/gold/silver H1 around release timestamps; 2025 FOMC missing in the older macro ledger was repaired as **8 more separate regular scheduled announcements** using the already published Astra independent event study. We audited **95 historical price-record to article-date** linkages, distinguishing ex-post commentary from initial cause. These findings concern **evidence for historic mechanism candidates**, not forecasting or AL/SAT.

**PRIMARY NEW RESEARCH OUTPUTS**
- [42 original-vs-corrected NY17 FULL-ZIGZAG rescan — 42 records](GOLD_HISTORICAL_42_V1_ZIGZAG_NY17_FULL_RESEGMENTATION_20261014.csv)
- [Reproducible 3% ZigZag+original/corrected timestamp SQL/Python](tools/gold_historical_42_ny17_zigzag_replay_20261014.py) — private 774-row vendor input intentionally NOT stored in public GitHub.
- [95 V1/V2 anchored old-vs-corrected endpoint audit, note V2 NOT resegmented](GOLD_HISTORICAL_95_NY17_FIXED_CLOCK_ENDPOINT_AUDIT_20261014.csv)
- [Four changed 2025 swing legs rejoined to metals, equities, CL/NQ/ZN and GVZ](GOLD_HISTORICAL_4_RESEGMENTED_SWINGS_CORRECTED_CROSS_MARKETS_20261014.csv)
- [95-event causal chronology rebalanced to corrected 42 V1 extrema; V2 provisional](GOLD_HISTORICAL_95_EVENT_CAUSAL_TIMELINE_CORRECTED_V1_RECONCILED_V2_20261014.csv)
- [85 dated macro notices × five CME H1 series =425 cross-price rows](GOLD_HISTORICAL_85_MACRO_RELEASE_CME_5_ASSET_H1_ENCLOSING_REACTIONS_20261014.csv)
- [85-release XAU spot M15 + CME cross-market joined signature](GOLD_HISTORICAL_85_MACRO_NEWS_XAU_M15_CROSSMARKET_H1_SIGNATURES_20261014.csv)
- [2025 **8 previously missing regular FOMC** × five XAU M15/control rows =40](GOLD_2025_FOMC_8_MISSING_EVENTS_XAU_M15_EXPLORATORY_REPAIR_20261014.csv)
- [2025 **8** FOMC × five CME assets =40](GOLD_2025_FOMC_8_MISSING_EVENTS_CME_5_ASSET_H1_20261014.csv)

## 1. Verifiable clock reconstruction — 2023–2025
**Raw source:** Neon Gold Control `gold_research_evduka_xau15m_bidask_candidate`, EVTradingLabs/Dukascopy-derived XAU M15 BID/ASK, single source id, price `mid=(bid_close+ask_close)/2`; bar timestamp is START, so bar end = start+15 minutes. NY17 close window must include a bar that **ENDS at 17:00 America/New_York** in the earlier session. Old session label `DATE((bar_end AT TIME ZONE 'America/New_York') + interval '7h')`; corrected session label **subtracts one microsecond** from the expression, so an exactly 17:00-ending bar stays at that NY session's close. Eligible weekdays at least **70 actual 15m bars**, no synthetic fill. Same eligible 774 days in both old and corrected (2023 **257**, 2024 **259**, 2025 **258**).

| Year | Paired eligible NY17 sessions | Old vs corrected close price differs | Mean absolute price difference | Largest absolute difference |
|---|---:|---:|---:|---:|
| 2023 | 257 | 248 | **0.023620%** | **0.394854%** |
| 2024 | 259 | 249 | **0.035964%** | **0.451177%** |
| 2025 | 258 | 249 | **0.045399%** | **0.264384%** |
| **All** | **774** | **746** | — | — |

**Reproducibility challenge passed:** `>=3%` reversal of *eligible completed NY17 daily close*, tracking peak and trough and recording retro-confirmation date; old series reproduces **42/42** original `GOLD_MAJOR_MOVE_EVENT_ATLAS_2023_2025_V1_20261013.csv` IDs, endpoints, directions, original percentages (rounding within 0.001 percentage point), 41 completed/one year-end open. Thus this is not a different heuristic dressed up as original. Running **same exact 3% code** on corrected close yields **42 legs, 42 direction matches, 38 matching extremum date intervals and 4 changed**.

| Original V1 key | Legacy old dates / return | CORRECTED NY17 resegmented dates / return | Original and new turning-point confirmation |
|---|---|---|---|
| `SWING_V1_028` | 2–8 April 2025, **−4.788287%** | **2–7 April**, **−4.776625%** | 9 April |
| `SWING_V1_029` | 8–21 April, **+14.876772%** | **7–21 April**, **+14.779037%** | 23 April |
| `SWING_V1_038` | 20 Oct–4 Nov, **−9.782227%** | **20–29 Oct**, **−9.784683%** | 10 November |
| `SWING_V1_039` | 4–12 Nov, **+6.779359%** | **29 Oct–12 Nov**, **+6.755117%** | 17 November |

**NO-FALSE-COMPLETION RULE:** The V2 53 groups are NOT the 42 ZigZag. V2 uses maximum fixed-horizon 1h/4h/12h and 1/3/5 sessions including intraday maxima, so simply comparing 53 old/new date-endpoint returns does **not** rederive V2 thresholds/first flags, clusters, 151 main +23 rapid event days. All 53 original V2 statuses in the 95-document index remain `V2_RECALC_PENDING`; four date-endpoint/label sign mismatches are **not** four reversed V2 event labels.

## 2. New-date market verification — a mechanism-relevant signature reversal
Source: previously archived daily StakTrakr XAG/XPT/XPD, FRED S&P500/Nasdaq100 and official Cboe GVZ; Databento CME CL/NQ/ZN 1h continuous futures selected last UTC bar before 20:00 at both dates. These are **same-date-window retrospective comparisons with differing provider market-closing clocks**, not synchronised newsgiven 15-minute causal impulses; futures contract-roll checks are still required.

| Corrected V1 gold event | XAU change | XAG daily | S&P500 daily | CL WTI futures | GVZ delta **points** | Observable broad market signature |
|---|---:|---:|---:|---:|---:|---|
| 2–7 Apr 2025 `V1_028` | **−4.777%** | −10.467% | −10.734% | −13.813% | **+1.76** | Precious metal + equity + oil common sale; financial liquidity/tariff **plausible** |
| 7–21 Apr `V1_029` | **+14.779%** | Missing at chosen aligned daily endpoints | +1.895% | +3.970% | **+8.46** | Gold + equities up, GVZ up. Volatility rose despite gold rise — GVZ isn't directional |
| 20–29 Oct `V1_038` | **−9.785%** | −6.998% | +2.308% | +5.157% | **−6.73** | Gold+metals vs rising equity and oil: **NOT broad risk-asset co-sell** |
| 29 Oct–12 Nov `V1_039` | **+6.755%** | +6.975% | **−0.576%** | −3.164% | **+1.12** | **Gold/white-metals UP while equities DOWN**, an equity-risk/gold-relative-demand candidate |

**Changed class:** before correcting the old Nov 4–12 window, `SWING_V1_039` had `EQUITY_UP_GOLD_UP_SIMULTANEOUS_RALLY`. On the corrected **Oct 29–Nov 12** window it has `EQUITY_DOWN_GOLD_UP_HAVEN_COMPATIBLE`. We **did not assert geopolitical or haven cause**. We only flagged the historical economic mechanism grouping for **renewed firstprint/FX/yield/ETF/COT investigation**. Attributing October 2025 correction to simple broad risky-asset selling contradicts these daily market observations.

## 3. Time alignment of 95 legacy economic accounts
The old 95-case candidate cause atlas held 42 V1 +53 V2 source leads. The new [35-column consolidated audit](GOLD_HISTORICAL_95_EVENT_CAUSAL_TIMELINE_CORRECTED_V1_RECONCILED_V2_20261014.csv) rebases all V1 extrema to corrected V1 dates (the V2 price flags are preserved provisional).

| Article's reported date relative to corresponding corrected V1 extremum/legacy V2 first threshold **date only** | Records |
|---|---:|
| **Article dated after** price anchor | **55** |
| Article dated on same calendar day | **16** |
| Article dated before | **7** |
| **No curated dated source** | **17** |
| **Total** | **95** |

**30 of the 55 after-anchor sources are even dated after their original entire legacy price window** (20 V1 and 10 V2). Those 30 **cannot themselves be the initial contemporaneously released information** behind prior prices, though their retrospective commentary may be valid. The remaining after-anchor reports may concern **new middle-of-leg subevents**; without original firstprint timestamp and move onset time, they cannot be assigned as initial onset triggers either. A V1 start is an ex-post extremum, and a V2 first flag is a threshold crossing, **not** necessarily the first price move minute. Newspaper URL metadata is often updated; publication date only is a conservative temporal limitation, not a 55-event causal refutation.

**13/95** price records share their retrospective start/threshold calendar date with at least one of the 85 originally catalogued CPI/NFP/FOMC release dates. Six of those records match one of the **five separately checked** BLS/Fed primary source release notices (same release may occur in more than one overlapping price record). None of these coincidences certifies first price-onset timing or unique economic cause.

## 4. Recomputed multi-asset scheduled macro reactions: cross-market mechanisms can conflict
Existing [85-release XAU M15 first-15min event study with same-weekday/hour weekly controls](GOLD_2023_2025_CPI_NFP_FOMC_M15_RELEASE_WEEKMATCH_EVENTSTUDY_20261014.csv) is not a full-year official-calendar audit: 35 NFP, 34 CPI and **only 16 FOMC for 2023–24**, 2025 FOMC missing. Original first15m NFP **29/34** > preceding same-hour matched-placebo abs move median; CPI **27/34**; that supports **conditional movement intensity**, not price move's cause or direction.

**New H1 extension (actual query):** All 85 events × five Databento CME continuous-futures roots =425 research rows with **last fully completed bar before announcement** and earliest admissible **fully completed bar at least 1h after event timestamp**, up to 4h. The full H1 **enclosing** interval between two bar-endpoints often lasts **1–3h** and may include the fraction of the pre-event hour. This is NOT identical to the XAU 15-minute first-release impulse or to a causal high-frequency instrument. No filling missing GC/SI/ZN bars.

| Futures series | Usable 85 original release comparisons | Missing or not admissible |
|---|---:|---:|
| WTI **CL.c.0** | **84/85** | 1 |
| Nasdaq **NQ.c.0** | **85/85** | 0 |
| US ten-year note **ZN.c.0 PRICE** | **79/85** | 6 |
| COMEX Gold **GC.c.0** | **50/85** | 35 |
| COMEX Silver **SI.c.0** | **30/85** | 55 |

Of these 85 release signatures, **17** had XAU↓, ZN-price↓ and NQ↓, **11** had XAU↓/ZN-price↓ but NQ↑, **8** XAU↓/ZN-price↑ (simple 'higher yield causes gold fall' insufficient), **13** XAU↑/ZN-price↓ (simple 'lower yield causes gold up' insufficient), **22** XAU↑/ZN-price↑/NQ↑, **7** XAU↑/ZN-price↑/NQ↓, and **7** insufficient valid multi-asset quotes. These are **descriptive observed sign combinations with different XAU M15 versus CME H1 windows**, *not 17+11+... independent mechanisms or identified effect coefficients*. Remember **ZN PRICE not 10Y treasury yield**; bond price commonly moves inversely to its yield, but roll, CTD and basis can complicate it.

**2025 FOMC gap partial REPAIR:** Reused eight regular FOMC timestamps exactly from Astra/USMPD [2020–25 statement pilot source](https://github.com/ataullahturgut/sim3-automation/blob/research-gold-fomc-mechanism-pilot-20261013/gold_axis_2026/GOLD_FOMC_PILOT_2020_2025_EVENT_LEVEL_V1_20261013.csv): Jan29 19:00Z, Mar19/May07/Jun18/Jul30/Sep17/Oct29 18:00Z and Dec10 19:00Z. Official Fed statement 2pm EDT/EST verified on representative primary sources. **8/8 XAU M15 first15/60 bars obtained**, 8×4 weekly same-time control windows pulled, not yet full other-macro contamination audit. CME 40 rows: CL8/8, NQ8/8, ZN7/8, GC4/8, SI4/8. **2023–25 named original macro announcement time pool now 85+8=93 dated records in separate datasets**, NOT '93 exhaustive official releases' because 2025 NFP/CPI old calendar gaps and other release families are still not repaired. **Do not mechanically extend previous 85-sample sign-test p-values to 93**.

First 15-minute 2025 FOMC spot responses: Jan29 **−0.134%**, Mar19 **+0.266%**, May07 **+0.301%**, Jun18 **+0.199%**, Jul30 **−0.061%**, Sep17 **+0.027%**, Oct29 **−0.288%**, Dec10 **+0.425%**. Several change sign by first hour, illustrating publication-time shock, conference and revised policy-path communication must be separated; USMPD paths back-compiled as of 2026, not pre-release available.

## 5. Four high-value mechanisms checked against dated primary source and actual quantitative markets
**A. 3 February 2023 US employment release, USD/rate candidate** — US BLS [original January 2023 employment release, 08:30 EST = 13:30 UTC, +517k jobs](https://www.bls.gov/news.release/archives/empsit_02032023.htm). Original MACRO ledger surprise +332k from its consensus. Same-period XAU M15 first15 **−1.349%**, first hour **−1.731%**; enclosing CME GC **−1.776%**, ZN **−0.676%**, NQ **−0.108%**, but CL **+1.710%**. A USD/discount-rate path is plausible, yet we have **NO synchronized direct 2Y/10Y rate and DXY**, so cannot prove the effect share. An **all-assets co-sell hypothesis is contradicted by oil rising** in the broader enclosing hourly window.

**B. 10 March 2023 BLS jobs versus bank stress — explicit competing shocks** — [BLS 08:30 EST/13:30 UTC +311k jobs](https://www.bls.gov/news.release/archives/empsit_03102023.htm), prior ledger surprise +106k. XAU M15 first15 **+0.540%** even though the headline payroll surprise was positive; enclosing CME ZN-price **+0.615%**, NQ **−0.835%**, CL **+0.972%**, GC/SI H1 missing. [FDIC bulletin on SVB receivership originally sent 11:42 EST = **16:42 UTC**](https://content.govdelivery.com/accounts/USFDIC/bulletins/34de35b); [California DFPI bank closure](https://dfpi.ca.gov/press_release/california-financial-regulator-takes-possession-of-silicon-valley-bank/) and previous banking distress already in news. **The 16:42 FDIC bulletin cannot be the initial new firstprint at 13:30 behind the first15m XAU reaction.** But bank stress *prior to announcement* can compete with payroll narrative; would require as-of news timeline and official job report's unemployment/wages and revisions. Do not overclaim NFP → gold UP cause.

**C. 7 June 2024 PBoC + NFP — two distinct dated catalysts** — [Bloomberg 09:42 UTC reported PBoC gold purchase pause with gold already down ~1.5%](https://www.bloomberg.com/news/articles/2024-06-07/gold-slumps-as-china-s-central-bank-halts-18-month-buying-spree). [BLS May employment report first released **12:30 UTC**, +272k](https://www.bls.gov/news.release/archives/empsit_06072024.htm), Reuters contemporaneous forecast around **185k**, while original research ledger says **182k** (consensus provenance discrepancy; +87k or +90k surprise). XAU spot M15 first15 *after NFP* **−0.612%**, CME GC **−0.960%**, ZN-price **−0.796%**, NQ **−0.289%**, CL **−0.092%**, SI missing. Neither PBoC story alone nor NFP alone identifies total day's effect; NFP cannot have caused all PBoC-era earlier decline. **Web page trap:** another Bloomberg URL is stamped **08:06 UTC** but was later updated and current page describes the **12:30 UTC** NFP outcome; never backdate its updated paragraph to 08:06 firstprint.

**D. 18 December 2024 Fed simultaneous statement+projections — broad rate/repricing** — [Official Fed statement 14:00 EST/19:00 UTC](https://www.federalreserve.gov/newsevents/pressreleases/monetary20241218a.htm), [projections also 19:00 UTC](https://www.federalreserve.gov/newsevents/pressreleases/monetary20241218b.htm), not 'rate cut alone = gold UP'. XAU M15 first15 **−0.760%**, first60 **−1.223%**. Enclosing CME GC **−1.051%**, SI **−0.955%**, ZN-price **−0.626%**, NQ **−1.681%**, CL **−0.396%**. Broad multi-asset repricing supports a policy/rate channel candidate, but surprise decomposition into monetary shock versus Fed private information and same-minute rate changes requires a separate instrument — see independent FOMC PR #122.

**E. 4 April 2025 tariff shock versus NFP — already falling before NFP** — [BLS Mar 2025 employment release at **12:30 UTC**, +228k](https://www.bls.gov/news.release/archives/empsit_04042025.htm). XAU M15 **PREVIOUS one hour −0.975%**, then after NFP first15 **−0.261%**, 4h **−2.165%**; enclosing CME GC **−1.625%**, SI **−1.828%**, ZN-price **−0.165%**, CL **−0.292%**, but NQ **+0.365%** in its short hour window. [April 3–4 tariff-driven broad equity losses documented contemporaneously](https://www.cbsnews.com/news/dow-jones-today-stock-tariff-trump-4-3-25/). **NFP cannot cause the substantial preceding hour's negative XAU move;** and the intraday Nasdaq NQ positive return (in enclosing selected window) contradicts "everything in every intraday bar sold together". Apr 2–7 corrected multi-day data nevertheless show gold+equities+oil *fall together*. Different time windows can support different mechanisms; do not replace them with a single up/down label.

## 6. Why this is not yet completed causal attribution
- Price clock **V1 corrected/rescanned**. Price clock **V2 53 original multi-horizon flags/clusters NOT recalculated**; first flags aren't exact true first price onset.
- Original firstprint exact UTC not verified for **all 95**; the 55 sources after price anchor and 17 undated expose limitations. Most WGC Reuters articles are retrospective, not contemporaneously as-of original firstnews.
- CL/NQ/ZN / GC/SI H1 "enclosing" and XAU 15m are **NOT IDENTICAL windows**; safe descriptive patterns only. We have no fully synchronized DXY, 2Y/10Y yields, inflation breakevens or real TIPS yields, metal tick series and original ETF/CFTC PIT for all events.
- Databento CME `continuous_c` may cross contract roll; not a direct ten-year yield or ETF flow. Pre/post H1 availability is partial. Cboe GVZ daily change reflects before *and after* included, never automatically initial trigger or directional sign.
- Temporal macro association (85+8 selected scheduled events) contains non-event release controls for 85 and exploratory 8 controls, **but full official macro completeness and control contamination checks remain pending**. Initial 95 price events are *selected by outcome*, not unbiased exposure denominator; 95 classified price records != 95 independent events.
- Even carefully verified official BLS/Fed times plus price jumps, without competing news and matched non-event controls **do not establish that one information item caused the whole gold movement**, much less calculate attributable percentages.

**Scientific disposition:** `NY17_42_V1_FULL_RESEGMENTATION_PASS`; `NEW_V1_TURN_DATES_CHANGED_FOUR_LEGS`; `REJOINED_FOUR_CROSSASSET_PASS`; `95_CAUSE_CONTEXT_TEMPORAL_AUDIT_PASS_DATE_LEVEL_ONLY`; `CME_85_SCHEDULED_H1_CROSS_REACTION_MEASURED`; `2025_FOMC_EIGHT_SOURCE_GAP_PARTIAL_REPAIR_PASS`; `FULL_V2_HORIZON_REPLAY_PENDING`; `FIRSTPRINT_95_AND_SAME_UTC_RATES_PENDING`; `COMPETING_CAUSAL_MECHANISM_DISCRIMINATION_PENDING`.

**Next valid scientific work:** Recreate corrected 2023–25 V2 1h/4h/12h and 1/3/5-session thresholds and 53 clusters from M15; keep original IDs and construct old/new crosswalk (never silently overwrite them). Then get primary firstprint timestamps, same-minute USD nominal/real yield and metals/CL/NQ panels, and all applicable *no-big-move* release controls. The deliverable is historic **economic cause/counterexample** evidence, explicitly **not** an investment or AL/SAT decision.
