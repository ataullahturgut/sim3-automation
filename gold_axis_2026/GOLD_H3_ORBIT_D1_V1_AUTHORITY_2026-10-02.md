# ORBIT-D1 V1 — DAILY CROSS-MARKET INFORMATION SCREEN AUTHORITY

**Date:** 2026-10-02
**Identity:** `ORBIT_D1_V1_RESEARCH`
**Parent:** `AURORA_H3_V1_RESEARCH`
**Status:** PREREGISTERED / RESEARCH-ONLY

## 1. Objective

Before paying the complexity cost of hourly cross-market history, test whether **daily cross-market state** contains incremental H3 direction information beyond frozen AURORA.

This is an information-family screen, not a production model.

## 2. Base probability

AURORA remains the base forecast.

For each candidate block:

`logit(p_ORBIT_BLOCK) = logit(p_AURORA) + beta' z_block`

The AURORA coefficient is fixed at 1.0.

Residual beta is fit by ridge-penalized Bernoulli likelihood with **lambda=10 fixed ex ante**.

## 3. Candidate daily blocks

### METALS_D1
Source: frozen StakTrakr common-metal daily snapshot already used by the Global-XAU project.

Features:
- XAG r1 / r3 / r5
- XPT r1 / r3 / r5
- XPD r1 / r3 / r5
- 1d metals breadth = mean(sign(XAG,XPT,XPD r1))
- 1d metals dispersion = std(XAG,XPT,XPD r1)
- Gold-minus-metal-basket r1
- Gold-minus-metal-basket r3.

Timing:
- values through feature_cutoff_date.
- Evidence class: retrospective research snapshot / not original PIT.

### USD_D1
Official Federal Reserve H.10 historical reconstruction.

Features:
- broad USD log return 1 / 3 / 5 observations
- CNY-per-USD log return 1 / 3 / 5 observations
- major-FX USD breadth across EUR, GBP, JPY, CHF, CNY over 1 observation
- major-FX dispersion over 1 observation.

Conservative availability:
- cutoff = feature_cutoff_date - **7 calendar days**.

### RATES_D1
Official Federal Reserve H.15 historical reconstruction.

Features:
- nominal 10Y change 1 / 3 / 5 observations
- real 10Y change 1 / 3 / 5 observations
- 10Y breakeven-proxy change 1 / 3 / 5 observations.

Conservative availability:
- cutoff = feature_cutoff_date - **2 calendar days**.

### RISK_D1
- Cboe VIX official history
- Nasdaq-100 daily history distributed through FRED/Nasdaq source lineage.

Features:
- VIX log return 1 / 3 / 5 observations
- VIX 20-observation level z-score
- NDX log return 1 / 3 / 5 observations
- NDX 5-observation realized volatility.

Conservative availability:
- cutoff = feature_cutoff_date - **1 calendar day**.

## 4. No feature search

Feature definitions above are fixed before outcomes.

No per-feature dropping, sign flipping, threshold search, or interactions are allowed in V1.

## 5. Chronology

For every monthly test block:
- fit only rows with `target_end_date_h3 <= first test feature cutoff`;
- standardizer fit on that same matured training set only;
- no random split.

Evaluation:
- Apr-Jun 2022: warm-up only
- **Jul-Dec 2022: block selection authority**
- **2023: frozen confirmation 1**
- **2024: frozen confirmation 2**
- 2025: frozen transport
- 2026: frozen stress transport.

## 6. Block selection gate — 2022 H2 only

A block is eligible if:
- balanced accuracy >= matched AURORA
- accuracy >= AURORA -0.5 pp
- Brier <= AURORA +0.0025
- prediction std >=0.02.

Each block is judged independently.

No cross-block combination is allowed in V1.

## 7. Frozen confirmation

A selected/eligible block becomes an **hourly-data candidate** only if separately in 2023 and 2024:
- accuracy >= AURORA -1 pp
- balanced accuracy >= AURORA -1 pp
- Brier <= AURORA +0.003

and in 2023-2024 aggregate:
- balanced accuracy >= AURORA
- Brier <= AURORA.

Only then may 2025/2026 be interpreted as transport evidence.

## 8. Hourly acquisition decision

- If no block passes: do not build broad hourly cross-market data yet.
- If one or more blocks pass: acquire hourly history **only for the passing information families**, preserving the same economic variables where possible.
- Daily success does not authorize promotion over AURORA; it only justifies hourly research.

## 9. Governance

These public historical daily series are retrospective reconstructions, not proof that the current database physically stored each observation at the historical origin. Conservative release lags are therefore mandatory and results must be labelled **RECONSTRUCTED_AVAILABILITY_RESEARCH**.

The already frozen AURORA prospective ledger is untouched.
