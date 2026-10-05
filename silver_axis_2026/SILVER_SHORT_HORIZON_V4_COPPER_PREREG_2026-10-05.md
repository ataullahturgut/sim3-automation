# SILVER SHORT-HORIZON V4 — COPPER / INDUSTRIAL-STATE PREREGISTRATION

**Date:** 2026-10-05  
**Identity:** `GLOBAL_XAG_COPPER_STATE_V4`  
**Status:** PREREGISTERED BEFORE V4 2025/2026 TRANSPORT IS OPENED.

## Motivation

V1/V2 show that Silver-only and precious-metal relative-value daily features do not transport.  
V3A shows that daily macro/risk information does not displace the frozen Silver-path baseline under the DEV selection rule.

V4 tests a genuinely different Silver mechanism: **industrial-demand state**, represented by Copper.

## Target

Frozen from V1/V2:
- Silver H5 direction.

## Copper source and clock

- World Bank Pink Sheet monthly Copper price.
- Native frequency is monthly; no daily interpolation is treated as new information.
- To avoid publication-timing leakage, every daily Silver origin may use only Copper data from **two calendar months before the forecast-issue month**.
  - Example: a June origin may use April Copper data, not May/June.
- This is deliberately conservative.

## Candidate blocks

### BASE
Frozen Silver path.

### COPPER
BASE plus:
- Copper 1-month log return;
- Copper 3-month log return;
- Copper 12-month rolling z-score.

### COPPER_RATES
COPPER plus:
- DGS10 5-observation change;
- DFII10 5-observation change;
- breakeven 5-observation change.

### COPPER_RISK
COPPER plus:
- VIX level / 5-observation change;
- NDX 5-observation return.

### COPPER_MACRO
COPPER + rates + broad USD 5-observation return + VIX/NDX risk state.

## Model / validation

- Standardized Logistic Regression L2, C=1.
- Threshold 0.5.
- 2022-2024 DEV only for selection.
- Expanding maturity-safe five-origin blocks.
- Eligible only if aggregate DEV BA > 50%.
- Primary lowest Brier; within 0.002 choose higher BA, then accuracy.
- 2025/2026 are opened only after DEV winner is frozen.

No 2025/2026 result may retune V4.
