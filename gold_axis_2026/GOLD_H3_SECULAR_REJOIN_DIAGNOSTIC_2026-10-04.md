# SECULAR REJOIN DIAGNOSTIC — OAR CANDIDATES

**Evidence class:** post-holdout development. 2026 is diagnostic, not independent validation.

- hourly source bridge pass: **True**
- OAR candidates 2024-2026: **53**

## OAR performance by secular state

| Year | State | N | Rescue | Broken | Net | Precision | median signed20 | median signed60 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | REJOIN_BOTH | 9 | 5 | 4 | +1 | 55.56% | -0.0134 | -0.0554 |
| 2024 | MIXED | 3 | 3 | 0 | +3 | 100.00% | +0.0029 | -0.0547 |
| 2024 | ALIGN_BOTH | 0 | 0 | 0 | +0 | 0.00% | +nan | +nan |
| 2024 | ALL_OAR | 12 | 8 | 4 | +4 | 66.67% | -0.0075 | -0.0549 |
| 2025 | REJOIN_BOTH | 14 | 7 | 7 | +0 | 50.00% | -0.0639 | -0.1179 |
| 2025 | MIXED | 5 | 4 | 1 | +3 | 80.00% | +0.0133 | -0.0078 |
| 2025 | ALIGN_BOTH | 3 | 3 | 0 | +3 | 100.00% | +0.0825 | +0.1600 |
| 2025 | ALL_OAR | 22 | 14 | 8 | +6 | 63.64% | -0.0373 | -0.0980 |
| 2026 | REJOIN_BOTH | 3 | 0 | 3 | -3 | 0.00% | -0.0574 | -0.1598 |
| 2026 | MIXED | 5 | 1 | 4 | -3 | 20.00% | +0.0229 | -0.0228 |
| 2026 | ALIGN_BOTH | 11 | 2 | 9 | -7 | 18.18% | +0.0450 | +0.1004 |
| 2026 | ALL_OAR | 19 | 3 | 16 | -13 | 15.79% | +0.0297 | +0.0730 |

## Structural sign-rule audit

| Rule | N | Rescue | Broken | Net | Precision |
|---|---:|---:|---:|---:|---:|
| REJOIN20 | 29 | 14 | 15 | -1 | 48.28% |
| REJOIN20_2024 | 9 | 5 | 4 | +1 | 55.56% |
| REJOIN20_2025 | 16 | 9 | 7 | +2 | 56.25% |
| REJOIN20_2026 | 4 | 0 | 4 | -4 | 0.00% |
| REJOIN60 | 36 | 18 | 18 | +0 | 50.00% |
| REJOIN60_2024 | 12 | 8 | 4 | +4 | 66.67% |
| REJOIN60_2025 | 17 | 9 | 8 | +1 | 52.94% |
| REJOIN60_2026 | 7 | 1 | 6 | -5 | 14.29% |
| REJOIN_EITHER | 39 | 20 | 19 | +1 | 51.28% |
| REJOIN_EITHER_2024 | 12 | 8 | 4 | +4 | 66.67% |
| REJOIN_EITHER_2025 | 19 | 11 | 8 | +3 | 57.89% |
| REJOIN_EITHER_2026 | 8 | 1 | 7 | -6 | 12.50% |
| REJOIN_BOTH | 26 | 12 | 14 | -2 | 46.15% |
| REJOIN_BOTH_2024 | 9 | 5 | 4 | +1 | 55.56% |
| REJOIN_BOTH_2025 | 14 | 7 | 7 | +0 | 50.00% |
| REJOIN_BOTH_2026 | 3 | 0 | 3 | -3 | 0.00% |
| ALIGN_BOTH | 14 | 5 | 9 | -4 | 35.71% |
| ALIGN_BOTH_2024 | 0 | 0 | 0 | +0 | 0.00% |
| ALIGN_BOTH_2025 | 3 | 3 | 0 | +3 | 100.00% |
| ALIGN_BOTH_2026 | 11 | 2 | 9 | -7 | 18.18% |
