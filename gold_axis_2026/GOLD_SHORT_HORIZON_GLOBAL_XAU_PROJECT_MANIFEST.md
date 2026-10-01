# GOLD SHORT-HORIZON GLOBAL XAU PROJECT MANIFEST

**Date:** 2026-10-01  
**Status:** ACTIVE — GLOBAL XAU MAINLINE  
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

## 9. Exact next action

1. build global-XAU readiness panel;
2. confirm 2022-2024 DEV H1/H3/H5 counts;
3. run first classical/boosting multi-horizon screen;
4. keep 2025 unopened.
