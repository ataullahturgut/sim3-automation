# RC-RTE-H3 V2 — SHADOW CREDIBILITY RESULT

**Status:** **NO_ROBUST_RC_RTE_V2_RULE**  
**Dynamic rule:** static regime enablement + last-3 matured shadow proposal credibility.

## Sequential pre-2026 blocks

| Block | Static regimes | Proposals | Actions | Rescue | Broken | Net | Precision | Transitions | V5 acc | Assisted acc |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024_H2 | - | 27 | 0 | 0 | 0 | +0 | 0.00% | 0 | 69.16% | 69.16% |
| 2025_H1 | 1;2 | 23 | 20 | 14 | 6 | +8 | 70.00% | 1 | 60.78% | 68.63% |
| 2025_H2 | 0;2 | 22 | 9 | 2 | 7 | -5 | 22.22% | 3 | 74.31% | 69.72% |

## Pooled robustness

- candidates: **29**
- rescued / broken / net: **16 / 13 / +3**
- rescue precision: **55.17%**
- positive blocks: **1/3**
- worst block: **-5**
- V5 -> assisted accuracy: **68.24% -> 69.18%**
- robustness gate: **FAIL**

## Governance

Shadow outcomes enter memory only after target maturity. Vetoed proposals remain observable in shadow mode, allowing a regime to recover without risking a live flip. 2026 is opened only after the full pre-2026 robustness gate.
