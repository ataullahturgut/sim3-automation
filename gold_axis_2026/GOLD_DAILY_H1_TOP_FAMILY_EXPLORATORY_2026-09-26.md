# GOLD MONTHLY TOP FAMILIES — DAILY H=1 EXPLORATORY BACKTEST

**Date:** 2026-09-26  
**Status:** COMPLETE — EXPLORATORY ONLY

## Purpose
Test whether the current monthly-family leaders retain predictive value when adapted to a next-trading-day price problem.

This is **not** the monthly model evaluated more frequently. It is a new daily H=1 adaptation of the same model families.

## Daily target
- Target: next weekday/common-market-day XAU price.
- 4 outputs jointly: next-day log return of Gold/Silver/Platinum/Palladium.
- 8 origin-safe daily inputs:
  - latest 1-day log return for each metal;
  - 20-day EWMA of log returns for each metal.
- Saturday/Sunday reconstruction rows excluded.
- Source series: frozen StakTrakr research daily series for XAU/XAG/XPT/XPD.
- Source status: APPROVED_HISTORICAL_RESEARCH_RECONSTRUCTION_NOT_PIT.

## Freeze/test protocol
- Training window: last 504 weekday/common-metal labelled observations ending by 2025-12-31.
- Model parameters frozen before 2026.
- No 2026 retraining.
- Training-only normalization frozen before 2026.
- Optimizer inner validation: chronological final 20% of the frozen training window where applicable.
- Test: 2026-01-02 through 2026-07-31.
- n = 145 weekday observations.
- August-September unavailable under the same 4-metal source contract because those governed metal series stop at 2026-07-31.

## Results

| Model | MAE USD | MAPE % | RMSE USD | Direction | Correct directions |
|---|---:|---:|---:|---:|---:|
| Random walk (previous price) | **61.59** | **1.3285** | 90.63 | n/a | n/a |
| SCA-ANN single | 62.11 | 1.3411 | 90.97 | 48.97% | 71/145 |
| MPA-ANN single | 62.31 | 1.3458 | 91.98 | 48.28% | 70/145 |
| **FULL7 ANN** | **62.60** | **1.3522** | 91.43 | **51.03%** | **74/145** |
| Adaptive TLBO-ANN | 62.76 | 1.3567 | 91.76 | 47.59% | 69/145 |
| **REDUCED4 ANN** | **62.83** | **1.3567** | 91.48 | **50.34%** | **73/145** |
| MPA+SCA ANN | 62.88 | 1.3595 | 91.57 | 46.21% | 67/145 |
| TLBO-tuned PSO ANN | 63.05 | 1.3625 | 91.76 | 48.97% | 71/145 |
| **AOA-ELM** | **63.19** | **1.3642** | **90.80** | **48.97%** | **71/145** |
| DE-ABC ANN | 63.37 | 1.3693 | 91.63 | 48.97% | 71/145 |
| Vanilla ANN | 65.88 | 1.4216 | 93.85 | 50.34% | 73/145 |
| **SMA-ELMFIS** | **70.66** | **1.5451** | **99.42** | **48.97%** | **71/145** |

## Interpretation
1. The monthly champions do **not** transfer cleanly to next-day price forecasting under this simple daily adaptation.
2. FULL7 ANN is the strongest of the four current top-family roles on direction, but only 74/145 = 51.03%.
3. On price error, the previous-day-price random walk is slightly better than every tested model.
4. SMA-ELMFIS loses the monthly-direction advantage when moved to daily H=1; it is 71/145 = 48.97%.
5. Therefore no daily version is promoted from this exploratory run.

## Governance
- 2026 used for training/tuning: NO.
- Random split: NO.
- Weekend reconstruction rows: EXCLUDED.
- Daily model selection based on 2026: NO.
- This experiment changes the target/frequency and therefore must not be mixed with the monthly H=1 family ranking.

## Run
Workflow: `Gold Daily H1 Top Family Exploratory V1`  
Final clean weekday run: **36200611626 — SUCCESS**  
Commit: `f0f01ae600f30c0e9db42bc18697e3b64c8de80b`
