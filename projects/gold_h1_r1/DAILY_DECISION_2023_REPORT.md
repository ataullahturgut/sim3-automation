# GOLD H1 R1 — 2023 Full Daily Decision Engine

Frozen policy selected only on 2010-2022: opposite-vote threshold=3, persistence=2, release=2.
Daily engine evaluates every available D1 bar and emits AL/TUT/SAT. Monthly prior is not recomputed intramonth; Tactical and Emergency are.

- 2023 net return (10 bp/change): 4.84%
- 2023 MDD: -7.14%
- Position changes: 10
- Buy&Hold close-to-close: 12.15%

## Action events
|Date|Action|Reason|Prior|MOM1|Fast|Slow|
|---|---|---|---:|---:|---:|---:|
|2023-03-02|SAT|REVERSAL_CONSENSUS|+1|-1|-1|-1|
|2023-03-14|AL|RETURN_PRIOR|+1|-1|+1|+1|
|2023-06-02|SAT|REVERSAL_CONSENSUS|+1|-1|-1|-1|
|2023-07-04|SAT|REVERSAL_CONSENSUS|+1|-1|-1|-1|
|2023-07-25|AL|RETURN_PRIOR|+1|-1|+1|+1|
|2023-10-13|AL|EMERGENCY_UP|-1|-1|+0|-1|
|2023-11-28|AL|EMERGENCY_UP|-1|+0|+1|+1|

## Monthly
|Month|Prior|End|Strategy|BuyHold|Trades|Actions|
|---|---:|---|---:|---:|---:|---|
|2023-01|+1|LONG|5.74%|4.84%|0|-|
|2023-02|+1|LONG|-5.27%|-6.33%|0|-|
|2023-03|+1|LONG|3.69%|7.19%|2|2023-03-02 SAT(REVERSAL_CONSENSUS); 2023-03-14 AL(RETURN_PRIOR)|
|2023-04|+1|LONG|1.09%|0.30%|0|-|
|2023-05|+1|LONG|-1.37%|-1.00%|0|-|
|2023-06|+1|CASH|-0.83%|-2.93%|1|2023-06-02 SAT(REVERSAL_CONSENSUS)|
|2023-07|+1|LONG|-0.05%|2.28%|3|2023-07-04 SAT(REVERSAL_CONSENSUS); 2023-07-25 AL(RETURN_PRIOR)|
|2023-08|-1|CASH|-1.16%|-0.21%|1|-|
|2023-09|-1|CASH|0.00%|-4.73%|0|-|
|2023-10|-1|LONG|2.52%|8.52%|1|2023-10-13 AL(EMERGENCY_UP)|
|2023-11|-1|LONG|-0.52%|2.73%|2|2023-11-28 AL(EMERGENCY_UP)|
|2023-12|+1|LONG|1.32%|-0.44%|0|-|

## Contract
- 2023 outcomes are not used for policy selection.
- Daily Fast Tactical is recomputed every D1 bar; Slow Tactical updates only after a completed Sunday-Friday week.
- MOM1 is known at month origin from prior completed month.
- Emergency rules are frozen pre-2023.
- Long/cash only; 10 bp per position change.
- VW remains level/secondary monthly context; exact pre-2023 VW execution history is not reproducible, so it is not used to tune the daily state machine.
