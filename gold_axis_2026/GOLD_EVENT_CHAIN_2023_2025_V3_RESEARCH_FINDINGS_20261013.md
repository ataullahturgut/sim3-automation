# GOLD EVENT CHAIN V3 — INDEPENDENT AUDIT AFTER CLAUDE PR #118
**Date:** 2026-10-13. **Purpose:** 2023–2025 explanatory historical XAU/USD event research; NOT a trained model or a validated alarm.
**Authority:** exploratory protocol `GOLD_EVENT_CHAIN_2023_2025_V3_EXPLORATORY_ANALYSIS_CONTRACT_20261013.md`; Claude's open PR #118 was read and used as a referee authority, not merged.
**CAVEAT:** Results have informed research choices. The fixed protocol was written immediately before V3 computations, but this is **not an untouched prospective preregistration**.

## 1. What was verified by independent calculation
Price source: 2022–2025 EV Trading Labs / Dukascopy XAU/USD M15 bid/ask-mid quotes from Neon Gold Control, NY 17:00 ET session, >=70 observations per gold session; valid dates 2023/2024/2025 = **257/259/258** (774).
Historical 2022 warmup allows a prior 60-session volatility estimate throughout 2023.
r1=100*(P_t/P_{t-1}-1), r5=100*(P_t/P_{t-5}-1), historical sd60 sample std of **60 prior completed** daily returns (exclude r1_t), z1=r1/sd60, z5=r5/(sd60 sqrt(5)).
Exploratory thresholds from referee: |z1|>=2.5 or |z5|>=2, with the individual criteria retained. 5TD window end is the last day, not its start; events are retrospective. Same-direction marked days joined when <=3 **unflagged** sessions separate them; opposite-direction clusters may temporally overlap.

| Year | Days | Fixed 5TD >=3% | Scaled 5TD | Scaled 1TD | Scaled union days | Directional groups |
|---|---:|---:|---:|---:|---:|---:|
| 2023 | 257 | 22 | 19 | 8 | 24 | 7 |
| 2024 | 259 | 40 | 21 | 8 | 26 | 9 |
| 2025 | 258 | 62 | 24 | 10 | 30 | 8 |
| **Total** | **774** | **124** | **64** | **26** | **80** | **24** |

These 24 scaled directional groups DO NOT supersede the descriptive 53 fixed-threshold groups and DO NOT represent 24 independently proven economic catalysts. Group-gap sensitivity: <=1/2/3/5 unflagged sessions => **27/25/24/21** groups, respectively. Raw separate signed flags = 80 under this definition (not the old 152 overlapping V2 flags); sample has changed. Price data and calendar label are source-specific.

## 2. Controls: previous return tension and forward 10-session first-passage
Eligible horizons: **764** observations, excluding the final 10 dates without an observed 10-session outcome inside 2023–25. Outcomes are whether any of next 10 *session closes* reaches +3% or -3% from contemporaneous close; both directions can be reached; time-order computed separately. These are retrospective association outcomes, NOT hypothetical fills or real-time alerts.
- All: future UP >=3% **291/764 (38.1%)**, future DOWN >=3% **88/764 (11.5%)**.
- Prior 20 session return >= +8%: future DOWN **21/74 (28.4%)**; UP **33/74 (44.6%)**.
- Prior 20 session return <+5%: future DOWN **47/571 (8.2%)**; UP **213/571 (37.3%)**.
- Year splits, >=8% antecedent: 2023 DOWN 1/12 (8.3%); 2024 4/13 (30.8%); 2025 16/49 (32.7%). Thus the apparent pooled relationship is dominated by the late volatility/trend regime and must NOT be called universal.
- Nonoverlapping 10-session offset sensitivity check, ten different calendar phases: >=8% group future DOWN frequencies range **10.0%–55.6%**, and <5% group **5.4%–14.3%**. Group sizes in high-tension offsets 5–10 cases; temporal dependence and uncertainty are severe. No adjusted statistical significance or calibrated probability claim.
- Same tension raises *both* future down and up frequencies and is a candidate VULNERABILITY state, not directional sell rule.
- No parameter training was conducted. Reproducible per-session outcome columns and quiet-period controls are in V3 DAILY CSV; key counts are in V3 JSON summary.

