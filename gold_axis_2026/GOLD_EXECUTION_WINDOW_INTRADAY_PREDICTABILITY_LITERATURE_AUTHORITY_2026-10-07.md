# GOLD EXECUTION-WINDOW INTRADAY PREDICTABILITY LITERATURE AUTHORITY — 2026-10-07

**Status:** RESEARCH AUTHORITY / LITERATURE-TRANSLATION COMPLETE / MODEL RUN NOT YET AUTHORIZED BY THIS FILE ALONE  
**Repository:** `ataullahturgut/sim3-automation`  
**Branch:** `gold-execution-channel-audit-20261006`  
**Parent manifest:** `gold_axis_2026/GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md`  
**Parent execution authority:** `gold_axis_2026/GOLD_EXECUTION_ALIGNED_HORIZON_HYBRID_RESEARCH_AUTHORITY_2026-10-07.md`

## 0. Binding interpretation

The academic literature does contain close precedents for the user's execution-horizon problem.

The literature does **not** establish that the exact targets
- `09:00 -> 17:00 Europe/Istanbul`, and
- `17:00 -> next eligible 09:00 Europe/Istanbul`

are already solved.

It does establish five mechanisms directly relevant to the current project:

1. intraday Gold returns can contain predictive information for later intraday returns;
2. the informative interval can be a **specific half-hour**, not necessarily a whole-day return;
3. momentum and reversal can coexist and their sign can change by market state;
4. night-session / international-information arrival materially changes Gold predictability;
5. volatility, jumps, liquidity and scheduled macro-news state can condition whether a return predictor is informative.

Therefore the next literature-backed direction is not a larger generic classifier. It is a **low-capacity, origin-safe momentum/reversal mechanism challenge** on the user's execution windows.

## 1. Closest direction-predictability evidence

### 1.1 Xu, Bouri, Saeed & Wen (2020) — GLD intraday return predictability

Reference:
- Xu, Y., Bouri, E., Saeed, T., Wen, Z. (2020), *Intraday return predictability: Evidence from commodity ETFs and their related volatility indices*, Resources Policy 69, 101830.
- DOI: `10.1016/j.resourpol.2020.101830`.

Data / clock:
- 1-minute high-frequency data;
- GLD sample: 2004-11-08 to 2019-05-30;
- regular US trading period 09:30-16:00 ET;
- 13 half-hour intervals.

Return definition:
`r[i,t] = log(p[i,t]) - log(p[i-1,t])`.

The first half-hour includes the overnight gap because its baseline is the prior day's 16:00 close.

Core predictive regression:
`r[13,t] = alpha_i + beta_i * r[i,t] + epsilon[i,t]`, for `i=1,...,12`.

Gold result:
- GLD's **5th half-hour return** is the significant in-sample predictor of the last half-hour;
- reported coefficient about `0.0436`;
- Newey-West t-stat about `3.03`;
- in-sample R2 about `0.49%`.

OOS:
- sample split approximately in half;
- predictive model estimated on first half and compared with historical-mean forecast on the second;
- GLD 5th-half-hour predictor retains positive `R2_OS` of about `0.26%`.

State dependence:
- predictive strength changes with realized volatility and jump magnitude;
- the paper explicitly tests first-half-hour realized volatility and jump subgroups.

Economic test:
- market-timing sign is taken from the sign of the efficient intraday predictor;
- performance is compared against an always-long benchmark.

### Project implication

This paper is direct evidence against treating every prior return interval as equally informative.

For our project:
- scan/define a **small preregistered set of pre-origin half-hour returns**;
- allow the sign of the relation to be learned (momentum or reversal);
- evaluate continuous-return forecast and directional sign separately;
- condition only on origin-known volatility/jump state.

It does **not** justify mining every 15/30-minute interval until a high 2025 score appears.

---

### 1.2 Ma, Bouri, Xu & Zhou (2025) — Gold/Silver "night effect"

Reference:
- Ma, G., Bouri, E., Xu, Y., Zhou, Z.I. (2025), *The "night effect" of intraday trading: Evidence from Chinese gold and silver futures markets*, Global Finance Journal 64, 101084.
- DOI: `10.1016/j.gfj.2025.101084`.

