# GOLD MONTHLY — ETF I1/I2 Historical Recurrence + I2 Episode Robustness Result

**Date:** 2026-09-30
**Status:** COMPLETE / SCIENTIFIC_GATES=PASS
**Scope:** model-free historical recurrence of ETF dynamic mechanisms. No routing/model switching.

## 1. Historical recurrence run

Authority:
- `GOLD_MONTHLY_CHHHO_ETF_I1_I2_HISTORICAL_RECURRENCE_V1_AUTHORITY_2026-09-30.md`
- authority commit: `4119c164e763680da65b8b6ca477b5eafa7fc89d`

Execution:
- workflow: **Gold Monthly ETF I1 I2 Historical Recurrence V1**
- run: **36705282325**
- artifact: **11091154474**
- code commit: `e9268fac4d823fbbaf9ad44f0e0c582f7fe6a9f8`
- workflow commit: `001b329935018456bb566c85df8715876daed61c`
- scientific gate: **PASS**

Outcome is next-month GLD absolute log return. Fixed thresholds:
- MOVE_3 >= 3 percentage points
- MOVE_5 >= 5 percentage points
- MOVE_8 >= 8 percentage points

This is a market-regime recurrence test, not a ChHHO-error backcast.

## 2. I1 — ETF FLOW DETERIORATION

Frozen rule:
- month-to-month deterioration in combined GLD/IAU flow <= **-4.2816pp**.

### 2010-2020

- events: **14**
- event mean next-month absolute move: **4.03pp**
- non-event mean: **3.62pp**
- mean ratio: **1.11x**
- bootstrap ratio 95% CI: **0.75x..1.57x**
- MOVE_3 event rate: **64.3%**
- MOVE_3 non-event: **50.0%**
- relative risk: **1.29x**
- Fisher p: **0.234**
- MOVE_5 event rate: **28.6%**
- MOVE_5 non-event: **29.7%**
- relative risk: **0.96x**
- Fisher p: **0.641**

Interpretation:
**I1 does not show robust historical large-move enrichment.**

It remains useful as a specific 2022-05 transition descriptor, but historical recurrence does not support promotion to a general storm alarm.

### Later descriptive transport

2021-2024:
- one I1 event: origin 2022-04
- next-month GLD absolute move: **3.32pp**
- this corresponds to target 2022-05, a HIGH-APE ChHHO miss.

2025-2026 Aug:
- one I1 event: origin 2026-03
- next-month absolute move: **1.55pp**
- no large-move confirmation.

Binding status:
**I1 = transition descriptor / candidate warning; not historically validated as a general high-movement alarm.**

## 3. I2 — ETF REDEMPTION PERSISTENCE

Frozen base rule:
- GLD and IAU both contract for at least **2 consecutive months**.

### Raw monthly-state recurrence, 2010-2020

- I2-active months: **21**
- event mean next-month absolute move: **4.94pp**
- non-event mean: **3.43pp**
- mean ratio: **1.44x**
- bootstrap ratio 95% CI: **1.08x..1.88x**
- MOVE_3: **76.2%** vs **46.8%**, RR **1.63x**, Fisher p **0.0118**
- MOVE_5: **57.1%** vs **24.3%**, RR **2.35x**, Fisher p **0.00383**
- MOVE_8: no enrichment

Initial interpretation:
I2 is strongly associated with elevated next-month medium/large Gold movement, especially the 3-5% range.

## 4. Required de-clustering: I2 episode-entry robustness

Long I2 streaks create serially dependent repeated months, especially the 2013 episode. A separate pre-registered robustness audit collapsed each continuous I2 run to its **first entry month**.

Authority:
- `GOLD_MONTHLY_ETF_I2_EPISODE_ROBUSTNESS_V1_AUTHORITY_2026-09-30.md`
- authority commit: `6d432dc1e373697bca3142630346c7b4724164d8`

Execution:
- workflow: **Gold Monthly ETF I2 Episode Robustness V1**
- run: **36705483191**
- artifact: **11091313948**
- code commit: `7f2b4093812f016a7aa46592276aecc74ae9bafc`
- workflow commit: `dcd2bb9e3d98d47e37b7eac9da83975c9f8f5fca`
- scientific gate: **PASS**

### 2010-2020 independent episode entries

