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
**Stage 1 Daily Data Authority & PIT Audit: COMPLETE / PASS**  
**Stage 2 Baseline & Daily Feature Contract: NEXT**

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

# 3. Data Architecture — Frozen Stage-1 State

## 3.1 Core four-metal authority

**Borsa İstanbul Precious Metals Market — Metal Price (USD/ONS)**

Covered metals:
- Gold
- Silver
- Platinum
- Palladium.

Official Metal Price history is available from **2011-01-01**.

Binding daily target:
- **Gold Metal Price USD/ONS**
- treated as this project's governed daily XAU/USD reference;
- not described as LBMA PM or global OTC close.

Core status: **READY / OFFICIAL**.

## 3.2 Forecast issue time

**00:30 Europe/Istanbul on each Borsa İstanbul target business date.**

At this cutoff:
- previous Borsa metal prices are final;
- prior U.S. session is complete;
- latest Fed H.15 release is available with safety buffer.

The target is the official Borsa İstanbul Gold Metal Price published later that target business day.

## 3.3 Rates

Authority:
- Federal Reserve H.15.

Rule:
- use only the latest observation actually published by the origin;
- never join by observation date alone.

Status:
**READY_LAGGED**.

## 3.4 FX

Authority:
- Federal Reserve H.10.

Important:
- H.10 daily observations are released in a **weekly Monday batch** for the previous business week.

Rule:
- publication-date / batch-aware join;
- carry only the latest officially released batch;
- record staleness.

Status:
**READY_WEEKLY_PIT**.

## 3.5 VIX

Authority:
- Cboe official daily VIX close.

Rule:
- use prior completed U.S. session only.

Status:
**READY**.

## 3.6 Nasdaq-100

Authority:
- Nasdaq official NDX Index History.

Rule:
- use prior completed U.S. session only.

Status:
**READY**.

## 3.7 WTI / Brent

Authority:
- EIA official daily closing spot-price histories.

History:
- WTI from 1986;
- Brent from 1987.

Issue:
- historical observation date is not automatically the historical public-availability date.

Status:
**SOURCE_READY / PIT_MAPPING_BLOCKED**.

Excluded from Stage-2 baseline feature blocks until release-date mapping is implemented.

## 3.8 GPR

Authority:
- Caldara-Iacoviello official GPR vintages.

Available:
- monthly vintages;
- Recent GPR daily data updated weekly;
- older daily/monthly vintages archived.

Rule:
- use only a vintage whose publication/update date is <= forecast origin.

Status:
**READY_PIT_VINTAGES**.

## 3.9 LBMA / StakTrakr boundary

LBMA:
- official international benchmark;
- historical tabular access requires IBA licence;
- **BENCHMARK_ONLY / LICENCE_BLOCKED** under current open-data workflow.

StakTrakr:
- prior reconstruction source;
- **RESEARCH_COMPARATOR_ONLY**;
- no longer core daily authority.

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
| 1 | Daily Data Authority & PIT Audit | **COMPLETE / PASS** |
| 2 | Baseline + feature contract | **NEXT** |
| 3 | Model-family screen | BLOCKED |
| 4 | Robustness / ensemble | BLOCKED |
| 5 | Frozen 2026 retrospective transport | BLOCKED |
| 6 | Prospective daily forecast ledger | NOT STARTED |

---

# 8. Exact Next Action

**Run Stage 2 — Baseline & Daily Feature Contract.**

Stage 2 must:
- extract and freeze the official Borsa İstanbul four-metal daily panel;
- audit coverage/common-calendar from 2011 through 2025;
- freeze pre-2026 train/DEV chronology;
- compute RW / zero-return / drift baselines;
- build initial low-dimensional daily feature blocks;
- implement release-aware as-of joins for H.15, H.10, VIX, NDX and GPR;
- exclude WTI/Brent until PIT release mapping passes;
- produce the first immutable daily modeling snapshot.

No complex model-family screen before Stage 2 passes.

---

# 9. Document Hierarchy

Canonical daily state:
- `GOLD_DAILY_FORECAST_PROJECT_MANIFEST.md`

Frozen Stage 0 authority:
- `GOLD_DAILY_FORECAST_STAGE0_SCIENTIFIC_CONTRACT_2026-10-01.md`

Stage 1 authority/result:
- `GOLD_DAILY_FORECAST_STAGE1_DATA_AUTHORITY_PIT_AUDIT_2026-10-01.md`
- `GOLD_DAILY_FORECAST_STAGE1_DATA_AUTHORITY_PIT_AUDIT_RESULT_2026-10-01.md`

Prior evidence:
- `GOLD_DAILY_H1_TOP_FAMILY_EXPLORATORY_2026-09-26.md`
- `GOLD_DAILY_H1_TOP_FAMILY_EXPLORATORY_V1_AUDIT_INVALIDATION_2026-09-26.md`
- `GOLD_DAILY_H1_V2_GPR_MIDAS_AUDIT_2026-09-26.md`

Monthly parent:
- `GOLD_MONTHLY_PROJECT_MANIFEST.md`

The monthly and daily manifests must not be merged.
