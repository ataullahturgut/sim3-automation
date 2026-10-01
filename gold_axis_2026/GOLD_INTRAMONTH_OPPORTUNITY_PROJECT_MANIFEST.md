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
- **Stage 3 Origin-Safe Opportunity Predictability Screen: NEXT**

No opportunity-model champion exists yet. Stage 2 proves that the opportunity phenomenon exists; predictability remains unproven.

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
| 3 | Origin-safe opportunity predictability screen | **NEXT** |
| 4 | Monthly-context incremental test | BLOCKED BY STAGE 3 |
| 5 | Robustness / calibration / ensemble | BLOCKED |
| 6 | Frozen 2026 retrospective transport | BLOCKED |
| 7 | Prospective opportunity ledger | NOT STARTED |

---

# 9. Exact Next Action

**Stage 3 — Origin-Safe Intramonth Opportunity Predictability Screen**

Question:

> Can information known at the daily origin predict MFE5 / MAE5 or K050/K075/K100 opportunity events better than frozen prior-history baselines?

Required order:

1. **CORE model only — no monthly ChHHO context**
   - Gold path features
   - cross-metal causal features
   - companion staleness controls

2. Low-capacity baselines first:
   - logistic regression for K050/K075/K100
   - ridge / robust linear regression for MFE5 and MAE5
   - one constrained tree/boosting benchmark if justified

3. Chronological / expanding DEV evaluation only.

4. Compare against Stage-2 frozen baselines:
   - prior prevalence probability
   - rolling-252 prevalence
   - prior/rolling median MFE/MAE.

5. Do **not** use 2025 for model/feature/hyperparameter selection.

6. Only after a core signal exists, Stage 4 may add monthly ChHHO direction / return / alarm / regime as an incremental context block.

Promotion requires genuine pre-2026 predictive improvement; mere existence of intramonth rallies is not sufficient.

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

Prior daily evidence:
- `GOLD_DAILY_H1_TOP_FAMILY_EXPLORATORY_V1_AUDIT_INVALIDATION_2026-09-26.md`
- `GOLD_DAILY_H1_V2_GPR_MIDAS_AUDIT_2026-09-26.md`

Monthly parent:
- `GOLD_MONTHLY_PROJECT_MANIFEST.md`
