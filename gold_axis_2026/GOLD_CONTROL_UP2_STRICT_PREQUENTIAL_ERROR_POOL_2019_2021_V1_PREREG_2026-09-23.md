# GOLD CONTROL — 2019-2021 STRICT PREQUENTIAL UP-2 ERROR-POOL EXTENSION V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `UP2_STRICT_PREQUENTIAL_ERROR_POOL_2019_2021_V1_RESEARCH`  
**Purpose:** enlarge the historical error pool for a future continuation-mimic veto without using 2025 or 2026  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Research question

Can the already corrected external 2018–2021 XAUUSD source support an additional **2019** route-consistent residual year, so that Frozen One-Sided UP-2 V1 can be reconstructed strictly prequentially over 2019–2021 and yield enough true/false UP-2 calls for failure-detector research?

This study does not fit a veto and does not change UP-2.

## 2. 2019 source reconstruction

Raw source:
`kevingtlin/Market-Data-Lab@922f83a60cc574e7395fb27397077288055a1ef6`.

Daily authority:
`gold_axis_2026/external_data/v2/dukascopy_xauusd_govsession_mid_5m_daily_features_2018_2021.csv`
at commit `509c5ffa762f4ea49644b8ffe723ed2591ba52bf`.

Build 2019 raw path using the same corrected session:
- bid/ask timestamp inner join;
- mid close;
- UTC 5-minute last-close bars;
- America/New_York;
- weekdays;
- remove 17:00–17:55 maintenance;
- require 276 bars/day.

2019 reconstruction must have:
- exact date set versus the frozen daily spine;
- no bad 276-bar days;
- max absolute close difference <=1e-8;
- max RV/DR difference <=1e-12.

## 3. Frozen 2019 SQRT extension

Apply the unchanged frozen SQRT-HAR-DR implementation to target year 2019 using only its allowable prior history.

Report:
- n targets;
- HIGH-RISK alarms;
- actual UP/DOWN among alarms.

No expected alarm count is preregistered because 2019 has not previously been governed under this external extension.

## 4. Frozen 2019 Router-V2 extension

Rebuild the exact frozen direct-expert/context rows from the external daily spine.

For 2019:
- competence history = matured 2018 expert outcomes only;
- within-2019 updates = causal after each matured 2019 target;
- eligibility/ranking is exactly frozen Router V2:
  - expert current vote = UP;
  - n_up >=30;
  - precision >0.50;
  - FPR <0.50;
  - rank by Wilson90 LCB, lower FPR, higher precision, fixed tie order.

No global or future-year fallback.

## 5. 2019 route-consistent residual population

A 2019 row enters the residual pool only if:
- frozen SQRT = HIGH RISK;
- frozen Router V2 = ABSTAIN.

Historical Router-UP cases terminate upstream and do not enter UP-2 formation.

Report exact 2019 residual n and UP/DOWN composition.

## 6. Combined 2019–2021 UP-2 historical pool

Concatenate route-consistent residual rows in chronological order:
- 2019 newly reconstructed;
- frozen-equivalent 2020;
- frozen-equivalent 2021.

The 2020–2021 counts must still reproduce exactly:
- 2020 residual 72 =35 UP +37 DOWN;
- 2021 residual 26 =11 UP +15 DOWN.

Any drift blocks the study.

## 7. Strict nested prequential UP-2 decisions

Use exactly Frozen One-Sided UP-2 Logit V1:
- same 9 features;
- L2 logistic C=1.0;
- same standardization;
- no tuning.

For each combined residual row i:
1. require >=40 prior residual cases;
2. reconstruct strictly prequential probabilities for prior rows j>=40 using only rows before j;
3. require >=20 prior DOWN calibration scores;
4. `tau_i=max(0.50, nearest-rank q80 prior prequential DOWN scores)`;
5. fit frozen UP-2 model on rows strictly before i;
6. score row i;
7. call UP2 iff `p_up > tau_i`.

Unsupported early rows remain NOT_SCORABLE.

## 8. Error-pool sufficiency gate

The historical extension is useful for future veto research only if among strictly scorable 2019–2021 rows:
- UP2 calls >=5;
- FALSE_UP_ACTUAL_DOWN >=2.

This is a sample sufficiency gate only, not model validation.

## 9. Mechanism feature check

For scorable UP2 calls compute the 18 mechanism-gap features already frozen under:
`DIRECTION_MECHANISM_GAP_AUDIT_V1_RESEARCH`.

Report for `last_hour_trend_r2`:
- captured-UP median;
- false-UP actual-DOWN median;
- Cliff's delta.

No veto threshold is selected.

## 10. Governance

- no random split;
- no 2025;
- no 2026;
- no modification of primary Router or UP-2;
- no model/veto fitting under this identity;
- no production writes;
- no runtime promotion.