Data / market:
- SHFE Gold and Silver futures;
- 1-minute prices aggregated to half-hour returns;
- Chinese night session: 21:00-02:30 China time after its 2013 introduction.

Critical clock translation:
- China is UTC+8;
- Türkiye is UTC+3;
- therefore the SHFE night open `21:00 China` maps to approximately **16:00 Europe/Istanbul**;
- the first SHFE night half-hour maps to approximately **16:00-16:30 Türkiye**.

This is unusually close to the user's 16:30-17:00 pre-bank-spread decision point.

Main result:
- both intraday momentum and intraday reversal are present;
- before night trading, the first daytime half-hour is informative;
- after night trading begins, the **first night-session half-hour becomes the dominant predictor** and daytime opening predictability weakens;
- OOS analysis confirms the change.

Mechanism evidence:
- stronger patterns appear when COMEX realized volatility / absolute return before the SHFE night open is high;
- liquidity conditions matter;
- the paper examines Amihud illiquidity and information-discreteness mechanisms;
- intraday reversal can precede later momentum.

Economic test:
- a market-timing strategy uses the sign of the first night half-hour to choose long/short direction for later predicted intervals;
- it outperforms always-long and buy-and-hold benchmarks in the reported setting.

### Project implication

This is the strongest literature analogue for **OVERNIGHT-HOLD**.

The first literature-faithful challenge should therefore test whether the completed:
- `16:00-16:30` XAU return,
- `16:30-17:00` XAU return,
- their interaction / reversal pattern,
- pre-17:00 realized volatility and jump state

predict `17:00 -> next 09:00`.

Do not assume positive beta. A negative coefficient is a valid reversal result.

COMEX/GC state is an important challenger input, but if governed intraday GC is unavailable, the first test may use only governed XAU pre-origin state and mark GC as a separate data-authority extension.

---

## 2. Session / information-arrival evidence

### 2.1 Sobti, Sehgal & Ilango (2021)

Reference:
- Sobti, N., Sehgal, S., Ilango, B. (2021), *How do macroeconomic news surprises affect round-the-clock price discovery of gold?*, International Review of Financial Analysis 78, 101893.
- DOI: `10.1016/j.irfa.2021.101893`.

Data:
- one-minute New York COMEX, London OTC and Shanghai futures;
- 2013-2018;
- 62 scheduled macroeconomic announcements from China, Eurozone and US.

Five sequential ET windows:
- Asia Morning: 21:00-23:30;
- Asia Afternoon: 01:30-03:30;
- Europe: 03:30-08:00;
- New York/London: 08:00-14:30;
- US: 14:30-21:00.

Method:
- GMM information-share framework for parallel price discovery;
- sequential information-share measures;
- LASSO and stepwise regressions for news-surprise selection;
- standardized news surprise based on actual minus consensus, scaled by historical forecast-error dispersion.

Findings:
- New York futures lead global price discovery;
- NY/London is the most informative sequential zone;
- US and Eurozone macro surprises alter information leadership;
- effects are asymmetric and state dependent;
- sign reversal can occur in extreme states.

### Project implication

The WGC/Sobti windows should remain **state/expert variables**, but they are not substitutes for DAY or OVERNIGHT labels.

For direction models:
- macro surprise may enter only after its release time;
- before release, only the known event-calendar state is legal;
- event sign and magnitude must never be backfilled into an earlier origin.

---

## 3. Tail / jump-state evidence

### 3.1 Sobti (2025) — intraday Gold jumps

Reference:
- Sobti, N. (2025), *What triggers intraday price jumps and co-jumps in gold?*, International Review of Financial Analysis 105, 104380.
- DOI: `10.1016/j.irfa.2025.104380`.

Data:
- CME Gold futures and SPDR Gold ETF;
- high-frequency TAQ;
- jump analysis at 5-minute baseline with multiple sampling-frequency robustness tests;
- 2010-2018.

Methods:
- Lee-Mykland jump detection as main method;
- alternative jump detectors as robustness;
- predictive stepwise logistic regression with ridge penalty;
- macro-news surprise, liquidity/order-flow, uncertainty and market-psych predictors.

