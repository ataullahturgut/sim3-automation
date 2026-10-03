# GOLD H3 CLEAN CORE REBUILD — 2026-10-03

**Status:** CLEAN-OVERLAY REBUILD; original frozen artifacts preserved.

## Corrected source row

- date: **2026-02-27**
- old: {"gold": 3516.02, "palladium": 1201.26, "platinum": 1585.39, "silver": 62.15}
- clean: {"gold": 5183.8, "palladium": 1789.96, "platinum": 2369.25, "silver": 88.14}

## AURORA clean-core metrics

| Model | Period | Accuracy | BA | Brier | Logloss |
|---|---|---:|---:|---:|---:|
| AURORA_CLEAN | 2023 | 71.23% | 71.83% | 0.2118 | 0.6149 |
| AURORA_OLD_PROB_CLEAN_LABEL | 2023 | 71.23% | 71.83% | 0.2118 | 0.6149 |
| AURORA_CLEAN | 2024 | 70.83% | 69.97% | 0.2006 | 0.5847 |
| AURORA_OLD_PROB_CLEAN_LABEL | 2024 | 70.83% | 69.97% | 0.2006 | 0.5847 |
| AURORA_CLEAN | 2025 | 64.52% | 62.93% | 0.2276 | 0.6585 |
| AURORA_OLD_PROB_CLEAN_LABEL | 2025 | 64.52% | 62.93% | 0.2276 | 0.6585 |
| AURORA_CLEAN | 2026 | 58.64% | 59.02% | 0.2532 | 0.7207 |
| AURORA_OLD_PROB_CLEAN_LABEL | 2026 | 59.69% | 60.07% | 0.2530 | 0.7207 |
| AURORA_CLEAN | 2025-2026 | 61.96% | 61.15% | 0.2388 | 0.6856 |
| AURORA_OLD_PROB_CLEAN_LABEL | 2025-2026 | 62.41% | 61.61% | 0.2387 | 0.6856 |

## Old vs clean AURORA call audit

- labels changed: **2**
- AURORA directions changed after full clean refit: **2**
- max absolute p(UP) change: **0.0364**
- direction-changed issue dates: **2026-09-15, 2026-09-22**
- label-changed issue dates: **2026-02-25, 2026-03-02**

This rebuild does not overwrite the original AURORA prospective freeze. It is a retrospective integrity correction branch of evidence.
