# GOLD MONTHLY — October 2026 Forecast Authority

**Date:** 2026-10-01  
**Target:** 2026-10 calendar-month average XAU/USD  
**Origin:** 2026-09 month end  
**Status:** AUTHORIZED FOR SEPTEMBER-COMPLETE FORWARD RESEARCH FORECAST

## 1. Objective

Produce the October 2026 forward forecast after September 2026 daily market data is complete.

Primary model:
- **ChHHO-ANFIS** — current main GOLD MONTHLY model.

Comparator:
- **DE-ABC RBFNN** — frozen competitive challenger, descriptive only.

## 2. Chronology

Only information available by the end of 2026-09 may enter the forecast.

Required:
- September-complete daily Gold/Silver/Platinum/Palladium observations;
- official GPR origin vintage for 2026-09;
- historical data through September 2026 for model fitting;
- no October 2026 price/market data.

The October target row is feature-only and contains no target outcome.

## 3. Frozen feature/model contract

Preserve the project's existing 8-feature VW-MIDAS contract:
- four metals;
- previous-month log return;
- origin-month GPR-weighted daily return.

No new feature, optimizer, threshold, or model parameter may be selected from September/October outcomes.

## 4. September-complete training update

Unlike the 2026-09-29 provisional October nowcast:
- September daily data must extend through **2026-09-30**;
- the September monthly metal averages are considered complete for the feature/return panel;
- model training may therefore include target month **2026-09**;
- October itself is never used as training Y.

## 5. Forecast level conversion

Preferred origin level:
1. official World Bank 2026-09 monthly Gold value if already published by execution time;
2. otherwise the **complete September StakTrakr daily Gold monthly average**.

If (2) is used, the result must be labeled:
**SEPTEMBER_COMPLETE_FEATURES / FULL_MONTH_STAK_LEVEL_PROXY**

and must not be described as canonical World-Bank-level final until the official September monthly Gold observation is available.

No post-hoc scaling between sources is allowed.

## 6. Data quality gates

Require:
- common four-metal daily coverage through 2026-09-30;
- at least 18 common daily observations in September;
- all four September monthly metal averages finite and positive;
- exact official GPR 202609 archive available;
- frozen DEV snapshot unchanged;
- Neon disabled for this public-source execution.

## 7. Outputs

For each model:
- predicted Gold log return;
- September origin level and source;
- October average-price forecast;
- training-row count and model diagnostics;
- full source/provenance metadata;
- final/proxy status.

No alarm/rescue action is inferred from the price forecast alone.
