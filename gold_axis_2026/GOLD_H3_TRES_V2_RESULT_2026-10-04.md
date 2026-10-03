# TRES-H3 V2 — LAST-DECISIVE PATH STATE RESULT

**Status:** **TRES_V2_PATH_GOVERNOR_FAIL**  
- predictions: **679**
- scored origins: **2024-01-02 .. 2026-09-24**
- maturity leakage failures: **0**

## Aggregate path governor

- V5-continuation eligible: **561**
- FLIP candidates: **35 (6.24%)**
- rescue / broken / net: **15 / 20 / -5**
- FLIP precision: **42.86%**
- V5 -> assisted accuracy: **67.30% -> 66.57%**
- path-state accuracy: **48.01%**
- path-state log loss: **1.0245**
- OPAL-no-candidate missed reversals hit: **12/166**

## mu_R terminal-reversal concentration

- bottom quintile: **23.53%**
- top quintile: **50.00%**
- separation: **+26.47 pp**

## Half-year stability

| Block | N | Flip | Rescue | Broken | Net | Precision | V5 acc | Assisted | Terminal sep |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024_H1 | 116 | 3 | 2 | 1 | +1 | 66.7% | 71.6% | 72.4% | +33.3pp |
| 2024_H2 | 124 | 7 | 3 | 4 | -1 | 42.9% | 71.0% | 70.2% | +48.0pp |
| 2025_H1 | 119 | 8 | 6 | 2 | +4 | 75.0% | 63.0% | 66.4% | +37.5pp |
| 2025_H2 | 129 | 8 | 1 | 7 | -6 | 12.5% | 69.8% | 65.1% | +23.1pp |
| 2026_H1 | 128 | 8 | 3 | 5 | -2 | 37.5% | 65.6% | 64.1% | +23.1pp |
| 2026_H2 | 63 | 1 | 0 | 1 | -1 | 0.0% | 58.7% | 57.1% | +15.4pp |

## Gate

- non-negative blocks: **2/6** (required 5)
- positive blocks: **2/6** (required 3)
- worst block net: **-6**
- V2 fails the frozen development gate.
- No prospective reversal FLIP challenger is authorized from this version.
