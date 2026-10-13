# XAU/USD 2023–2025 MULTI-HORIZON MOVE AND HISTORICAL NEWS ATLAS — V2
**Completed:** 2026-10-13. **Type:** descriptive archival research and candidate-catalyst dossier, NOT a predictive signal or econometric causal model.
**GitHub branch:** `gold-execution-channel-audit-20261006`. **Research data:** Neon Gold Control, `gold_research_evduka_xau15m_bidask_candidate`.

## 1. Answer to the objective
The legacy 42 ZigZag large trends are **not** the complete set of shorter important events. Re-scanning bid/ask-derived mid XAU quotes at actual 15-minute timestamps (not fabricated 1h OHLC) found:
- **774** valid 2023–25 New York 17:00-rollover source days (2023 257; 2024 259; 2025 258);
- **151** distinct source days with at least one absolute **3%** change over real elapsed 1h, 4h, 12h, or over 1/3/5 consecutive eligible trading-day closes; 1-hour had **0** qualifying dates, 4h/12h collectively **15** dates;
- **23** additional days with a **2%** 4h/12h move but no 3% primary condition; **174** distinct analysis days including these secondary days;
- these 151 3%-primary days yield **152 signed flagged-day rows** (one day meets both UP and DOWN in different windows) and are grouped into **53 directional contextual clusters** with a merge gap <=3 eligible trading sessions, separately by UP/DOWN; clusters may overlap between directions;
- The original **42 long ZigZag episodes** are retained as a separate descriptive map, not summed with 53 or 151.
- The % peak stated for a cluster is its **largest observed fixed-horizon absolute change among its flagged days**, not total low-to-high episode yield. `start` is first 3%-flagged date, **not necessarily true price-move start**, and not real-time entry issue.

| Year | Valid days | 3%-flagged days | Extra fast 2%-flagged days | Directional clusters | CPI/NFP release-day observed | Of those, 3%-flagged |
|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 257 | 24 | 11 | 10 | 23 | 4 |
| 2024 | 259 | 48 | 3 | 19 | 24 | 6 |
| 2025 | 258 | 79 | 9 | 24 | 21 | 5 |
| **Total** | **774** | **151** | **23** | **53** | **68** | **15** |

## 2. Data and timing contract
- Close = (15m bid_close + ask_close)/2, observed at `bar_start_utc + 15 minutes`. 1h/4h/12h are exact wall-clock lags (4/16/48 previous bars) only if observed endpoints are separated by **exactly** the required elapsed time. Market gaps/closed hours invalidate short-horizon comparisons; do not bridge weekends by counting bars.
- Session date = `(available_utc AT TIME ZONE 'America/New_York' + INTERVAL '7 hours')::date` to assign a 17:00 US Eastern rollover to the next trading-day label; daylight-saving conversion handled by Postgres zone. Calendar date label is not another publication time.
- 1/3/5 session returns use N previous *eligible* NY17 sessions' closes; do not confuse with 24/72/120 consecutive wall-clock hours.
- A given day can have price up and down in different windows; direction clusters need not be disjoint.
- Historic bid/ask-derived mid quotes are **not actual bank executable fills**. This work has no Turkey-hour or bank commission filter as requested.
- Existing prior forensic data QC (GitHub `GOLD_EXECUTION_2020_2025_PRICE_LABEL_FORENSIC_AUDIT_20261008.json`) is relevant but does not verify every external event narrative.
- 42-cluster source leads from older atlas are merely topic leads, not all checked against first-print archives.

## 3. Time-labelled, corroborated illustrative chains (not automatic causality)
**A. Banking crisis — 2023 Mar (C003, UP).** US regional-bank stress and bond-volatility repricing occurred in March. The 10 March SVB failure preceded the 13 March first flagged date; WGC 24 March discussed the developing banking/rates situation. Later documentation is **not an advance forecast**. https://www.gold.org/goldhub/gold-focus/2023/03/what-next-gold-volatile-bond-market

**B. 2023 Oct geopolitical repricing (C006, UP).** 7 October Israel attack was a surprise; following days saw haven buying and futures short covering. WGC's 7 November report is POST event; October COMEX short positioning and ETF stabilization were identified retrospectively. https://www.gold.org/goldhub/research/gold-market-commentary-october-2023

