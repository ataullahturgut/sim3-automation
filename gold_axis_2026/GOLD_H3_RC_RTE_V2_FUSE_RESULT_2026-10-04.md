# RC-RTE-H3 V2 — ONLINE CREDIBILITY FUSE RESULT

**Status:** **RC_RTE_V2_FUSE_ROBUST_PASS_2026_OPENED**  
**Safety layer:** one unresolved event per regime + close regime after matured live score turns negative.

## Sequential pre-2026 blocks

| Block | Enabled | Proposals | Accepted | Ovlp suppr | Fuse suppr | Rescue | Broken | Net | Precision | V5 acc | Assisted |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024_H2 | - | 27 | 0 | 0 | 0 | 0 | 0 | +0 | 0.00% | 69.16% | 69.16% |
| 2025_H1 | 1;2 | 23 | 9 | 1 | 12 | 7 | 2 | +5 | 77.78% | 60.78% | 65.69% |
| 2025_H2 | 0;2 | 22 | 2 | 1 | 17 | 0 | 2 | -2 | 0.00% | 74.31% | 72.48% |

## Pooled robustness

- accepted candidates: **11**
- rescue / broken / net: **7 / 4 / +3**
- precision: **63.64%**
- non-negative blocks: **2/3**
- positive blocks: **1/3**
- worst block net: **-2**
- V5 -> assisted pooled accuracy: **68.24% -> 69.18%**
- robustness gate: **PASS**

## 2026 final holdout

- final static enabled regimes: **[1]**
- proposals / accepted: **35 / 1**
- overlap-suppressed: **1**
- fuse-suppressed: **9**
- rescue / broken / net: **0 / 1 / -1**
- precision: **0.00%**
- eligible V5 -> assisted: **62.09% -> 61.44%**
- OPAL-no-candidate missed reversals hit: **0/55**
- whole clean 2026: **121 -> 120 / 191**
- whole clean 2026 accuracy: **63.35% -> 62.83%**

## Governance

Every fuse decision used only previously matured accepted candidate outcomes. Overlapping unresolved H3 events were suppressed before their outcomes existed. 2026 was opened only if the fixed pre-2026 robustness gate passed.
