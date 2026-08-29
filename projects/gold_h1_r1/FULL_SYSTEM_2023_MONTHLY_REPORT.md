# GOLD H1 R1 — 2023 Monthly Full-System Replay

Frozen upside emergency rule selected on 2010-2022 only: 5D return >= 2.0%, MTD rally >= 3.0%, above SMA50.
Existing downside Emergency R1 preserved: MTD drawdown <= -3.0%, 5D return <= -4.0%, below SMA50.

- Start-of-month 3M strict accuracy: 58.3333%
- Start-of-month economic accuracy excluding exact-flat October: 63.6364%
- Intramonth emergency-adjusted accuracy excluding flat: 72.7273%
- VW MAPE: 1.9602%
- Patch MAPE: 2.1280%
- IDMA MAPE: 2.1824%
- 3M level MAPE: 2.3013%

|Month|Actual|3M|MOM1|VW|Tactical|Emergency|Date|Final|Action|
|---|---:|---:|---:|---:|---|---|---|---:|---|
|2023-01|+1|+1|+1|+1|NEUTRAL|-|-|+1|KEEP_PRIOR|
|2023-02|-1|+1|+1|+1|CONFIRM|-|-|+1|KEEP_PRIOR|
|2023-03|+1|+1|-1|-1|CONFLICT|-|-|+1|LOW_CONFIDENCE_KEEP_PRIOR|
|2023-04|+1|+1|+1|+1|CONFIRM|-|-|+1|KEEP_PRIOR|
|2023-05|-1|+1|+1|+1|CONFLICT|-|-|+1|LOW_CONFIDENCE_KEEP_PRIOR|
|2023-06|-1|+1|-1|-1|CONFLICT|-|-|+1|LOW_CONFIDENCE_KEEP_PRIOR|
|2023-07|+1|+1|-1|-1|CONFLICT|-|-|+1|LOW_CONFIDENCE_KEEP_PRIOR|
|2023-08|-1|-1|+1|+1|CONFLICT|-|-|-1|LOW_CONFIDENCE_KEEP_PRIOR|
|2023-09|-1|-1|-1|+1|CONFIRM|-|-|-1|LOW_CONFIDENCE_KEEP_PRIOR|
|2023-10|+0|-1|-1|-1|CONFIRM|UP_SHOCK|2023-10-13|+1|INTRAMONTH_EMERGENCY_FLIP|
|2023-11|+1|-1|+0|+1|CONFLICT|UP_SHOCK|2023-11-28|+1|INTRAMONTH_EMERGENCY_FLIP|
|2023-12|+1|+1|+1|+1|CONFIRM|-|-|+1|KEEP_PRIOR|

## Contract
- Each month is evaluated separately at its own origin.
- 2023 outcomes do not select the upside emergency rule; selection uses only 2010-2022.
- Tactical disagreement does not automatically flip direction.
- Emergency signals are intramonth; they are reported separately from start-of-month forecast.
- Exact-flat October is shown separately rather than treated as an economic reversal.
