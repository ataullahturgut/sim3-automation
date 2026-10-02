# GOLD SHORT-HORIZON GLOBAL XAU R2 — Stage 2 H3 Direction Robustness Result

**Status:** **ROBUST_PASS**

Binding baseline: **EXPAND_PREV**

## H3 aggregate representations

| Representation | Brier | Baseline | Rel improvement | Logloss | Pred SD |
|---|---:|---:|---:|---:|---:|
| GOLD_ONLY | 0.250051 | 0.249707 | -0.14% | 0.693254 | 0.0176 |
| CORE3 | 0.246637 | 0.249707 | 1.23% | 0.686447 | 0.0448 |
| CORE4 | 0.247800 | 0.249707 | 0.76% | 0.688940 | 0.0493 |
| CORE3_SAFE_EXTERNAL_RAW | 0.250299 | 0.249707 | -0.24% | 0.693941 | 0.0654 |
| CORE3_SAFE_EXTERNAL_CHG | 0.250489 | 0.249707 | -0.31% | 0.694299 | 0.0631 |

## CORE3 annual robustness

| Year | N | Brier | Baseline | Rel improvement |
|---|---:|---:|---:|---:|
| 2022 | 250 | 0.245748 | 0.250593 | 1.93% |
| 2023 | 251 | 0.249436 | 0.249913 | 0.19% |
| 2024 | 254 | 0.244747 | 0.248632 | 1.56% |

## Binding decision
- CORE3 robust: **True**
- final representation: **CORE3**
- H5 secondary >=1% gate: **False**
- positive CORE3 years: 3/3
- worst CORE3 annual relative Brier improvement: 0.19%.