**C. Mar-Apr 2024 unconventional gold rally (C011/C012).** WGC April 9 explained March's outsized strength with gold-specific implied volatility and futures speculation; May 8 noted China/central bank/ETF activity and *an unexplained residual*. Therefore USD/yields alone do NOT exhaust explanation. https://www.gold.org/goldhub/research/gold-market-commentary-march-2024 ; https://www.gold.org/goldhub/research/gold-market-commentary-april-2024

**D. China demand and June 7 2024 shock (C016/C017, DOWN).** WGC **15 May** reported PBoC bought only 2 tonnes in April (slowest month after 18-month string), with local investment demand softening. That fact predates the June 7 down move. On **7 June**, news of PBoC halting May buying combined with +272k US NFP vs +185k expected; the two latter facts were NOT known until release. Context + new surprise = candidate amplifier. https://www.gold.org/goldhub/gold-focus/2024/05/chinas-gold-market-april-investment-demand-remained-strong ; https://www.reuters.com/markets/commodities/gold-prices-dip-china-central-bank-holds-off-buying-2024-06-07/

**E. 2024 Sep (C022/C023, UP).** Reuters on 13 September documented an *expectation* shift from 25bp to possible 50bp Fed cut. Actual 50bp decision announced 18 September; Reuters Sept 19 reported subsequent gold move. These are different times and must not be merged as an ex-ante known policy decision. https://www.reuters.com/markets/us/global-markets-view-usa-pix-2024-09-13/ ; https://www.kitco.com/news/off-the-wire/2024-09-19/gold-gains-over-1-fed-begins-deeper-rate-cut-cycle

**F. November/December 2024 Fed and dollar (C025/C029, DOWN).** Trump-election-related risk repricing, stronger yields/USD and later hawkish December Fed guidance accompanied separate down episodes. WGC Jan 8 2025 later described Dec 18–19 as a risk-asset/treasury/gold shock. https://www.gold.org/goldhub/research/gold-market-commentary-october-2024 ; https://www.gold.org/goldhub/research/gold-market-commentary-december-2024

**G. Tariff whipsaw — April/May 2025 (C032–C040).** Tariff fears were publicly discussed by Reuters **31 March** before the April 2 US reciprocal tariff announcements. The **4–8 April DOWN** liquidity leg and **9–22 April UP** haven/dollar leg show an identical trade-policy topic triggering **opposite gold signs across liquidity regimes**. The May 12 US/China tariff truce also coincided with renewed DOWN. WGC's May 8 review of April is after those price moves, not a predictive data vintage. https://www.reuters.com/markets/commodities/gold-sails-above-3100-uncharted-territory-us-tariffs-approach-2025-03-31/ ; https://www.gold.org/goldhub/research/gold-market-commentary-april-2025 ; https://www.kitco.com/news/off-the-wire/2025-05-12/gold-slides-3-us-china-agree-slash-reciprocal-tariffs

**H. June 13 2025 geopolitical flashpoint (C041, UP).** Israel-Iran military escalation led contemporaneous haven demand; external news not necessarily forecastable. https://www.reuters.com/world/china/gold-tops-1-month-high-middle-east-tensions-spur-safe-haven-demand-2025-06-13/

**I. Aug-Oct 2025 trend and October correction (C045–C048).** WGC Sept 4 had documented Aug USD weakness and +$5.5bn ETF inflows. Oct 7 WGC documented September record +$17.3bn ETF inflows and options-related investment. Crucially, **13 October 2025 WGC advance risk note** (before initial down-cluster 17 Oct) noted RSI >90, gold >20% above 200d average, profit-taking/dollar squeeze/liquidity risks. On **21 October** gold underwent severe reversal; Reuters and WGC Nov 6 reported momentum unwind and stronger USD. The 13 Oct warning was **vulnerability, not a proven exact-day/direction alarm**. https://www.gold.org/goldhub/research/gold-market-commentary-august-2025 ; https://www.gold.org/goldhub/research/gold-market-commentary-september-2025 ; https://www.gold.org/goldhub/gold-focus/2025/10/gold-hits-us4000oz-trend-or-turning-point ; https://www.reuters.com/world/india/golds-record-run-pauses-investors-book-profits-2025-10-21/ ; https://www.gold.org/goldhub/research/gold-market-commentary-october-2025

