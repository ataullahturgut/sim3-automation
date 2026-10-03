# RC-RTE-H3 V1 — REGIME-CONDITIONAL REVERSAL TRANSITION RESULT

**Status:** **NO_ROBUST_RC_RTE_RULE**  
**Regime map:** K=3 unsupervised mechanism-state clusters; reversal proposals are allowed only in historically reversal-enabled regimes.

## Sequential pre-2026 blocks

| Block | Train n | Enabled regimes | Proposals | Gated | Rescue | Broken | Net | Precision | V5 acc | Assisted acc |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024_H2 | 102 | - | 27 | 0 | 0 | 0 | +0 | 0.00% | 69.16% | 69.16% |
| 2025_H1 | 209 | 1;2 | 23 | 22 | 15 | 7 | +8 | 68.18% | 60.78% | 68.63% |
| 2025_H2 | 311 | 0;2 | 22 | 20 | 6 | 14 | -8 | 30.00% | 74.31% | 66.97% |

## Pooled pre-2026 robustness

- candidates: **42**
- rescued / broken / net: **21 / 21 / +0**
- rescue precision: **50.00%**
- positive blocks: **1/3**
- worst block net: **-8**
- V5 -> assisted pooled accuracy: **68.24% -> 68.24%**
- robustness gate: **FAIL**

## Training-regime audits

| Block | Regime | Support | Rescue | Broken | Net | Precision | Enabled | Persistence | Fragility | Option opposition | Participation |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|
| 2024_H2 | 0 | 6 | 4 | 2 | +2 | 66.67% | False | -0.694 | +0.565 | +0.363 | +0.838 |
| 2024_H2 | 1 | 4 | 3 | 1 | +2 | 75.00% | False | -0.201 | +0.134 | -0.301 | -0.735 |
| 2024_H2 | 2 | 2 | 0 | 2 | -2 | 0.00% | False | +0.686 | -0.527 | +0.081 | +0.229 |
| 2025_H1 | 0 | 11 | 6 | 5 | +1 | 54.55% | False | +0.662 | -0.493 | -0.078 | -0.093 |
| 2025_H1 | 1 | 16 | 10 | 6 | +4 | 62.50% | True | -0.346 | +0.212 | +0.599 | +0.992 |
| 2025_H1 | 2 | 12 | 7 | 5 | +2 | 58.33% | True | -0.565 | +0.455 | -0.348 | -0.621 |
| 2025_H2 | 0 | 20 | 14 | 6 | +8 | 70.00% | True | -0.547 | +0.435 | -0.323 | -0.588 |
| 2025_H2 | 1 | 14 | 7 | 7 | +0 | 50.00% | False | +0.668 | -0.503 | -0.012 | -0.075 |
| 2025_H2 | 2 | 28 | 17 | 11 | +6 | 60.71% | True | -0.316 | +0.204 | +0.504 | +1.011 |

## Governance

2026 was opened only if the three sequential pre-2026 blocks passed the preregistered robustness gate. Regime construction uses origin-observable state only; outcomes are used only to enable or protect regimes within matured training data.
