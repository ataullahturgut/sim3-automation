# GOLD H1 R1 — 2023 Intramonth Trading Replay

Chosen policy (selected only on 2010-2022): **monthly**.

- 2023 strategy net return (10 bp per position change): 5.93%
- 2023 max drawdown: -9.58%
- 2023 position changes: 2
- Buy-and-hold close-to-close: 12.15%
- Monthly-prior-only net return: 5.93%
- Monthly-prior-only MDD: -9.58%
- Monthly-prior-only position changes: 2

## Monthly results
|Month|Prior|End pos|Strategy|Buy&Hold|Trades|First change|Actions|
|---|---:|---:|---:|---:|---:|---|---|
|2023-01|+1|LONG|5.74%|4.84%|0|-|-|
|2023-02|+1|LONG|-5.27%|-6.33%|0|-|-|
|2023-03|+1|LONG|7.76%|7.19%|0|-|-|
|2023-04|+1|LONG|1.09%|0.30%|0|-|-|
|2023-05|+1|LONG|-1.37%|-1.00%|0|-|-|
|2023-06|+1|LONG|-2.19%|-2.93%|0|-|-|
|2023-07|+1|LONG|2.38%|2.28%|0|-|-|
|2023-08|-1|CASH|-1.16%|-0.21%|1|2023-08-01|2023-08-01 SAT|
|2023-09|-1|CASH|0.00%|-4.73%|0|-|-|
|2023-10|-1|CASH|0.00%|8.52%|0|-|-|
|2023-11|-1|CASH|0.00%|2.73%|0|-|-|
|2023-12|+1|LONG|-0.54%|-0.44%|1|2023-12-01|2023-12-01 AL|

## Policy scorecard (selection periods only)
|Policy|DEV net|DEV MDD|VAL net|VAL MDD|2023 net|2023 MDD|
|---|---:|---:|---:|---:|---:|---:|
|monthly|18.49%|-42.30%|-1.48%|-11.62%|5.93%|-9.58%|
|fast|24.76%|-24.28%|-6.29%|-18.27%|-0.96%|-10.10%|
|slow|-15.87%|-57.31%|-10.20%|-20.54%|-1.44%|-12.77%|
|dual|-7.47%|-53.72%|-9.77%|-18.07%|4.10%|-9.54%|
|dual2|-0.90%|-48.72%|-7.98%|-17.47%|5.33%|-8.77%|

## Contract
- 2023 is never used to select the execution policy.
- Monthly prior is the existing 3M direction layer.
- Fast Tactical = daily close vs SMA20 with 2-market-day persistence.
- Slow Tactical = completed Sunday-Friday weekly close vs SMA4 with 2-completed-week persistence.
- Direction takers update position only after signals are observable.
- Long/cash only; no shorting.
- Transaction cost = 10 bp per position change.