**J. 29 December 2025 forced unwind possibility (C053, DOWN).** Heavy cross-metal selling with year-end profit taking and reported CME margin increases. Reuters and AP Dec 29 were contemporaneous; exact pre-effective margin schedule and raw open-interest reaction still require evidence. https://www.kitco.com/news/off-the-wire/2025-12-29/precious-metals-drop-amid-profit-taking-silver-platinum-retreat-record ; https://apnews.com/article/c49577dedd4c799005de5b7af552ce81

## 4. Macro calendar is NOT a sufficient discriminator
Only the available dated CPI/NFP releases were counted (34 CPI and 35 NFP raw rows; some dates shared and release-day data incomplete in other families). Among **68** CPI-or-NFP release dates in the 774 eligible days, **15** were also 3%-flagged (**22.1%**). Among **706** other dates, **136** were flagged (**19.3%**). By year:
- 2023: 4/23 release days flagged (17.4%), versus nonrelease-day 8.5%;
- 2024: 6/24 release days flagged (25.0%), versus nonrelease-day 17.9%;
- 2025: 5/21 release days flagged (23.8%), versus nonrelease-day 31.2%;
These figures are merely descriptive *same-day associations*, not probabilities of advance signals or independent observations: the 3/5-day rolling returns heavily overlap, 2025 legacy macro ledger is incomplete in several families, and publication availability must be respected. In 2025, CPI/NFP release dates actually showed a lower flagged-day frequency than other days under this definition.

## 5. What the documents contain
1. `GOLD_MAJOR_MOVE_MULTIHORIZON_2023_2025_V2_ALL_774_DAYS_20261013.csv`: ALL 774 days, including quiet control days, raw threshold fields, release-day proxies; zero causal claims.
2. `GOLD_MAJOR_MOVE_MULTIHORIZON_2023_2025_V2_174_FLAGGED_DAYS_20261013.csv`: complete short-listed 151 primary +23 second-tier days, without cherry-picking.
3. `GOLD_MAJOR_MOVE_MULTIHORIZON_2023_2025_V2_DIRECTIONAL_CLUSTERS_20261013.csv`: complete 53 descriptive signed clusters.
4. `GOLD_MAJOR_MOVE_MULTIHORIZON_2023_2025_V2_53_CLUSTER_NEWS_RESEARCH_20261013.csv`: **all 53 clusters**, 28 curated dated news/context links, 25 flagged as `NO_CURATED_DATE_SOURCE`, 52 with one or more older 42-episode context leads. PRE/DURING/POST publication label refers to **first flagged cluster date**, not true movement start. No curated source is represented as proof of an actionable warning.

