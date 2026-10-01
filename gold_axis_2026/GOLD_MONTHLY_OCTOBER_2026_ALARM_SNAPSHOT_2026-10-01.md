# GOLD MONTHLY — October 2026 Alarm Snapshot

**Date / as-of:** 2026-10-01  
**Origin:** 2026-09 month end  
**Target:** 2026-10  
**Forecast:** ChHHO-ANFIS 4278.3084 USD/oz  
**Status:** CURRENT T0 SNAPSHOT / NO ALARM

## Frozen signal snapshot

| Signal | State |
|---|---|
| A | OFF |
| B | OFF |
| C | OFF |
| D | OFF |
| E | OFF |
| G | OFF |
| H | OFF |
| I1 | OFF |
| I2 | OFF |
| V2_TRANSITION | OFF / STABLE |
| T1_WGC | SLEEPING / September-flow October report not yet available as of the cutoff |

Frozen Specialist Hedge parameters:
- eta = 0.25
- alpha = 0
- tau = 0.50

Current active experts:
- **none**

Therefore:
- **p_HIGH = 0.0000**
- **p_ELEVATED = 0.0000**
- **HIGH alarm = NO**

This result does not depend on the pending September World Bank target outcome because no Specialist expert is awake at the current origin; with an empty active set, the frozen router emits zero risk score before any subsequent T1 information arrives.

## Market-state context

- R1 probability: **0.9823228737**
- Transition V2: **STABLE**
- Extreme V1: **NORMAL**
- OOD: **NO**
- combined state: **R1 / STABLE / NORMAL**

## Signal diagnostics

A-G:
- September Gold r1 = -0.01695284
- ChHHO predicted October Gold log return = -0.01359089
- only 1 of 3 other metals is opposite Gold in September, so A is OFF
- nominal 10Y and real 10Y monthly changes are positive, so C is OFF
- Gold r3 = +0.02541952, so G is OFF
- Gold vs prior-12m average = -0.01381031, so E is OFF.

H:
- CFTC managed-money net/OI month change is about -0.04007, below the frozen absolute q90 threshold 0.14998.
- futures-only open-interest month change is also below the frozen 0.14977 threshold.
- H is OFF.

I1/I2:
- ETF combined-flow change = -0.00671005 versus frozen q10 = -0.04281622 -> I1 OFF.
- September two-fund outflow breadth = 0, breadth streak = 0 versus frozen q90 = 2 -> I2 OFF.

## Important timing note

T1_WGC is an early-target-month specialist and is not a month-end T0 signal. It must remain asleep until the September-flow WGC October publication becomes available. If that later T1 report fires, the Specialist score must be recomputed at that publication time.

No forecast correction, model switch, blend, or trading action is authorized by this snapshot.