Findings:
- intraday jumps are rare but large;
- negative jumps are larger in magnitude than positive jumps;
- US macro news is associated with a material fraction of intraday jumps;
- FOMC rate decisions are especially important;
- trading activity, transaction costs, order imbalance, USD volatility and stock-market uncertainty help predict jump/co-jump risk.

### Project implication

This is **not** a primary UP/DOWN model.

It supports a separate origin-known **TAIL/JUMP STATE**:
- scheduled FOMC / CPI / NFP etc.;
- already-released actual-consensus surprise;
- pre-origin RV / jump proxy;
- liquidity proxy if governed;
- VIX / USD-volatility state if origin-safe.

The tail state may later:
- attenuate a direction model;
- trigger abstention;
- activate a reversal/rescue specialist.

It must not be allowed to leak post-origin jump information.

---

## 4. Volatility-state evidence

### 4.1 Yao, Hui & Kang (2021)

Reference:
- Yao, X., Hui, X., Kang, K. (2021), *Can night trading sessions improve forecasting performance of gold futures' volatility in China?*, Journal of Forecasting 40, 849-860.
- DOI: `10.1002/for.2748`.

Methods:
- HAR realized-volatility model;
- HAR-V-J extension with trading volume and jump components;
- HAR-GARCH extension.

Finding:
- night trading changes Gold volatility dynamics;
- before night trading, substantial volatility arises from overnight international information;
- adding jump/volume/dynamic volatility information improves state modelling.

### 4.2 Wei et al. (2020)

Reference:
- Wei, Y., Liang, C., Li, Y., Zhang, X., Wei, G. (2020), *Can CBOE gold and silver implied volatility help to forecast gold futures volatility in China?*, Finance Research Letters 35, 101287.
- DOI: `10.1016/j.frl.2019.09.002`.

Finding:
- GVZ and VXSLV improve Gold-futures volatility forecasts;
- HAR extensions and Ridge are useful where volatility predictors are collinear.

### Project implication

Volatility should initially be a **conditioning/state variable**, not a large standalone direction model.

The repo already contains a governed GVZ history for part of the sample. Same-day values can be used only when source-ready before the relevant origin; otherwise use lagged GVZ.

---

# 5. Literature-to-project model specification

## 5.1 Target A — OVERNIGHT-HOLD

Frozen candidate target:
`Y_OVN(t) = sign(log(P[next eligible 09:00] / P[17:00]))`.

Continuous companion:
`R_OVN(t) = log(P[next eligible 09:00] / P[17:00])`.

### LIT-OVN-0 — publication-faithful single-interval screen

Preregistered predictors, all complete by 17:00:
- `r_1530_1600`
- `r_1600_1630`
- `r_1630_1700`

Test each separately:
`R_OVN = alpha + beta_j r_j + epsilon`.

Purpose:
- identify whether one narrow pre-origin interval contains direction information;
- beta may be positive (momentum) or negative (reversal).

### LIT-OVN-1 — night-open momentum/reversal pair

Predictors:
- `r_1600_1630`;
- `r_1630_1700`;
- interaction `r_1600_1630 * r_1630_1700`;
- indicator for same-sign continuation vs sign flip.

This directly tests whether early reversal followed by momentum exists around the user's decision clock.

### LIT-OVN-2 — state-conditioned extension

Add only origin-known:
- pre-17:00 realized volatility;
- pre-17:00 absolute return;
- jump proxy;
- current Sobti/WGC session state;
- scheduled-macro event state;
- actual-consensus surprise only when already released;
- lagged / source-ready GVZ;
- optional governed GC/COMEX RV challenger if/when intraday GC authority is available.

Use low-capacity interaction / ridge / logistic variants only after LIT-OVN-0/1.

---

## 5.2 Target B — DAY

Frozen candidate target:
`Y_DAY(t) = sign(log(P[17:00] / P[09:00]))`.

Continuous companion:
`R_DAY(t) = log(P[17:00] / P[09:00])`.

### Critical causality constraint

At 09:00, the model cannot use the 09:00-09:30 return.

Therefore two distinct questions must be kept separate.

### LIT-DAY-0 — executable 09:00 model

