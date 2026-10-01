# GOLD DAILY FORECAST — CANONICAL PROJECT MANIFEST

**Manifest version:** 1.0  
**Date:** 2026-10-01  
**Status:** **CURRENT / BINDING / PROJECT INITIATED**  
**Repository:** `ataullahturgut/sim3-automation`  
**Branch:** `gold-midas-headswap-v1-20260925`  
**Parent project:** `GOLD_MONTHLY_PROJECT_MANIFEST.md`

> This is a separate frequency/target contract. Monthly-model results are prior evidence only and do not automatically transfer to the daily project.

---

# 1. Executive State

## 1.1 Goal

Forecast the **next common-market-day XAU/USD daily reference price** at H=1.

Working model target:
- next-day Gold log return;
- reconstruct to the governed next-day Gold price.

Gold is the primary scored target. Joint four-metal output is allowed where justified.

## 1.2 Current project stage

**Stage 0 Scientific Contract: FROZEN / COMPLETE**  
**Stage 1 Daily Data Authority & PIT Audit: NEXT**

No daily production champion exists.

## 1.3 Governance status

- model selection/tuning ends no later than **2025-12-31**
- 2026 = **OPENED / RETROSPECTIVE**
- no random split
- no future-day leakage
- no target-day feature use
- persistence baseline mandatory
- prospective ledger begins only with forecasts timestamped after project freeze.

## 1.4 Prior daily evidence

### V1 exploratory
Status: **INVALID / SUPERSEDED**

Main defect:
- generic EWMA substituted for the governed adaptive feature concept;
- PIT provenance not proven.

### V2 GPR-MIDAS frequency-transfer audit
Status: **VALID RETROSPECTIVE RESEARCH / NOT PRODUCTION**

2026 Jan-Jul:
| Model | MAE USD | Direction |
|---|---:|---:|
| RW / previous price | **61.59** | — |
| AOA-ELM | 61.75 | 48.97% |
| FULL7 ANN | 61.95 | 47.59% |
| SMA-ELMFIS | 61.96 | 46.21% |
| REDUCED4 ANN | 61.99 | 48.28% |

Conclusion:
- none beat persistence MAE;
- direct monthly-family transfer is not the daily solution;
- same V2 experiment must not be repeated as if new.

---

# 2. Scientific Contract

Authority:
`GOLD_DAILY_FORECAST_STAGE0_SCIENTIFIC_CONTRACT_2026-10-01.md`

Binding principles:
- H=1 common observation day;
- exact daily price convention frozen only after source audit;
- daily feature definitions are separate from monthly feature definitions;
- 2026 cannot select a model because it has already been inspected;
- prospective performance must be logged before outcomes.

Primary metrics:
1. cumulative absolute price error;
2. MAE USD;
3. direction accuracy.

Supporting:
- RMSE;
- MAPE/WAPE;
- return correlation;
- predicted-return dispersion;
- worst-day;
- stability by month/state;
- relative error vs persistence.

---

# 3. Data Architecture — Current Status

## 3.1 Four-metal core

Required:
- Gold
- Silver
- Platinum
- Palladium.

Known issue:
- prior historical daily metal series are labeled **APPROVED_HISTORICAL_RESEARCH_RECONSTRUCTION_NOT_PIT**.

Therefore governed daily modeling is blocked until Stage 1 establishes an acceptable source/timestamp contract or explicitly accepts reconstruction-only research scope.

## 3.2 Rates

Existing monthly-project authority already contains official Federal Reserve H.15 daily histories through September 2026.

Daily-project task:
- define daily origin timestamp/release safety;
- determine usable nominal 10Y / real 10Y / breakeven representations.

Status: **SOURCE EXISTS / DAILY CONTRACT NOT YET FROZEN**.

## 3.3 FX

Existing authority contains official Federal Reserve H.10 daily histories including Broad USD and major FX.

Status:
**SOURCE EXISTS / DAILY CONTRACT NOT YET FROZEN**.

## 3.4 VIX

Existing authority contains official Cboe daily VIX history.

Status:
**SOURCE EXISTS / DAILY CONTRACT NOT YET FROZEN**.

## 3.5 Nasdaq-100

Prior data-readiness result:
- monthly Nasdaq is ready;
- credential-free long-history daily Nasdaq-100 was **NOT PROVEN**.

Status:
**DAILY SOURCE BLOCKED / MUST BE RESOLVED IN STAGE 1**.

No silent proxy substitution.

## 3.6 WTI / Brent

Prior governed store proves World Bank **monthly** WTI/Brent, not a governed daily oil series.

