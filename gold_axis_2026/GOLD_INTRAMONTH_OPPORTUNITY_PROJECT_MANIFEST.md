# GOLD INTRAMONTH OPPORTUNITY — CANONICAL PROJECT MANIFEST

**Manifest version:** 1.1  
**Date:** 2026-10-01  
**Last governance update:** 2026-10-06  
**Status:** **CURRENT / BINDING / PROJECT INITIATED**  
**Repository:** `ataullahturgut/sim3-automation`  
**Branch:** `gold-midas-headswap-v1-20260925`  
**Parent monthly project:** `GOLD_MONTHLY_PROJECT_MANIFEST.md`

> **Mission:** identify short-horizon upside opportunities inside a month, including months for which the frozen monthly Gold model forecasts DOWN.

> **Separation:** monthly average forecast ≠ intramonth path opportunity. A monthly DOWN forecast does not imply that every daily/weekly move inside that month is DOWN.

---

# 1. Executive State

## 1.1 Primary business question

Can we identify, from information known at a daily origin, whether Gold is likely to produce a meaningful upward excursion over the next few Borsa İstanbul observation days?

Primary focus:
- **opportunities occurring inside monthly-DOWN forecasts**.

The system is not primarily a “tomorrow price” model.

## 1.2 Primary output horizon

Primary:
- **5 future Borsa İstanbul Gold observations**

Supporting:
- 1 day
- 3 days
- 10 days.

Primary path targets:
- **MFE_5** = Maximum Favorable Excursion
- **MAE_5** = Maximum Adverse Excursion.

## 1.3 Current stage

- Stage 0 scientific contract: COMPLETE
- Stage 0A intramonth-opportunity objective amendment: COMPLETE / FROZEN
- Stage 1 Daily Data Authority & PIT Audit: COMPLETE / PASS
- Stage 2A Opportunity Label, Baseline & Core Feature Contract: **COMPLETE / PASS**
- Stage 3 Origin-Safe Opportunity Predictability Screen: **COMPLETE / PASS**
- Stage 4 Monthly Context Incremental Test: **COMPLETE / NO_CONTEXT_PASS**
- Stage 5 K100 Robustness, Calibration & Decision-Threshold Audit: **COMPLETE / PASS**
- **Stage 6 Frozen 2025 Transport: NEXT**
- **Global Session / Execution redesign: ACTIVE — dual externally anchored partition protocol is binding; operational head count is not preselected; V5 premodel data gate PASS**

Current frozen opportunity rule:
- target: **K100**
- feature block: **G_ONLY**
- model: **HGB_CLASS**
- probability: **RAW**
- alert threshold: **p >= 0.30**
- Stage-3 DEV Brier improvement vs best matured baseline: **+1.46%**
- Stage-5 DEV alert precision: **35.6%**
- Stage-5 DEV alert recall: **24.2%**
- monthly context augmentation: **REJECTED**
- monthly direction / magnitude / T0 reliability / prior-month state remain descriptive only.

Supporting linear comparator:
- G_ONLY / LOGIT_L2
- Brier improvement: **+1.09%**.

Secondary downside-risk research channel:
- target: **MAE5**
- FOUR_METAL / HGB_REG
- aggregate DEV MAE improvement: **+2.47%**
- yearly stability caution: gain concentrated in 2024.

## 1.4 Governance

- all model/feature/threshold selection uses data ending no later than **2025-12-31**
- 2026 is OPENED / retrospective
- no random split
- no target-window leakage
- no target-month realized monthly information
- prospective opportunity ledger begins only with forecasts timestamped before outcomes.

---

# 2. Opportunity Target Contract

## 2.1 Origin

Signal issue time:
- **00:30 Europe/Istanbul** on each eligible Borsa İstanbul business date.

At issue time:
- latest known official Borsa İstanbul Gold Metal Price = `P0`
- same-day/future Borsa Gold prices are unknown.

## 2.2 Future path

For horizon h:
- future official Borsa Gold prices = `P1...Ph`.

### Maximum Favorable Excursion

`MFE_h = max(log(Pk/P0)), k=1..h`

### Maximum Adverse Excursion

`MAE_h = min(log(Pk/P0)), k=1..h`

Primary:
- MFE_5
- MAE_5.

Supporting:
- MFE/MAE for 1, 3, 10 observations.

## 2.3 Opportunity event

A binary `UP_OPPORTUNITY_h` label will be frozen in Stage 2 using an **origin-scaled threshold** selected only from pre-2026 chronology.

No fixed percent threshold may be chosen after inspecting 2026.

The threshold may depend only on origin-known risk scale, such as recent realized volatility / absolute-return scale.

## 2.4 Intended eventual model outputs

- P_UP_1D
- P_UP_3D
- **P_UP_5D**
- P_UP_10D
- expected MFE_5
- expected MAE_5
- optional risk-adjusted opportunity score.

The risk-adjusted score formula is not yet frozen.

---

# 3. Monthly Forecast Integration

## 3.1 Monthly model role

Frozen monthly ChHHO-ANFIS remains a **context layer**, not a gate.

Allowed origin-known monthly context:
- monthly predicted return
- monthly UP/DOWN sign
- forecast-vs-origin distance
- monthly reliability/alarm state
- monthly market regime/state known at the daily origin.

Forbidden:
- target-month realized monthly average
- future monthly regime
- any monthly outcome not known at the daily origin.

## 3.2 Required comparison

Every monthly-context experiment must compare:

1. daily opportunity model **without monthly context**
2. same model family **with monthly context**.

Monthly context is retained only if it improves pre-2026 chronological opportunity prediction.

## 3.3 Critical business subset

Primary diagnostic subset:

**daily origins that fall inside months where the frozen monthly forecast is DOWN.**

Supporting subsets:
- all daily origins
- monthly-UP months
- monthly alarm HIGH / no-HIGH where chronology permits.

A monthly DOWN forecast never automatically blocks an intramonth UP opportunity.

---

# 4. Data Authority

Stage 1 result:
**PASS**

## 4.1 Core four-metal authority

Official source:
**Borsa İstanbul Precious Metals Market — Metal Price, USD/ONS**

Core:
- Gold
- Silver
- Platinum
- Palladium.

History:
- available from 2011-01-01.

Primary governed daily Gold reference:
- Borsa İstanbul Gold Metal Price USD/ONS.

## 4.2 Cross-market status

| Family | Status |
|---|---|
| Nominal 10Y / real 10Y | READY_LAGGED — Fed H.15 |
| Broad USD / FX | READY_WEEKLY_PIT — Fed H.10 publication-batch join |
| VIX | READY — Cboe prior completed session |
| Nasdaq-100 | READY — Nasdaq NDX prior completed session |
| GPR daily/monthly vintages | READY_PIT_VINTAGES |
| WTI / Brent | SOURCE_READY / PIT_MAPPING_BLOCKED |
| LBMA metal history | BENCHMARK_ONLY / LICENCE_BLOCKED |
| StakTrakr | RESEARCH_COMPARATOR_ONLY |

WTI/Brent remain excluded until historical public-availability mapping is frozen.

---

# 5. Feature Research Plan

Stage 2 will construct small, interpretable feature blocks before complex model screening.

## 5.1 Gold path

- 1-day return
- 3/5/10/21-day momentum
- rolling realized volatility
- rolling absolute-return scale
- drawdown
- distance from rolling high/low
- short-term acceleration / reversal measures.

## 5.2 Cross-metal

- Silver/Platinum/Palladium returns
- cross-metal breadth
- cross-metal dispersion
- Gold-vs-companion divergence
- precious-metal relative momentum.

## 5.3 Macro / risk

- H.15 nominal / real yield changes
- breakeven proxy
- H.10 Broad USD / major-FX context
- VIX level/change/stress
- Nasdaq-100 return/momentum
- GPR daily/monthly state.

## 5.4 Monthly context

Candidate context:
- monthly predicted return
- monthly direction
- monthly p_HIGH / alarm status
- R0/R1/R2
- STABLE/TRANSITION
- NORMAL/EXTREME/OOD.

Monthly context is optional and must earn inclusion on pre-2026 chronology.

---

# 5A. Stage-2 Empirical Opportunity Result

Authoritative result:
`GOLD_INTRAMONTH_OPPORTUNITY_STAGE2_RESULT_2026-10-01.md`

Run:
- **36860536563**
- artifact **11161358194**

Frozen DEV monthly context:
- 33 ChHHO target months
- **19 DOWN**
- **14 UP**.

Inside the 19 monthly-DOWN months, same-calendar-month five-observation upside excursions occurred at least once in:
- **18/19 (94.7%)** for >= +1%
- **15/19 (78.9%)** for >= +2%
- **7/19 (36.8%)** for >= +3%.

Median month-level maximum same-month MFE5 across monthly-DOWN months:
- **+2.78%**

Range:
- minimum **+0.86%**
- maximum **+7.40%**.

Volatility-scaled DEV event prevalence:

| Candidate | Full DEV | Monthly-DOWN | Monthly-UP | DOWN same-month |
|---|---:|---:|---:|---:|
| K050 | 48.6% | 39.0% | 59.4% | 35.2% |
| K075 | 36.3% | 26.5% | 46.4% | 23.7% |
| K100 | 25.9% | 17.6% | 33.8% | 15.1% |

Binding interpretation:
- monthly DOWN lowers opportunity base rate;
- monthly DOWN does **not** eliminate tactical rallies;
- monthly direction is a candidate context variable, never a veto;
- all three event definitions remain viable for model screening;
- the next scientific question is ex-ante predictability.

2025 frozen transport is consistent descriptively:
- ChHHO DOWN months = 4
- all 4 contain >= +2% same-month opportunity
- 2/4 contain >= +3%.

This transport evidence did not select the label or threshold.

---

# 5B. Stage-3 Predictability Result

Authoritative result:
`GOLD_INTRAMONTH_OPPORTUNITY_STAGE3_RESULT_2026-10-01.md`

Run:
- **36862897415**
- artifact **11163151830**
- artifact digest `sha256:2fd22603ab47d573d47716a3e87fb380d3a2795b42af62fb194d827e1dcecff6`.

Protocol:
- 749 DEV daily origins, 2022-2024
- five-Gold-origin block prequential refit
- full five-observation label maturity/purge before a row may enter training
- 2025/2026 unused
- monthly ChHHO context excluded.

### Target decisions

| Target | Decision | Best core |
|---|---|---|
| K050 | NO PASS | G_ONLY / LOGIT_L2 |
| K075 | NO PASS | FOUR_METAL / LOGIT_L2 |
| **K100** | **PASS** | **G_ONLY / HGB_CLASS** |
| MFE5 continuous | NO PASS | FOUR_METAL / RIDGE |
| **MAE5 continuous** | **PASS** | **FOUR_METAL / HGB_REG** |

### Binding K100 core

**G_ONLY / HGB_CLASS**
- Brier **0.18942**
- matured baseline **0.19223**
- relative improvement **+1.46%**
- log loss **0.56550**
- baseline log loss **0.57283**
- PR-AUC **0.3296**
- ROC-AUC **0.6078**.

Supporting G_ONLY / LOGIT_L2:
- Brier improvement **+1.09%**
- log loss **0.56834**
- ROC-AUC **0.6027**.

K100 definition:
`MFE5 >= SIGMA20 × sqrt(5)`.

DEV K100 hurdle distribution:
- median ≈ **+2.09%**
- p25 ≈ **+1.57%**
- p75 ≈ **+3.10%**
- p90 ≈ **+4.01%**.

### Business-relevant descriptive slice

Monthly ChHHO direction was **not** a Stage-3 feature. It was used only after prediction generation to inspect the frozen DEV subsets.

K100 G_ONLY/HGB:

- monthly-DOWN origins: n=392, Brier **0.14115** vs baseline **0.15128**, improvement ≈ **+6.70%**
- monthly-UP origins: n=293, Brier **0.24182** vs baseline **0.23110**, change ≈ **-4.64%**.

This is precisely why Stage 4 must test monthly context formally rather than hard-code a DOWN gate.

### Binding interpretation

The current evidence supports a **strong-rally detector**, not a generic rally detector and not a validated continuous MFE forecast.

The Stage-3 core may not be retuned merely to favor Stage 4.

---

# 5C. Stage-4 Monthly Context Result

Authoritative result:
`GOLD_INTRAMONTH_OPPORTUNITY_STAGE4_RESULT_2026-10-01.md`

Run:
- **36865648243**
- artifact **11164440527**
- artifact digest `sha256:ff16d38d3114efa1650e05b250af8c6646d6b1895097a0234511d4acf3965ccb`.

Common Stage-4 DEV population:
- 685 daily origins
- 392 monthly-DOWN
- 293 monthly-UP.

Frozen CORE_ONLY reference:
- Brier **0.18421**
- log loss **0.55394**.

Monthly context results:

| Block | Brier relative vs core | DOWN-slice relative vs core | Decision |
|---|---:|---:|---|
| CORE_DIR | **-0.81%** | **-7.59%** | FAIL |
| CORE_MAG | **-5.95%** | **-16.24%** | FAIL |
| CORE_DIR_MAG | **-6.00%** | **-17.21%** | FAIL |
| CORE_DIR_MAG_T0REL | **-9.76%** | **-16.55%** | FAIL |
| CORE_DIR_MAG_STATE | **-15.31%** | **-33.46%** | FAIL |
| CORE_ALL_SAFE | **-13.55%** | **-12.72%** | FAIL |

Binding interpretation:
- Stage-3 core performs relatively well inside monthly-DOWN periods, but explicitly feeding monthly DOWN/UP into the model **does not improve it**.
- Monthly forecast magnitude, T0 reliability, and prior-month state also degrade probability quality.
- Monthly context therefore remains **display/reporting context only**, not a probability modifier or gate.
- K100 remains a local daily-path signal.

Do not:
- suppress opportunity because monthly forecast is DOWN;
- boost probability because monthly forecast is UP;
- multiply K100 by monthly p_HIGH;
- condition K100 on R0/R1/R2/Transition/Extreme.

---

# 5D. Stage-5 Calibration & Alert Result

Authoritative result:
`GOLD_INTRAMONTH_OPPORTUNITY_STAGE5_RESULT_2026-10-01.md`

Run:
- **36866945286**
- artifact **11164696977**
- artifact digest `sha256:3c3133b79cf40655d9a3f266405547096f275153d4e83a3a71cbdbdc8a3b85be`.

### Calibration

Selected:
- **RAW probability**

Rejected:
- Platt
- Isotonic.

RAW remains best on the frozen primary metrics:
- Brier **0.18942**
- log loss **0.56550**.

### Frozen alert

Selected threshold:
- **p(K100) >= 0.30**

DEV:
- alerts **132**
- alert rate **17.6%**
- precision **35.6%**
- recall **24.2%**
- precision lift vs unconditional K100 prevalence: **+9.7 pp**.

Yearly:
- 2022 precision 30.1%, recall 36.1%
- 2023 precision 39.6%, recall 27.1%
- 2024 precision 54.5%, recall 9.5%.

Monthly-DOWN subset:
- alerts 74
- precision **25.7%**
- recall **27.5%**.

Episode-deduplicated diagnostic:
- 39 alert episodes
- 19 successful
- episode precision **48.7%**.

Binding caution:
- this is still a modest research edge, not a standalone trading instruction;
- false K100-alert share remains high;
- 2025 transport is mandatory before any prospective operational use.

---


# 5E. Global Gold Session & Execution Research Authority — 2026-10-06


## 5E.0 Data Availability Gate — MUST PRECEDE SESSION MODEL DESIGN

**Binding order correction (2026-10-06):** before timestamp auditing, session modelling, or execution-hour optimisation, the project must first prove that the required historical data actually exist at sufficient frequency and coverage.

### Full 15-minute coverage audit result — 2026-10-06

Authoritative artifacts:
- `GOLD_EXECUTION_15M_COVERAGE_PROFILE_2026-10-06.json`
- `GOLD_EXECUTION_15M_SIGNAL_DATE_COVERAGE_2026-10-06.csv`
- `GOLD_EXECUTION_15M_PROFILE_AGGREGATE_2026-10-06.csv`
- `GOLD_EXECUTION_15M_SESSION_ROWS_2026-10-06.csv`

Window audited:
- **2025-07-01 .. 2026-09-25**
- XAU/USD 15-minute rows downloaded: **40,504**
- all **320** signal-panel dates have XAU/USD 15-minute data
- missing signal dates: **0**
- 2025 H2: 129/129 dates covered; median 96 bars/day
- 2026 Jan-Jul: 151/151 dates covered; median 96 bars/day
- 2026 Aug-Sep: 40/40 dates covered; median 96 bars/day
- only thin date: **2025-07-04**, 87 bars; retain as a flagged holiday/short-session observation, not as a data-gap failure.

**Coverage gate decision: PASS for the signal-day XAU/USD 15-minute hour-of-day/session study.**

This PASS authorizes session-path attribution for the existing CIG-D1 signals. It does **not** authorize treating pre-08:00 New York price movement as executable P&L from CIG-D1 V1.

### Current probe result

