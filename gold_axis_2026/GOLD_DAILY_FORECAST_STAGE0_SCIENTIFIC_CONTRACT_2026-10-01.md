# GOLD DAILY FORECAST — Stage 0 Scientific Contract

**Date:** 2026-10-01  
**Status:** FROZEN PROJECT-INITIATION AUTHORITY  
**Parent research program:** GOLD MONTHLY FORECAST  
**Canonical daily manifest:** `gold_axis_2026/GOLD_DAILY_FORECAST_PROJECT_MANIFEST.md`

## 1. Scope

This is a **separate daily-frequency forecasting project**. It is not the monthly ChHHO model executed more often.

Primary task:
- forecast the **next common-market-day XAU/USD daily reference price**;
- H=1 common trading/observation day;
- default modeling target = next-day Gold log return, reconstructed to price;
- Gold is the scored primary target.

Multi-output Gold/Silver/Platinum/Palladium architectures may be used where the model family requires or benefits from joint learning, but family parity does not override the Gold primary score.

## 2. Observation identity

The exact daily price timestamp/source convention must be frozen by Stage 1 Data Authority Audit before production-grade modeling.

Until then:
- historical StakTrakr four-metal series are **research reconstruction**, not PIT-proven;
- current/public daily rows may be used only under their explicit source/timestamp provenance;
- no source convention may be silently changed between training and evaluation.

No "daily close" claim is authorized unless the source audit proves that the governed series is in fact a close-price series.

## 3. Chronology and outcome status

Prior daily experiments already inspected 2026-01-02..2026-07-31. Therefore:
- **2026 is opened / retrospective evidence**, not a blind test;
- 2026 outcomes may not select model family, feature set, hyperparameters, thresholds or ensemble weights.

Model-development authority:
- all selection/tuning must use data ending **no later than 2025-12-31**;
- evaluation inside development must be chronological / expanding or rolling;
- no random split.

Prospective evidence:
- forecasts issued after the 2026-10-01 project freeze and timestamped before their outcomes form the clean prospective ledger.

## 4. Primary metrics

Primary:
1. cumulative absolute price error, Σ|P_hat-P|;
2. MAE in USD;
3. daily direction accuracy versus prior governed daily reference price.

Supporting:
- RMSE;
- MAPE/WAPE;
- error vs random-walk persistence;
- return correlation;
- predicted-return dispersion / collapse-to-zero diagnostic;
- worst-day error;
- monthly and regime stability.

A candidate must beat or materially improve on persistence under a frozen protocol; directional accuracy alone is insufficient.

## 5. Mandatory baselines

Every governed model comparison must include:
- **RW / previous governed daily price**;
- zero-return forecast;
- simple historical-mean / drift control where chronology-safe.

No complex model may be promoted without reporting against persistence.

## 6. Candidate data families

### Core four-metal daily layer
- Gold
- Silver
- Platinum
- Palladium.

### Macro / cross-market daily candidates
Subject to Stage 1 source/PIT audit:
- nominal rates;
- real rates / breakeven proxy;
- Broad USD and selected FX;
- VIX;
- Nasdaq-100;
- WTI;
- Brent.

Monthly-only availability does not qualify as daily input. A daily family is blocked until a governed daily source and release/timestamp convention are proven.

### GPR
GPR may be used only with explicit publication/vintage timing. Daily use must not import target-month information unavailable at the daily origin.

## 7. Feature-family principles

Daily analogues must be explicitly defined; monthly features are not mechanically copied.

Allowed research families after Stage 1:
- 1-day / multi-day returns;
- rolling momentum;
- realized volatility;
- range / drawdown;
- causal distributed-lag / MIDAS summaries;
- GPR-adaptive daily-return summaries;
- cross-metal dispersion / breadth;
- rates / FX / risk / oil daily-path summaries.

Every transform must use information available by the daily forecast origin timestamp.

## 8. Prior daily evidence and supersession

### Daily V1
`GOLD_DAILY_H1_TOP_FAMILY_EXPLORATORY_2026-09-26.md`

Status:
**INVALID AS GOVERNED DAILY BACKTEST / SUPERSEDED**

Reason:
- silently replaced the governed GPR-adaptive structure with generic 20-day EWMA;
- four-metal historical daily PIT provenance not proven.

Its performance table may not select a daily model.

### Daily V2
`GOLD_DAILY_H1_V2_GPR_MIDAS_AUDIT_2026-09-26.md`

Status:
**VALID RETROSPECTIVE FREQUENCY-TRANSFER AUDIT / NOT PRODUCTION**

Frozen V2:
- 8 inputs = for each metal 21-session return + GPR-adaptive trailing-21 weighted daily return;
- four outputs jointly;
- 2026 Jan-Jul not used for fit/selection;
- PIT timing logic passed;
- daily metal source provenance remained reconstruction-only.

2026 Jan-Jul results:
- RW MAE ≈ 61.59 USD;
- AOA-ELM ≈ 61.75;
- FULL7 ≈ 61.95;
- REDUCED4 ≈ 61.99;
- SMA-ELMFIS ≈ 61.96;
- all headline transfers failed to beat RW MAE;
- daily return predictions showed strong shrinkage toward zero.

Binding interpretation:
monthly champions do not transfer directly to daily H=1 under the tested analogue. Do not rerun the same V2 family transfer and call it new evidence.

## 9. Stage gates

### Stage 0 — scientific contract
This document. COMPLETE when committed.

### Stage 1 — Daily Data Authority & PIT Audit
Must determine:
- exact Gold/Silver/Platinum/Palladium daily source and observation timestamp;
- historical coverage and common-day calendar;
- PIT status;
- daily Rates source/timestamp;
- daily FX source/timestamp;
- VIX source/timestamp;
- daily Nasdaq-100 source/timestamp;
- daily WTI/Brent source/timestamp;
- GPR daily-origin vintage rule;
- missing-day and holiday policy.

No governed model development before Stage 1 is PASS.

### Stage 2 — Baseline & Feature Contract
Freeze:
- persistence baseline;
- primary target reconstruction;
- development window;
- daily feature blocks;
- scaling and lag rules.

### Stage 3 — Model-family screen
Start parsimoniously. Monthly champions are references, not automatic first choices.

### Stage 4 — Robustness / ensemble
Only after a DEV leader exists.

### Stage 5 — Opened 2026 transport
Descriptive only; no retuning.

### Stage 6 — Prospective daily ledger
Timestamped forecasts before outcomes.

## 10. Current authorized next action

**Stage 1 — Daily Data Authority & PIT Audit.**

No daily champion exists yet.
No production daily forecast is authorized yet.
