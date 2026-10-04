# GOLD H3 — RULEFLOW V2 Q2-Q3 CLOSURE AND ROOT CAUSE

**Date:** 2026-10-04

## Frozen stress result

RuleFlow V2 was frozen before the 2026 Q2-Q3 stress run.

### Q2
- scored events: 18
- actions: 2
- rescue / broken / net: **0 / 2 / -2**
- precision: **0%**

### Q3
- scored events: 15
- actions: 2
- rescue / broken / net: **0 / 2 / -2**
- precision: **0%**

### Combined
- scored events: 33
- actions: 4
- rescue / broken / net: **0 / 4 / -4**
- precision: **0%**

Action dates:
- 2026-06-17 FOMC — broken
- 2026-06-25 PCE — broken
- 2026-07-29 FOMC — broken
- 2026-08-04 JOLTS — broken

RuleFlow V2 is therefore **closed as a production rule**.

## Root-cause diagnosis

The macro-breadth gate used mean absolute rolling correlations of Gold with USD, 10Y yield, Nasdaq and VIX.

That destroys the sign/topology of the macro relationship.

### Successful 2025 reversal actions

Representative rolling-60 correlations:

| Date | Gold-USD | Gold-TNX | Gold-NDX | Gold-VIX |
|---|---:|---:|---:|---:|
| 2025-05-02 | -0.260 | -0.082 | +0.113 | -0.186 |
| 2025-05-30 | -0.437 | -0.040 | -0.063 | +0.049 |
| 2025-06-04 | -0.415 | -0.019 | -0.072 | +0.054 |
| 2025-07-29 | -0.455 | +0.063 | -0.525 | +0.450 |
| 2025-07-30 | -0.420 | +0.091 | -0.514 | +0.461 |

### Broken 2026 Q2-Q3 actions

| Date | Gold-USD | Gold-TNX | Gold-NDX | Gold-VIX |
|---|---:|---:|---:|---:|
| 2026-06-17 | -0.380 | -0.419 | +0.465 | -0.458 |
| 2026-06-25 | -0.498 | -0.266 | +0.373 | -0.332 |
| 2026-07-29 | -0.475 | -0.107 | +0.206 | -0.308 |
| 2026-08-04 | -0.444 | -0.038 | +0.196 | -0.324 |

The four failures share a clear topology:
- Gold-USD remains negative;
- Gold-Nasdaq is **positive**;
- Gold-VIX is **negative**;
- Gold-Treasury is negative or strongly negative.

This is qualitatively different from the strong 2025 Jul reversal regime, where:
- Gold-Nasdaq was strongly negative;
- Gold-VIX was strongly positive.

## Interpretation

A high absolute macro correlation does not mean the same economic regime.

RuleFlow V2 treated:
- safe-haven/risk-off transmission
and
- pro-risk/liquidity transmission

as equivalent because it used absolute correlations.

They are not equivalent.

The successor must model **macro topology/sign**, not only breadth magnitude.

A natural topology diagnostic is the Gold risk-axis orientation:
- safe-haven topology: Gold-NDX negative and/or Gold-VIX positive;
- pro-risk topology: Gold-NDX positive and Gold-VIX negative.

Any new topology gate is post-Q2Q3 diagnostic and must be preregistered/tested separately. No retroactive rescue claim is permitted.
