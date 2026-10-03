# ORS-H3 V1 — ORTHOGONAL REVERSAL SURPRISE RESULT

**Status:** **ORS_H3_V1_FAIL**  
- predictions: **395**
- scored origins: **2024-10-31 .. 2026-09-24**
- maturity leakage failures: **0**

## Aggregate

- FLIP candidates: **15 (3.80%)**
- DAMP candidates: **28**
- rescue / broken / net: **5 / 10 / -5**
- FLIP precision: **33.33%**
- V5 -> assisted accuracy: **66.08% -> 64.81%**
- OPAL-no-candidate missed reversals hit: **5/125**

## State diagnostic

| State | N | Terminal reversal | Mean F_R | Mean surprise |
|---|---:|---:|---:|---:|
| HIGH_SURPRISE_DOMINANT | 15 | 33.33% | 0.497 | 0.935 |
| HIGH_SURPRISE_NONDominant | 28 | 50.00% | 0.172 | 0.927 |
| LOW_SURPRISE | 352 | 32.67% | 0.135 | 0.565 |

## Half-year stability

| Block | N | Flip | Damp | Rescue | Broken | Net | Precision | V5 acc | Assisted |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024_H2 | 31 | 1 | 0 | 0 | 1 | -1 | 0.0% | 74.2% | 71.0% |
| 2025_H1 | 102 | 5 | 2 | 4 | 1 | +3 | 80.0% | 60.8% | 63.7% |
| 2025_H2 | 109 | 2 | 7 | 0 | 2 | -2 | 0.0% | 74.3% | 72.5% |
| 2026_H1 | 109 | 5 | 16 | 1 | 4 | -3 | 20.0% | 63.3% | 60.6% |
| 2026_H2 | 44 | 2 | 3 | 0 | 2 | -2 | 0.0% | 59.1% | 54.5% |

## Gate

- non-negative blocks: **1/5** (required 4)
- positive blocks: **1/5** (required 3)
- worst block net: **-3**
- ORS V1 failed the frozen development gate.
- K and surprise threshold must not be tuned on this same replay.