Status:
**DAILY SOURCE NOT YET PROVEN**.

No monthly oil series may be mislabeled as a daily input.

## 3.7 GPR

Daily GPR use requires an explicit origin-time vintage rule.

Prior V2 used:
- an origin in month M may use only vintage M-1 and GPR month M-2.

Stage 1 must confirm or replace this with a documented daily-origin rule before modeling.

---

# 4. Daily Feature Research Plan

Feature blocks will be frozen only after data-source audit.

Candidate families:

**Core price path**
- 1-day return
- 5/10/21-session momentum
- rolling realized volatility
- range / drawdown
- GPR-adaptive weighted daily-return summary.

**Cross-metal**
- return breadth
- dispersion
- relative momentum
- safe-haven divergence.

**Rates**
- level/change
- real yield
- breakeven proxy
- short distributed lags.

**FX**
- Broad USD return/momentum
- selected major-FX breadth/dispersion
- daily risk-off rotation.

**Risk/equity**
- VIX level/change/volatility
- Nasdaq-100 only after daily source PASS.

**Oil**
- WTI / Brent only after governed daily source PASS.

No feature enters the model because it worked in the monthly project; daily incremental evidence is required.

---

# 5. Development & Evaluation Design

## 5.1 Development period

All model/feature/hyperparameter decisions must use observations ending **no later than 2025-12-31**.

Exact training-window length and expanding/rolling schedule will be frozen in Stage 2 after data coverage is known.

## 5.2 Opened 2026

2026 Jan-Jul daily outcomes were already inspected in V1/V2.

Therefore 2026 is:
- retrospective stress;
- diagnostic transport;
- never selection authority.

August/September 2026 must also not be converted into an ad-hoc selection holdout after seeing current project context.

## 5.3 Prospective ledger

Clean forward evidence begins with forecasts issued after the daily project freeze.

Every forecast record should contain:
- forecast timestamp;
- target date;
- source cutoff;
- feature snapshot/hash;
- model/version;
- predicted return;
- predicted price;
- direction;
- later actual;
- error metrics.

---

# 6. Model Research Policy

Do not begin by copying all monthly model families.

First governed screen should include:
- persistence / zero-return controls;
- low-capacity linear/regularized baseline;
- one tree/boosting baseline;
- selected nonlinear/neural candidates only after baseline feature signal is established.

Monthly families may later be ported under an explicit daily architecture.

Prior V2 already shows that AOA-ELM, FULL7, REDUCED4 and SMA-ELMFIS direct transfers do not beat persistence under the tested daily analogue.

---

# 7. Stage Roadmap

| Stage | Purpose | Status |
|---|---|---|
| 0 | Scientific contract | **COMPLETE / FROZEN** |
| 1 | Daily Data Authority & PIT Audit | **NEXT** |
| 2 | Baseline + feature contract | BLOCKED BY STAGE 1 |
| 3 | Model-family screen | BLOCKED |
| 4 | Robustness / ensemble | BLOCKED |
| 5 | Frozen 2026 retrospective transport | BLOCKED |
| 6 | Prospective daily forecast ledger | NOT STARTED |

---

# 8. Exact Next Action

**Run Stage 1 — Daily Data Authority & PIT Audit.**

Audit must answer:
1. What exactly is the daily Gold target observation?
2. Are four-metal historical daily rows PIT-safe or only reconstruction?
3. What is the common-market-day calendar?
4. Which daily Rates/FX/VIX series are already governed?
5. Can official/governed daily Nasdaq-100 be established?
6. Can official/governed daily WTI and Brent be established?
7. What is the daily GPR publication/vintage rule?
8. What are the missing-day/holiday/stale-price rules?

No governed daily model should be run before this stage passes.

---

# 9. Document Hierarchy

Canonical daily state:
- `GOLD_DAILY_FORECAST_PROJECT_MANIFEST.md`

Frozen Stage 0 authority:
- `GOLD_DAILY_FORECAST_STAGE0_SCIENTIFIC_CONTRACT_2026-10-01.md`

Prior evidence:
- `GOLD_DAILY_H1_TOP_FAMILY_EXPLORATORY_2026-09-26.md`
- `GOLD_DAILY_H1_TOP_FAMILY_EXPLORATORY_V1_AUDIT_INVALIDATION_2026-09-26.md`
- `GOLD_DAILY_H1_V2_GPR_MIDAS_AUDIT_2026-09-26.md`

Monthly parent:
- `GOLD_MONTHLY_PROJECT_MANIFEST.md`

The monthly and daily manifests must not be merged.
