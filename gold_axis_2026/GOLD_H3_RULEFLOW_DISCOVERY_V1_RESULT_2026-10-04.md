# GOLD H3 — RULE-FLOW DISCOVERY V1

**Scope:** major U.S. macro/Fed event origins, 2025-03-12..2025-09-30.
**Status:** exploratory structure discovery; not promotion evidence.

## Shallow tree

~~~~
|--- conflict_ratio <= 0.359
|   |--- first_aligns_rates <= 0.500
|   |   |--- event_momentum_flip <= 0.500
|   |   |   |--- class: 1
|   |   |--- event_momentum_flip >  0.500
|   |   |   |--- class: 0
|   |--- first_aligns_rates >  0.500
|   |   |--- class: 0
|--- conflict_ratio >  0.359
|   |--- current_dominance <= 0.502
|   |   |--- current_dominance <= 0.294
|   |   |   |--- class: 0
|   |   |--- current_dominance >  0.294
|   |   |   |--- class: 1
|   |--- current_dominance >  0.502
|   |   |--- class: 0

~~~~

## Predefined rule flows

| Flow | Period | Flag N | Reversal | Reversal rate | V5 actions | Rescue | Broken | Net | Precision |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| F1_FRAGMENTED_UNRESOLVED | H1ish | 11 | 5 | 45.5% | 8 | 3 | 5 | -2 | 37.5% |
| F1_FRAGMENTED_UNRESOLVED | H2ish | 4 | 3 | 75.0% | 4 | 3 | 1 | +2 | 75.0% |
| F1_FRAGMENTED_UNRESOLVED | ALL | 15 | 8 | 53.3% | 12 | 6 | 6 | +0 | 50.0% |
| F2_F1_PLUS_FLIP | H1ish | 7 | 3 | 42.9% | 5 | 2 | 3 | -1 | 40.0% |
| F2_F1_PLUS_FLIP | H2ish | 2 | 2 | 100.0% | 2 | 2 | 0 | +2 | 100.0% |
| F2_F1_PLUS_FLIP | ALL | 9 | 5 | 55.6% | 7 | 4 | 3 | +1 | 57.1% |
| F3_F1_PLUS_SUS | H1ish | 7 | 4 | 57.1% | 4 | 2 | 2 | +0 | 50.0% |
| F3_F1_PLUS_SUS | H2ish | 1 | 1 | 100.0% | 1 | 1 | 0 | +1 | 100.0% |
| F3_F1_PLUS_SUS | ALL | 8 | 5 | 62.5% | 5 | 3 | 2 | +1 | 60.0% |
| F4_F1_PLUS_RATE_ALIGN | H1ish | 4 | 2 | 50.0% | 3 | 1 | 2 | -1 | 33.3% |
| F4_F1_PLUS_RATE_ALIGN | H2ish | 2 | 2 | 100.0% | 2 | 2 | 0 | +2 | 100.0% |
| F4_F1_PLUS_RATE_ALIGN | ALL | 6 | 4 | 66.7% | 5 | 3 | 2 | +1 | 60.0% |
| F5_FRAGMENTED_RESOLVED | H1ish | 3 | 0 | 0.0% | 3 | 0 | 3 | -3 | 0.0% |
| F5_FRAGMENTED_RESOLVED | H2ish | 0 | 0 | 0.0% | 0 | 0 | 0 | +0 | 0.0% |
| F5_FRAGMENTED_RESOLVED | ALL | 3 | 0 | 0.0% | 3 | 0 | 3 | -3 | 0.0% |
| F6_COHERENT | H1ish | 5 | 2 | 40.0% | 5 | 2 | 3 | -1 | 40.0% |
| F6_COHERENT | H2ish | 13 | 2 | 15.4% | 9 | 2 | 7 | -5 | 22.2% |
| F6_COHERENT | ALL | 18 | 4 | 22.2% | 14 | 4 | 10 | -6 | 28.6% |