Preregistered pre-origin predictors:
- `r_0800_0830`;
- `r_0830_0900`;
- overnight `17:00(prev) -> 09:00` return;
- pre-09:00 RV / absolute-return / jump proxy;
- Asia / Europe state realized before 09:00.

Simple form:
`R_DAY = alpha + beta1*r_0800_0830 + beta2*r_0830_0900 + beta3*R_overnight + epsilon`.

Feature count must stay small.

### LIT-DAY-1 — literature-faithful delayed-decision challenger

Decision/origin:
- 09:30 Europe/Istanbul.

Predictor:
- observed `09:00-09:30` return.

Target:
- `09:30 -> 17:00`.

This is **not** a replacement for the user's 09:00 decision unless it materially improves skill enough to justify a 30-minute execution delay.

It is included because it is the closest clean analogue to the opening-half-hour literature.

---

# 6. Statistical governance

## 6.1 Chronology

Maintain project governance:
- 2022: warm-up only where required;
- 2023-2024: development / mechanism discovery;
- 2025: retrospective frozen transport only;
- 2026: excluded from selection.

No 2025/2026 result may be used to choose:
- interval;
- sign;
- threshold;
- state cut;
- model family.

## 6.2 Multiple-testing control

Do not scan every possible intraday interval and report the best.

First preregister:
- three OVERNIGHT pre-origin half-hours;
- two DAY pre-origin half-hours;
- one DAY delayed-opening challenger.

If a broader scan is later authorized, use development-only false-discovery / max-t style control and freeze the selected interval before transport.

## 6.3 Required metrics

For continuous-return models:
- coefficient and Newey-West t-stat;
- MSE;
- historical-mean benchmark;
- `R2_OS`;
- sign accuracy.

For direction models:
- N / coverage;
- Accuracy;
- Balanced Accuracy;
- UP recall;
- DOWN recall;
- precision;
- Brier / log loss;
- calibration.

For state splits:
- report both state sample sizes;
- do not promote a state with a high metric on sparse rows;
- test coefficient / skill stability across 2023 and 2024 separately.

## 6.4 Promotion logic

A literature-inspired challenger is retained only if:
1. development evidence is not one-year-only;
2. it does not collapse to one class;
3. effect survives chronological/nested estimation;
4. 2025 transport is reported without retuning;
5. it adds information beyond the existing structural/path expert on identical rows.

---

# 7. Priority order

### Priority 1 — OVERNIGHT mechanism challenge

Reason:
- strongest direct literature analogue;
- published SHFE night first half-hour maps approximately to 16:00-16:30 Türkiye;
- current old CIG rescore shows only 49.07% on 17:00->09:00, leaving a clear unresolved target;
- the candidate uses only governed XAU pre-origin bars initially.

Run:
1. LIT-OVN-0;
2. LIT-OVN-1;
3. only if signal exists, LIT-OVN-2 state conditioning.

### Priority 2 — DAY 09:00 executable challenge

Run:
1. LIT-DAY-0;
2. compare against existing session/path states;
3. do not use 09:00-09:30 information.

### Priority 3 — DAY 09:30 delayed challenger

Only to answer:
> Does observing the first 30 minutes after 09:00 buy enough predictability to justify delaying the user's decision?

---

# 8. What this literature does NOT authorize

Do not jump directly to:
- consensus;
- ECCG;
- AURORA/HELIOS;
- deep neural sequence models;
- unrestricted half-hour mining;
- same-day future GVZ / macro-surprise leakage;
- using realized target-window reversal labels as state inputs;
- selecting the best specification from 2025.

The literature supports a **mechanism-first, low-capacity, state-conditioned** test.

---

# 9. Data-readiness notes in the current repository

Already present / directly usable:
- governed 15-minute XAU/USD archive for 2022 and 2023-2025;
- V5 WGC/Sobti session targets and state artifacts;
- macro-event raw ledger / availability map;
- GVZ raw history for 2021-2025;
- existing structural / PATH / SAGE state outputs.

Not assumed available under a governed intraday contract:
- COMEX GC intraday RV;
- intraday GVZ;
- order-book depth / bid-ask / order imbalance for XAU;
- Thomson Reuters MarketPsych variables.

