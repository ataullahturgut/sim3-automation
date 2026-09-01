# GOLD CONTROL — SUCCESSOR INPUT READINESS AUDIT

**Date:** 2026-09-01  
**Scope:** `GOLD_H1_SUCCESSOR_R1` historical target and forecast-input readiness  
**Status:** `AUDIT_FROZEN; TARGET_BRIDGE_PENDING; NO_MODEL_SCORE_AUTHORIZED`

## 1. Purpose

This audit inventories the forecast inputs that are actually evidenced in the retained Gold Control artifacts and separates them from merely plausible research features. It does not approve a model, alter a production rule, or authorize comparative model scoring.

Binding rules:

- no feature enters a successor candidate because it appeared in a legacy model;
- historical observation date is not automatically historical availability;
- current/retrieved-late history may not be backdated into old forecast origins without independent publication/vintage reconstruction;
- old Yahoo/StakTrakr/proxy identities may not be silently relabelled as current authority/vendor series;
- all successor score runs remain blocked until the historical target contract and the relevant feature PIT contract are frozen.

## 2. Historical target gate

Future operational target remains:

`XAU_MONTHLY_AVG_NY17`

from canonical `XAU_EOD_TWELVE_NY17` observations.

Known Twelve depth evidence:

- exact 1-minute NY17 history is not proven back to 2016;
- 1-hour NY17 reconstruction is proven at sampled dates to approximately 2020 and sampled recent overlap showed the 16:00→17:00 hourly close equal to the exact 16:59 one-minute close;
- sampled depth is not itself a proof of complete 2020+ monthly coverage.

World Bank Pink Sheet monthly gold is under separate Option-2 bridge audit. It covers 1960-01 onward and contains 2016-01. It is London-afternoon-fixing monthly-average semantics, not NY17 semantics. It may become only a separately named historical research lineage if the pre-frozen materiality bridge gates pass. It must never be relabelled as Twelve NY17.

Current target status:

`TARGET_BRIDGE_PENDING; MODEL_SCORE_RUN_PROHIBITED`

## 3. Inputs actually evidenced in retained forecasting artifacts

### 3.1 Core monthly / retained Patch surface

The locked CORE5 package and retained Patch code evidence the following historical variables:

- gold monthly average / lagged gold return;
- Federal funds rate;
- Nasdaq level / monthly return;
- USD/CNY level / monthly return;
- GPR;
- GPRT / GPRA are also present in the canonical dataset/research package;
- target-derived lag/rolling features.

The retained Patch architecture additionally used daily returns for:

- Gold;
- Silver;
- Platinum;
- Palladium;

plus a macro vector containing Fed funds, Nasdaq return, USD/CNY return, `log1p(GPR)`, and normalized GPR.

This proves historical use, not successor admission.

### 3.2 Retained VW / SVR research surface

Retained VW rebuild research contains or discusses:

- target-return lags (`MR_lag1`, `MR_lag2`, `MR_lag3`);
- `MR_abs_lag1`, `MR_MA_3`, `MR_MA_6`, `MR_sign_lag1`;
- GPR/GPRT/GPRA;
- GPR-weighted daily return (`weighted_DR`);
- calendar seasonality (`month_sin/cos`, `quarter_sin/cos`);
- DJI;
- DXY;
- Nasdaq 100;
- S&P 500;
- US 10Y yield;
- VIX;
- Hecla preferred (`HL_pb`);
- Newmont (`NEM`);
- DZZ;
- GLL;
- Barrick proxy;
- GVZ proxy/research extension.

Known unresolved legacy inputs remain blocked:

- `GPY` identity conflict;
- exact legacy `long_term_trend` definition;
- exact legacy `volatility` definition;
- exact legacy `g_volatility` identity/definition;
- legacy `^TNX` identity as a current production source;
- exact ICE DXY without licensed/authorized lineage.

The retained VW identity itself is not reproducible and these inputs do not inherit production authorization.

## 4. Successor input lanes

### Lane A — target-only core

**Purpose:** reproducible candidates requiring no external macro/market feature history.

Candidate models:

- `RW_R1`;
- `DRIFT_R1`;
- `MOM3_R1`;
- `DAMPED_TREND_R1`.

Potential feature surface:

- frozen target levels;
- lagged target returns;
- pre-frozen deterministic target transformations where specified.

Readiness:

`BLOCKED_ONLY_BY_HISTORICAL_TARGET_CONTRACT`