Authoritative artifact:
\`GOLD_SESSION_DATA_AVAILABILITY_GATE_2026-10-06.json\`

Confirmed with the connected Twelve Data source:
- XAU/USD **15-minute** historical samples: PASS for **2023, 2024, 2025, 2026**
- XAU/USD **1-hour** historical samples: PASS for **2023, 2024, 2025, 2026**
- representative 2025 **EUR/USD, GBP/USD, USD/JPY 15-minute** samples: PASS
- registered XAU/USD 1-hour research backfill already contains **17,644 rows for 2022-2024**
- 2025-2026 XAU/USD hourly retrieval has already passed in execution audits
- 2026 Aug-Sep XAU/USD 15-minute retrieval has already passed in the intraday scan.

Confirmed through project probe + vendor authority:
- Databento \`GLBX.MDP3\` access/symbology: PASS
- CME historical futures coverage: available from 2010+, including GC and OHLCV-1m / OHLCV-1h schemas.
- Existing project cost probe shows historical CME bridge data are economically accessible at small test cost.

Not yet available/governed in the repository:
- continuous London OTC intraday trade/volume history (LBMA Trade Data is a subscription product; public pages are not a minute-level historical OTC feed)
- Shanghai Gold Exchange intraday historical series
- full historical actual-vs-consensus macro surprise database
- governed Europe/UK/China event-surprise history
- long-horizon Borsa İstanbul execution-instrument intraday history at 15-minute or finer resolution.

### Gate interpretation

**PASS for a first session-price study:**  
We already have enough data to test where XAU/USD moves across Asia/Europe/New York clock windows and to add CME/COMEX futures price/volume as a second price-discovery channel.

**PARTIAL for a full institutional microstructure study:**  
We do not yet have direct continuous London OTC and Shanghai intraday histories, so those venues cannot initially be modelled as fully observed order-flow markets.

**PARTIAL for event-conditioned session models:**  
US event calendars exist in the project and some actual-consensus observations exist, but complete governed surprise histories are not yet present; Europe/China event-surprise histories are missing.

### Binding rule

No missing series may be silently replaced by a proxy.

The research must proceed in two tiers:

**Tier A — immediately feasible**
- XAU/USD 15m/1h global path
- COMEX GC futures price/volume via Databento
- EUR/USD, GBP/USD, USD/JPY intraday context
- session and overlap decomposition
- DST-aware time mapping.

**Tier B — blocked until sourced**
- direct London OTC flow/liquidity
- Shanghai venue-specific intraday flow
- full event-surprise conditioning
- exact Borsa İstanbul execution reconstruction over long history.

Only after this gate is documented may the source-ready timestamp audit and session-head modelling proceed.


**Status:** ACTIVE RESEARCH AUTHORITY / EXECUTION CLOCK NOT YET FROZEN  
**Purpose:** determine **when** a valid short-horizon UP/DOWN signal becomes actionable, which global gold session carries the relevant price discovery, and whether one global forecast is sufficient or session-specific heads are required.

This section supersedes ad-hoc “best hour” searches. No execution hour may be promoted from a retrospective timing scan alone.

## 5E.1 Core business question

The project must answer four different questions separately:

1. **Forecast clock:** at what timestamp can the complete signal actually be computed using only information already available?
2. **Price-discovery clock:** in which global session is the relevant gold information incorporated into price?
3. **Execution clock:** after the signal is genuinely available, what entry/exit window is economically executable?
4. **Venue clock:** can the intended instrument (spot/OTC, COMEX/Globex, Borsa İstanbul ETF/certificate, etc.) actually be traded in that window?

A model can be directionally correct and still be a poor trading system if most of the move occurs before its actionable timestamp.

## 5E.2 Global gold is not a three-box market

The gold market is continuous and overlapping rather than three isolated “Asia / Europe / America” blocks.

World Gold Council identifies the three dominant global centres as:
- **London OTC**
- **US futures / COMEX**
- **Shanghai (SGE/SHFE)**

These three centres account for **more than 90% of global gold trading volume** in the cited WGC market-structure framework. London OTC is the key wholesale hub; COMEX is the leading listed-derivatives venue; Shanghai is the principal Chinese physical/futures centre.

Binding interpretation:
- **three dominant market centres do not imply three forecast models**;
- the number of operational forecast heads must not be chosen from geography alone;
- the project will carry **two externally anchored candidate partitions** before model testing: (A) the World Gold Council 2026 three-session **New-York-local / DST-aware** partition and (B) the Sobti et al. five-zone ET academic replication partition;
- the 2013–2018 Sobti Asia Morning/Asia Afternoon split must not be misdescribed as the official modern 2023–2026 SGE matching-session structure because SGE extended its day matching session to 09:00–15:30 effective 2019-06-10;
- only after 2023–2024 development and frozen 2025 transport may the final operational architecture be reduced/expanded to **3, 4, or 5 heads**; that count is an empirical result, not a geographic prior;
- do not assume a move belongs exclusively to one geography;
- overlapping hours must be tested explicitly because price discovery can migrate between venues.

## 5E.3 Authoritative market clocks

### London / LBMA

- Loco London precious-metals trading operates on a **24-hour basis** through the OTC market.
- LBMA Gold Price auctions begin at:
  - **10:30 London time — AM**
  - **15:00 London time — PM**
- These benchmarks are used for valuation/pricing across institutional gold products.
- The benchmark has direct participants including major banks and market makers such as Goldman Sachs, JPMorgan, Morgan Stanley, HSBC, Citibank, Jane Street, Virtu, Standard Chartered, StoneX and others.

These auction windows are therefore mandatory event-time markers in the execution study; they are **not** assumed automatically to be profitable entry points.

### New York / COMEX

- Standard COMEX Gold futures (GC) trade electronically for approximately **23 hours per trading day** on Globex, with a daily maintenance break.
- The current project’s CIG-D1 issuance contract is **08:00 America/New_York**.
- That timestamp is important because it lies at the beginning of the academically defined **New York/London overlap** window, not at the beginning of the European gold day.

US macroeconomic-announcement time must be treated separately from ordinary clock time. High-frequency academic evidence finds that scheduled **08:30 New York** releases — especially employment-related and other major macro surprises — can have unusually large effects on gold futures returns, volatility and volume.

### Shanghai / China

Shanghai Gold Exchange has both night and day trading:
- night session: **20:00–02:30 China time**
- day session: **09:00–15:30 China time**
with session breaks under the official SGE schedule.

Therefore “Asia” itself must not be represented as one undifferentiated bucket.

### Time-zone governance

All canonical clocks must be stored in the **local market timezone**:
- America/New_York
- Europe/London
- Asia/Shanghai
- Europe/Istanbul

Istanbul equivalents are derived per date using timezone-aware conversion. Fixed UTC offsets are forbidden because US/UK daylight-saving transitions do not match Türkiye.

## 5E.4 Academic price-discovery map

The primary academic authority for 24-hour session decomposition is:

**Sobti, Sehgal & Ilango (2021), International Review of Financial Analysis, “How do macroeconomic news surprises affect round-the-clock price discovery of gold?”**

Using one-minute data across New York, London and Shanghai, the paper partitions the day into five sequential zones (ET):
- Asia Morning: **21:00–23:30**
- Asia Afternoon: **01:30–03:30**
- European: **03:30–08:00**
- New York/London overlap (“Nylon”): **08:00–14:30**
- US: **14:30–21:00**

Key findings relevant to this project:
- New York futures lead global price discovery overall, with about **56% information share** in the study.
- The **New York/London overlap** is the most informative sequential trading zone, with about **51%** of price discovery in the study’s measure.
- US macro surprises materially alter price-discovery leadership.
- Eurozone and China news effects differ; the influence is state-dependent and asymmetric.

Additional academic authority:
- **Hauptfleisch, Putniņš & Lucey (2016), Journal of Futures Markets:** both London spot and New York futures contribute to gold price discovery, but New York futures play the larger role on average; the share varies intraday, across years, with daylight hours and macro announcements.
- **Iwatsubo, Watkins & Xu (2018), Journal of Commodity Markets:** intraday efficiency/liquidity/volatility differ by session; the New York day session shows more informed trading than Tokyo for gold.
- **Elder, Miao & Ramchander (2012), Journal of Banking & Finance:** US macro news effects on metals are swift and significant; the 08:30 US announcement cluster is particularly important.

Binding interpretation:
**the research unit is not merely “day”; it is signal × session × event state.**

## 5E.5 What institutional practice implies — and what it does not

Public institutional evidence supports the following structure:

- Large wholesale gold trading is heavily OTC/London because OTC allows flexible deal size, pricing and bilateral execution.
- COMEX futures provide deep, transparent, centrally cleared derivative liquidity and are widely used for price discovery and risk transfer.
- Gold ETFs provide exchange-traded exposure, while authorised participants create/redeem large baskets; major products such as iShares Gold Trust reference the **LBMA Gold Price**, and IAU values bullion using the LBMA Gold Price PM for NAV.
- Major institutions participate directly in the LBMA benchmark process.

What public sources **do not** provide:
- a universal proprietary “fund buys gold at X o’clock” rule;
- a single institutional entry algorithm applicable to all funds;
- evidence that VWAP/TWAP/benchmark execution automatically maximises directional alpha.

Therefore the project may learn from institutional **venue, benchmark, liquidity and event-time structure**, but it must not fabricate proprietary fund timing rules.

## 5E.6 Current short-term model clock — binding interpretation

The present CIG-D1 action contract is issued at **08:00 New York**.

Therefore:
- it is **not an Asia-session forecast**;
- it is **not a Europe-open forecast**;
- **08:00 New York is only the governed issue deadline of legacy CIG-D1 V1**; it must not be silently reused as the issue clock for future Asia/Europe/session-specific heads;
- CIG-D1 V1 is issued at the start of the academically defined New York/London-overlap window, but its recovered historical target is a **date-labelled daily reference**, not an overlap return;
- any European-session price move occurring before 08:00 New York cannot be counted as executable P&L from this signal.

This distinction is mandatory.

If the complete CIG-D1 state can in fact be reconstructed earlier than 08:00 New York using only already-published inputs, that would constitute a **new, separately frozen issuance identity**, not a silent change to CIG-D1 V1.

## 5E.7 Required execution audit before any “best hour” claim

The following audit is mandatory and must be completed in order.

### A. Source-ready timestamp audit

For every binding expert/input:
- source observation timestamp
- publication timestamp
- historical availability lag
- API/file arrival timestamp where observable
- computation completion time.

Define:

t_ready = max(all required source availability timestamps) + compute latency

No execution price earlier than t_ready is allowed.

### B. Session-path attribution

For each frozen signal state:
- 4/4 UP
- 4/4 DOWN
- UNCERTAIN

measure the price path separately across:
- Asia night / Asia day
- Europe pre-overlap
- New York/London overlap
- late US
- benchmark/event windows.

This is attribution first, not optimisation.

### C. Event-time controls

Tag at minimum:
- LBMA Gold Price AM
- LBMA Gold Price PM
- scheduled US 08:30 macro releases
- major US central-bank/event times where applicable
- major Eurozone/UK/China releases when an authoritative event calendar is available.

Clock-time alpha must be separated from event-time alpha.

### D. Development/transport rule

- select execution logic only on **pre-2026 development chronology**
- freeze it
- transport unchanged into opened 2026
- report 2026 by Jan–Jul and Aug–Sep separately
- no re-optimisation on 2026.

### E. Metrics

For each candidate session rule report:
- number of eligible signals
- compound gross return
- arithmetic mean and median trade return
- hit rate
- max drawdown
- worst trade
- return by month/quarter
- turnover
- sensitivity to ±15/30/60 minute entry shifts
- cost/slippage break-even threshold.

No candidate may be called robust if its edge exists only at one exact bar.

## 5E.8 Binding session-model discovery protocol

The project must **not** jump directly from the three dominant physical/financial gold centres to three forecast models.

The research hierarchy is:

**Layer 1 — Global State/Core**  
A common origin-safe global state may be retained as shared context. Existing H3/CIG expert families are candidate information channels, not automatically valid session predictors.

**Layer 2A — Two externally anchored candidate target partitions**  
The project carries both structures into pre-2026 model testing:

**A. WGC_2026_NY3**
1. Asia — 18:00–03:00 America/New_York
2. Europe — 03:00–08:00 America/New_York
3. US — 08:00–17:00 America/New_York

**B. SOBTI_5_ET**
1. Asia Morning — 21:00–23:30 ET
2. Asia Afternoon — 01:30–03:30 ET
3. Europe — 03:30–08:00 ET
4. New York/London overlap — 08:00–14:30 ET
5. Late US — 14:30–21:00 ET

The two partitions are **alternative externally anchored research decompositions**. They must not be blended into a synthetic clock after seeing accuracy.

Each target window must have:
- target start/end timestamps;
- latest permissible feature timestamp;
- source-ready / issue timestamp;
- realized return and direction label;
- DST-aware mapping;
- no-leakage rule;
- explicit market/venue eligibility;
- explicit data-quality eligibility.

A session prediction is valid only if its full information set is available **before that target begins**. For later windows, already-completed earlier-session price action may be used only when it is origin-known at that head's issue time.

**Layer 2B — Expert revalidation by target**  
SAGE, V5-DCE, RIFT, VEGA, RuleFlow and other existing H3 experts are **not copied blindly into every session consensus**. Each expert/family must earn inclusion separately for each retained target under pre-2026 chronological testing. An expert may be useful in one target and harmful or redundant in another.

**Layer 2C — Data-driven architecture decision**  
Use 2023–2024 for development and **2025 frozen transport** to decide whether:
- the current-industry three-window WGC structure transports best;
- explicit NY/London overlap adds stable incremental value;
- the two Sobti Asia subzones carry distinct predictive information;
- contiguous targets should be merged or retained separately.

The final operational head count may therefore be **3, 4, or 5**. It is an empirical transport result, not a geographic prior.

The default hypothesis remains **not** “three centres = three models.”  
The binding question is: **how many distinct forecast targets are reproducibly justified out of sample?**

**Layer 3 — Session Consensus**  
For each retained operational target, construct a separate selective consensus (UP / DOWN / UNCERTAIN) only from experts that passed that target's development/transport gate.

**Layer 4 — Execution Head**  
Entry/exit logic is evaluated only after the corresponding session forecast is genuinely available. Execution-window optimisation cannot redefine the forecasting target after results are seen.

### Chronology for session-model discovery

- **2023–2024:** development / expert and partition-structure study;
- **2025:** frozen transport / architecture decision;
- **2026:** retrospective stress only; no clock or architecture retuning.

The governed 2023–2025 15-minute UTC backfill and final premodel quality/venue gate are now **complete** under Section 5E.8B. Model work may begin only from rows carrying `final_trainable == True`.

Separate full models for every target are **not yet binding**. The number of production heads is decided only after the frozen chronological comparison.

### 5E.8A Session clock / DST authority — corrected 2026-10-06

Authority:
- `GOLD_GLOBAL_5WINDOW_CLOCK_CONTRACT_2026-10-06.md`

Independent verification found a material modernization issue in the first same-day draft: Shanghai Gold Exchange extended its matching-market daytime session effective **2019-06-10** by adding the former 11:30–13:30 interval. Therefore the old 09:00–11:30 / 13:30–15:30 split from pre-2019 market structure is **not** binding as the modern 2023–2026 SGE target definition.

Binding candidate partitions are now:

**A — WGC_2026_NY3 (current industry benchmark candidate, New-York-local / DST-aware)**
- Asia: **18:00–03:00 America/New_York**
- Europe: **03:00–08:00 America/New_York**
- US: **08:00–17:00 America/New_York**
- spring/summer EDT UTC equivalents: 22:00–07:00 / 07:00–12:00 / 12:00–21:00
- winter EST UTC equivalents: 23:00–08:00 / 08:00–13:00 / 13:00–22:00

The UTC equivalents published in WGC spring-2026 charts must not be hard-coded across winter dates. WGC has also used different analytical partitions in other research (for example 2024: 22:00–11:00 / 11:00–14:00 / 14:00–22:00 UTC), so this is an external benchmark candidate, not a universal exchange-hours definition.

**B — SOBTI_5_ET (academic replication, America/New_York date-aware)**
- Asia Morning: **21:00–23:30 ET**
- Asia Afternoon: **01:30–03:30 ET**
- Europe: **03:30–08:00 ET**
- NY/London overlap: **08:00–14:30 ET**
- US: **14:30–21:00 ET**

These two schemes must remain distinct:
- WGC_2026_NY3 is the current operational/session-attribution candidate;
- SOBTI_5_ET is the historical academic price-discovery replication candidate;
- neither may be silently rewritten to match the other.

Raw clock provenance:
- governed 15-minute XAU/USD research data are requested/stored in **UTC**;
- Twelve Data intraday `datetime` denotes the **bar-open timestamp**;
- local clocks are derived from UTC using IANA timezone rules;
- fixed manual DST offsets are forbidden;
- an observed historical source-coverage regime change exists: 2023–early-2025 commonly show a one-hour 17:00 New York gap (92 x 15m bars on full trading dates), while later 2025 often contains 96 bars; this is a source/data-contract issue that must be audited and must not be mistaken for economic session structure.

Modern SGE venue marker:
- day matching session = **09:00–15:30 Asia/Shanghai** after the 2019 extension;
- night matching session = **20:00–02:30 Asia/Shanghai**;
- these are venue-state features/telemetry, not automatic target boundaries.

Forecast and realization remain separate:
- `SESSION_DIRECTION` = theoretical partition boundary-to-boundary move;
- `EXECUTABLE_DIRECTION` = strictly post-ready/post-signal entry to frozen exit;
- the two must never be reported as the same accuracy.

Chronology:
- 2023–2024 = development / partition and expert-structure study;
- 2025 = frozen transport / architecture decision;
- 2026 = retrospective stress only; no clock retuning.

Older coarse session buckets remain diagnostic only and are not binding training labels for the new session project.

### 5E.8B Final 2023–2025 premodel target/data gate — V5, 2026-10-06

**Binding status:** PASS — this section supersedes the earlier V2/V3/V4 target-panel wording for primary modelling.

Authorities:
- `GOLD_SESSION_TARGETS_V5_FINAL_RESULT_2026-10-06.md`
- `GOLD_SESSION_TARGETS_V5_FINAL_SUMMARY_2026-10-06.json`
- `GOLD_SESSION_TARGETS_WGC2026_NY3_FINAL_V5_2023_2025.csv`
- `GOLD_SESSION_TARGETS_SOBTI5_ET_FINAL_V5_2023_2025.csv`
- `GOLD_SESSION_TARGETS_V4_VENUE_GATE_SUMMARY_2026-10-06.json`
- `GOLD_SESSION_V3_INTEGRITY_GATE_2026-10-06.json`
- `GOLD_XAU15M_HOUR_COVERAGE_AUDIT_2026-10-06.json`
- `GOLD_XAU15M_MISSING_SLOT_AUDIT_2026-10-06.json`

Raw governed XAU/USD 15-minute UTC backfill:
- **74,163 rows**
- raw range: **2022-12-30 00:00 UTC -> 2026-01-02 23:45 UTC**
- duplicate UTC timestamps: **0**
- 15-minute timestamp grid: PASS
- OHLC internal consistency: PASS
- frozen raw SHA256: `8f1c00b34a95b7cef6a44c3c0bef59035fa9dde9cf6d241ba0b87fd146235308`

**Schema correction — 2026-10-06:** V4/V5 generation originally propagated the `return` field as `_20` because pandas `itertuples()` renamed the reserved/non-identifier column during row serialization. The V4 gate was corrected to preserve dataframe column names via `iterrows()/to_dict()`, V4 and V5 were regenerated, and the semantic counts remained unchanged. Any V5 artifact carrying `_20` instead of `return` is superseded and must not be used.

**Final target-price semantics**
- session start = **OPEN of the exact 15-minute bar beginning at target start T**;
- session end = **CLOSE of the exact final 15-minute bar beginning at T−15 and ending at target end T**;
- no nearest-bar substitution;
- no forward-fill/back-fill;
- no cross-source price imputation;
- zero-return rows are excluded from binary UP/DOWN training.

This corrects the earlier V2 endpoint treatment. Recomputing V2 -> V3 changed **30 direction labels** across comparable trainable rows:
- WGC candidate: **16** direction changes;
- Sobti candidate: **14** direction changes.

Therefore V2 target files are **SUPERSEDED / DO NOT TRAIN**.

**Venue/calendar gate — V4**
Primary clean targets additionally require the appropriate venue state:
- WGC Europe: London business day;
- WGC US: GC activity around target boundaries;
- Sobti Asia zones: SGE business day;
- Sobti Europe: London business day;
- Sobti NY/London: London business day + GC boundary activity;
- Sobti Late-US: GC boundary activity;
- Friday Sobti Late-US: **NOT_ELIGIBLE** irrespective of vendor 24x7 quotes.

WGC Asia remains a broad regional target; SGE state is retained as telemetry rather than a hard gate.

**Internal 15-minute path gate — V5**
For primary modelling:
- every expected 15-minute slot inside the target window must exist;
- sole structural exception: inside Sobti Late-US, the four New York maintenance slots **17:00, 17:15, 17:30, 17:45** may be absent;
- any other internal gap excludes the row;
- this rule added **36 further exclusions** beyond the V4 venue-clean core.

Final V5 integrity:
- candidate rows across both partitions: **6,264**
- duplicates: **0**
- final trainable rows: **5,721**
- final excluded rows: **543**
- invalid final rows: **0**
- final trainable rows with missing direction: **0**

Final file hashes:
- WGC final: `178f45e708b9faf415fb9e6d20bd15dda01983f0b3e0d269f3fa243a671e1e26`
- Sobti final: `cef50b30f895bb420196e1efd4ac01493c3939474199d098ca57428375a4cf06`

**Independent futures clock sanity check**
A Databento GLBX.MDP3 GC continuous-futures comparison was used only as a clock/date sanity check, not as a replacement target source. On comparable WGC-window rows, spot-vs-GC direction agreement was generally high (roughly 91%–99.6% by year/window in the completed audit). This supports the date/clock alignment while preserving XAU/USD spot as the target source.

The successful audit artifact remains:
- `GOLD_WGC3_DATABENTO_CLOCK_CROSSCHECK_2026-10-06.json`

A later redundant rerun encountered code/runtime issues and is non-authoritative; it does not replace the successful stored audit.

**Source-regime guardrail**
The Twelve Data feed changes coverage character during 2025. This is treated as source metadata only:
- it is **not** an economic regime;
- it must **not** be used as a predictive feature;
- model code may use it only for diagnostics/sensitivity.

**Hard model gate**
Primary session modelling must:
1. read only the V5 final target files;
2. assert `final_trainable == True`;
3. reject V2/V3/V4-only price-valid rows from the primary sample;
4. keep all excluded/review rows out of fitting and headline evaluation;
5. keep 2026 unopened for clock/architecture tuning.

### 5E.8C Raw-source rebuild rule for all session replays — BINDING

For every session-model replay, **stored derived artifacts are QA evidence only and are not authoritative model inputs**.

Do not feed any historical:
- `*_FEATURE_PANEL*.csv`
- `*_PREDICTIONS*.csv`
- `*_STATE*.csv`
- `*_SCORES*.csv`
- `*_INFERENCE*.csv`
- precomputed expert-state / controller-state files

directly into a new WGC/Sobti session model.

Each model must be rebuilt from its **rawest governed source available** for the required chronology.

Binding source order:

1. raw market / macro / positioning observations from the governed database or frozen raw vendor extract;
2. date-aware timestamp normalization and publication-lag/source-ready handling;
3. feature engineering reproduced from code;
4. V5 target reconstructed from raw XAU/USD 15-minute bars under the binding target-price semantics;
5. fit/predict;
6. only then compare the newly generated features/predictions against historical derived artifacts as QA.

Examples:
- XAU intraday target: rebuild from `GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv`;
- XAU hourly features: rebuild from raw Neon/Twelve hourly observations, not IRIS historical feature/prediction CSVs;
- GC/SI/NQ/ZN/CL features: rebuild from raw Databento/CME observations;
- DGS2/rates: rebuild from raw FRED observations with the governed publication/carry rule;
- GVZ/VIX/FX/oil/Nasdaq inputs: rebuild from their raw source series;
- CFTC/COT: rebuild from raw report observations using the report/publication date available at the forecast cutoff.

Model lineage must also be recomputed:
- AURORA must consume **freshly regenerated** IRIS/base-expert outputs, not archived AURORA/IRIS predictions;
- HELIOS must consume freshly regenerated upstream AURORA/OPAL/controller inputs;
- BOCPD/DPTC/RTE/RC-RTE/SCR-RTE must be rebuilt only after the corresponding fresh session baseline/error history exists.

V5 CSV target files remain **frozen audit authorities**, but model code must independently reconstruct target prices/directions from raw 15-minute XAU/USD and verify equality against V5 before fitting. A mismatch is a hard FAIL.

Historical derived files are allowed only for:
- reproduction checks;
- hash/count comparisons;
- regression tests;
- diagnosing divergence from the prior implementation.

They must never be used merely because rebuilding from raw data is inconvenient.

### 5E.8D Session replay checklist — IRIS checkpoint 1

**Status:** IRIS raw-source checkpoint completed for the correctly runnable hourly-only branch.

Authorities:
- `GOLD_SESSION_IRIS_HOURLY_RAW_REPLAY_V1_RESULT_2026-10-06.md`
- `GOLD_SESSION_IRIS_HOURLY_RAW_REPLAY_V1_SUMMARY_2026-10-06.json`
- `GOLD_SESSION_IRIS_HOURLY_RAW_REPLAY_V1_METRICS_2023_2024.csv`

Raw inputs:
- Neon hourly series: `XAU_USD_TWELVE_1H_RESEARCH_V1`
- observed hourly span used: **2022-01-02 23:00 UTC -> 2024-12-31 21:00 UTC**
- rows: **17,644**
- target reconstruction source: frozen raw XAU/USD 15-minute file
- historical IRIS feature/prediction/state artifacts used as model inputs: **NO**

Clock/leakage rule:
- Twelve hourly timestamp is the bar-open timestamp while the stored observation used by legacy IRIS is the bar close;
- therefore an hourly row opened at T becomes feature-available only at **T+1h**;
- replay uses the latest completed hourly close with availability <= session start;
- V5 targets were independently reproduced from raw 15-minute XAU before fitting: PASS.

Scope:
- only the original IRIS **HOURLY_ONLY_ALL Logistic-L2 candidate** was runnable without violating the new raw-source rule;
- 2023-2024 only;
- 2025 remained unopened;
- minimum 180 matured same-window observations were required before scoring, therefore 2023 scored samples begin late in the year.

Pooled 2023-2024 scored results:
- WGC Asia: accuracy **47.78%**, balanced **43.85%**
- WGC Europe: accuracy **47.20%**, balanced **45.08%**
- WGC US: accuracy **49.30%**, balanced **49.61%**
- Sobti Asia Morning: accuracy **47.65%**, balanced **47.88%**
- Sobti Asia Afternoon: accuracy **45.64%**, balanced **45.86%**
- Sobti Europe: accuracy **50.77%**, balanced **50.36%**
- Sobti NY/London: accuracy **52.66%**, balanced **52.61%**
- Sobti Late-US: accuracy **57.01%**, but balanced **48.04%**, UP recall **84.96%**, DOWN recall **11.11%**; this is class-direction bias rather than robust balanced skill.

Binding interpretation:
- **IRIS hourly-only branch: NO ROBUST SESSION EDGE / diagnostic only.**
- The apparently higher Late-US raw accuracy is not promoted because balanced accuracy and DOWN recall fail.
- **Full original IRIS A1+PATH branch: BLOCKED**, not failed. Its structural `base_logit` came from the NOVA/A1 lineage. Reusing archived H3 NOVA/IRIS predictions is prohibited by Section 5E.8C.
- To rebuild full IRIS against session targets, a separately governed structural training/warm-up history prior to the 2023 V5 target interval is required, or a preregistered alternative structural-training design must be created without looking at 2025/2026 outcomes.
- No 2025 transport decision is made for IRIS hourly-only because the development branch did not establish robust balanced skill.

Checklist:
- [x] raw hourly source used
- [x] raw 15m target independently reconstructed
- [x] hourly bar-close availability/leakage corrected
- [x] 2023-2024 only
- [x] WGC-3 and Sobti-5 scored
- [x] accuracy / balanced accuracy / UP recall / DOWN recall / Brier reported
- [x] no archived derived IRIS artifact used as input
- [ ] full A1+PATH IRIS session rebuild — BLOCKED pending valid structural training history
- [ ] 2025 transport — NOT OPENED for this non-passing hourly-only branch

Next checklist item after IRIS:
- proceed to the next model only if its full required upstream lineage can be rebuilt from raw governed sources;
- do not use archived H3 expert predictions as substitutes.

### 5E.8E COT publication-time repair gate — 2026-10-06

Authority:
- `GOLD_COT_PIT_AVAILABILITY_AUTHORITY_2026-10-06.md`
- `GOLD_COT_PIT_REAUDIT_SUMMARY_2026-10-06.json`
- `GOLD_COT_PUBLICATION_CALENDAR_PIT_V1.csv`
- `GOLD_COT_GOLD_PIT_STATE_RAW_REBUILT_2026-10-06.csv`
- `GOLD_OPAL_OLD_PROVEN_EARLY_COT_ROWS_2026-10-06.csv`
- `GOLD_V5_SESSION_COT_AVAILABILITY_MAP_2023_2025.csv`

Independent raw CFTC reaudit reproduces the Work audit leakage finding exactly:
- 2023 proven early-use legacy OPAL rows: **21**
- 2025 proven early-use legacy OPAL rows: **53**
- total: **74**

Root cause:
- legacy OPAL used date-only `report_date + 7 calendar days`;
- extraordinary CFTC publication interruptions in the 2023 ION incident and 2025 appropriations lapse exceeded that buffer.

Binding replacement:
- source clock is timezone-aware;
- normal governed default remains intentionally conservative: `report_date + 7 calendar days at 15:30 America/New_York`;
- if an official documented delayed publication is later, the official delayed date at 15:30 ET overrides;
- new joins must enforce `cot_available_at_utc <= feature_cutoff_or_target_start_utc`.

Raw source:
- CFTC Public Reporting Environment, Gold contract code `088691`;
- Futures Only dataset `72hh-3qpy`;
- Futures-and-Options Combined dataset `kh3c-gbw2`;
- options-only exposure continues to be reconstructed as combined minus futures-only.

Availability result:
- every V5 `final_trainable` session row in 2023–2025 maps to a governed latest-available COT report;
- therefore the COT series itself is **available**;
- the failure was historical availability timing, not absence of COT observations.

Model status:
- archived OPAL panels/predictions remain **QA-only / contaminated for 74 feature rows**;
- OPAL session replay remains **BLOCKED** until a fresh session feature panel is rebuilt from raw CFTC + raw XAU with the new availability authority;
- HELIOS variants consuming OPAL remain **BLOCKED DOWNSTREAM** until fresh OPAL session state exists;
- legacy OPAL performance must not be promoted as PIT-clean evidence.

### 5E.8E COT publication-time PIT remediation — 2026-10-06

**Status:** publication-time defect reproduced and source-level availability authority corrected; OPAL/HELIOS session replay remains blocked until fresh upstream session baselines exist.

Authorities:
- `tools/gold_cot_publication_pit_v1.py`
- `GOLD_COT_PIT_REAUDIT_SUMMARY_2026-10-06.json`
- `GOLD_COT_PUBLICATION_CALENDAR_PIT_V1.csv`
- `GOLD_COT_GOLD_PIT_STATE_RAW_REBUILT_2026-10-06.csv`
- `GOLD_V5_SESSION_COT_AVAILABILITY_MAP_2023_2025.csv`
- `GOLD_OPAL_OLD_PROVEN_EARLY_COT_ROWS_2026-10-06.csv`

Raw source:
- official CFTC Public Reporting API;
- COMEX Gold contract code `088691`;
- futures-only disaggregated dataset `72hh-3qpy`;
- futures+options combined disaggregated dataset `kh3c-gbw2`.

Availability rule:
- default governed availability remains intentionally conservative: **report/as-of date + 7 calendar days at 15:30 America/New_York**;
- if an official CFTC special announcement documents a later publication date, the official delayed publication date at 15:30 ET overrides the default;
- if an official holiday publication occurs earlier than the +7d conservative buffer, the conservative buffer is retained;
- all joins are timestamp-aware and use `cot_available_at_utc <= feature/target cutoff`.

Official delay regimes explicitly encoded:
- 2023 ION outage / backlog;
- 2025 appropriations-lapse backlog, using the final accelerated CFTC schedule announced 2025-12-09.

Independent raw CFTC reaudit result:
- rebuilt CFTC report rows: **1,060**
- first report date: **2006-06-13**
- last report date at audit: **2026-09-29**
- legacy OPAL panel rows audited: **1,029**
- proven early-COT-use rows: **74**
  - 2023: **21**
  - 2025: **53**
- legacy rows whose selected COT report changes under governed PIT: **74**

This exactly reproduces the lower-bound leakage finding from the independent Work audit.

Interpretation:
- the old OPAL statement that a fixed `report_date + 7 days` lag was always conservative is **SUPERSEDED**;
- the 2023 and 2025 exceptional release regimes violate that assumption;
- historical OPAL/HELIOS predictions that depended on those early rows cannot be treated as clean PIT evidence without full downstream regeneration;
- merely replacing the date column in an archived OPAL feature/prediction file is prohibited.

V5 session mapping:
- every current final-trainable WGC/Sobti session row in 2023-2025 can be mapped to a governed COT report using the corrected availability timestamp;
- this establishes **COT data availability**, not OPAL model readiness.

OPAL session status:
- raw COT feature-state generation is now **READY**;
- OPAL as a session reversal/controller model remains **BLOCKED_UPSTREAM_BASELINE**, because its routing logic depends on a fresh session baseline/AURORA direction and momentum state;
- archived AURORA/OPAL predictions may not be used as substitutes under Section 5E.8C.

HELIOS status:
- HELIOS V1-V5 remains **BLOCKED_UPSTREAM_OPAL/AURORA** for session replay;
- once fresh upstream session predictions exist, OPAL and HELIOS must be regenerated from raw COT plus the fresh upstream state.

### 5E.8F SELLR / STCR provenance gate — 2026-10-06

Repository lineage audit result:

- `GOLD_H3_COMPETENCE_TRANSITION_V1_SELLR_SCORES_SOURCE_2026-10-05.csv` exists and contains frozen `sellr_score` values;
- `gold_h3_competence_transition_program_v1.py` **consumes** those scores but does not generate them;
- the score file entered the inspected branch in commit `3b7135390fd3531ea701d188520ebd5e0724513b` with message **"Import frozen SELLR scores for competence transition program"**;
- the import commit added the score CSV, not a producer implementation;
- current branch, competence-transition branch, catalyst-diagnostic branch, exception-channel branch, hazard branch and repository code search did not recover an authoritative raw-source SELLR producer formula;
- STCR itself is resolved as `simulate_stcr` in `gold_h3_competence_transition_program_v1.py`, but its entry catalyst depends on the unresolved SELLR score.

Binding status:
- **SELLR = PRODUCER_LINEAGE_UNRESOLVED / BLOCKED_FOR_RAW_SOURCE_REPLAY**
- **STCR = BLOCKED_DOWNSTREAM** until SELLR can be regenerated from governed raw inputs;
- the existing frozen SELLR score CSV is QA/history evidence only and is prohibited as a new session-model input under Section 5E.8C;
- no attempt may reverse-engineer a new SELLR formula from its historical scores or 2026 outcomes.

Reopening condition:
- locate the original score-producing code with explicit feature definitions and chronology, or
- separately preregister a new catalyst model from raw sources without using the historical SELLR scores as targets.

### 5E.8G Macro-event raw ledger / source-ready gate — 2026-10-06

Authorities:
- `GOLD_MACRO_EVENT_RAW_OBSERVATIONS_2023_2025.csv`
- `GOLD_MACRO_EVENT_LEDGER_RAW_V1_2023_2025.csv`
- `GOLD_SESSION_MACRO_EVENT_AVAILABILITY_MAP_2023_2025.csv`
- `GOLD_MACRO_EVENT_LEDGER_RAW_V1_SUMMARY_2026-10-06.json`

Raw Neon event families verified for 2023–2025:
- CPI actual first print + consensus PIT: **34 complete paired events**
- NFP actual first print + consensus PIT: **35 complete paired events**
- unemployment-rate actual first print + consensus PIT: **35**
- average-hourly-earnings actual first print + consensus PIT: **35**
- each paired surprise uses `surprise_ready_at = max(actual.available_as_of, consensus.available_as_of)`.

Binding availability rule:
- an event surprise is **POST-RELEASE ONLY**;
- if its `surprise_ready_at_utc > target_start_utc`, it cannot be used as a feature for that full session;
- therefore an 08:30 New York CPI/NFP release cannot be backdated into an 08:00 New York WGC-US or Sobti NY/London forecast;
- it may be available to a later head such as Sobti Late-US if the release has already occurred and source-ready conditions pass.

FOMC:
- `MACRO_EVENT_V3_FOMC_SCORE` contains reconstructed score records whose `available_as_of` is the 2026 load/reconstruction time, not historical event-time PIT;
- its score value is **not** admissible as historical PIT feature;
- 2023–2024 event timestamps may be used only as event markers;
- no 2025 FOMC rows exist in this Neon series, so 2025 FOMC event coverage remains incomplete.

Still missing as governed raw actual/consensus event families:
- **PCE**
- **JOLTS**
- **ADP**

Any model requiring these three families, or a historical PIT FOMC score/surprise, remains blocked for that component. Missing families must not be synthesized from hard-coded event dates or reconstructed from future knowledge.

### 5E.8H GVZ / DGS2 raw-source closure — 2026-10-06

Authorities:
- `GOLD_GVZCLS_RAW_2021_2025.csv`
- `GOLD_DGS2_RAW_2022_2025.csv`
- `GOLD_GVZ_DGS2_RAW_BACKFILL_SUMMARY_2026-10-06.json`

GVZ:
- primary source: **Cboe official GVZ historical data**
- valid rows: **1,257**
- span: **2021-01-04 -> 2025-12-31**
- 2023 rows: 250
- 2024 rows: 252
- 2025 rows: 250
- SHA256: `ae9f34014d0b3ef42c3230097b2e982139b517059e82dd688917f350acfa597f`
- full-session governance: **D-1 completed GVZ only** until historical same-day publication/readiness timing is separately proven.

DGS2:
- primary source: **Federal Reserve H.15 Data Download Program**
- official series: `H15/H15/RIFLGFCY02_N.B`
- valid rows: **757**
- span: **2022-12-20 -> 2025-12-31**
- 2023 rows: 250
- 2024 rows: 250
- 2025 rows: 249
- SHA256: `eca51920e8a2711cc6faaf93238ceedfde6dfb2349f8d3fe18ac8e8382a3871b`
- full-session governance: **D-1 completed DGS2 only**;
- same-day DGS2 is admissible only to a later head after a historical publication timestamp/readiness contract is separately proven.

The original FRED graph-download route repeatedly timed out in Actions and is not the authority. Raw coverage was recovered from the primary publishers instead.

Implications:
- VEGA's raw GVZ coverage blocker for 2023–2025 is closed, subject to session-specific feature rebuilding and D-1 source-ready use;
- RuleFlow's previous 2025-Q4 DGS2 coverage blocker is closed;
- RuleFlow same-day rate/event-response logic remains **BLOCKED_FOR_FULL_SESSION** and may only be reconsidered for later heads after source-ready timing proof.

### 5E.8I Binding session-model execution hierarchy — 2026-10-06

**Purpose:** prevent primary direction engines, specialist correction layers, routers, controllers and final consensus logic from being mixed into one undifferentiated model list.

All new WGC/Sobti session work must follow this dependency order. A downstream layer may not be replayed until the fresh upstream predictions/states it consumes have been regenerated under Sections 5E.8B–5E.8H.

#### Stage 1 — Primary / stand-alone session direction engines

These models produce a direct UP/DOWN probability or direction from governed raw features and may be evaluated as independent session heads.

1. **NOVA A0 / CORE3**
   - structural daily direction baseline;
   - Gold/Silver/Platinum CORE3 feature block;
   - direct Logistic-L2 UP/DOWN head.

2. **NOVA A1 / ARCR**
   - structural daily direction model;
   - global CORE3 + recent balanced CORE3 expert mixture;
   - direct UP/DOWN output.

3. **IRIS HOURLY_ONLY_ALL / PATH_GLOBAL**
   - XAU/USD hourly PATH/VOL/SHAPE information only;
   - direct UP/DOWN head;
   - raw-source session checkpoint already completed;
   - current session verdict: **NO ROBUST SESSION EDGE / diagnostic only**.

4. **IRIS A1_PLUS_PATH / STRUCTURAL_IRIS**
   - NOVA A1 structural logit + hourly PATH;
   - direct UP/DOWN head;
   - currently **BLOCKED_UPSTREAM** until A1 is regenerated under the new session target chronology.

5. **SAGE SESSION_ONLY**
   - hourly session/phase decomposition only;
   - direct UP/DOWN head.

6. **SAGE PATH_SESSION**
   - IRIS PATH + hourly session/phase features;
   - direct UP/DOWN head.

7. **SAGE A1_SESSION**
   - NOVA A1 structural logit + session features;
   - direct UP/DOWN head;
   - blocked until fresh A1 exists.

8. **SAGE A1_PATH_SESSION**
   - NOVA A1 + IRIS PATH + session features;
   - direct UP/DOWN head;
   - blocked until fresh A1 exists.

**Stage-1 evaluation rule**
- rebuild every feature from governed raw sources;
- reconstruct V5 target from raw 15-minute XAU and verify equality before fitting;
- evaluate 2023–2024 development only until the representation/head is frozen;
- do not open 2025 transport merely because one 2023–2024 slice looks attractive;
- do not use any archived H3 prediction, feature, state, score or inference file as a model input.

#### Stage 2 — Specialist reversal / correction layers

These are **not stand-alone primary direction engines** for the new session hierarchy. They act on a fresh primary baseline or model a correction state.

- **RIFT** — predicts reversal relative to recent momentum; historically routed as an AURORA correction.
- **VEGA** — GVZ/options-implied-volatility reversal specialist.
- **OPAL** — CFTC/COT options-positioning reversal specialist.
- **TURN** — semivariance/tail reversal rule.
- **PRISM** — spectral residual correction to a primary probability.
- **TWIN** — local path-analogue rescue layer.

They may only be rebuilt after the required fresh Stage-1 baseline exists. Their old AURORA/H3 correction outputs are QA/history evidence only.

#### Stage 3 — Expert combiners / routers

These combine or select among already-generated primary experts.

- **SENTRY** — causal expert failover.
- **DART** — disagreement-aware regime transfer / expert selector.
- **AIM** — adaptive expert mixture.
- **AURORA** — asymmetric router between STRUCTURAL_IRIS and PATH_GLOBAL.
- **HELIOS V1–V5** — higher-order routing/exception architecture consuming AURORA/OPAL and related state.

They may not be treated as independent raw-feature direction engines.

#### Stage 4 — Meta-controller / rescue / transition layers

These operate on fresh baseline predictions, matured error history, disagreement history or transition state.

- **BOCPD Handoff Competence**
- **DPTC Q95/Q99**
- **RTE V1–V4**
- **RC-RTE V1/V2**
- **SCR-RTE V1**
- **STCR**
- **SELLR catalyst input** only where its producer lineage is proven.

Binding role rule:
- DPTC / BOCPD / RTE-family / STCR are not benchmarked as if they were independent session direction engines;
- they are evaluated by rescue, broken-call, abstention/coverage and net contribution relative to the fresh Stage-1/Stage-3 baseline they govern.

#### Stage 5 — Final consensus / governor

Only after Stages 1–4 are frozen may a final session consensus/governor be constructed.

The final governor may decide:
- which expert is eligible per session;
- whether a specialist/controller may override;
- confidence/abstain state;
- final session UP/DOWN/UNCERTAIN output.

No consensus weight, membership rule or override rule may be selected using 2025 or 2026 outcomes.

#### Binding execution order

`NOVA A0 -> NOVA A1 -> PATH_GLOBAL -> STRUCTURAL_IRIS -> SAGE primary heads`

then

`RIFT / VEGA / OPAL / TURN / PRISM / TWIN`

then

`SENTRY / DART / AIM / AURORA / HELIOS`

then

`BOCPD / DPTC / RTE / RC-RTE / SCR-RTE / STCR`

then

`FINAL SESSION CONSENSUS / GOVERNOR`.

A model may be skipped or marked BLOCKED, but the dependency direction may not be reversed merely to obtain a result sooner.

#### Current first executable item

**Checkpoint S1.1 = NOVA A0 / CORE3 raw-source session rebuild.**

Before fitting S1.1:
- identify the authoritative raw Gold/Silver/Platinum daily series;
- reproduce CORE3 transforms from raw observations;
- prove feature availability before each session target start;
- reconstruct V5 target from raw 15-minute XAU;
- fit only after all checks pass.

### 5E.8J Stage-1 checkpoint S1.1 — NOVA A0 / CORE3 raw session replay

Authorities:
- `GOLD_SESSION_NOVA_A0_CORE3_RAW_REPLAY_V1_SUMMARY_2026-10-06.json`
- `GOLD_SESSION_NOVA_A0_CORE3_RAW_REPLAY_V1_RESULT_2026-10-06.md`
- `GOLD_SESSION_NOVA_A0_CORE3_RAW_REPLAY_V1_METRICS_2023_2024.csv`

Status:
- **Stage-1 primary direction engine replay COMPLETE**
- raw daily Gold/Silver/Platinum payloads rebuilt from pinned StakTrakr commit `54fdf1c8d39b7b6c7b874d0f30f784296e886044`;
- no historical readiness feature panel or NOVA prediction artifact used as model input;
- V5 session targets independently reconstructed from raw 15-minute XAU/USD before fitting: PASS;
- 2023–2024 development only; 2025/2026 unopened.

Source-ready rule:
- Stak daily labels do not have a proven intraday publication timestamp;
- therefore each session may use only the latest common Gold/Silver/Platinum observation from a **strictly earlier America/New_York calendar date** than the session start;
- same-day daily metal observations are prohibited.

Model:
- CORE3 feature set reproduced from raw daily metal observations;
- StandardScaler + LogisticRegression(L2, C=1.0);
- per-partition/per-window expanding replay;
- minimum 120 matured same-window session outcomes before scoring;
- five-row scoring blocks.

Pooled 2023–2024 scored results:
- Sobti Asia Morning: accuracy **54.19%**, balanced **53.88%**
- Sobti Asia Afternoon: accuracy **47.77%**, balanced **47.91%**
- Sobti Europe: accuracy **51.44%**, balanced **51.12%**
- Sobti NY/London: accuracy **50.40%**, balanced **50.34%**
- Sobti Late-US: accuracy **56.93%**, balanced **49.94%**, UP recall **79.88%**, DOWN recall **20.00%**
- WGC Asia: accuracy **53.72%**, balanced **51.05%**
- WGC Europe: accuracy **51.05%**, balanced **49.59%**
- WGC US: accuracy **47.69%**, balanced **47.55%**

Binding interpretation:
- **NOVA A0 / CORE3: NO ROBUST SESSION EDGE as a stand-alone primary head.**
- Sobti Late-US nominal accuracy is rejected as evidence of edge because balanced accuracy is ~50% and DOWN recall collapses to 20%.
- Sobti Asia Morning is the least weak slice but does not establish sufficiently strong/stable evidence for promotion.
- A0 remains a required structural baseline for A1/STRUCTURAL_IRIS comparison, not a promoted session champion.
- 2025 transport remains unopened.

Next Stage-1 item:
- **S1.2 = NOVA A1 / ARCR raw-source session replay.**

### 5E.8K Databento raw cross-market archive closure — 2026-10-06

Authority:
- `GOLD_DATABENTO_RAW_ARCHIVE_2022_2024_SUMMARY_2026-10-06.json`
- `GOLD_DATABENTO_RAW_ARCHIVE_COVERAGE_2022_2024.csv`
- `GOLD_DATABENTO_CONTINUOUS_SYMBOLOGY_2022_2024.json`
- raw gzip archives for roll groups `c/n/v`.

Status: **RAW ARCHIVE BLOCKER CLOSED for 2022–2024.**

Governed archive:
- Databento dataset: `GLBX.MDP3`
- schema: `ohlcv-1h`
- window: **2022-01-01 -> 2025-01-01** (end-exclusive)
- roots: **GC, SI, NQ, ZN, CL**
- continuous rolls archived: **c, n, v**
- total continuous symbols: **15**
- estimated billed cost: **USD 2.358644604683**
- cost cap: **USD 3.00**

Validation:
- continuous symbology retained;
- `instrument_id` retained;
- UTC `ts_event` retained;
- duplicate `ts_event + symbol`: 0;
- OHLC validity gate: PASS;
- negative-volume gate: PASS;
- 2022, 2023 and 2024 presence required per symbol.

Guardrail:
- the raw archive closes the historical source/provenance blocker only;
- it does not prove that every hourly bar is source-ready at each session target start;
- model-specific use must still enforce bar-completion and `t_ready <= target_start`;
- no roll rule may be chosen by outcome performance.

### 5E.8L Stage-1 checkpoint S1.2 — NOVA A1 / ARCR raw session replay

Authorities:
- `GOLD_SESSION_NOVA_A1_ARCR_RAW_REPLAY_V1_SUMMARY_2026-10-06.json`
- `GOLD_SESSION_NOVA_A1_ARCR_RAW_REPLAY_V1_RESULT_2026-10-06.md`
- `GOLD_SESSION_NOVA_A1_ARCR_RAW_REPLAY_V1_METRICS_2023_2024.csv`

Status:
- **Stage-1 primary direction engine replay COMPLETE**
- A1 was rebuilt from the same pinned raw Gold/Silver/Platinum payloads as A0;
- archived A0/NOVA prediction files were not used;
- A0 comparator was regenerated inside the same raw replay on identical A1-scored rows;
- V5 target reproduction: PASS;
- 2025/2026 unopened.

Model:
- global CORE3 Logistic-L2;
- recent expert = latest **252 matured same-window** rows, balanced Logistic-L2;
- A1 probability = **0.75 × global + 0.25 × recent252**;
- same conservative daily source-ready rule as S1.1.

Because 252 matured same-window outcomes are required, the scored sample begins in 2024.

Matched 2024 results:
- Sobti Asia Afternoon: A0 **49.78% / 49.81% bal** -> A1 **47.53% / 47.55% bal**
- Sobti Asia Morning: **54.26% / 53.78%** -> **53.81% / 53.39%**
- Sobti Europe: **50.81% / 49.97%** -> **47.98% / 47.37%**
- Sobti NY/London: **48.77% / 48.46%** -> **47.95% / 47.80%**
- Sobti Late-US: **56.12% / 52.09%** -> **54.68% / 51.28%**
- WGC Asia: **53.11% / 50.21%** -> **52.70% / 50.60%**
- WGC Europe: **51.82% / 50.30%** -> **51.82% / 50.75%**
- WGC US: **44.55% / 44.69%** -> **46.45% / 46.44%**

Binding interpretation:
- **NOVA A1 / ARCR: NO ROBUST SESSION EDGE as a stand-alone primary head.**
- the recent-252 repair degrades most Sobti slices;
- small balanced-accuracy improvements in WGC Asia/Europe are not material;
- WGC US improves vs A0 but remains well below a useful stand-alone direction threshold.
- A1 is retained only as a structural input candidate for STRUCTURAL_IRIS / SAGE A1-based heads, not as a promoted session champion.

Stage-1 status:
- [x] S1.1 NOVA A0 / CORE3
- [x] S1.2 NOVA A1 / ARCR
- [x] S1.3 IRIS HOURLY_ONLY_ALL / PATH_GLOBAL — no robust stand-alone session edge
- [x] S1.4 IRIS A1_PLUS_PATH / STRUCTURAL_IRIS — fresh replay complete with governed 2022 warm-up; no global promotion
- [ ] S1.5 SAGE SESSION_ONLY — **NEXT**
- [ ] S1.6 SAGE PATH_SESSION
- [ ] S1.7 SAGE A1_SESSION
- [ ] S1.8 SAGE A1_PATH_SESSION

S1.4 binding inputs were regenerated in one chronology:
- fresh A1 probability from raw daily metals;
- fresh hourly PATH features from raw XAU;
- no archived IRIS/A1 prediction file consumed.

### 5E.8M Cross-metal intraday PATH diagnostic — 2026-10-06

Authorities:
- `GOLD_SESSION_STRUCTURAL_IRIS_CROSSMETAL_V1_SUMMARY_2026-10-06.json`
- `GOLD_SESSION_STRUCTURAL_IRIS_CROSSMETAL_V1_RESULT_2026-10-06.md`
- `GOLD_SESSION_STRUCTURAL_IRIS_CROSSMETAL_V1_METRICS_2023_2024.csv`
- `GOLD_SESSION_STRUCTURAL_IRIS_CROSSMETAL_V1_COVERAGE_2023_2024.csv`

Status:
- **DIAGNOSTIC COMPLETE; NOT A PROMOTED S1.4 RESULT**
- purpose: isolate whether intraday Silver/Platinum PATH adds information beyond fresh A1 + XAU PATH;
- 2025/2026 remain unopened;
- all variants are evaluated on the same common feature rows;
- no archived NOVA/A1/IRIS prediction artifact is consumed.

Raw intraday sources:
- XAU/USD: Twelve/Neon hourly research series, **17,644** rows over 2022–2024;
- Silver: Databento GLBX.MDP3 **SI.n.0**, **17,748** hourly rows over 2022–2024;
- Platinum: Databento GLBX.MDP3 **PL.n.0**, source gate **PASS**, **17,749** hourly rows over 2022–2024;
- PL fetch estimated billed cost: **USD 0.17588**;
- all hourly close features become available only after the corresponding hourly bar completes;
- maximum accepted feature staleness = **120 minutes**, fixed as a source-quality rule rather than tuned by outcome.

Matched variants:
- `A1_XAU_PATH` = fresh session A1 structural logit + XAU PATH;
- `A1_XAU_SI_PATH` = baseline + Silver PATH;
- `A1_XAU_SI_PL_PATH` = baseline + Silver + Platinum PATH.

Important chronology limitation:
- fresh A1 itself requires **252 matured same-window outcomes**;
- the downstream Structural-IRIS diagnostic then requires **180 matured A1 rows** before scoring;
- therefore scored rows occur only in **late 2024** and are small (**N=15–68** by window);
- Sobti Late-US has only **139** common feature rows and therefore produces **no scored downstream row** under the 180-row rule;
- this experiment must not be interpreted as a full 2023–2024 S1.4 validation or used to open 2025.

Diagnostic findings on matched scored rows:
- **Sobti Asia Afternoon:** XAU-only **44.59% BA** -> +SI **53.46%** -> +SI+PL **53.68%**; Silver is materially helpful in this small late-2024 slice and also improves Brier from **0.2661 to 0.2508**;
- **Sobti NY/London:** **53.77% BA** -> +SI **56.55%** -> +SI+PL **55.56%**; Silver improves classification balance, while Platinum does not add further value;
- **Sobti Asia Morning:** XAU-only **55.37% BA** -> +SI **47.04%** -> +SI+PL **51.75%**; cross-metal PATH degrades the stronger XAU-only result;
- **Sobti Europe:** **41.06% BA** -> +SI **39.71%** -> +SI+PL **38.36%**; cross-metal PATH is harmful;
- **WGC Europe:** XAU-only **41.49% BA** -> +SI **40.14%** -> +SI+PL **44.19%**; Platinum lifts direction metrics modestly but sharply worsens Brier, so this is not promotion evidence;
- **WGC US:** **48.75% BA** -> +SI **48.75%** -> +SI+PL **42.50%**; no Silver gain and Platinum is harmful;
- **WGC Asia:** N=15 only; the apparent BA lift to **50.00%** is too small to interpret.

Binding interpretation:
- intraday Silver/Platinum omission is **not proven to be a universal model defect**;
- **Silver shows a targeted signal in Sobti Asia Afternoon and NY/London**, but degrades other windows;
- Platinum provides **no broad incremental edge** over Silver and often worsens probability quality;
- cross-metal intraday information, if retained, must therefore be **window-specific rather than globally appended**;
- because the downstream sample is too small, **S1.4 remains open** and 2025 must remain unopened;
- the next scientifically valid step is to solve the structural warm-up/history problem or use a preregistered one-stage representation that yields materially larger 2023–2024 scored samples without using 2025/2026.

Stage-1 status after cross-metal diagnostic:
- [x] S1.1 NOVA A0 / CORE3
- [x] S1.2 NOVA A1 / ARCR
- [x] S1.3 IRIS HOURLY_ONLY_ALL / PATH_GLOBAL
- [ ] S1.4 IRIS A1_PLUS_PATH / STRUCTURAL_IRIS — **OPEN; cross-metal diagnostic completed but insufficient downstream history**
- [ ] S1.5 SAGE SESSION_ONLY
- [ ] S1.6 SAGE PATH_SESSION
- [ ] S1.7 SAGE A1_SESSION
- [ ] S1.8 SAGE A1_PATH_SESSION

### 5E.8M Cross-metal intraday PATH ablation checkpoint — 2026-10-06

Authorities:
- `GOLD_SESSION_STRUCTURAL_IRIS_CROSSMETAL_V1_RESULT_2026-10-06.md`
- `GOLD_SESSION_STRUCTURAL_IRIS_CROSSMETAL_V1_SUMMARY_2026-10-06.json`
- `GOLD_SESSION_STRUCTURAL_IRIS_CROSSMETAL_V1_METRICS_2023_2024.csv`
- `GOLD_SESSION_STRUCTURAL_IRIS_CROSSMETAL_V1_PREDICTIONS_2023_2024.csv`
- `GOLD_SESSION_STRUCTURAL_IRIS_CROSSMETAL_V1_COVERAGE_2023_2024.csv`

Status:
- **matched-sample development diagnostic COMPLETE**;
- 2025/2026 remain unopened;
- no archived NOVA/A1 prediction file was consumed;
- fresh A1 was regenerated from the governed raw daily Gold/Silver/Platinum lineage before the hourly experiment.

Intraday source gate:
- XAU/USD Twelve/Neon 1h: **17,644 rows**, 2022-01-02 -> 2024-12-31;
- Silver Databento `SI.n.0` 1h: **17,748 rows**, 2022-01-02 -> 2024-12-31;
- Platinum Databento `PL.n.0` 1h: **17,749 rows**, 2022-01-02 -> 2024-12-31;
- Platinum source gate: **PASS**;
- Databento estimated PL retrieval cost: **USD 0.17587967217**;
- every hourly close is usable only after its bar completes;
- maximum admitted source staleness at target start: **120 minutes**, fixed before scoring.

Matched representations:
1. `A1_XAU_PATH` = fresh A1 base logit + XAU hourly PATH;
2. `A1_XAU_SI_PATH` = baseline + Silver hourly PATH;
3. `A1_XAU_SI_PL_PATH` = baseline + Silver + Platinum hourly PATH.

All three variants were fitted on the same common rows. SI/PL are GLBX.MDP3 futures-derived exogenous PATH features and are **not** treated as spot-metal replacements. The `n.0` continuous identity was fixed ex ante for this source experiment; no roll rule was chosen from outcomes.

Because fresh session A1 itself requires **252 matured same-window observations**, and the Structural-IRIS layer then requires **180 matured rows**, the causally scored comparison begins only in 2024. This is a warm-up limitation, not missing-market-data evidence. Sobti Late-US had only 139 common post-A1 rows and therefore produced no Structural-IRIS score; WGC Asia produced only 15 scored rows and is too small for promotion inference.

Key matched 2024 results:

| Window | A1+XAU Acc / BA / Brier | +SI Acc / BA / Brier | +SI+PL Acc / BA / Brier |
|---|---:|---:|---:|
| Sobti Asia Afternoon | 44.19% / 44.59% / 0.2661 | **53.49% / 53.46% / 0.2508** | 53.49% / 53.68% / 0.2551 |
| Sobti Asia Morning | **58.14% / 55.37% / 0.2476** | 48.84% / 47.04% / 0.2645 | 53.49% / 51.75% / 0.2832 |
| Sobti Europe | 44.12% / 41.06% / 0.2750 | 42.65% / 39.71% / 0.2920 | 41.18% / 38.36% / 0.3049 |
| Sobti NY/London | 51.56% / 53.77% / **0.2639** | **54.69% / 56.55%** / 0.2674 | 53.12% / 55.56% / 0.2683 |
| WGC Europe | 44.78% / 41.49% / 0.2734 | 43.28% / 40.14% / 0.2931 | 47.76% / 44.19% / 0.3083 |
| WGC US | 48.39% / 48.75% / 0.2769 | 48.39% / 48.75% / 0.2736 | 41.94% / 42.50% / 0.3081 |

Binding interpretation:
- hourly **Silver is not universally additive**;
- the only development slices with a meaningful directional lift from SI are **Sobti Asia Afternoon** and **Sobti NY/London**;
- on NY/London the directional lift comes with a slightly worse Brier score, so this is not yet a full probability-quality pass;
- hourly **Platinum does not show robust incremental value** over XAU+SI and often worsens probability quality;
- therefore SI/PL must **not** be added wholesale to every session head;
- Platinum is **NOT PROMOTED** at this checkpoint;
- Silver remains a **selective per-window challenger** only, principally Asia Afternoon and NY/London;
- 2025 transport remains closed. No 2025 result may be used to choose whether SI is retained.

This cross-metal diagnostic does **not** replace the full-coverage S1.4 `IRIS A1_PLUS_PATH / STRUCTURAL_IRIS` replay. The canonical S1.4 baseline still needs its maximal admissible A1+XAU panel; the SI challenger, if carried forward, must be compared against that frozen baseline without using 2025 outcomes.


### 5E.8N Clock-safe one-stage cross-metal diagnostic V2 — 2026-10-06

Authorities:
- `GOLD_SESSION_CROSSMETAL_V2_CLOCKSAFE_SUMMARY_2026-10-06.json`
- `GOLD_SESSION_CROSSMETAL_V2_CLOCKSAFE_RESULT_2026-10-06.md`
- `GOLD_SESSION_CROSSMETAL_V2_CLOCKSAFE_METRICS_2023_2024.csv`
- `GOLD_SESSION_CROSSMETAL_V2_CLOCKSAFE_COVERAGE_2023_2024.csv`
- `GOLD_SESSION_CROSSMETAL_V2_CLOCKSAFE_TIMING_AUDIT_2023_2024.csv`

Status:
- **CLOCK AUDIT PASS / ONE-STAGE WARM-UP DIAGNOSTIC COMPLETE**
- 2023–2024 only; 2025/2026 unopened;
- purpose: remove the A1→Structural-IRIS double warm-up and re-test XAU/Silver/Platinum intraday PATH with stricter timestamp governance.

Binding clock controls:
- all **3,816** frozen target rows were re-audited in `America/New_York` against the exact Sobti-5 and WGC-3 start/end clocks;
- hourly timestamps are treated as **bar-open timestamps** and the close becomes usable at bar-open + 1h;
- feature selection uses the latest completed bar with `available_at_utc < target_start` — **strict inequality**;
- a bar completing exactly at the target start is deliberately excluded from the primary V2 run;
- maximum admitted source lag at target start = **120 minutes**, fixed before scoring;
- the prior NY-calendar `session_ret` feature is excluded because its boundary is not the same thing as the frozen target-session boundary;
- V2 PATH returns are explicitly defined over the last N completed hourly observations (`1/3/6/12/24/48` completed bars);
- only matured same-window outcomes with `end_utc <= training cutoff` enter training.

Clock consequence:
- half-hour target starts generally use a latest completed feature bar **30 minutes** old;
- exact-hour target starts generally use a latest completed feature bar **60 minutes** old because exact-boundary completion is rejected;
- this is intentional conservatism, not a data gap.

One-stage representations:
1. `CORE3_XAU_PATH_CLOCKSAFE`
2. `CORE3_XAU_SI_PATH_CLOCKSAFE`
3. `CORE3_XAU_SI_PL_PATH_CLOCKSAFE`

The one-stage form consumes raw daily CORE3 state directly rather than a separately matured A1 probability, reducing warm-up while preserving causal same-window training. Common eligible feature panel = **3,711 rows** across the alternative Sobti-5 and WGC-3 partitions.

Combined 2023–2024 matched results:

| Window | XAU-only Acc / BA | +SI Acc / BA | +SI+PL Acc / BA | Binding V2 reading |
|---|---:|---:|---:|---|
| Sobti Asia Afternoon | 46.65% / 46.79% | 46.09% / 46.13% | 45.25% / 45.26% | cross-metal does not help |
| Sobti Asia Morning | **54.06% / 53.84%** | 52.66% / 52.34% | 53.50% / 53.33% | XAU-only remains better |
| Sobti Europe | 48.04% / 47.54% | 48.83% / 48.26% | 48.56% / 48.11% | tiny SI lift, still below useful edge |
| Sobti NY/London | 51.19% / 51.14% | **53.83% / 53.79%** | 51.98% / 51.95% | Silver selective challenger survives |
| Sobti Late-US | **59.85% / 54.29%** | 59.49% / 54.36% | 57.66% / 53.06% | SI neutral on BA; PL harmful |
| WGC Asia | 57.35% / 51.94% | **59.56% / 55.11%** | 57.72% / 53.42% | Silver selective challenger survives |
| WGC Europe | 51.05% / 50.23% | 51.31% / 50.53% | 50.52% / 49.44% | no material edge |
| WGC US | 51.16% / 51.08% | 50.58% / 50.51% | **53.18% / 53.11%** | PL lift is not cross-year stable |

Cross-year stability checks:
- **Sobti NY/London +SI:** BA **54.29% in 2023** and **52.16% in 2024**, versus XAU-only **51.99% / 49.41%**; directional improvement appears in both years, although Brier is slightly worse;
- **WGC Asia +SI:** BA **57.94% in 2023** and **54.20% in 2024**, versus XAU-only **47.23% / 53.67%**; improvement is present in both years, but the 2023 jump is much larger than 2024 and therefore requires frozen transport before promotion;
- **Sobti Asia Afternoon +SI:** 2023 improves but 2024 degrades; the small-sample V1 suggestion is therefore **NOT CONFIRMED** and is superseded as a promotion hypothesis;
- **WGC US +SI+PL:** 2023 degrades while 2024 improves; not stable and not promotable.

Binding interpretation after V2:
- the user's clock concern is valid and is now explicitly governed; no V2 hourly feature is allowed to use a bar completing at or after target start;
- **Silver is not globally additive**;
- the only cross-metal candidates that retain a meaningful directional case under the larger clock-safe sample are **Sobti NY/London +SI** and **WGC Asia +SI**;
- Platinum still has **no broad robust case** and remains **NOT PROMOTED**;
- V1's late-2024 Asia-Afternoon Silver lift was sample/warm-up-sensitive and must not be cited as a robust finding;
- the V2 one-stage experiment is a **representation diagnostic**, not a replacement for canonical S1.4 A1_PLUS_PATH;
- 2025 remains unopened and is reserved for frozen transport after representation/feature membership is fixed.

Stage-1 implication:
- S1.4 canonical A1_PLUS_PATH remains open;
- V2 establishes a clock-safe, larger-sample challenger representation and narrows cross-metal follow-up to NY/London Silver and WGC-Asia Silver;
- no consensus/router membership is changed yet.


### 5E.8O Exact-clock cross-metal timing authority V3 — 2026-10-06

Authorities:
- `GOLD_SESSION_CROSSMETAL_V3_EXACTCLOCK_SUMMARY_2026-10-06.json`
- `GOLD_SESSION_CROSSMETAL_V3_EXACTCLOCK_RESULT_2026-10-06.md`
- `GOLD_SESSION_CROSSMETAL_V3_EXACTCLOCK_METRICS_2023_2024.csv`
- `GOLD_SESSION_CROSSMETAL_V3_EXACTCLOCK_COVERAGE_2023_2024.csv`
- `GOLD_SESSION_CROSSMETAL_V3_EXACTCLOCK_CLOCK_QUALITY_2026-10-06.csv`
- `GOLD_SESSION_CROSSMETAL_V3_EXACTCLOCK_CLOCK_SAMPLES_2026-10-06.csv`

Status:
- **TIMING AUTHORITY PASS / EXACT-CLOCK DIAGNOSTIC COMPLETE**
- 2023–2024 only; 2025/2026 unopened.
- This section is stricter than V2 and supersedes any V2 cross-metal promotion interpretation that depends on last-N-bar rather than exact target-clock horizon semantics.

Binding target/source clock rules:
- all **3,816** governed target rows pass the frozen Sobti-5/WGC-3 clock audit in `America/New_York`;
- XAU/SI/PL hourly timestamps are treated as bar-open timestamps; close information is considered available only after the one-hour bar completes;
- target anchor = latest completed hourly close with `available_at < target_start`;
- exact-boundary bars are prohibited;
- for each horizon h in **1/3/6/12/24/48 hours**, reference cutoff = `target_start - h`;
- reference bar = latest completed hourly close with `available_at < reference_cutoff`;
- a row is retained only when the actual anchor-to-reference availability span equals **exactly h × 60 minutes** for every retained horizon and every source;
- maximum anchor/reference staleness = **120 minutes**;
- NY-calendar `session_ret` is not used.

External timestamp semantics are consistent with this contract:
- Databento OHLCV `ts_event` marks the **start** of the aggregation interval;
- Twelve Data intraday `datetime` denotes when the interval bar was **opened**.
The project still uses the stricter `available_at < target_start` rule to avoid ambiguity at the exact issue boundary.

Clock-quality evidence before the all-horizon gate:
- XAU exact-span pass rate: 1h **96.91%**, 3h **94.31%**, 6h **94.23%**, 12h **86.56%**, 24h **76.91%**, 48h **55.42%**;
- SI: **97.25%, 94.37%, 94.68%, 87.26%, 76.97%, 55.53%**;
- PL: **97.27%, 94.37%, 94.73%, 87.29%, 77.02%, 55.53%**.
- Requiring all three sources and all six exact horizons reduces the common panel from **3,816 to 2,103 rows**. This is deliberate timing purification, not a missing-data claim.

Representative audited timing examples:
- Sobti Asia Afternoon target start 06:30 UTC: XAU/SI/PL anchor available 06:00 UTC; 1h reference 05:00; 3h 03:00; 6h 00:00; 12h prior 18:00; 24h prior-day 06:00; 48h two-days-prior 06:00.
- Sobti Asia Morning target start 02:00 UTC: anchor available 01:00 UTC; exact 1/3/6/12/24/48h references preserve 60/180/360/720/1440/2880-minute spans.
- Sobti Europe target start 08:30 UTC: anchor available 08:00 UTC; the same exact-span contract is enforced for Gold, Silver and Platinum.
- Sobti NY/London target start 13:00 UTC in winter: anchor available 12:00 UTC; the 13:00-completing boundary bar is not used.

Combined exact-clock 2023–2024 scored results:

| Window | XAU-only Acc / BA | +SI Acc / BA | +SI+PL Acc / BA |
|---|---:|---:|---:|
| Sobti Asia Afternoon | 50.94% / **51.22%** | 51.57% / 51.44% | 49.06% / 49.02% |
| Sobti Asia Morning | 45.75% / 45.03% | 50.33% / 48.74% | **51.63% / 50.97%** |
| Sobti Europe | 48.09% / 46.97% | 48.09% / 47.17% | 44.81% / 44.48% |
| Sobti NY/London | 53.89% / 53.97% | 52.78% / 52.82% | **55.56% / 55.51%** |
| Sobti Late-US | **53.95% / 53.95%** | 50.00% / 50.00% | 46.05% / 46.05% |
| WGC Asia | **61.90% / 53.21%** | 60.32% / 51.92% | 60.32% / 54.33% |
| WGC Europe | **52.46% / 51.20%** | 51.91% / 50.47% | 50.82% / 49.37% |
| WGC US | 51.37% / 51.69% | 47.95% / 48.17% | **52.74% / 52.91%** |

Critical interpretation:
- the larger-sample V2 finding that Silver looked selectively useful in Sobti NY/London and WGC Asia **does not survive cleanly under the stricter exact-clock horizon contract**;
- Sobti NY/London +SI alone is worse than XAU-only under V3; +SI+PL is higher in the combined slice, but 2023 and 2024 behavior is not stable enough for promotion;
- WGC Asia +SI is worse than XAU-only in the exact-clock 2024 scored slice; no scored 2023 evidence survives the all-horizon warm-up/gate;
- Platinum still has no stable cross-year promotion case;
- therefore **no intraday Silver or Platinum path is promoted yet**;
- earlier V1/V2 cross-metal directional lifts are retained only as diagnostics/hypotheses and must not be quoted as robust model gains.

Methodological implication:
- the user's concern that loose hour alignment can materially change session-model conclusions is confirmed;
- future session-model feature engineering must use explicit target-clock horizon semantics, not ambiguous "last N bars" wording when N-hour interpretation is intended;
- because the exact 48h gate is the main coverage bottleneck, any next feature-screen should be preregistered and may compare shorter exact-clock horizon sets (for example 1/3/6/12h) to recover sample size **without relaxing the no-leakage clock contract**;
- 2025 remains unopened until this representation choice is frozen.

Stage-1 status:
- S1.4 canonical A1_PLUS_PATH remains open;
- V3 is the current cross-metal timing authority;
- no Silver/Platinum feature is admitted to consensus/router membership at this point.


### 5E.8P SI / Platinum 1-minute source validation and 15-minute archive authority — 2026-10-06

Authorities:
- `GOLD_SI_PL_1M_15M_VALIDATION_SUMMARY_2026-10-06.json`
- `GOLD_SI_PL_1M_15M_PREFLIGHT_COST_2026-10-06.json`
- `GOLD_SI_PL_1M_15M_CROSS_RESOLUTION_AUDIT_2026-10-06.csv`
- `GOLD_SI_PL_15M_COVERAGE_2022_2024.csv`
- `GOLD_SI_PL_1M_15M_MANUAL_SAMPLES_2026-10-06.csv`
- raw archive: `GOLD_DATABENTO_SI_PL_OHLCV1M_N0_RAW_2022_2024.csv.gz`
- derived 15m archive: `GOLD_DATABENTO_SI_PL_OHLCV15M_N0_DERIVED_2022_2024.csv.gz`
- native 1h validation archive: `GOLD_DATABENTO_SI_PL_NATIVE_OHLCV1H_N0_2022_2024.csv.gz`

Status:
- **SOURCE VALUE / CLOCK INTEGRITY: PASS**
- 2022–2024 only for the archived training/development source; no 2025/2026 model outcome was opened.
- Databento preflight estimated total retrieval cost: **USD 7.222839817405**, below the preregistered USD 8 cap.

Frozen source identity:
- vendor = **Databento**
- dataset = **GLBX.MDP3**
- input symbology = **continuous**
- Silver = **SI.n.0**
- Platinum = **PL.n.0**
- raw schema = **ohlcv-1m**
- timestamp = **UTC `ts_event` interval-start semantics**
- 15-minute archive = deterministic UTC 15-minute aggregation from the governed 1-minute source.

Downloaded / derived volume:
- raw SI+PL 1-minute rows: **1,882,086**
- derived 15-minute rows: **141,682**
- native Databento 1-hour validation rows: **35,497**

Binding value-integrity test:
- the governed 1-minute series was independently aggregated to 1-hour OHLCV;
- that aggregation was then matched timestamp-by-timestamp against Databento's **native ohlcv-1h** for the same continuous identities;
- **PL.n.0: 17,749 / 17,749 matched hours have exact O/H/L/C/volume agreement; 0 mismatches; max absolute difference = 0**
- **SI.n.0: 17,748 / 17,748 matched hours have exact O/H/L/C/volume agreement; 0 mismatches; max absolute difference = 0**
- no roll-ambiguous validation hour was present in either series.

15-minute coverage:
- PL.n.0: 23,548 bars in 2022; 23,513 in 2023; 23,732 in 2024.
- SI.n.0: 23,626 bars in 2022; 23,535 in 2023; 23,728 in 2024.
- no 15-minute bucket spans more than one underlying instrument identity under the frozen `n.0` mapping.

Important interpretation:
- **training/live source consistency is now a model contract, not an assumption.**
- any live/prospective Silver or Platinum feature must use the same Databento dataset, continuous identity, roll convention, timestamp semantics and completed-bar availability rule, unless a separately audited bridge is approved;
- exact cross-vendor level equality with spot XAG/USD or XPT/USD is **not** a valid integrity requirement because COMEX SI/PL futures and OTC/spot metals are different instruments and may legitimately differ in level/basis;
- therefore a future implementation must not silently substitute XAG/XPT spot, another continuous-roll convention, Yahoo front-month, or another vendor for SI.n.0 / PL.n.0 and still call it the same model input;
- if another vendor must be used in production, a separate matched-clock bridge/transport audit is mandatory before deployment.

Data decision:
- **SI 15m: READY for clock-safe model experimentation**
- **PL 15m: READY for clock-safe model experimentation**
- model promotion remains separate; source PASS does not imply predictive value.



### 5E.8Q IRIS15 full lag / volatility / shape cross-metal replay — 2026-10-06

Authorities:
- `GOLD_SESSION_IRIS15_CROSSMETAL_V2_MAINTAWARE_SUMMARY_2026-10-06.json`
- `GOLD_SESSION_IRIS15_CROSSMETAL_V2_MAINTAWARE_RESULT_2026-10-06.md`
- `GOLD_SESSION_IRIS15_CROSSMETAL_V2_MAINTAWARE_METRICS_2023_2024.csv`
- `GOLD_SESSION_IRIS15_CROSSMETAL_V2_MAINTAWARE_COVERAGE_2023_2024.csv`
- `GOLD_SESSION_IRIS15_CROSSMETAL_V2_MAINTAWARE_ASIA_SAMPLES_2026-10-06.csv`

Status:
- **15-MINUTE FULL-IRIS DIAGNOSTIC COMPLETE**
- 2023–2024 development chronology only; **2025/2026 remain unopened**.
- This is a one-stage CORE3 + intraday-IRIS representation diagnostic, not the canonical S1.4 A1_PLUS_PATH promotion result.

Features retained:
- daily CORE3 is unchanged and still contains **Gold `sigma20`**;
- exact-clock intraday returns: **1h, 3h, 6h, 12h, 24h, 48h**;
- original IRIS **lag2** semantics retained as an exact 1-hour return ending two hours before the anchor;
- realized volatility: **RV 6h / 12h / 24h / 48h**;
- 24h upside semivolatility, downside semivolatility, downside/upside semivol ratio;
- jump concentration and 24h range;
- shape family: up-fraction, 6h/24h slope, max drawdown, recovery, close location, age of maximum positive/negative move;
- former NY-calendar `session_ret` is **excluded** because it is not identical to the frozen target-session clock.

15-minute source/clock rules:
- XAU = governed XAU/USD 15m backfill;
- Silver = validated Databento `SI.n.0` 1m→15m archive;
- Platinum = validated Databento `PL.n.0` 1m→15m archive;
- normal target heads use the latest completed 15m bar strictly before target start, with median lag **15 minutes**;
- no bar completing at target start is used;
- exact-clock reference cutoffs are used rather than last-N-bar approximations.

Maintenance-aware correction:
- known New York **17:00–18:00** maintenance is treated as a deterministic as-of state only;
- no OHLC bar is fabricated;
- if an exact historical reference cutoff falls inside maintenance, the last real observed price may be carried as the known state, capped at **60 minutes** staleness;
- outside the registered maintenance interval, stale reference substitution is rejected;
- Sobti Asia Morning has up to **45 minutes** reference staleness only because its exact feature clock intersects the registered maintenance interval;
- WGC Asia starts at 18:00 New York, immediately after maintenance, so its last pre-target real state is structurally **60 minutes** old.

Common eligible feature rows after this gate:
- Sobti Asia Afternoon: **273**
- Sobti Asia Morning: **270**
- Sobti Europe: **293**
- Sobti NY/London: **296**
- Sobti Late-US: **195**
- WGC Asia: **183**
- WGC Europe: **294**
- WGC US: **263**

Chronology caveat:
- same-window minimum matured training history = **180**;
- therefore scored predictions in this replay occur **only in 2024**;
- the displayed `2023-2024_SCORED` rows equal the 2024 scored rows and must not be described as an independent two-year performance result;
- WGC Asia has only **3** scored rows after the 180-row warm-up and is non-interpretable;
- Sobti Late-US has only **15** scored rows and is also too small for promotion inference.

2024 matched results:

| Window | XAU15 full IRIS Acc / BA / Brier | +SI15 Acc / BA / Brier | +SI15+PL15 Acc / BA / Brier |
|---|---:|---:|---:|
| Sobti Asia Afternoon | 52.69% / 52.43% / **0.2999** | 50.54% / 50.21% / 0.3093 | **53.76% / 53.47%** / 0.3129 |
| Sobti Asia Morning | **54.44% / 55.20% / 0.2991** | 51.11% / 50.33% / 0.3277 | 47.78% / 46.69% / 0.3432 |
| Sobti Europe | 47.79% / 45.50% / **0.3093** | 49.56% / 46.71% / 0.3282 | **52.21% / 50.82%** / 0.3427 |
| Sobti NY/London | **55.17% / 55.13% / 0.2891** | 50.86% / 50.89% / 0.3106 | 51.72% / 51.74% / 0.3332 |
| Sobti Late-US | 66.67% / 69.44% / 0.2188 | 66.67% / 66.67% / 0.2184 | **73.33% / 75.00% / 0.1818** |
| WGC Asia | 66.67% / 66.67% / 0.1396 | 100% / 100% / 0.1096 | 100% / 100% / 0.0317 |
| WGC Europe | 50.00% / 48.62% / **0.2845** | 50.88% / 48.89% / 0.3008 | 50.00% / 48.12% / 0.3148 |
| WGC US | 50.60% / 50.41% / **0.2796** | 53.01% / 52.87% / 0.2988 | **56.63% / 56.42%** / 0.2845 |

Binding interpretation:
- preserving the original IRIS lag / realized-vol / semivol / shape families materially changes the 15m test relative to return-only diagnostics;
- **XAU15-only is the strongest credible representation for Sobti Asia Morning and NY/London** in this first 15m replay;
- wholesale Silver addition is not supported and often worsens Brier / balanced accuracy;
- adding Silver+Platinum raises direction metrics in some windows, especially WGC US, but probability quality is generally worse and there is no independent cross-year scored evidence;
- the apparent Late-US and WGC-Asia gains are **not promotable** because N=15 and N=3 respectively;
- therefore **no SI15 or PL15 block is promoted** at this checkpoint;
- XAU15 full-IRIS itself remains a serious challenger, principally for Sobti Asia Morning and NY/London, but requires a matched 1h full-IRIS control and/or larger causal scored history before architecture selection;
- 2025 remains frozen.

Stage-1 implication:
- canonical S1.4 A1_PLUS_PATH remains open;
- the 15m representation has passed source/clock construction but not promotion;
- the next fair test is **15m full IRIS versus 1h full IRIS on the same rows and same feature semantics**, rather than comparing against the earlier return-only hourly V3.



### 5E.8R Matched 15-minute vs 1-hour full-IRIS resolution authority — 2026-10-06

Authorities:
- `GOLD_SESSION_IRIS_RESOLUTION_MATCHED_V2_DERIVEDXAU_SUMMARY_2026-10-06.json`
- `GOLD_SESSION_IRIS_RESOLUTION_MATCHED_V2_DERIVEDXAU_RESULT_2026-10-06.md`
- `GOLD_SESSION_IRIS_RESOLUTION_MATCHED_V2_DERIVEDXAU_PAIRED_2026-10-06.csv`
- `GOLD_SESSION_IRIS_RESOLUTION_MATCHED_V2_DERIVEDXAU_COVERAGE_2026-10-06.csv`
- XAU cross-resolution audit: `GOLD_XAU15_NATIVE1H_CROSS_RESOLUTION_SUMMARY_2026-10-06.json`

Status:
- **MATCHED RESOLUTION TEST COMPLETE**
- development chronology only; **2025/2026 remain unopened**.
- This section supersedes any earlier direct 15m-vs-native-1h resolution interpretation because the binding comparison uses a 1h XAU series deterministically aggregated from the exact same governed XAU/USD 15m archive.

XAU source-integrity prerequisite:
- 11,706 complete 2023–2024 XAU hours were matched between 15m aggregation and the independently stored native Twelve 1h series;
- **11,699 / 11,706 = 99.9402%** were exact;
- **7 hours differed**, with maximum absolute close difference **$4.23999**;
- therefore native 1h is not used as the binding resolution control;
- the binding 1h XAU control is rebuilt directly from the governed 15m XAU bars, removing cross-resolution vendor aggregation/vintage differences as a confound.

Binding comparison contract:
- same target rows;
- same daily CORE3, including **Gold `sigma20`**;
- same StandardScaler + LogisticRegression(C=1.0);
- same minimum **180 matured same-window** training rows;
- same feature families: exact-clock 1/3/6/12/24/48h returns, lag2, RV 6/12/24/48h, semivolatility, jump/range and shape;
- `session_ret` excluded from both;
- same deterministic 17:00–18:00 New York maintenance handling;
- no bar completing at target start is used;
- difference under test = intraday sampling resolution / path granularity / pre-target freshness;
- SI/PL 1h controls retain the already validated Databento native 1h series, whose 1m-derived-vs-native 1h OHLCV audit was exact.

Common feature panel after requiring both resolutions = **2,055 rows**.

For the interpretable XAU-only heads (excluding WGC Asia N=2 and Sobti Late-US N=15), the matched 2024 directional comparison is:

| Window | N | 15m Acc / BA | derived-1h Acc / BA | ΔBA pp (15m−1h) | Brier 15m / 1h |
|---|---:|---:|---:|---:|---:|
| Sobti Asia Afternoon | 93 | 52.69% / **52.43%** | 47.31% / 47.43% | **+5.00** | 0.2999 / **0.2975** |
| Sobti Asia Morning | 88 | 54.55% / **55.13%** | 52.27% / 51.07% | **+4.06** | 0.3010 / **0.3000** |
| Sobti Europe | 112 | 46.43% / 43.68% | **47.32% / 44.76%** | **−1.09** | 0.3131 / **0.3087** |
| Sobti NY/London | 114 | **56.14% / 56.16%** | 52.63% / 52.56% | **+3.60** | 0.2983 / **0.2917** |
| WGC Europe | 109 | **52.29% / 50.60%** | 51.38% / 49.54% | **+1.06** | **0.2863** / 0.2867 |
| WGC US | 82 | **53.66% / 53.27%** | 47.56% / 47.14% | **+6.13** | 0.2798 / **0.2762** |

Resolution interpretation:
- 15m XAU wins Balanced Accuracy in **5 of 6** interpretable XAU-only heads;
- the largest matched directional gains are WGC US (**+6.13 pp BA**), Sobti Asia Afternoon (**+5.00 pp**), Sobti Asia Morning (**+4.06 pp**) and Sobti NY/London (**+3.60 pp**);
- Sobti Europe is the only interpretable XAU-only head where 1h is directionally better, by about **1.09 pp BA**;
- however 15m has a lower Brier score in only **1 of 6** interpretable XAU-only heads;
- therefore finer 15m sampling appears to improve threshold direction decisions more consistently than it improves probability calibration;
- this is compatible with a higher-information but noisier / more weakly calibrated representation and argues for calibration / shrinkage work before any operational promotion.

Cross-metal resolution interpretation:
- Silver and Platinum remain **window-specific and unstable**, not globally additive;
- 15m XAU+SI improves some Sobti heads but loses others;
- 15m XAU+SI+PL likewise alternates between gains and losses versus 1h;
- the notable 1h XAU+SI+PL WGC-US result (N=82, BA about **62.02%**) is retained only as a challenger hypothesis because scoring is still 2024-only, feature dimensionality is high, and its probability-quality advantage is not established;
- no SI/PL block is promoted from this test.

Chronology / evidence limitation:
- because same-window training requires 180 matured observations, scored rows are still effectively **2024 only**;
- WGC Asia (N=2) and Sobti Late-US (N=15) are non-interpretable for model selection;
- no individual head has yet passed an independent frozen-year transport test;
- therefore the matched test supports **15m XAU full-IRIS as the preferred development-resolution challenger**, not a final operational model.

Stage-1 implication:
- keep **15m XAU full-IRIS** as the primary intraday-resolution challenger for Sobti Asia Morning, Sobti Asia Afternoon, Sobti NY/London and WGC US;
- retain Sobti Europe as a window where 1h remains competitive / slightly better directionally;
- do not promote cross-metal blocks yet;
- next methodological task is to reduce the 15m calibration penalty through preregistered regularization/calibration or lower-dimensional feature selection **within 2023–2024 only**, then freeze the representation before opening 2025;
- canonical S1.4 A1_PLUS_PATH remains open.



### 5E.8S Nested variable / lag selection authority and development blueprint — 2026-10-06

Authorities:
- `GOLD_SESSION_IRIS15_NESTED_SELECTION_V1_SUMMARY_2026-10-06.json`
- `GOLD_SESSION_IRIS15_NESTED_SELECTION_V1_FEATURE_STABILITY_2026-10-06.csv`
- `GOLD_SESSION_IRIS15_NESTED_SELECTION_V2_BALANCED_SUMMARY_2026-10-06.json`
- `GOLD_SESSION_IRIS15_NESTED_SELECTION_V2_BALANCED_FEATURE_STABILITY_2026-10-06.csv`
- frozen development blueprint: `GOLD_SESSION_IRIS15_VARIABLE_SELECTION_DEV_BLUEPRINT_2026-10-06.json`

Status:
- **TRAINING-ONLY VARIABLE/LAG SELECTION COMPLETE**
- 2023–2024 development chronology only; **2025/2026 remain unopened**.
- Variable selection is now part of the challenger architecture, but only where it improves the window under explicit class-balance safeguards.

Leakage control:
- every outer 5-row test block is predicted from a model built only on matured same-window history before that block;
- inside each outer training set, C/feature selection uses up to three chronological expanding validation folds of 20 rows;
- no outer test label is used to select its own variables, lag, regularization strength, or coefficient;
- the selector is standardized L1 logistic with C in `[0.03, 0.10, 0.30, 1.00, 3.00]`;
- among candidates within 1 percentage point of best inner Balanced Accuracy, lower Brier is preferred, then fewer features / smaller C;
- selected variables are refit with L2 C=0.30;
- a second run repeated the same nested procedure with `class_weight=balanced` in both selector and refit.

Candidate pools:
1. `SELECT_XAU15`: daily CORE3 + XAU15 full IRIS.
2. `SELECT_ALL15`: daily CORE3 + XAU15 + SI15 + PL15 full IRIS.
3. Balanced versions of both.
4. Fixed reference = `FULL_XAU15_L2_C1`.

Important result:
- sparse selection materially improves probability quality in several windows, but **selection must not be forced everywhere**;
- some selected models improve Brier while degrading Balanced Accuracy or collapsing one class;
- therefore window-specific selection is required.

Examples of stable lag/variable structure:
- **Sobti Asia Afternoon:** XAU `lag2`, 6h, 12h and 24h returns repeatedly survive selection; daily `gold_r3`, `platinum_r21`, daily Silver/Platinum returns and `sigma20` also recur;
- **Sobti Asia Morning:** `gold_r5`, XAU 3h/1h/6h returns, 24h max drawdown and 24h slope are recurrent;
- **Sobti NY/London:** `gold_r5`, `sigma20`, XAU 48h RV, 6h slope, 24h jump/range/shape and 3h return recur;
- **WGC Europe:** daily `silver_r1`, `gold_r21`, `silver_r21`, XAU 3h return and XAU `lag2` are the clearest recurrent features;
- **WGC US:** no comparably stable high-frequency subset emerges; the sparse model is materially less stable.

Balanced-selection findings:
- Sobti Asia Afternoon `SELECT_XAU15_BAL`: **Acc 55.91%, BA 55.83%, Brier 0.2699**, versus FULL XAU15 **52.69%, 52.43%, 0.2999**;
- Sobti Asia Morning: FULL XAU15 remains directionally stronger (**BA 55.20%**) than selected balanced (**53.03%**);
- Sobti Europe: sparse variants improve Brier but produce one-sided class recall and therefore do not pass the selection safety rule;
- Sobti NY/London: FULL XAU15 remains directionally stronger (**BA 55.13%**) than selected balanced (**54.28%**);
- WGC Europe: unbalanced nested `SELECT_XAU15` is the strongest admissible sparse challenger (**BA 51.95%, Brier 0.2727**) and retains both class recalls above the preregistered floor;
- WGC US: sparse/cross-metal candidates either underperform or produce one-sided recall collapse; FULL XAU15 is retained;
- Sobti Late-US and WGC Asia remain non-interpretable because scored N is too small.

Development model-selection safety rule:
- minimum scored N for choosing a head = **80**;
- candidate must satisfy **min(UP recall, DOWN recall) >= 30%**;
- among admissible candidates, primary metric = Balanced Accuracy; Brier is secondary;
- a model cannot be chosen merely because overall accuracy or Brier improves while one class collapses.

Frozen 2023–2024 development blueprint:
- Sobti Asia Afternoon → **SELECT_XAU15_BAL**
- Sobti Asia Morning → **FULL_XAU15_L2_C1**
- Sobti Europe → **FULL_XAU15_L2_C1**
- Sobti NY/London → **FULL_XAU15_L2_C1**
- Sobti Late-US → **INSUFFICIENT_DEV_SCORE**
- WGC Asia → **INSUFFICIENT_DEV_SCORE**
- WGC Europe → **SELECT_XAU15**
- WGC US → **FULL_XAU15_L2_C1**

Cross-metal interpretation:
- SI15/PL15 are often selected in some training blocks, especially Asia Afternoon and NY/London;
- nevertheless, **intraday SI15/PL15 are still NOT PROMOTED** because the all-metal models do not yield a stable class-balanced improvement over the chosen per-window representation;
- daily Silver/Platinum variables remain part of CORE3 and may survive the selector.

Stage-1 implication:
- variable and lag selection is now integrated into the development architecture where evidence supports it;
- no global single feature set is imposed across all sessions;
- the above blueprint is a **development freeze**, not a final operational promotion;
- canonical S1.4 A1_PLUS_PATH has subsequently been completed under §5E.8T;
- 2025 remains reserved for frozen transport after the full Stage-1 representation contract is complete.



### 5E.8T S1.4 STRUCTURAL_IRIS closure with governed 2022 warm-up — 2026-10-07

Authorities:
- `GOLD_SESSION_2022_WARMUP_V5_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_2022_WARMUP_V5_RESULT_2026-10-07.md`
- `GOLD_SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP2022_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP2022_RESULT_2026-10-07.md`
- `GOLD_SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP2022_PAIRED_2026-10-07.csv`
- `GOLD_SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP2022_COVERAGE_2026-10-07.csv`

Status:
- **S1.4 COMPLETE**
- **NO GLOBAL STRUCTURAL_IRIS PROMOTION**
- 2025/2026 remain unopened.
- S1.5 SAGE SESSION_ONLY is the next Stage-1 dependency.

#### 2022 warm-up authority

The original 2023–2024-only S1.4 replay suffered a second-stage sample collapse because A1 itself requires 252 matured same-window observations before a structural probability exists. A governed 2022 warm-up layer was therefore added **only to mature/train the models**, never as an evaluation period.

Source/value gate:
- Twelve XAU/USD 15m was fetched from 2021-12-30 through 2023-01-03 using the same symbol, interval, UTC timezone and bar-open semantics as the governed later archive;
- the overlap with the existing governed archive contains **176 matched 15m bars**;
- Open / High / Low / Close mismatches on that overlap = **0 / 0 / 0 / 0**, maximum absolute difference = **0**;
- 2022 target construction uses the same exact start-OPEN / final-15m-CLOSE rule, date-aware New York clocks, venue/calendar gate and internal-path gate as the later V5 authority;
- Databento GC actual bar presence is reused for the US venue-state gate;
- 2022 final-trainable warm-up rows = **1,912**;
- 2022 is **WARMUP_ONLY_NOT_EVALUATION**.

2022 final-trainable rows by candidate head:
- Sobti Asia Afternoon **239**
- Sobti Asia Morning **238**
- Sobti Europe **249**
- Sobti NY/London **248**
- Sobti Late-US **197**
- WGC Asia **255**
- WGC Europe **249**
- WGC US **237**

#### Fresh S1.4 identity

Every S1.4 input is regenerated inside the replay:
- A1 = fresh raw daily Gold/Silver/Platinum CORE3 global + recent-252 mixture;
- A1 structural input = clipped A1 logit and is **mandatory** in every STRUCTURAL_IRIS fit;
- canonical PATH = same-source-derived **1h XAU** full IRIS PATH;
- resolution challenger = governed **15m XAU** full IRIS PATH;
- blueprint challenger = A1 + 15m XAU using the previously frozen per-window selection mode, with any variable selection recomputed only from current training history;
- no archived A1 / IRIS prediction artifact is read as a model feature.

Chronology:
- 2022 = warm-up / training only;
- 2023–2024 = scored development;
- downstream structural minimum history = **80 matured A1-feature rows**;
- block size = 5;
- 2025 / 2026 = unopened.

Scored coverage after warm-up:
- Sobti Asia Afternoon: **N=190** (2023 50; 2024 140)
- Sobti Asia Morning: **N=183** (47; 136)
- Sobti Europe: **N=213** (65; 148)
- Sobti NY/London: **N=215** (65; 150)
- Sobti Late-US: **N=89** (0; 89)
- WGC Asia: **N=102** (11; 91)
- WGC Europe: **N=210** (62; 148)
- WGC US: **N=177** (35; 142)

#### Combined 2023–2024 matched results

| Window | A1 BA / Brier | A1+1h BA / Brier | A1+15m BA / Brier | A1+15m blueprint BA / Brier | Binding reading |
|---|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 46.25% / 0.2595 | **51.02%** / 0.2908 | 48.54% / 0.2951 | 50.09% / 0.2719 | path lift is not year-stable |
| Sobti Asia Morning | 45.36% / **0.2578** | 49.91% / 0.2861 | **53.57%** / 0.2853 | **53.57%** / 0.2853 | strongest repeated directional 15m hypothesis |
| Sobti Europe | **50.07% / 0.2604** | 48.17% / 0.2842 | 41.42% / 0.3051 | 41.42% / 0.3051 | PATH rejected |
| Sobti NY/London | 48.54% / **0.2550** | **53.26%** / 0.2796 | 45.84% / 0.2896 | 45.84% / 0.2896 | 1h lift driven by 2024; not stable |
| Sobti Late-US | **54.22% / 0.2497** | 50.05% / 0.3042 | 48.50% / 0.3008 | 48.50% / 0.3008 | PATH hurts; no 2023 scored rows |
| WGC Asia | 38.93% / **0.2625** | 47.36% / 0.2622 | **53.49%** / 0.2747 | **53.49%** / 0.2747 | apparent lift fails DOWN-recall floor |
| WGC Europe | 52.22% / **0.2451** | 52.28% / 0.2681 | 47.81% / 0.2752 | **54.62%** / 0.2504 | blueprint is one-sided; fails recall floor |
| WGC US | 43.82% / **0.2566** | **50.28%** / 0.2811 | 49.15% / 0.2917 | 49.15% / 0.2917 | 1h direction lift, calibration worse |

Year-stability interpretation:
- **Sobti Asia Morning** is the only clear directional mechanism where the 15m Structural-IRIS improvement has the same sign in both scored years: 2023 BA **59.63% vs A1 50.83%** and 2024 BA **51.49% vs 43.49%**; however 2023 has only N=47 and combined Brier is worse, so this remains a challenger rather than a promotion.
- **Sobti Asia Afternoon:** combined PATH gain is largely 2024; 2023 PATH is worse than A1.
- **Sobti NY/London:** canonical 1h is strong in 2024 (**57.37% BA**) but materially worse than A1 in 2023; no stable promotion.
- **Sobti Europe:** STRUCTURAL_IRIS degrades direction and produces weak DOWN recall; reject for this window.
- **Sobti Late-US:** PATH degrades A1 and only 2024 is scored; reject.
- **WGC Asia:** 15m directional gain exists but combined DOWN recall is only **27.27%**, below the 30% safety floor; reject promotion.
- **WGC Europe:** canonical 1h is essentially neutral versus A1; the 15m blueprint raises BA but DOWN recall is only **22.47%**; reject promotion.
- **WGC US:** 1h raises BA by about **+6.47 pp** combined and passes the combined 30% recall floor narrowly, but Brier deteriorates and the 2023 scored slice is only N=35; retain as a challenger, not a promotion.

Binding S1.4 verdict:
- S1.4 is **methodologically complete**.
- There is **no single STRUCTURAL_IRIS representation that earns global session promotion** across the candidate heads.
- A1+PATH usefulness is **window-dependent**.
- The two principal hypotheses retained for later frozen transport are:
  1. Sobti Asia Morning → A1 + 15m XAU full PATH;
  2. WGC US → A1 + 1h XAU full PATH.
- These are not operational champions and do not authorize opening 2025 by themselves.
- No SI15 / PL15 block is promoted by S1.4.

Updated Stage-1 status:
- [x] S1.1 NOVA A0 / CORE3
- [x] S1.2 NOVA A1 / ARCR
- [x] S1.3 IRIS HOURLY_ONLY_ALL / PATH_GLOBAL
- [x] S1.4 IRIS A1_PLUS_PATH / STRUCTURAL_IRIS
- [ ] S1.5 SAGE SESSION_ONLY — **NEXT**
- [ ] S1.6 SAGE PATH_SESSION
- [ ] S1.7 SAGE A1_SESSION
- [ ] S1.8 SAGE A1_PATH_SESSION

Transport gate:
- **2025 remains CLOSED** until S1.5–S1.8 are completed and the full Stage-1 representation contract is frozen.



### 5E.8T Stage-1 checkpoint S1.4 — STRUCTURAL_IRIS with governed 2022 warm-up — 2026-10-07

Authorities:
- `GOLD_SESSION_2022_WARMUP_AUTHORITY_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP22_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP22_RESULT_2026-10-07.md`
- `GOLD_SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP22_PAIRED_2026-10-07.csv`
- `GOLD_SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP22_COVERAGE_2026-10-07.csv`

Status:
- **S1.4 IRIS A1_PLUS_PATH / STRUCTURAL_IRIS: COMPLETE**
- 2022 is training/warm-up only.
- 2023–2024 are scored development.
- **2025/2026 remain unopened.**

2022 warm-up authority:
- Twelve Data XAU/USD 15m rows: **23,727** from 2021-12-30 through 2023-01-02 overlap buffer;
- exact overlap with the existing governed archive: **84 / 84 OHLC rows exact, 0 mismatches**;
- V3 exact target, V4 venue/calendar and V5 internal-path rules were replicated for 2022;
- 2022 final warm-up rows per head range from **197 to 255**;
- official SGE 2022 holiday schedule and GOV.UK England/Wales 2022 bank holidays are the calendar authorities;
- Databento GC n/v hourly activity remains the US venue-state authority.

Fresh S1.4 construction:
- fresh A1 regenerated in-process from pinned raw daily Gold/Silver/Platinum CORE3;
- A1 recent expert = **252 matured same-window rows**;
- no archived A1/IRIS prediction file is consumed;
- canonical STRUCTURAL_IRIS = **A1 structural logit + same-source-derived 1h XAU full IRIS PATH**;
- 15m full-PATH and 15m nested-selection variants are development challengers;
- XAU 1h is deterministically aggregated from the same governed XAU15 archive;
- downstream Structural-IRIS requires **80 matured A1-feature rows**;
- all variable selection in nested variants is training-only inside the outer causal replay.

Coverage after warm-up:
- Sobti Asia Afternoon: **N=190** scored;
- Sobti Asia Morning: **N=183**;
- Sobti Europe: **N=213**;
- Sobti NY/London: **N=215**;
- Sobti Late-US: **N=89**;
- WGC Asia: **N=102**;
- WGC Europe: **N=210**;
- WGC US: **N=177**.

Combined 2023–2024 matched Balanced Accuracy:

| Window | A1 direct | A1+1h full | A1+15m full | A1+15m select | A1+15m select-balanced |
|---|---:|---:|---:|---:|---:|
| Sobti Asia Afternoon | 46.25% | **51.02%** | 48.54% | 46.77% | 50.09% |
| Sobti Asia Morning | 45.36% | 49.91% | 53.57% | **54.98%** | 53.22% |
| Sobti Europe | **50.07%** | 48.17% | 41.42% | 46.92% | 42.31% |
| Sobti NY/London | 48.54% | **53.26%** | 45.84% | 51.51% | 48.09% |
| Sobti Late-US | **54.22%** | 50.05% | 48.50% | 44.46% | 49.06% |
| WGC Asia | 38.93% | 47.36% | 53.49% | 47.30% | **54.22%** |
| WGC Europe | 52.22% | 52.28% | 47.81% | **54.62%*** | 50.01% |
| WGC US | 43.82% | 50.28% | 49.15% | 46.93% | **50.73%** |

* WGC Europe unbalanced selector fails the 30% minimum-class-recall floor because DOWN recall is only about 22.47%; it is therefore **not admissible** under the frozen selection safety rule.

Year-stability interpretation:
- **Sobti Asia Morning** is the clearest 15m Structural-IRIS opportunity: 15m nested selection is strong in 2023 and remains directionally positive in 2024, though magnitude drops;
- **Sobti NY/London** favors canonical 1h Structural-IRIS in 2024 but 2023 is weak, so transport confidence is still limited;
- **Sobti Asia Afternoon** favors canonical 1h on combined data, but the gain is concentrated in 2024 and reverses in 2023;
- **Sobti Europe** and **Sobti Late-US** show no case for adding PATH to A1; A1 direct is retained as the safer development reference;
- **WGC Asia** has adequate combined N only because 2024 dominates; 2023 N=11 is too small for year-stability inference;
- **WGC Europe** does not support the unbalanced selector after class-recall governance; A1 direct / canonical 1h remain effectively tied on combined BA, with A1 materially better calibrated;
- **WGC US** gains directionally from PATH, but the balanced 15m selector is only about 50.73% BA combined and does not yet establish a robust edge.

Binding S1.4 verdict:
- STRUCTURAL_IRIS is **not** promoted as one universal all-session replacement for A1;
- its value is **window-specific**;
- canonical 1h A1+PATH remains a viable primary challenger for Sobti NY/London and selected US/Asia heads;
- 15m nested PATH remains a viable challenger principally for Sobti Asia Morning and WGC Asia, subject to independent transport;
- Sobti Europe and Late-US should retain structural-only A1 as the development reference unless a later SAGE head proves otherwise;
- cross-metal intraday SI/PL remain **not promoted**.

Stage-1 status after S1.4:
- [x] S1.1 NOVA A0 / CORE3
- [x] S1.2 NOVA A1 / ARCR
- [x] S1.3 IRIS HOURLY_ONLY_ALL / PATH_GLOBAL
- [x] S1.4 IRIS A1_PLUS_PATH / STRUCTURAL_IRIS
- [ ] S1.5 SAGE SESSION_ONLY — **NEXT**
- [ ] S1.6 SAGE PATH_SESSION
- [ ] S1.7 SAGE A1_SESSION
- [ ] S1.8 SAGE A1_PATH_SESSION

Transport gate:
- **do not open 2025 yet**;
- complete S1.5–S1.8 under the same 2022-warm-up / 2023–2024-development chronology;
- only after Stage-1 representation/head choice is frozen may 2025 be opened once for transport.



### 5E.8U SAGE Stage-1 closure — 2026-10-07

Authorities: `GOLD_SESSION_SAGE_V1_PREREG_2026-10-07.md`, `GOLD_SESSION_SAGE_V2_STAGE1_CORRECTED_SUMMARY_2026-10-07.json`, and `GOLD_SESSION_2022_WARMUP_EQUIVALENCE_SUMMARY_2026-10-07.json`.

Status:
- [x] S1.5 SAGE SESSION_ONLY
- [x] S1.6 SAGE PATH_SESSION
- [x] S1.7 SAGE A1_SESSION
- [x] S1.8 SAGE A1_PATH_SESSION
- 2022 warm-up only; 2023–2024 scored; **2025/2026 unopened**.

Warm-up equivalence audit: 2,080/2,080 target keys matched; 0 mismatches in start/end timestamps, start/end prices, return, direction or `final_trainable`; 1,912/1,912 final-trainable keys identical. On 23,727 common XAU15 timestamps, open/high/low/close mismatches were all zero. Existing SAGE V2 corrected results therefore use a warm-up authority equivalent to the independently rebuilt V3/V4/V5 authority.

Preregistered transport eligibility:
- S1.5: **WGC Asia SESSION_ONLY PASS**; all other heads fail.
- S1.6: **Sobti NY/London PATH_SESSION PASS** and **WGC US PATH_SESSION PASS**; all other heads fail.
- S1.7: no head passes.
- S1.8: no head passes.

Key combined metrics: WGC Asia SESSION_ONLY N=152, BA 56.21%, Brier 0.2497. Sobti NY/London PATH_SESSION N=297, BA 52.21% versus matched PATH_GLOBAL 48.25%. WGC US PATH_SESSION N=264, BA 47.46% versus matched PATH_GLOBAL 45.75%.

All eight Stage-1 model families are now complete. **2025 remains closed until an explicit Stage-1 development-freeze artifact defines the allowed transport candidates.**


### 5E.8V Stage-1 development freeze — 2026-10-07

Authority: `GOLD_SESSION_STAGE1_DEVELOPMENT_FREEZE_2026-10-07.json`.

All eight Stage-1 model families are complete and the pre-2025 candidate set is frozen. Global controls are A0 CORE3, A1 ARCR, 1h PATH_GLOBAL and canonical A1+1h STRUCTURAL_IRIS. Window-specific frozen additions are Sobti Asia Morning 15m Structural-IRIS, WGC Asia 15m Structural-IRIS challenger, WGC Asia S1.5 SESSION_ONLY, Sobti NY/London S1.6 PATH_SESSION and WGC US S1.6 PATH_SESSION. S1.7 and S1.8 are rejected before transport; intraday SI/PL remain unpromoted.

From this point, the one-time 2025 transport test may evaluate only the frozen candidates. Clocks, features, lag horizons, model forms, regularization and the 0.5 decision threshold may not be changed using 2025 outcomes.


### 5E.8W Frozen 2025 Stage-1 transport — FINAL CORRECTED AUTHORITY — 2026-10-07

Authority: `GOLD_SESSION_STAGE1_2025_TRANSPORT_AUTHORITY_2026-10-07.json`.

The earlier `GOLD_SESSION_STAGE1_2025_TRANSPORT_DECISION_2026-10-07.json` and restarted-block intermediate control summaries are **superseded / non-authoritative**. The corrected transport preserves the original 5-row replay block phase continuously through 2023→2024→2025, reports only 2025 rows, and does not retune clocks, features, lags, regularization or the 0.5 threshold.

Identity audit:
- A1: **1,061 matched rows**, max probability difference **2.7e-13**;
- PATH_GLOBAL: **284 matched rows**, max probability difference **0**.
Thus the corrected independent transport implementations are identity-consistent.

Matched 2025 frozen-candidate decisions on exact common rows, with the frozen **30% minimum class-recall floor**:
- Sobti Asia Afternoon: **A0 CORE3**, BA **64.19%**;
- Sobti Asia Morning: **A1 + 1h Structural-IRIS**, BA **60.86%**;
- Sobti Europe: **PATH_GLOBAL 1h**, BA **51.12%**;
- Sobti NY/London: **A0 CORE3**, BA **53.88%**;
- Sobti Late-US: **no admissible model**;
- WGC Asia: **PATH_GLOBAL 1h**, BA **58.58%**;
- WGC Europe: **PATH_GLOBAL 1h**, BA **51.59%**;
- WGC US: best frozen candidate is PATH_GLOBAL 1h at **49.38% BA**, therefore **not promoted**.

SAGE does not earn a 2025 transport promotion:
- WGC Asia S1.5 SESSION_ONLY: BA about **48.06%**;
- Sobti NY/London S1.6 PATH_SESSION: BA about **45.94%**;
- WGC US S1.6 PATH_SESSION: BA about **46.69%**.

Critical coverage guardrail:
- matched-candidate common-row coverage is only about **41%–59%** depending on the head;
- therefore these winners are transport winners only on the exact common frozen-candidate rows;
- **no new fallback/router is created for non-common rows at Stage 1**.

Binding conclusion:
- Stage 1 does **not** support one universal session model;
- heterogeneous single-model experts are retained;
- 2025 may select among the already frozen candidates but may not alter their specification;
- 2026 remains unopened for this session project;
- the next dependency is **Stage 2 specialist correction/reversal layers**, after which Stage 3 router/combiner and final consensus may be evaluated.


### 5E.8X Sobti Late-US label-integrity authority — 2026-10-07

Authority: `GOLD_SOBTI_LATE_US_LABEL_AUDIT_SUMMARY_2026-10-07.json`.

Status: **PASS**.

The Sobti Late-US target chain was independently rebuilt from the governed raw XAU/USD 15m archive and compared row-by-row against the frozen V5 target table. The binding label is **14:30 America/New_York exact OPEN → CLOSE of the exact 20:45 New York 15m bar ending at 21:00**. Friday rows are ineligible; the only registered internal-gap exception is the known **17:00–18:00 New York maintenance** interval.

Audit results across 2023–2025:
- target rows checked: **783**; 2025 target rows: **261**;
- final-trainable rows: **589**; 2025 final-trainable rows: **195**;
- start/end clock mismatches: **0**;
- start-price mismatches versus raw exact OPEN: **0**;
- end-price mismatches versus raw exact final-bar CLOSE: **0**;
- return mismatches: **0**;
- UP/DOWN direction mismatches: **0**;
- Friday-exclusion mismatches: **0**;
- internal-path / maintenance-gate mismatches: **0**;
- final-trainable mismatches: **0**.

DST was verified explicitly: winter 14:30 NY maps to 19:30 UTC and 21:00 NY maps to 02:00 UTC next day; summer 14:30 NY maps to 18:30 UTC and 21:00 NY maps to 01:00 UTC next day.

Prediction-label binding also passes: global-control predictions **497/497** and S1.4 predictions **321/321** match the audited target key and `y_up` label exactly, with **0 bad rows**.

Therefore Sobti Late-US Stage-1 failure is **not attributed to target-label corruption, DST conversion, boundary pricing, Friday handling, or the maintenance-gap rule**. The remaining issue is model/representation adequacy for this window.


### 5E.8Y Stage-2 RIFT V1 development checkpoint — 2026-10-07

Authorities:
- `GOLD_SESSION_RIFT_V1_PREREG_2026-10-07.md`
- `GOLD_SESSION_RIFT_V1_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_RIFT_V1_RESULT_2026-10-07.md`
- `GOLD_SESSION_RIFT_V1_TRANSPORT_ELIGIBILITY_2026-10-07.csv`

Status: **RIFT V1 DEVELOPMENT COMPLETE**.

RIFT is a specialist reversal layer, not a new primary session engine. It predicts reversal relative to pre-target 12h XAU momentum using the fixed nine-feature exact-clock XAU15 representation and the preregistered `p_reversal >= 0.70` override threshold. 2022 is warm-up; 2023-2024 are development; no 2025 outcome was used to fit or select RIFT.

Only one session survives the full preregistered development gate:

- **Sobti Asia Afternoon** — PASS against all four audited upstream baselines: A0 CORE3, A1 ARCR, PATH_GLOBAL 1h and canonical A1+1h STRUCTURAL_IRIS.

Combined 2023-2024 examples:
- A0: BA **46.03% -> 47.51%**, Brier **0.2677 -> 0.2650**, 4 rescues / 1 break, net +3.
- A1: BA **46.25% -> 47.89%**, Brier **0.2595 -> 0.2564**, 4 rescues / 1 break, net +3.
- PATH_GLOBAL: BA **45.79% -> 47.99%**, Brier **0.2820 -> 0.2754**, 4 rescues / 0 breaks, net +4.
- STRUCTURAL_IRIS: BA **51.02% -> 51.59%**, Brier **0.2908 -> 0.2891**, 2 rescues / 1 break, net +1.

Sobti Late-US shows an interesting aggregate rescue signal against A0 (BA 51.59% -> 53.38%, net +2), but **fails the binding gate** because 2024 is harmful and corrected DOWN recall remains below the 30% floor. It is therefore not transport-eligible.

All other window/baseline pairs fail closed. RIFT V1 may proceed to 2025 transport **only for Sobti Asia Afternoon**, with the representation and threshold frozen exactly as preregistered.


### 5E.8Z Stage-2 VEGA V1 development checkpoint — 2026-10-07

Authorities:
- `GOLD_SESSION_VEGA_V1_PREREG_2026-10-07.md`
- `GOLD_SESSION_VEGA_V1_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_VEGA_V1_RESULT_2026-10-07.md`
- `GOLD_SESSION_VEGA_V1_TRANSPORT_ELIGIBILITY_2026-10-07.csv`

Status: **VEGA V1 DEVELOPMENT COMPLETE**.

VEGA is a GVZ/options-implied-volatility reversal specialist. It uses only governed official Cboe GVZ observations dated **D-1 calendar day or earlier** relative to the actual New York session-origin date, plus maintenance-aware exact-clock XAU15 volatility/momentum state. Threshold `p_reversal >= 0.70` is frozen; no feature or threshold search was performed. 2022 is warm-up; 2023-2024 are development; no 2025 outcome was used for VEGA fitting or gate selection.

Only one window/baseline pair survives the full preregistered development gate:
- **WGC US / PATH_GLOBAL 1h — PASS**.

Combined 2023-2024 on that pair:
- PATH_GLOBAL BA **46.28% -> 46.88%**;
- Brier **0.2816 -> 0.2798**;
- 1 override, 1 rescue, 0 breaks, net +1.

All other VEGA window/baseline pairs fail closed. In particular, VEGA produces no stable broad session advantage and is not promoted as a universal correction layer.

VEGA V1 may proceed to 2025 transport **only for WGC US correcting PATH_GLOBAL 1h**, with the D-1 GVZ rule, feature set, model and 0.70 threshold frozen exactly as preregistered.


## 5E.9 Research hypotheses — not conclusions

H1. Europe and New York/London overlap contain different information sets and should not share one unconditional execution rule.

H2. The New York/London overlap may be the highest-information zone, but a meaningful part of the daily move can occur before it; therefore a late issuance can be directionally correct while economically late.

H3. Asia may contribute more through inventory/demand and overnight repricing than through the same information channel that dominates New York.

H4. Benchmark and macro-announcement windows may explain apparent clock-time effects.

H5. The optimal design may be **one shared global state/core + a data-selected set of session forecast heads + session-specific execution logic**. The number of retained heads is not fixed ex ante.

H6. The two Asia windows may be mergeable, but this must be demonstrated rather than assumed.

H7. An expert that is useful for one session target may be neutral or harmful for another; session consensus membership must therefore be selected per window rather than copied wholesale.

All seven hypotheses require project-specific validation.

## 5E.10 Governance of prior timing experiments

All execution-window results produced before this authority section — including retrospective “best hour” scans — are classified:

**DIAGNOSTIC / NON-BINDING**

They may be used to generate hypotheses only.

No prior +return number may be reported as an expected investment return until:
- source-ready timing is proven,
- the same clock rule is frozen,
- 2026 transport is reported,
- costs/slippage/instrument availability are added.

## 5E.11 External authority register

Primary sources:
- World Gold Council — Global Gold Market / Market Structure: https://www.gold.org/gold-market-structure/global-gold-market
- World Gold Council — Wholesale OTC vs Exchange: https://www.gold.org/about-us/what-we-do/market-infrastructure/gold-trading-wholesale-market
- LBMA — Loco London: https://www.lbma.org.uk/market-standards/about-loco-london
- LBMA — Daily Auction Prices: https://www.lbma.org.uk/prices-and-data/about-lbma-daily-auction-prices
- LBMA — Gold Price / direct participants: https://www.lbma.org.uk/prices-and-data/lbma-gold-price
- CME Group — Gold futures: https://www.cmegroup.com/markets/metals/precious/gold-futures.html
- Shanghai Gold Exchange — Trading Hours: https://en.sge.com.cn/h5_trading_ProductsIntroduce
- iShares Gold Trust — institutional product / LBMA benchmark reference: https://www.ishares.com/us/products/239561/ishares-gold-trust

Academic sources:
- Sobti, N., Sehgal, S., Ilango, B. (2021), *International Review of Financial Analysis* 78, 101893. DOI: 10.1016/j.irfa.2021.101893
- Hauptfleisch, M., Putniņš, T. J., Lucey, B. (2016), *Journal of Futures Markets* 36, 564–586. DOI: 10.1002/fut.21775
- Iwatsubo, K., Watkins, C., Xu, T. (2018), *Journal of Commodity Markets* 11, 59–71. DOI: 10.1016/j.jcomm.2018.05.001
- Elder, J., Miao, H., Ramchander, S. (2012), *Journal of Banking & Finance* 36, 51–65. DOI: 10.1016/j.jbankfin.2011.06.007


## 5E.10A Binding Model Clock Identity — 2026-10-06

Authority:
- `GOLD_MODEL_CLOCK_IDENTITY_2026-10-06.md`

The current legacy H3/CIG-D1 stack is a **mixed-clock architecture**:

- governed historical daily Gold realization/target source = **pinned StakTrakr calendar-date Gold reference**; its exact intraday fixing/observation clock is not established by the stored timestamp;
- hourly intraday feature clock = **America/New_York**, anchored at 16:00 NY;
- legacy CIG-D1 forecast issue/deadline clock = **America/New_York**, 08:00 NY;
- historical CIG-D1 label = direction derived from the pinned Stak daily date-labelled reference values;
- `Europe/Istanbul` = reporting/execution conversion only; it is not currently a legacy model target, feature, or issue clock.

Therefore:
- the legacy model is **not a Turkey-clock model**;
- the historical CIG-D1 label is **not a New York-session label, UTC close-to-close label, or proven full-UTC-day-average label**;
- no intraday target window may be inferred from the Stak date label;
- session-model research must construct new timestamped target labels directly from governed intraday data.

This source/clock identity is binding and supersedes earlier wording that called the Stak daily reference a normal close or a proven UTC-calendar-day/full-UTC-day average.

## 5E.11A Forecast Clock / Target Window Correction — 2026-10-06

Authoritative audit:
- `GOLD_FORECAST_CLOCK_TARGET_AUDIT_2026-10-06.md`

Binding correction:
- H3 `target_r3` begins from the governed daily reference on the **feature_cutoff_date**, not from the 08:00 New York forecast issue timestamp.
- CIG-D1 historical "same-day" label also begins from a previous daily reference and therefore includes movement that can occur before the 08:00 issue time.
- Existing H3/CIG model scores remain label-space research scores.
- They must not be described as post-signal executable direction/return until separately re-scored from the actual issue timestamp.
- Original CIG accuracy is henceforth called **historical label accuracy** until post-08:00 reconciliation is complete.

## 5E.11B Clock Reconciliation Result — 2026-10-06

Authoritative correction:
- `GOLD_D1_FORECAST_CLOCK_RECONCILIATION_2026-10-06.md`
- `GOLD_FORECAST_CLOCK_RECONCILIATION_2026-10-06.json`

**Binding timing facts**
- H3 hourly feature anchor: 16:00 New York on feature-cutoff date.
- The pinned Stak daily realization has **no proven intraday fixing/completion clock**; the synthetic noon timestamp is only a calendar-date label.
- Any earlier statement that a “full-UTC-day daily reference completes at 03:00 Istanbul” is **superseded** and must not be used as a readiness fact.
- Legacy CIG-D1 governed issue deadline: 08:00 New York = approximately 15:00 Istanbul in New York daylight time / 16:00 Istanbul in New York standard time.
- Historical retrospective rows have no actual `issued_at_utc`; therefore exact historical production time is unknown.
- Legacy CIG-D1 execution claims must use 08:00 New York unless an earlier all-source-ready timestamp is separately proven.
- Future session heads require their **own** source-ready/issue clocks, fixed before their target windows begin.

**New diagnostic**
On the reconstructed raw 4/4 execution panel, signal direction versus the clean 08:00->20:00 New York interval is:
- 2025 H2: **50.45%** (N=111)
- 2026 Jan-Jul: **51.15%** (N=131)
- 2026 Aug-Sep: **42.31%** (N=26).

This does **not** directly replace the canonical 2026 Jan-Jul CIG figure of 93/125 = 74.40%, because the timing reconstruction contains 131 consensus rows while the canonical CIG evaluation contains 125. The populations are not identical.

**Do-not-mix rule**
- 74.40% = historical **daily-label accuracy** on the canonical 125 CIG rows.
- 08:00->20:00 figures = **post-governed-issue clock diagnostics** on the reconstructed execution population.
- Neither may be relabeled as the other.
- Exact apples-to-apples publication is blocked until the canonical 145/125 row-level CIG universe is reproduced and joined to the 15-minute clock.

**Superseded wording**
It is prohibited to say that CIG-D1 is "74.4% accurate after 08:00 New York" or that the historical daily realized move is fully tradable after the signal.

## 5E.11C Exact Canonical 145/125 Recovery and Post-Issue Rescore — 2026-10-06

Authority:
- `GOLD_CIG_EXACT_125_CLOCK_RESCORE_RESULT_2026-10-06.md`
- `GOLD_CIG_EXACT_125_RESCORE_2026-10-06.json`
- `GOLD_CIG_EXACT_125_ROWS_2026-10-06.csv`
- recovered realization ledger: `GOLD_DAILY_H1_V2_2026_GERCEKLESEN_TAHMIN_RECOVERED_2026-10-06.csv`

### Canonical population recovered

The exact old Jan-Jul 2026 daily realization snapshot was recovered from the prior project artifact.

It contains **145 rows**. The six dates absent from that frozen snapshot are:
- 2026-02-27
- 2026-03-02
- 2026-03-03
- 2026-03-04
- 2026-03-05
- 2026-03-06.

These six missing rows are a **snapshot coverage gap**, not a market-session rule and not a timezone rule.

Pinned expert states reproduce the published result exactly:
- SAGE+RuleFlow: 103/145
- V5: 102/145
- RIFT: 102/145
- VEGA: 102/145
- 4/4 consensus: **125**
- consensus correct: **93**
- historical label accuracy: **74.40%**
- disagreement: 20, of which SAGE forced direction is correct on 10.

**Canonical reconstruction gate: PASS.**

### Exact same-125 post-issue rescore

Using the identical 125 consensus rows and the first strictly post-deadline 15-minute bar at **08:15 New York**:

| Executable clock window | Correct | Accuracy |
|---|---:|---:|
| 08:15 -> 16:00 NY | 59/125 | **47.20%** |
| 08:15 -> 20:00 NY | 59/125 | **47.20%** |
| 17:00 -> 20:00 NY | 63/125 | **50.40%** |

Signal-side detail:
- UP, 08:15->16:00: 34/71 = **47.89%**
- UP, 08:15->20:00: 34/71 = **47.89%**
- UP, 17:00->20:00: 35/71 = **49.30%**
- DOWN, 08:15->16:00: 25/54 = **46.30%**
- DOWN, 08:15->20:00: 25/54 = **46.30%**
- DOWN, 17:00->20:00: 28/54 = **51.85%**.

### Binding interpretation

The original **74.40%** result is valid **for the recovered historical daily-reference label**.

It is **not** a post-08:00-New-York trading accuracy.

On the exact same 125 signal rows, the post-issue direction is approximately chance under the tested windows.

Therefore:
- CIG-D1 V1 remains a valid selective historical daily-label classifier;
- CIG-D1 V1 is **not established as an 08:00-NY-forward tradable D1 direction model**;
- execution timing optimisation cannot be used to reinterpret 74.40% as tradable post-signal accuracy.

### Supersession

The earlier 151-row / 131-consensus timing reconstruction remains diagnostic only.

For the canonical 2026 Jan-Jul CIG claim, it is superseded by the exact-125 rescore above.

In particular, the earlier late-US UP plateau must not be reported as canonical 2026 CIG evidence. On the exact 71 canonical UP rows, 17:00->20:00 NY direction hit is **49.30%**.

### Clock identity retained

- historical daily realization = date-labelled daily reference; not an executable intraday print;
- hourly feature clock = America/New_York, 16:00 anchor;
- governed issue deadline = America/New_York 08:00;
- Istanbul = user-facing execution conversion only.

The investment problem therefore requires a **new post-issuance target identity** if the objective is to trade after the morning signal.

## 5E.11C Exact Canonical 125 Clock Reconciliation — 2026-10-06

Authoritative artifacts:
- `GOLD_CIG_EXACT_125_CLOCK_RESCORE_RESULT_2026-10-06.md`
- `GOLD_CIG_EXACT_125_RESCORE_2026-10-06.json`
- `GOLD_CIG_EXACT_125_ROWS_2026-10-06.csv`

**Canonical sample recovered and exactly reproduced.**

Recovered historical daily-realization source:
`GOLD_DAILY_H1_V2_2026_GERCEKLESEN_TAHMIN_RECOVERED_2026-10-06.csv`

The exact published 2026 Jan-Jul CIG-D1 counts were reproduced:
- daily universe: **145**
- SAGE+RuleFlow correct: **103/145**
- V5 correct: **102/145**
- RIFT correct: **102/145**
- VEGA correct: **102/145**
- 4/4 consensus: **125**
- consensus correct: **93**
- canonical label accuracy: **74.40%**
- disagreement: **20**
- disagreement correct: **10**

The six dates missing from the old 145-row snapshot are:
- 2026-02-27
- 2026-03-02
- 2026-03-03
- 2026-03-04
- 2026-03-05
- 2026-03-06

This is a historical snapshot coverage gap, **not** a market-session/holiday definition.

### Exact same-125 post-issue result

Using the identical 125 consensus rows and XAU/USD 15-minute prices, with the first strictly post-deadline bar at **08:15 New York**:

- 08:15 -> 16:00 NY: **59/125 = 47.20%**
- 08:15 -> 20:00 NY: **59/125 = 47.20%**
- 17:00 -> 20:00 NY: **63/125 = 50.40%**

UP-only on the exact 71 canonical UP rows:
- 08:15 -> 16:00 NY: **34/71 = 47.89%**
- 08:15 -> 20:00 NY: **34/71 = 47.89%**
- 17:00 -> 20:00 NY: **35/71 = 49.30%**

DOWN-only on the exact 54 canonical DOWN rows:
- 08:15 -> 16:00 NY: **25/54 = 46.30%**
- 08:15 -> 20:00 NY: **25/54 = 46.30%**
- 17:00 -> 20:00 NY: **28/54 = 51.85%**

### Binding interpretation

The **74.40%** figure is genuine and exactly reproducible for the recovered historical **daily-reference label**.

It is **not** an 08:00-NY-forward tradable same-day accuracy.

On the same exact 125 rows, post-issue direction is approximately chance under the tested fixed endpoints.

Therefore prior 151/131-row timing diagnostics are superseded for any claim about the canonical 2026 Jan-Jul CIG population.

In particular, the previously reported late-US UP timing plateau is **not canonical CIG evidence**. On the exact 71 canonical UP rows, 17:00 -> 20:00 NY direction hit is only **49.30%**.

**Do-not-mix rule:**
- 74.40% = canonical historical daily-label accuracy.
- 47.20% = exact-canonical 08:15-NY-forward direction accuracy for the tested same-day endpoints.
- 50.40% = exact-canonical 17:00->20:00 NY direction accuracy.
- tradable D1 accuracy from CIG-D1 V1 = **not established**.

If the operational objective is a signal available around 08:00 NY, a new execution-aware target must be defined from a post-issue price to a frozen future endpoint. CIG-D1 V1 must not be silently relabelled.

## 5E.11D Exact-125 Reference-Clock Audit — 2026-10-06

Authority:
- `GOLD_CIG_EXACT125_REFERENCE_CLOCK_AUDIT_2026-10-06.json`
- `GOLD_CIG_EXACT125_REFERENCE_CLOCK_ROWS_2026-10-06.csv`

This audit tests whether the canonical 74.40% CIG-D1 result can be interpreted as skill over any simple point-to-point clock interval.

Exact same 125 consensus rows:

| Window | Direction accuracy |
|---|---:|
| feature-cutoff 16:00 NY -> current UTC 00:00 | **49.60%** |
| current UTC 00:00 -> issue 08:00 NY | **45.60%** |
| current UTC 00:00 -> first post 08:15 NY | **46.40%** |
| feature-cutoff 16:00 NY -> issue 08:00 NY | **47.20%** |
| feature-cutoff 16:00 NY -> first post 08:15 NY | **50.40%** |
| post-issue 08:15 -> 20:00 NY | **47.20%** |

Daily-reference semantic cross-check:
- old Stak-derived daily label versus Twelve Data UTC-calendar-day hourly-mean direction: **88.0% agreement**
- CIG signal versus the Twelve UTC-day-mean direction: **67.2% accuracy**.

**Binding interpretation**

The canonical **74.40%** cannot be assigned to a simple clock return such as 16:00 NY->08:00 NY, 00:00 UTC->08:00 NY, or 08:15 NY->20:00 NY.

It belongs to the provider-specific **daily-average/reference label**.

Therefore the previously suggested explanation that CIG's directional edge is concentrated specifically in the 03:00 Istanbul -> 15:00/16:00 Istanbul pre-issue interval is **not supported and is superseded**.

The correct conclusion is narrower:
- the old daily label has a UTC-calendar-day average/reference semantic;
- it is not an executable point-price interval;
- none of the tested simple pre-issue or post-issue point-to-point windows reproduces the 74.40% signal accuracy.

## 5E.12 Fifteen-Minute CIG Execution Timing Transport — 2026-10-06

**SUPERSESSION NOTICE:** the exact canonical 125-row Jan-Jul CIG ledger has now been recovered in Section 5E.11C. Therefore this subsection's 151/131 reconstructed-population timing results are **legacy diagnostics only** and are superseded for canonical 2026 Jan-Jul CIG interpretation.

**Population warning:** this subsection uses the reconstructed raw execution panel rather than the exact canonical 125-row Jan-Jul CIG ledger. Do not cite its 2026 Jan-Jul timing statistics as canonical CIG evidence.

**Status:** SUPERSEDED RECONSTRUCTED-POPULATION DIAGNOSTIC — NOT PROSPECTIVE  
**Signal:** raw CIG-D1 4/4 consensus only  
**Execution clock:** no price before 08:00 America/New_York is permitted in executable timing tests.

Authoritative artifacts:
- \`GOLD_EXECUTION_15M_TIMING_TRANSPORT_2026-10-06.json\`
- \`GOLD_EXECUTION_15M_UP_WINDOW_DEV_ROBUST_TOP_2026-10-06.csv\`
- \`GOLD_EXECUTION_15M_DOWN_EXIT_DEV_ROBUST_TOP_2026-10-06.csv\`
- \`GOLD_EXECUTION_15M_FORWARD_CLOCK_MAP_2026-10-06.csv\`

Protocol:
- 2025 H2 = timing-development period;
- 2026 Jan-Jul and 2026 Aug-Sep = unchanged transport diagnostics;
- candidate UP windows require >=60 minutes holding time;
- selection must survive ±30-minute entry/exit perturbations;
- exact-bar winners are not accepted.

### UP timing result

The highest robustness score on 2025 H2 selected:
- entry **17:15 New York**
- exit **20:00 New York**
- holding time **165 minutes**.

Performance:
- 2025 H2: n=72, compound **+7.36%**, hit **61.1%**
- 2026 Jan-Jul: n=73, compound **+4.70%**, hit **56.2%**
- 2026 Aug-Sep: n=18, compound **+1.69%**, hit **66.7%**

Robustness:
- 15 neighboring ±30-minute variants evaluated
- all 15 positive on 2025 H2
- worst neighboring 2025 H2 compound result: **+7.09%**
- median neighboring result: **+8.49%**.

Important interpretation:
the evidence supports a **late-US execution plateau**, not one magic 17:15 bar. Neighboring entries from roughly **16:00–17:30 New York**, with exits around **19:45–20:00**, remain broadly positive across 2025 development and both 2026 transport windows.

Representative fixed windows:
- 16:00→20:00 NY: 2025 +7.60%, 2026 Jan-Jul +4.77%, Aug-Sep +0.59%
- 16:15→20:00 NY: 2025 +7.62%, 2026 Jan-Jul +5.08%, Aug-Sep +0.99%
- 16:45→20:00 NY: 2025 +7.22%, 2026 Jan-Jul +4.81%, Aug-Sep +1.97%
- 17:00→20:00 NY: 2025 +8.34%, 2026 Jan-Jul +3.84%, Aug-Sep +1.76%
- 17:15→20:00 NY: 2025 +7.36%, 2026 Jan-Jul +4.70%, Aug-Sep +1.69%
- 17:30→20:00 NY: 2025 +7.44%, 2026 Jan-Jul +4.59%, Aug-Sep +1.69%.

Thus the canonical research object is a **time plateau**, not an exact timestamp.

### UP path structure after issuance

On 2025 H2, the strongest positive one-hour block after the 08:00 issue time is:
- **18:30→19:30 New York**
- compound +4.69%
- hit 65.3%.

Unchanged transport:
- 2026 Jan-Jul: +2.01%
- 2026 Aug-Sep: +0.60%.

The strongest 2025 negative/giveback one-hour block is:
- **09:30→10:30 New York**
- 2025 H2: -3.79%
- 2026 Jan-Jul: -2.10%
- 2026 Aug-Sep: **+1.98%**.

Interpretation:
- early-overlap giveback is not regime-stable through Aug-Sep 2026;
- late-US positive acceleration is more stable across the three reported periods;
- the robust UP execution hypothesis is therefore **late-US continuation**, not “buy immediately at 08:00” and not “always wait for an early-overlap pullback”.

### DOWN timing result

A 2025-only robust search selected 15:45 New York as the best delayed exit relative to holding to 20:00:
- 2025 H2 avoided-return compound: **+2.13%**
- 2026 Jan-Jul transport: **-3.22%**
- 2026 Aug-Sep transport: **-0.30%**.

Therefore the delayed DOWN exit **fails transport**.

The strongest 2025 DOWN one-hour decline was:
- 16:30→17:30 New York
- 2025 H2: -3.71%
- 2026 Jan-Jul: -2.21%
- 2026 Aug-Sep: +0.54%.

This also fails the Aug-Sep regime.

**Binding interpretation:** no fixed delayed sell hour is supported for DOWN. Do not promote 15:45, 16:00 or 16:30 New York as a production exit rule.

### Istanbul clock interpretation

Because Türkiye does not change daylight-saving time while New York does, the late-US plateau maps to two Istanbul clocks depending on date.

Approximate mapping:
- entry plateau 16:00–17:30 NY -> roughly **23:00–01:30 Istanbul** depending on US DST
- exit plateau 19:45–20:00 NY -> roughly **02:45–04:00 Istanbul** depending on US DST.

All production reporting must use date-aware timezone conversion, never a fixed +7/+8 assumption.

### Historical interpretation of this superseded scan

Within this reconstructed 151/131 panel, a late-US continuation plateau appeared in the UP subset and DOWN timing remained unstable.

**This is no longer the canonical 2026 Jan-Jul conclusion.** The exact-125 audit in Section 5E.11C gives only **35/71 = 49.30%** UP direction hit for 17:00->20:00 New York. Therefore no late-US UP plateau is currently accepted as canonical CIG execution evidence.

Europe/Türkiye daytime movement remains attribution only for the current 08:00-NY issue identity.

No result in this subsection is prospective evidence or net investment return. Costs, spread, slippage, swap and instrument basis remain excluded.


**Next authorized action from this section:** complete the remaining Tier-A data acquisition/normalization matrix first; then perform the source-ready timestamp audit and build the session-attribution panel. No further entry-hour optimisation before those gates pass.


# 6. Evaluation Contract

## 6.1 Event prediction

Primary event-probability metrics:
- Brier score
- log loss
- precision
- recall / opportunity capture
- false-opportunity rate
- PR-AUC where sample size supports it.

## 6.2 Continuous path prediction

For MFE_5 / MAE_5:
- MAE
- RMSE
- calibration by prediction bucket
- worst underprediction / overprediction.

## 6.3 Business diagnostics

Especially inside monthly-DOWN months:
- realized upside captured after positive opportunity signals
- missed large upside events
- downside experienced after positive signals
- opportunity frequency
- stability by regime/month.

Trading P&L is not a primary metric until a separate entry/exit/cost contract is frozen.

---

# 7. Prior Daily Evidence

## 7.1 Daily V1

Status:
**INVALID / SUPERSEDED**

Reason:
- feature-contract substitution
- PIT provenance not proven.

## 7.2 Daily V2

Status:
**VALID RETROSPECTIVE PRICE-TRANSFER AUDIT / NOT OPPORTUNITY MODEL**

2026 Jan-Jul:
- RW MAE ≈61.59 USD
- monthly-family transfers did not beat persistence on next-day point-price MAE
- predictions strongly shrank toward zero.

Interpretation:
- direct monthly-family transfer is not the answer;
- V2 does not test MFE/MAE opportunity targets and is therefore not a duplicate of the new project.

---

# 8. Stage Roadmap

| Stage | Purpose | Status |
|---|---|---|
| 0 | Daily scientific contract | COMPLETE |
| 0A | Intramonth opportunity objective | **COMPLETE / FROZEN** |
| 1 | Daily Data Authority & PIT Audit | **COMPLETE / PASS** |
| 2 | Opportunity labels + baselines + core feature contract | **COMPLETE / PASS** |
| 3 | Origin-safe opportunity predictability screen | **COMPLETE / PASS** |
| 4 | Monthly-context incremental test | **COMPLETE / NO_CONTEXT_PASS** |
| 5 | K100 robustness / calibration / decision threshold | **COMPLETE / PASS** |
| 6 | Frozen 2025 transport | **NEXT** |
| 7 | Prospective opportunity ledger | BLOCKED BY TRANSPORT |
| 7 | Prospective opportunity ledger | NOT STARTED |

---

# 9. Exact Next Action

**Stage 6 — Frozen 2025 Transport**

Frozen without modification:
- K100 target
- G_ONLY features
- HGB_CLASS architecture/hyperparameters
- RAW probability
- alert threshold **p >= 0.30**
- 5-origin prequential refit
- label-maturity purge
- no monthly context in probability.

Stage 6 must:
1. continue chronology into 2025 using only matured prior labels;
2. make 2025 predictions without retuning;
3. report Brier/log loss vs matured prior-history baselines;
4. report T30:
   - alerts
   - precision
   - recall
   - false-opportunity rate
   - alert frequency
   - MFE5 / MAE5 after alerts;
5. report monthly-DOWN 2025 subset separately;
6. report quarter stability and episode-deduplicated performance;
7. compare transport qualitatively with DEV without changing the rule.

If 2025 transport fails, do not rescue the threshold or calibration with 2025 hindsight.

Only after frozen transport may the project decide whether to start the prospective daily opportunity ledger.
---

# 10. Document Hierarchy

Canonical intramonth project:
- `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md`

Objective amendment:
- `GOLD_DAILY_INTRAMONTH_OPPORTUNITY_OBJECTIVE_AMENDMENT_V1_2026-10-01.md`

Stage 0:
- `GOLD_DAILY_FORECAST_STAGE0_SCIENTIFIC_CONTRACT_2026-10-01.md`

Stage 1:
- `GOLD_DAILY_FORECAST_STAGE1_DATA_AUTHORITY_PIT_AUDIT_2026-10-01.md`
- `GOLD_DAILY_FORECAST_STAGE1_DATA_AUTHORITY_PIT_AUDIT_RESULT_2026-10-01.md`

Stage 2:
- `GOLD_INTRAMONTH_OPPORTUNITY_STAGE2_AUTHORITY_2026-10-01.md`
- `GOLD_INTRAMONTH_OPPORTUNITY_STAGE2_RESULT_2026-10-01.md`
- authoritative artifact: **11161358194**

Stage 3:
- `GOLD_INTRAMONTH_OPPORTUNITY_STAGE3_AUTHORITY_2026-10-01.md`
- `GOLD_INTRAMONTH_OPPORTUNITY_STAGE3_RESULT_2026-10-01.md`
- authoritative run: **36862897415**
- authoritative artifact: **11163151830**

Stage 4:
- `GOLD_INTRAMONTH_OPPORTUNITY_STAGE4_AUTHORITY_2026-10-01.md`
- `GOLD_INTRAMONTH_OPPORTUNITY_STAGE4_RESULT_2026-10-01.md`
- authoritative run: **36865648243**
- authoritative artifact: **11164440527**

Stage 5:
- `GOLD_INTRAMONTH_OPPORTUNITY_STAGE5_AUTHORITY_2026-10-01.md`
- `GOLD_INTRAMONTH_OPPORTUNITY_STAGE5_RESULT_2026-10-01.md`
- authoritative run: **36866945286**
- authoritative artifact: **11164696977**

Prior daily evidence:
- `GOLD_DAILY_H1_TOP_FAMILY_EXPLORATORY_V1_AUDIT_INVALIDATION_2026-09-26.md`
- `GOLD_DAILY_H1_V2_GPR_MIDAS_AUDIT_2026-09-26.md`

Monthly parent:
- `GOLD_MONTHLY_PROJECT_MANIFEST.md`


## 5E.11E Daily Realization Source Correction — 2026-10-06

Authority:
- `GOLD_DAILY_REALIZATION_SOURCE_AUDIT_2026-10-06.md`

The historical numeric `Gerçekleşen` values used in the recovered daily H1/CIG ledger have now been traced exactly.

Source:
- StakTrakr `data/spot-history-2026.json`
- pinned commit `ed2e549f82ba0d1cd3ca32842b82d3888d301e01`
- Gold daily-history value.

Audit result:
- **145/145** recovered `Gerçekleşen` values match the pinned StakTrakr Gold value exactly.

Binding correction — **this section supersedes every earlier conflicting clock-semantic statement in this manifest**:
- the Stak daily timestamp at synthetic noon is a calendar-date label, **not** a proven 12:00 market observation;
- the Stak daily value is **not proven** to be a New York close, London close, Istanbul close, or full-UTC-day average;
- the prior Twelve Data UTC-day-average comparison remains only a similarity/cross-check, not source-semantic proof.

Therefore:
- CIG **74.40%** = accuracy against the pinned Stak daily date-labelled reference direction;
- no intraday clock may be inferred from that daily label;
- all execution claims require separately timestamped intraday prices.


### 5E.11F CIG source-vintage mismatch — 2026-10-06

Binding source audit:
- `GOLD_DAILY_REALIZATION_SOURCE_AUDIT_2026-10-06.md`

The recovered 145-row daily `Gerçekleşen` ledger is exactly tied to StakTrakr ref `ed2e549f82ba0d1cd3ca32842b82d3888d301e01`, while the later clean H3/AURORA daily snapshot is frozen from ref `54fdf1c8d39b7b6c7b874d0f30f784296e886044`.

Comparison:
- 34/145 daily Gold levels differ;
- 10/145 daily directions differ;
- on the exact 125 CIG consensus rows, 9 labels differ.

Result impact on the same exact 125 signals:
- old recovered label: **93/125 = 74.40%**
- later H3 frozen-source daily direction: **88/125 = 70.40%**.

Therefore **74.40% is no longer allowed to be described as a clean source-consistent H3/CIG validation statistic**. It is a historical mixed-vintage daily-label diagnostic.

A source-consistent re-score requires one frozen Stak ref/data contract to be used consistently for both model/expert replay and realized labels.
