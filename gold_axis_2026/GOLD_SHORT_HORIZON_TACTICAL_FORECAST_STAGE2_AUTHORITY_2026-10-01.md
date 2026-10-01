# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 2 H3 Robustness & Feature Representation Authority

**Date:** 2026-10-01  
**Status:** FROZEN PRE-RUN AUTHORITY  
**Parent:** `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_PROJECT_MANIFEST.md`

## 1. Frozen research target

Horizon:
- **H3 only**

Target:
- `r3f = log(P[t+3]/P[t])`
- direction = 1 iff r3f > 0
- quantiles = Q10/Q50/Q90.

No H1/H5 selection in Stage 2.
No 2025 use.

## 2. Frozen Stage-1 models

Direction:
- **XGB_CLASS**
- exact Stage-1 hyperparameters.

Point return:
- **LGBM_REG**
- exact Stage-1 hyperparameters.

Quantiles:
- **LGBM_QUANT**
- exact Stage-1 hyperparameters.

No hyperparameter tuning.

## 3. Frozen chronology

- train/background: 2011-2021
- DEV: 2022-2024
- 2025: frozen / forbidden for selection
- refit every 5 Gold origins
- full H3 label-maturity purge.

## 4. Robustness audit of Stage-1 winners

Report for each frozen H3 winner:
- aggregate DEV
- 2022
- 2023
- 2024
- Gold sigma20 LOW/MID/HIGH tercile.

Primary stability concern:
- no head may be called robust if its aggregate gain is driven by a single year while the other two years materially deteriorate.

This is diagnostic; the Stage-1 PASS is not retroactively changed unless a Stage-2 replacement is explicitly promoted.

## 5. Feature blocks

### GOLD_ONLY
Frozen Stage-1 Gold features:
- r1/r3/r5/r10/r21
- sigma20.

### CORE3
GOLD_ONLY plus:
- Silver r1/r5/r21 + age
- Platinum r1/r5/r21 + age.

### CORE4
CORE3 plus:
- Palladium r1/r5/r21 + age.

CORE4 has shorter pre-DEV history and must be compared honestly under its own available matured training history.

## 6. External transformed representation

Stage-1 raw/as-of external levels are not promoted.

Stage 2 tests only origin-safe transforms derived from the same conservative as-of joined series.

### RATES_XFORM
- DGS10 change over 1 and 5 Gold origins
- DFII10 change over 1 and 5 Gold origins
- breakeven-proxy change over 1 and 5 Gold origins
- nominal-real spread level
- spread change over 5 Gold origins.

### FX_XFORM
For Broad USD, EUR, GBP, JPY, CHF, CNY:
- 1-origin log change
- 5-origin log change.

### VIX_XFORM
- VIX log change 1
- VIX log change 5
- VIX 20-origin z-score, using only prior/current observations.

### NDX_XFORM
- Nasdaq-100 log return 1
- log return 5
- log return 21.

### ALL_XFORM
CORE3 + all transformed blocks above.

No raw external level enters these challenger blocks except the rate spread level explicitly preregistered above.

## 7. Comparison design

For each frozen H3 head, test:
1. GOLD_ONLY
2. CORE3
3. CORE4
4. CORE3 + RATES_XFORM
5. CORE3 + FX_XFORM
6. CORE3 + VIX_XFORM
7. CORE3 + NDX_XFORM
8. CORE3 + ALL_XFORM

All DEV rows remain 2022-2024 H3 origins.

## 8. Primary metrics

Direction:
- Brier primary
- log loss co-primary.

Return:
- MAE primary
- RMSE co-primary.

Quantile:
- mean Q10/Q50/Q90 pinball primary
- empirical coverage supporting.

## 9. Promotion rule

A challenger may replace the Stage-1 head feature contract only if versus that head's current Stage-1 winner on the same DEV population:

- primary metric improves by >= **0.5% relative**
- co-primary is not worse
- no DEV year deteriorates by more than **3% relative** on the primary metric.

Quantile has no separate co-primary; require:
- mean pinball improves >=0.5%
- no DEV year worsens >3%.

If no challenger passes:
- retain the Stage-1 feature block for that head.

## 10. CORE4 rule

Because CORE4 starts later:
- it may be promoted only if the above gate passes despite shorter history;
- shorter history itself is not penalized beyond realized OOS performance;
- do not backfill Palladium.

## 11. No tactical utility yet

No transaction-cost, entry/exit, Sharpe, or position-sizing selection in Stage 2.

## 12. Required outputs

- aggregate head metrics by feature block
- year metrics
- volatility-tercile metrics
- feature-block decisions
- transformed-feature availability audit
- immutable hashes.

## 13. Exact next action

Run Stage 2 on frozen H3 DEV only.

If all three H3 heads retain/earn stable contracts:
- proceed to sequence-model challengers (TCN / GRU / BiGRU), still pre-2025.

If one or more heads prove unstable:
- repair only that head using DEV-authorized representation work before deep models.