Once the target bridge/completeness contract passes, this lane can proceed without waiting for macro PIT reconstruction. It must still use the same frozen replay origin/window contract.

### Lane B — authority-grade macro/market

**Purpose:** common feature surface for `RIDGE_MACRO_R1`, `HUBER_MACRO_R1`, `SVR_RBF_MACRO_R1`.

Preferred minimal domains already admitted by R1 subject to historical availability audit:

- DGS10 / authority 10Y Treasury yield;
- Fed funds / EFFR-equivalent policy-rate domain under an explicitly frozen identity;
- USD/CNY;
- broad USD index `DTWEXBGS` as a proxy, explicitly not ICE DXY;
- Nasdaq 100;
- optionally S&P 500 / DJIA only if the common history and PIT contract supports the frozen evaluation window;
- VIX / GVZ only if historical availability can be reconstructed without treating 2026 retrieval as old-origin knowledge;
- GPR/GPRT/GPRA only with publication/vintage controls.

Current Neon state does not by itself prove old-origin availability. Several direct Fed/Cboe/GPR histories were first retrieved in 2026; several FRED macro contract series currently have zero persisted rows. Historical authority data may be obtainable, but PIT/publication reconstruction is a separate required gate.

Readiness:

`BLOCKED_HISTORICAL_PIT_AVAILABILITY_NOT_YET_PROVEN`

No macro candidate may be scored until a versioned, common feature set and PIT/lag rules are frozen.

### Lane C — legacy-specialized / auxiliary market

Includes:

- four-metal daily mixed-frequency features;
- NEM, Barrick B, HL.PR.B, GLL, DZZ;
- exact/proxy DXY/US10Y legacy identities;
- other archived VW/Patch-specific transformations.

Current Twelve identities for NEM, Barrick B, HL.PR.B, GLL and DZZ are vendor-identity validated and current Neon histories begin in 2016, but those rows were first retrieved in 2026. Therefore identity/coverage is not equivalent to historical PIT readiness. Their use in a historical successor score requires a separately frozen historical-availability contract.

Readiness:

`CONDITIONAL_RESEARCH_ONLY_NOT_IN_COMMON_R1_SCORE_SURFACE`

`PATCH_SUCCESSOR_R1` remains conditional and cannot enter until its complete input pipeline, preprocessing, seeds and fold contract are frozen before comparative scoring.

### Lane D — broader challenger research

Economic/market domains previously researched include real yields/TIPS, breakeven inflation, CPI/PCE, industrial production, MOVE/financial stress, ETF flows/holdings, CFTC positioning, futures curve, options IV/skew, central-bank purchases, China/India demand, jewellery/mine/recycling supply, liquidity and external forecast vintages.

These are not part of the frozen R1 comparative surface and remain:

`RESEARCH_ONLY_REQUIRES_SEPARATE_CHANGE_CONTROL`

They must not delay the minimal reproducible successor lane and must not be added after looking at candidate scores.

## 5. Readiness decision before scoring

The successor validation should be dependency-gated rather than forcing every model to share features that are not historically available.

Proposed R2 structure, to be frozen only after the target bridge result is known:

1. freeze one historical target/evaluation contract;
2. authorize Lane A when target readiness passes;
3. independently audit Lane B historical PIT availability and freeze one minimal common macro feature set before any Lane-B score;
4. keep Lane C outside the common score surface until its own historical PIT/input contract passes;
5. keep Lane D research-only unless a future versioned change-control admits it before scoring.

This does **not** authorize running Lane-A scores yet. The target gate must close first.

## 6. Current blocker summary

- `SUCCESSOR_HISTORICAL_TARGET_NOT_YET_PROVEN`;
- `MACRO_FEATURE_HISTORICAL_PIT_NOT_YET_PROVEN`;
- `LEGACY_SPECIALIZED_FEATURE_HISTORICAL_PIT_NOT_YET_PROVEN`;
- `GOLD_H1_SUCCESSOR_R1_NOT_VALIDATED`;
- no immutable future forecast snapshot/contract issued.

## 7. Immediate next work

1. finish the hardened World Bank ↔ Twelve NY17 target bridge audit;
2. if bridge passes, open a versioned R2 target contract with explicit World Bank research-lineage vs future NY17 separation; if it fails, open evaluation-window change control before any score;
3. update the project manifest after the target result and this input audit are reconciled;
4. execute historical PIT/source-availability audit for the minimal Lane-B feature set;
5. only after the relevant lane gates are frozen, run leakage-safe comparative historical replay.
