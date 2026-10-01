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
- **Stage 4 Monthly Context Incremental Test: NEXT**

Current frozen core opportunity classifier:
- target: **K100**
- feature block: **G_ONLY**
- model: **HGB_CLASS**
- DEV Brier improvement vs best matured baseline: **+1.46%**
- DEV log loss: **0.56550** vs baseline **0.57283**.

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
| 4 | Monthly-context incremental test | **NEXT** |
| 5 | Robustness / calibration / ensemble | BLOCKED |
| 6 | Frozen 2026 retrospective transport | BLOCKED |
| 7 | Prospective opportunity ledger | NOT STARTED |

---

# 9. Exact Next Action

**Stage 4 — Monthly Context Incremental Test**

Question:

> Does origin-known monthly ChHHO context improve the frozen Stage-3 K100 strong-rally detector, especially in the monthly-DOWN situations that motivate this project?

Frozen core that may not be changed:
- target: **K100**
- feature block: **G_ONLY**
- primary model: **HGB_CLASS**
- supporting model: **LOGIT_L2**
- Stage-3 chronology/refit/purge rules unchanged.

Stage 4 test order:

1. **CORE_ONLY**
   - exact Stage-3 G_ONLY features.

2. **CORE + MONTHLY_DIRECTION**
   - ChHHO UP/DOWN sign only.

3. **CORE + MONTHLY_FORECAST_MAGNITUDE**
   - predicted monthly log return and/or frozen forecast-distance representation.

4. **CORE + MONTHLY_RELIABILITY**
   - only alarm/reliability fields that are causally available at the daily origin.

5. **CORE + MONTHLY_STATE**
   - only causally available regime/state fields.

Each context block must be tested incrementally against the frozen core under the same 2022-2024 prequential DEV protocol.

Promotion requires:
- lower Brier than frozen Stage-3 core;
- log loss not worse;
- no material collapse inside monthly-DOWN origins;
- no 2025/2026 selection.

Monthly DOWN remains **context, not an automatic veto**.

Secondary MAE5 monthly-context research may follow only after the K100 context test is resolved.
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

Prior daily evidence:
- `GOLD_DAILY_H1_TOP_FAMILY_EXPLORATORY_V1_AUDIT_INVALIDATION_2026-09-26.md`
- `GOLD_DAILY_H1_V2_GPR_MIDAS_AUDIT_2026-09-26.md`

Monthly parent:
- `GOLD_MONTHLY_PROJECT_MANIFEST.md`
