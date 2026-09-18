# GOLD CONTROL — DIRECTION_RSM_V1_RESEARCH PREREGISTRATION

**Date:** 2026-09-18  
**Status:** FROZEN BEFORE 2025 PRICE/RETURN OUTCOME INSPECTION  
**Identity:** `DIRECTION_RSM_V1_RESEARCH`  
**Evidence class:** historical research replay only; no production authority

## 1. Objective

Replicate the 52-week rolling Return Signal Momentum direction-of-change method on Gold Control XAU/USD research data and evaluate next-week direction without using 2025 outcomes for any model choice.

## 2. Literature anchor

Liu, Papailias & Quinn (2021), *International Review of Financial Analysis*, 74, 101677, DOI 10.1016/j.irfa.2021.101677.

Source-replication settings used here:
- weekly direction target;
- rolling 52-week information window;
- RSM probability = equally weighted share of positive return signs;
- UP when forecast probability is >= 0.5, DOWN otherwise.

No alternative lookback or probability threshold will be selected from 2025.

## 3. Frozen data source and weekly construction

Series: `XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`.

Semantics:
- provider: Twelve Data;
- research-only series;
- New York-local 16:00 hourly-derived daily close;
- Monday-Friday New York-local observations only;
- no interpolation;
- no forward-fill;
- no alternate-provider substitution.

Weekly close `C_w`:
- calendar week begins Monday;
- select the last available governed weekday observation in that week;
- normally Friday; if Friday is not observed, use the last actually observed governed weekday;
- do not fabricate a Friday value.

Weekly return:
`r_w = ln(C_w / C_(w-1))`.

Binary state:
`x_w = 1[r_w > 0]`; zero/non-positive return maps to 0.

## 4. Frozen RSM-52 forecast

At the close of week w, provided 52 prior weekly return signs exist:

`p_w = (1/52) * sum(x_(w-51), ..., x_w)`.

Target is the return sign of the next represented calendar week `x_(w+1)`.

Direction rule:
- `UP` if `p_w >= 0.5`;
- `DOWN` otherwise.

The probability `p_w` must be retained even when the binary forecast is evaluated.

## 5. Chronology

- 2022-03 onward: warm-up/history only.
- 2023: implementation/development audit after the 52-sign warm-up is satisfied.
- 2024: fixed-rule pre-2025 validation.
- 2025: locked historical test, queried only after this preregistration and implementation are frozen.

RSM has no fitted regression coefficients. The rolling 52-week sign frequency is the only adaptive quantity.

## 6. Metrics

Primary:
- success rate / directional accuracy.

Required diagnostics:
- balanced accuracy;
- Brier score;
- log-loss;
- class counts;
- UP/DOWN forecast counts;
- exact 0.5 probability count;
- baseline comparisons: always-UP and previous-week-sign.

No model choice may be based only on raw hit rate.

## 7. 2025 volatility overlay

The frozen 19-event 2025 abnormal-volatility inventory is not an input to RSM.

Only after the complete 2025 weekly forecast table is generated and frozen:
- map each event date to its calendar target week;
- use the RSM forecast issued at the prior week's close;
- compare event direction with the pre-existing weekly forecast;
- preserve all weekly forecasts, including weeks with no volatility event.

Event-overlay agreement is secondary diagnostic evidence, not the primary weekly direction accuracy.

## 8. Locks

Forbidden:
- 2025-driven window tuning;
- 2025-driven threshold tuning;
- switching source/provider after observing results;
- changing weekly-close semantics after observing results;
- adding FAST/GVZ/BOCPD/Macro/Emergency features in V1;
- flat voting;
- random split;
- relabelling this historical replay as prospective evidence.
