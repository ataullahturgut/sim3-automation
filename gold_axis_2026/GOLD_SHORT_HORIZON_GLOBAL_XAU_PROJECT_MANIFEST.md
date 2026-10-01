# GOLD SHORT-HORIZON GLOBAL XAU PROJECT MANIFEST

**Date:** 2026-10-01  
**Status:** ACTIVE — STAGE 1 COMPLETE / H3 DIRECTION PARTIAL PASS  
**Supersedes for tactical objective:** BIST-Metal-Price short-horizon mainline.

## 1. Objective

Build a separate short-horizon Gold forecast engine for **global XAU/USD** investment research.

Primary horizons:
- H1
- H3
- H5

Primary target form:
- forward log return
- direction
- Q10/Q50/Q90 distribution.

## 2. Target authority

Historical development target:
- `XAU_STAKTRAKR_RESEARCH_DAILY_R1`
- source lineage: lbruton/StakTrakr
- underlying spot source: MetalPriceAPI XAU
- daily history semantic: daily spot-average representation
- coverage currently verified: 2010-01-04 .. 2026-07-31.

This is a **global spot research target**, not Borsa İstanbul Metal Price.

Prospective live fixed-time anchor:
- `XAU_EOD_TWELVE_NY17`
- retained separately;
- historical bridge to StakTrakr daily-average does not pass strict same-target equivalence because time aggregation differs.

Therefore do not stitch NY17 into the development target series.

## 3. Governance

- DEV selection: 2022-2024 only.
- 2025: frozen transport, no tuning.
- 2026: retrospective/prospective only after model contract freeze.
- no random split.
- chronological expanding evaluation.
- no BIST target values enter this mainline.

## 4. Global metal features

Historical daily research series:
- Gold: XAU_STAKTRAKR_RESEARCH_DAILY_R1
- Silver: XAG_STAKTRAKR_RESEARCH_DAILY_R1
- Platinum: XPT_STAKTRAKR_RESEARCH_DAILY_R1
- Palladium: XPD_STAKTRAKR_RESEARCH_DAILY_R1.

Initial blocks:
- GOLD_ONLY
- CORE3 = Gold + Silver + Platinum
- CORE4 = CORE3 + Palladium
- CORE3 + safe external.

## 5. Safe external families

Reuse existing release-aware authorities:
- H.15 nominal / real 10Y / breakeven proxy
- H.10 Broad USD + major FX
- VIX
- Nasdaq-100.

WTI/Brent remain excluded from first screen pending short-horizon PIT release mapping.
Daily GPR remains optional challenger.

## 6. Model order

First screen:
- direction baselines
- Logistic L2
- LightGBM
- XGBoost
- return zero/mean baselines
- Elastic Net
- LightGBM
- XGBoost
- LightGBM quantile Q10/Q50/Q90.

Deep models remain blocked until classical global-XAU evidence is established.

## 7. Economic scope

No trading/P&L rule is authorized in the first global-XAU screen.

First determine:
- which horizon passes;
- which model/feature block passes;
- whether the global target behaves materially better than the archived BIST target for short-horizon forecasting.

## 8. Prior BIST project

Stages 0-6C of the prior BIST-target short-horizon project remain archived evidence.

They must not be merged into global-XAU performance tables.

## 9. Current evidence

Data readiness:
- COMPLETE / PASS
- run **36900860852**
- artifact **11181284118**
- pre-DEV safe history: 3,011
- DEV: 755
- frozen 2025: 253.

Stage 1 classical / boosting screen:
- COMPLETE / PARTIAL SIGNAL
- run **36901409925**
- aggregate artifact **11181622889**.

| Horizon | Direction | Return | Quantile |
|---|---|---|---|
| H1 | FAIL | FAIL | FAIL |
| **H3** | **PASS** | FAIL | FAIL |
| H5 | FAIL | FAIL | FAIL |

Frozen first-screen H3 direction leader:
- **CORE3 / Logistic L2**
- Brier **0.246731**
- baseline **0.249712**
- relative improvement **+1.19%**
- log loss **0.686634** vs baseline **0.692572**.

Binding interpretation:
- H3 is the only horizon with pre-2025 predictive evidence;
- the evidence is direction-only;
- no return-magnitude, quantile, or tactical engine is yet promoted.

## 10. Exact next action

**Stage 2 — H3 Direction Robustness & Representation Audit**

1. H3 CORE3 / Logistic L2 by 2022 / 2023 / 2024;
2. LOW / MID / HIGH volatility diagnostics;
3. coefficient stability across expanding refits;
4. GOLD_ONLY / CORE3 / CORE4 / transformed-external Logistic comparisons;
5. secondary diagnostic of H5 direction;
6. keep 2025 unopened.

Do not return to BIST as the tactical target.
