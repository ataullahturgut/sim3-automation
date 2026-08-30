# Gold R4 / R4.1 Direction Engine

This directory is the current continuation of the Gold work already stored under `gold_axis_2026`.

## Frozen architecture

- CORE PRICE: VW-MIDAS-SVR Adapt V2 analytical primary.
- CORE DIRECTION: 3M Momentum monthly prior.
- FAST Tactical: daily close vs SMA20, 2 consecutive market-day persistence.
- SLOW Tactical: completed weekly close vs SMA4, 2 consecutive completed-week persistence.
- LEVEL EMERGENCY DIRECTION: frozen monthly VW displacement >= +4% => UP; <= -4% => DOWN.
- REVERSAL EMERGENCY: after a Level Emergency, counter-move >=4% from the running extreme => alert only. It is not an automatic direction flip.
- GVZ: risk cap only; no direction vote.
- BOCPD-return: regime context only; no direction vote and no automatic exposure modifier.
- Macro Event DOWN: partial frozen contract known, but full timestamp-safe macro-score construction remains BLOCKED_NOT_FULLY_RECOVERED.

## Anti-leakage contract

- No random split.
- No target-month data may refit the monthly H=1 forecast.
- No threshold may be tuned on 2026 outcomes.
- EOD signals affect the next trading session unless an independently frozen intraday contract exists.

## Relationship to existing files

The pre-existing scripts in `gold_axis_2026/` remain the historical monthly/VW model lineage. They are not duplicated here. `r4_1/` adds the frozen daily direction/risk layer and its replay engine on top of that history.

## Intentionally not invented

- exact original archived VW production source chain;
- exact final R4 exposure ladder/arbitration;
- full Macro Event score-vintage implementation;
- intraday Emergency rule.

These remain explicit blockers rather than reconstructed guesses.