## 3. Corrected historical news publication timing
New file `GOLD_EVENT_CHAIN_2023_2025_V3_CORRECTED_V2_NEWS_TIMING_20261013.csv` maps all original 53 V2 clusters to the earliest qualifying window baseline from Claude's *unmerged PR #118* referee `RECOMPUTED_CLUSTER_TIMING`. Those baseline dates are inherited from the referee and NOT independently rederived in this V3 audit. Using original 28 dated source leads:
- 25 clusters have no curated dated cluster-specific source; 10 articles strictly after the candidate window; 17 inside the candidate window; **only one** dated article before the earliest qualifying window.
- Of the old "PRE" labels, C023 Sept 19 2024 is DURING (window baseline Sept 17), C030 Feb 4 2025 is DURING (baseline Jan 29), and **C048 Oct 13 2025 WGC** is PRE (baseline Oct 16). These date-only labels are not minute-stamped first-publication proof.
- The 22 additional Claude contemporaneous articles documented in PR #118 are not falsely represented as independently verified PIT news or transferred into this 28-source subset. Narrative-correlation is not proof of causation.
- A causal dossier must distinguish preparatory vulnerability (before baseline), catalyst (after price movement begins), amplifier (later cross-asset follow-through), and disconfirming evidence.
- **World Gold Council 13 Oct 2025** warns overbought >90 RSI and >20% above 200-day average, portfolio liquidation and USD short-squeeze risk. Same analysis explicitly says ETF/COMEX positioning is not historically saturated, and investors may be in early accumulation: a material **counterargument** omitted in V2. Report uses 23 Sep 2025 COMEX positions, which were pre-shutdown available, NOT hidden 30 Sep+ CFTC COT reports. https://www.gold.org/goldhub/gold-focus/2025/10/gold-hits-us4000oz-trend-or-turning-point
- **Official CFTC**: COT report dated 30 Sep 2025, nominally due Oct 3, actually published Nov 19; Oct 7 report published Nov 21; Oct 21 report Dec 2. Those new-week exposures CANNOT be claimed as available in early Oct; **older reports published earlier can still be consulted as stale context**. https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalSpecialAnnouncements/index.htm
- **WGC 15 May 2024** disclosed PBoC April 2t holdings increase (slower than prior average), while Chinese local ETFs added 17t and SGE offtake 131t. So treating the article as purely bearish without countervailing demand is false. Subsequent 7 Jun NFP and PBoC stop were new information; May note is *context*, not a validated sell signal. https://www.gold.org/goldhub/gold-focus/2024/05/chinas-gold-market-april-investment-demand-remained-strong

## 4. Macro release timing independently reaudited
Neon `observations`, dated 2023–25:
- FOMC USMPD historical **24** scheduled-event dates (8 each year), correcting partial raw event ledger's 16. **0/24** corresponding USMPD scores satisfy true 2023–25 `available_as_of`; all were reconstructed/loaded Sep 8, 2026, so cannot be used to "predict" then.
- Across 24 FOMC days, |z1|>=2 occurred on **4/24 (16.7%)**, vs **46/683 (6.7%)** when none of the examined FOMC/CPI/NFP calendar dates had a release, under our separate 60-day lagged-volatility z1 definition.
- Matched same-day CPI first prints **34**, with >=2σ **1/34**; NFP first prints **34 matched of 35**, with >=2σ **6/34** (one no matched eligible XAU date). Both are available only upon release, **not in advance**. Overlaps among release families prevent naive additive counts.
- The 4/24 is **not** Claude's 4/15 because its earlier FOMC event-coverage denominator was incomplete, and z1 sample design differs. These associations are descriptive and do not prove unusual statistically significant FOMC effects, nor forecast sign. Publication intraday time vs trade-close alignment matters.