Exactly **8** I2 episode entries:
- 2012-04
- 2013-03
- 2014-05
- 2014-09
- 2015-12
- 2016-12
- 2018-06
- 2019-05

Next-month absolute GLD moves:
- 6.55pp
- 7.86pp
- 6.13pp
- 3.10pp
- 5.28pp
- 5.28pp
- 2.27pp
- 7.70pp

Results:
- mean absolute next move: **5.52pp**
- non-entry mean: **3.55pp**
- mean uplift: **+1.97pp**
- mean ratio: **1.56x**
- bootstrap ratio 95% CI: **1.14x..2.01x**

MOVE_3:
- episode entry: **7/8 = 87.5%**
- non-entry: **49.2%**
- relative risk: **1.78x**
- Fisher one-sided p: **0.0377**

MOVE_5:
- episode entry: **6/8 = 75.0%**
- non-entry: **26.6%**
- relative risk: **2.82x**
- Fisher one-sided p: **0.00839**

MOVE_8:
- episode entry: 0/8
- no enrichment.

Key interpretation:
**The I2 result survives and strengthens after serial-dependence correction.**
The 2010-2020 finding is not an artifact of counting every month of the 2013 redemption streak as an independent observation.

## 5. Transport stability

### 2021-2024 episode entries

I2 entries:
- 2021-03
- 2021-08
- 2022-06
- 2023-07
- 2024-02

Results:
- mean next-month absolute move: **3.80pp**
- non-entry mean: **3.27pp**
- ratio: **1.16x**
- bootstrap ratio CI: **0.62x..1.99x**
- MOVE_3: 60.0% vs 39.5%
- MOVE_5: 20.0% vs 25.6%
- no statistically stable enrichment.

Therefore the very strong 2010-2020 I2 magnitude effect weakens materially in 2021-2024.

However, among the three I2 episode entries that fall inside the canonical DEV ChHHO era:
- origin 2022-06 -> target **2022-07 HIGH APE**
- origin 2023-07 -> target **2023-08 HIGH APE**
- origin 2024-02 -> target **2024-03 HIGH APE**

Thus the episode-entry state is still highly relevant to the observed ChHHO error mechanism in DEV, even though next-month market-move magnitude transport is weaker.

### 2025-2026 Aug

Only one new I2 episode entry:
- origin **2026-06**
- next-month GLD move: **+0.85pp**
- target 2026-07 is not HIGH APE.

This is a clear counterexample to any claim that I2 always precedes a large move or a ChHHO high error.

## 6. Relation to the four core HIGH-error misses

Previously unexplained core:

### 2022-05 / origin 2022-04
- I1 = TRUE
- next-month GLD move = -3.32pp
- I1 historical evidence is weak.
- Treat as transition-warning evidence, not validated storm mechanism.

### 2022-07 / origin 2022-06
- I2 episode entry = TRUE
- next-month GLD move = -2.62pp
- ChHHO APE = 3.75% HIGH.
- The model error is large even though market movement itself is slightly below 3pp.

### 2022-09 / origin 2022-08
- inside an active I2 episode, not a new entry.
- 4-month simultaneous redemption streak.
- 3m combined ETF flow below historical Q10.
- next-month GLD move = -2.93pp.
- ChHHO APE = 3.51% HIGH.
- This shows I2 can be a persistent model-risk regime even when the subsequent market move is just below 3pp.

### 2024-03 / origin 2024-02
- I2 episode entry = TRUE
- next-month GLD move = +8.31pp.
- ChHHO APE = 6.10% HIGH.
- strongest clean example of I2 as a true storm-regime precursor.

## 7. Binding interpretation

### I1
- not historically robust as a general next-month high-movement signal;
- keep as **candidate transition warning only**.

### I2
- historically strong in 2010-2020;
- survives episode de-clustering;
- strongest evidence is for elevated probability of **3-5%+ next-month Gold movement**;
- effect is not stationary across all later periods;
- one 2026 counterexample exists;
- in canonical DEV, all three eligible I2 episode entries precede HIGH-APE ChHHO targets.

Binding status:
**I2 = HISTORICALLY SUPPORTED, REGIME-DEPENDENT ETF RISK WARNING.**
It is stronger than a purely post-hoc descriptor, but it is not a universal hard ChHHO-error alarm.

No I1 OR I2 composite hard rule is authorized.
No routing/model switching is authorized.
