# GOLD INTRAMONTH OPPORTUNITY — CANONICAL PROJECT MANIFEST

**Manifest version:** 1.0  
**Date:** 2026-10-01  
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
- use **Asia, Europe, New York/London overlap, and late-US** as distinct research states;
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
- it is best described as a **New York/London-overlap anchored daily action signal** whose features may contain global prior information;
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

## 5E.8 Architecture candidates to test

The default research hierarchy is:

**Layer 1 — Global Direction Core**  
A common 24-hour state / CIG-style directional core.

**Layer 2 — Session Heads**  
Separate conditional heads for:
- Asia
- Europe
- New York/London overlap
- late US.

Each head estimates whether the global direction remains actionable in that session.

**Layer 3 — Execution Head**  
Chooses entry/exit only after the relevant session head confirms that the move has not already been exhausted.

Separate full models for every session are **not yet binding**. They are promoted only if session-specific heads materially outperform a common global model under frozen transport.

## 5E.9 Research hypotheses — not conclusions

H1. Europe and New York/London overlap contain different information sets and should not share one unconditional execution rule.

H2. The New York/London overlap may be the highest-information zone, but a meaningful part of the daily move can occur before it; therefore a late issuance can be directionally correct while economically late.

H3. Asia may contribute more through inventory/demand and overnight repricing than through the same information channel that dominates New York.

H4. Benchmark and macro-announcement windows may explain apparent clock-time effects.

H5. The optimal design may be **one global direction model + multiple session execution heads**, rather than fully independent Asia/Europe/US prediction models.

All five hypotheses require project-specific validation.

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

The current short-horizon stack is a **mixed-clock architecture**:

- governed daily Gold reference / H3 target = **UTC calendar-day reference**
- hourly intraday feature clock = **America/New_York**, anchored at 16:00 NY
- forecast issue/deadline clock = **America/New_York**, 08:00 NY
- historical CIG-D1 label = derived from the governed UTC-day reference series
- `Europe/Istanbul` = reporting/execution conversion only; it is not currently a model target, feature, or issue clock.

Therefore:
- the model is **not a Turkey-clock model**;
- the historical CIG-D1 label is **not a New York-session label** either;
- D1 execution research must explicitly compare the UTC-day-derived historical label with a separate post-08:00-NY executable label.

This clock identity is binding and supersedes informal wording that called the governed daily reference a normal close.

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
- Full-UTC-day daily reference completes at 03:00 Istanbul; this is only a theoretical lower-bound readiness clock.
- Governed issue deadline: 08:00 New York = approximately 15:00 Istanbul in New York daylight time / 16:00 Istanbul in New York standard time.
- Historical retrospective rows have no actual `issued_at_utc`; therefore exact historical production time is unknown.
- Execution claims must use 08:00 New York unless an earlier all-source-ready timestamp is separately proven.

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

Binding correction:
- the Stak daily timestamp at synthetic noon is a calendar-date label, **not** a proven 12:00 market observation;
- the Stak daily value is **not proven** to be a New York close, London close, Istanbul close, or full-UTC-day average;
- the prior Twelve Data UTC-day-average comparison remains only a similarity/cross-check, not source-semantic proof.

Therefore:
- CIG **74.40%** = accuracy against the pinned Stak daily date-labelled reference direction;
- no intraday clock may be inferred from that daily label;
- all execution claims require separately timestamped intraday prices.