## 6. Full cluster inventory (threshold-first date, not original onset)
| ID | First flagged → last flagged | Direction | Maximum sampled fixed-horizon move | Curated dated source timing |
|---|---|---|---:|---|
| C001 | 2023-01-12 → 2023-01-12 | UP | 3.481% | needs verification |
| C002 | 2023-02-03 → 2023-02-08 | DOWN | 4.296% | DURING |
| C003 | 2023-03-13 → 2023-03-23 | UP | 6.248% | POST |
| C004 | 2023-05-04 → 2023-05-04 | UP | 3.450% | needs verification |
| C005 | 2023-09-29 → 2023-10-03 | DOWN | 4.586% | POST |
| C006 | 2023-10-13 → 2023-10-19 | UP | 5.631% | POST |
| C007 | 2023-12-01 → 2023-12-01 | UP | 3.549% | needs verification |
| C008 | 2023-12-04 → 2023-12-04 | DOWN | 3.054% | DURING |
| C009 | 2023-12-08 → 2023-12-08 | DOWN | 3.280% | DURING |
| C010 | 2023-12-19 → 2023-12-19 | UP | 3.049% | needs verification |
| C011 | 2024-03-04 → 2024-03-11 | UP | 5.686% | POST |
| C012 | 2024-04-01 → 2024-04-11 | UP | 5.683% | POST |
| C013 | 2024-04-12 → 2024-04-12 | DOWN | 3.620% | DURING |
| C014 | 2024-04-24 → 2024-04-24 | DOWN | 3.133% | needs verification |
| C015 | 2024-05-15 → 2024-05-20 | UP | 3.793% | needs verification |
| C016 | 2024-05-23 → 2024-05-27 | DOWN | 3.981% | DURING |
| C017 | 2024-06-07 → 2024-06-07 | DOWN | 3.592% | DURING |
| C018 | 2024-07-16 → 2024-07-17 | UP | 4.420% | needs verification |
| C019 | 2024-07-25 → 2024-07-25 | DOWN | 3.292% | needs verification |
| C020 | 2024-08-01 → 2024-08-01 | UP | 3.345% | needs verification |
| C021 | 2024-08-12 → 2024-08-16 | UP | 3.718% | needs verification |
| C022 | 2024-09-13 → 2024-09-16 | UP | 3.380% | DURING |
| C023 | 2024-09-24 → 2024-09-26 | UP | 3.870% | PRE |
| C024 | 2024-10-22 → 2024-10-22 | UP | 3.220% | needs verification |
| C025 | 2024-11-06 → 2024-11-15 | DOWN | 5.338% | DURING |
| C026 | 2024-11-20 → 2024-11-22 | UP | 5.876% | needs verification |
| C027 | 2024-11-25 → 2024-11-25 | DOWN | 3.166% | DURING |
| C028 | 2024-12-11 → 2024-12-11 | UP | 3.236% | needs verification |
| C029 | 2024-12-18 → 2024-12-19 | DOWN | 4.803% | needs verification |
| C030 | 2025-02-05 → 2025-02-10 | UP | 3.906% | PRE |
| C031 | 2025-03-13 → 2025-03-19 | UP | 4.018% | needs verification |
| C032 | 2025-03-31 → 2025-04-02 | UP | 3.700% | DURING |
| C033 | 2025-04-04 → 2025-04-08 | DOWN | 4.647% | POST |
| C034 | 2025-04-09 → 2025-04-22 | UP | 8.567% | POST |
| C035 | 2025-04-23 → 2025-04-23 | DOWN | 3.035% | POST |
| C036 | 2025-05-01 → 2025-05-01 | DOWN | 3.186% | needs verification |
| C037 | 2025-05-06 → 2025-05-07 | UP | 5.828% | needs verification |
| C038 | 2025-05-12 → 2025-05-16 | DOWN | 5.578% | DURING |
| C039 | 2025-05-15 → 2025-05-15 | UP | 3.143% | needs verification |
| C040 | 2025-05-21 → 2025-05-26 | UP | 4.967% | POST |
| C041 | 2025-06-13 → 2025-06-13 | UP | 3.712% | DURING |
| C042 | 2025-07-22 → 2025-07-22 | UP | 3.068% | needs verification |
| C043 | 2025-07-30 → 2025-07-30 | DOWN | 3.381% | needs verification |
| C044 | 2025-08-04 → 2025-08-07 | UP | 3.257% | POST |
| C045 | 2025-09-01 → 2025-09-08 | UP | 4.882% | DURING |
| C046 | 2025-09-23 → 2025-09-23 | UP | 3.276% | needs verification |
| C047 | 2025-10-01 → 2025-10-20 | UP | 8.642% | DURING |
| C048 | 2025-10-17 → 2025-10-29 | DOWN | 8.476% | PRE |
| C049 | 2025-11-10 → 2025-11-13 | UP | 5.409% | needs verification |
| C050 | 2025-11-14 → 2025-11-17 | DOWN | 3.668% | needs verification |
| C051 | 2025-11-28 → 2025-11-28 | UP | 3.795% | needs verification |
| C052 | 2025-12-22 → 2025-12-26 | UP | 4.654% | needs verification |
| C053 | 2025-12-29 → 2025-12-31 | DOWN | 4.798% | DURING |

## 7. Strict stopping point: NOT a model
This V2 atlas is exhaustive **only for the specified thresholds, horizons, price source and study years**. It is not an exhaustive global-news event study and cannot discover news not in accessible feeds. There is no inferential demonstration that proposed catalysts preceded a higher future probability of large moves. Distinguish pre-existing vulnerability, unpredictable new catalyst and post-release price/position amplification. A follow-on research stage must verify timestamped articles and historical vintages for the remaining 25 clusters, join FX/yields/VIX/CFTC/ETF flows with their true availability times, and select matched control days before drawing statistical generalizations.