## 5. External market dataset readiness — NEW INDEPENDENT QC
CME Databento H1 continuous .c.0 calendar-rolled five roots retained in Neon 2023–25; roll gaps not adjusted. **Strict coverage test:** a futures NY17 daily session must have >=18 actual H1 bars, and prior-completed XAU session used for the return must ALSO have >=18. All cross-asset lagged return cells not meeting this bar coverage are BLANKED in V3 daily and 24 cluster CSVs, to avoid manufacturing precursor correlation. Usable previous-day cross-asset return samples out of 774 XAU sessions:
- NQ **744/774**, CL **758/774**, ZN **625/774**, GC only **41/774**, SI only **12/774**. Roll gaps and clock mismatch remain; zero claim of GC/SI intraday validation from these gated data.
- Claude's referee GC/SI cross-asset narrative is a potentially valuable *retrospective hypothesis*, but current sparse hourly source does NOT establish robust matched prior-market signals. Do not promote it as a live precursor.
- Neon public `observations`: 2023–25 daily **DXY / DTWEXBGS, DFII10, ETF flow, COT and archived FedWatch** observations are not available as usable first-published series. Existing `GOLD_MONTHLY_PREDEV_MACRO_RECON_V1_2026-09-30.json` contains DGS10/DFII10/DTWEXBGS data ONLY through March 2022 and explicitly says historical reconstruction, not original PIT proof. Therefore NO 2023–25 dollar or real-yield correlation was computed or invented.
- Authoritative candidate public historical references: FRED DFII10 https://fred.stlouisfed.org/series/DFII10 , FRED DTWEXBGS https://fred.stlouisfed.org/series/DTWEXBGS . Need verified publication vintage and conservative release lag before using as antecedents.

## 6. Evidence hierarchy and remaining research
CONFIRMED:
- priced-move threshold and volatility-normalized counts are reproducible for chosen convention;
- overly strong statements about 53 "events" and about 2025 rise have been corrected;
- pooled prior-rally tension co-occurs with more future downside risk but does NOT reliably give direction;
- 24 FOMC meeting date entries in Neon vs legacy partial 16, but score vintage unusable;
- CME GC/SI sampling deficiency; it must not be papered over;
- official CFTC vintage gap; WGC pre-warning had BOTH bearish and bullish caveats.
NOT CONFIRMED:
- 24 statistical groups are 24 independent economic catalysts;
- news triggered each threshold crossing rather than coinciding;
- 2023–25 native 1h gold–other-market causal lead-lag in thin GC/SI;
- actual published pre-event DXY/realyield/ETF/COT levels for all cases;
- bank profitability, return direction predictor, stable cross-regime alarm or fresh untouched test.

NEXT RESEARCH ONLY: chronological first-publication event archive for each cluster and the >3% intraday-range missed Aug 5 2024; 2025 Jan EFP/physical transfer; C003 SVB vs Credit Suisse and 2025 Apr liquidity vs trade tariff reversal; matched year/volatility-regime controls using calendar-time/venue fidelity; validate economic series vintage or explicitly block; consider longer 10/20 sessions for slow developments. No predictive model now.

## 7. Files written
1. V3 exploratory analysis contract (documented before V3 computations; not externally preregistered).
2. `GOLD_EVENT_CHAIN_2023_2025_V3_DAILY_VOL_SCALED_CONTROLS_20261013.csv` — 774 observations, retrospectively computed prior 60d volatility, 10-session outcomes, quiet controls and **coverage-gated** prior-day futures returns.
3. `GOLD_EVENT_CHAIN_2023_2025_V3_VOL_SCALED_DIRECTIONAL_CLUSTERS_20261013.csv` — 24 groups with bounded source coverage.
4. `GOLD_EVENT_CHAIN_2023_2025_V3_AGGREGATE_SUMMARY_20261013.json` — exact counts and sample sizes.
5. `GOLD_EVENT_CHAIN_2023_2025_V3_CORRECTED_V2_NEWS_TIMING_20261013.csv` — 53 original cluster source timings anchored to PR #118 window-baseline dates.

**No existing V2 research file or Claude referee PR file modified. No model trained; no GitHub PR merged.**
