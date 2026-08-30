# GOLD H1 R1 — Full Daily Investment Engine 2026 R4

## Contract
- Replay window: 2026-01-01 through latest completed D1 bar 2026-08-28; Aug-30 is Sunday, so no synthetic weekend price is created.
- D1 source lock: simom1/XAUUSD-history@a33d38a29cc84aa0cd641ae07bee80874a6cfb7b.
- Position is continuous LONG/CASH; 10bp per position change; close-t action applies from next bar.
- Monthly price forecasts are monthly-average anchors/context, never daily targets.
- 2026 outcomes are NOT used to select/tune any execution threshold.
- Fast/Slow, GVZ and BOCPD remain evidence/risk context only.
- Execution-authorized intramonth rules were frozen pre-2023: Price Emergency DOWN/UP and Macro Event DOWN.
- Macro Event UP remains context-only/rejected.

- YTD net return: 8.4141%
- YTD MDD: -20.4792%
- Position changes: 7
- D1 close-to-close buy&hold comparator: 6.0271%
- Current position at 2026-08-28 close: LONG
- Current close: 4593.71
- August 3M monthly-average forecast: 3878.43 (DOWN from July 4073)

## August main price experts
- rw: 4073.0
- 3m_momentum: 3878.434368295046
- vw_midas_msvr: 4090.462171912403
- causal_patch_transformer: 4081.814211214794

## Trades
|Date|Close|Action|Reason|Prior|Fast|Slow|GVZ|Evidence|
|---|---:|---|---|---:|---:|---:|---:|---|
|2026-01-02|4332.58|AL|INITIAL_MONTHLY_ANCHOR|+1|+1|+1|23.80|ANCHOR_CONFIRMED|
|2026-03-18|4818.56|SAT|MACRO_EVENT_DOWN|+1|-1|+0|29.42|MACRO_EVENT_REVERSAL_DOWN|
|2026-04-01|4756.82|AL|MONTHLY_ORIGIN_REEVALUATION|+1|-1|-1|36.11|TACTICAL_REVERSAL_CONFIRMED|
|2026-04-30|4566.37|SAT|MACRO_EVENT_DOWN|+1|-1|+0|26.64|MACRO_EVENT_REVERSAL_DOWN|
|2026-05-12|4765.54|AL|PRICE_EMERGENCY_UP|-1|+0|-1|27.16|PRICE_SHOCK_UP|
|2026-06-01|4537.57|SAT|MONTHLY_ORIGIN_REEVALUATION|-1|-1|-1|25.64|ANCHOR_CONFIRMED|
|2026-08-06|4277.13|AL|PRICE_EMERGENCY_UP|-1|+1|-1|24.86|PRICE_SHOCK_UP|

## Monthly
|Month|3M prior|Actual completed|Main forecast context|Forecast|End pos|Actions|
|---|---:|---:|---|---:|---|---|
|2026-01|+1|1.0|patch|4360.65041761|LONG|2026-01-02 AL(INITIAL_MONTHLY_ANCHOR)|
|2026-02|+1|1.0|patch|4918.79269951|LONG|-|
|2026-03|+1|-1.0|patch|5092.11234674|CASH|2026-03-18 SAT(MACRO_EVENT_DOWN)|
|2026-04|+1|-1.0|momentum|5060.83558668|CASH|2026-04-01 AL(MONTHLY_ORIGIN_REEVALUATION); 2026-04-30 SAT(MACRO_EVENT_DOWN)|
|2026-05|-1|-1.0|momentum|4714.24120498|LONG|2026-05-12 AL(PRICE_EMERGENCY_UP)|
|2026-06|-1|-1.0|momentum|4451.14254182|CASH|2026-06-01 SAT(MONTHLY_ORIGIN_REEVALUATION)|
|2026-07|-1|-1.0|momentum|4038.51634964|CASH|-|
|2026-08|-1|PARTIAL|AUG_CONTEXT|see expert block|LONG|2026-08-06 AL(PRICE_EMERGENCY_UP)|

## Source/authority status
- GVZ: official Cboe daily history; non-directional.
- Macro actual/consensus through Apr-26: pinned fred-us-macro-open-data@c3e2d4c79868ee516dc0ed111e1e4a28608a3a8b; Apr-30 Core PCE exact calendar evidence appended. After May-1 the monthly prior is DOWN, so the authorized Macro Event DOWN rule is not execution-eligible; missing later consensus history therefore cannot change R4 execution.
- August target month is incomplete. August actual monthly direction is NOT scored. Daily execution through Aug-28 is current-state replay.
- 2026 hierarchy that fixed Apr diagnostically remains DIAGNOSTIC_ONLY and is not granted execution authority after seeing 2026.
