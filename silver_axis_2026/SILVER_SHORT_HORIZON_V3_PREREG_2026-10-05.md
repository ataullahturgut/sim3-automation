# SILVER SHORT-HORIZON V3 — MACRO/RISK BLOCK PREREGISTRATION

**Date:** 2026-10-05  
**Identity:** `GLOBAL_XAG_MACRO_RISK_V3`  
**Status:** PREREGISTERED BEFORE V3 2025/2026 TRANSPORT IS OPENED.

## Motivation

V1/V2 established:
- H1/H3 daily metal-return targets are near chance;
- H5 SILVER_PATH is the weak DEV champion;
- Silver/Gold relative-value and four-metal breadth do not repair 2025-2026 transport.

V3 therefore introduces information not contained in the precious-metal return complex.

## Frozen target

To avoid reopening target selection after V1/V2, V3 keeps:
- target: Silver H5 direction;
- base path: SILVER_PATH.

V3 asks whether exogenous macro/risk information repairs the H5 signal.

## Source clock / availability lags

Reuse the existing reconstructed external research store already used in the Gold project.

Conservative origin-safe joins:
- Federal Reserve H.15 rates: available cutoff = forecast_issue_date - 2 calendar days;
- Federal Reserve H.10 FX: available cutoff = forecast_issue_date - 7 calendar days;
- VIX / Nasdaq-100: available cutoff = forecast_issue_date - 1 calendar day.

These are reconstructed availability research features, not claimed to be original stored PIT observations.

## Feature families

### BASE
SILVER_PATH only.

### RATES
BASE plus:
- DGS10
- DFII10
- BREAKEVEN10_PROXY
- 1-observation changes for all three

### FX
BASE plus:
- BROAD_USD_INDEX
- EURUSD_QUOTE
- GBPUSD_QUOTE
- JPY_PER_USD
- CHF_PER_USD
- CNY_PER_USD
- 1-observation log/level changes as appropriate

### RISK
BASE plus:
- VIX level and 1/5-observation change
- NDX level and 1/5-observation return

### MACRO_RISK
BASE + RATES + FX + RISK.

## Models

Fixed:
- standardized Logistic Regression L2, C=1;
- HistGradientBoosting shallow fixed specification.

Threshold = 0.5. No threshold optimization.

## DEV protocol and selection

- Selection: 2022-2024 only.
- Expanding maturity-safe five-origin blocks.
- Candidate eligible only if balanced accuracy > 50%.
- Primary selection: lowest Brier.
- Within 0.002 Brier: higher balanced accuracy, then accuracy.
- Annual stability reported.

Only after the DEV winner is frozen may 2025 and 2026 transport be opened.

## Transport

Report:
- STATIC_PRE2025
- ADAPTIVE_ORIGIN_SAFE

2025/2026 cannot change V3 configuration.