Therefore the first LIT-OVN / LIT-DAY test must **not wait for proprietary microstructure data**. Start with governed XAU path + existing origin-safe event/session state. Add COMEX/liquidity variables only as separately governed challengers.

---

# 10. Binding conclusion

The most defensible next experiment is **not** another generic Gold direction model.

It is:

`pre-origin half-hour return / reversal structure + origin-known volatility/jump/session/event state -> execution-window return/direction`.

The strongest first target is OVERNIGHT because the 2025 Gold/Silver night-effect literature places a high-information first half-hour at a clock that maps unusually closely to the user's 16:00-17:00 Türkiye decision zone.

If this simple literature-faithful mechanism fails under 2023-2024 chronological development, that is strong negative evidence and a reason not to build a larger router around it.

If it succeeds and transports without retuning, it becomes a scientifically grounded expert candidate for the later execution router.


---

## 11. Executed Stage-1 / Stage-2 evidence — 2026-10-07

Artifacts:
- `GOLD_EXECUTION_LIT_STAGE1_RESULT_2026-10-07.md`
- `GOLD_EXECUTION_LIT_STAGE1_METRICS_2026-10-07.csv`
- `GOLD_EXECUTION_LIT_STAGE1_PREDICTIONS_2026-10-07.csv`
- `GOLD_EXECUTION_LIT_STAGE2_RESULT_2026-10-07.md`
- `GOLD_EXECUTION_LIT_STAGE2_METRICS_2026-10-07.csv`
- `GOLD_EXECUTION_LIT_STAGE2_PREDICTIONS_2026-10-07.csv`

### Stage-1

The preregistered half-hour screen and low-capacity chronological challenge were executed with 2022 warm-up, 2023-2024 development and frozen 2025 transport.

Key OVERNIGHT findings:
- `16:00-16:30` has the clearest continuous-return relation to `17:00 -> next 09:00`: development beta about **+0.358**, HAC t about **2.345**, p about **0.019**, pooled chronological OLS `R2_OS` about **+0.78%**.
- Its 2025 OLS-sign result is **BA 55.11%, accuracy 59.06%**; logistic transport is **BA 53.48%, accuracy 57.87%**.
- The two-half-hour `16:00-17:00` pair logistic is more balanced in development: **BA 53.04%**, with **2023 BA 53.05%** and **2024 BA 52.76%**. Frozen 2025 BA is **53.44%**.
- This is a modest mechanism/challenger signal, not a deployment-grade edge.

DAY findings:
- executable `09:00 -> 17:00` LIT-DAY0 fails: development OLS-sign BA **47.32%**, frozen 2025 BA **44.11%**.
- delayed `09:30 -> 17:00` shows only weak evidence: development OLS-sign BA **52.01%** with negative development `R2_OS`; it is not a 09:00 model.

### Stage-2

A single fixed origin-known state-conditioned OVERNIGHT challenger was tested using:
- `16:00-16:30`;
- `16:30-17:00`;
- same-sign state;
- pre-17:00 3-hour realized volatility;
- maximum absolute 15-minute jump proxy;
- 3-hour absolute return;
- return × RV and return × jump interactions.

It **failed the frozen development retention rule**:
- development Logit BA **50.53%**;
- 2023 BA **53.80%**;
- 2024 BA **46.68%**;
- development BA change versus the single `16:00-16:30` base: **-0.81 pp**;
- development continuous `R2_OS` change versus base: **-1.14 pp**;
- retention = **False**.

2025 does not alter this decision.

### Binding interpretation after execution

1. The literature-backed hypothesis is not generally rejected: the **16:00-16:30 Türkiye interval contains a small, statistically visible continuous relation** to the overnight target.
2. A simple `16:00-17:00` pair remains a **modest directional challenger**, not a proven primary model.
3. Adding XAU-only RV/jump state in the tested low-capacity form does **not** improve robustness and is rejected.
4. The executable 09:00 DAY literature translation is currently negative.
5. Do not mine additional half-hours or tune thresholds on 2025.
6. Any next extension must be mechanism-specific and origin-safe, preferably external price-discovery / information-arrival variables already motivated by the literature (for example governed GC/COMEX state if later available, or governed event/GVZ context), rather than more generic model capacity.
