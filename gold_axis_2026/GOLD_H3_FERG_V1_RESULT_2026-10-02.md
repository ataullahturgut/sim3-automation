# FERG-H3 V1 — RESULT

**Status:** **NOT_PROMOTED**  
**Selected meta-model:** **META_HGB_SHALLOW**  
**Frozen P(ERROR) acceptance threshold:** **0.388797**  
**Selection:** 2019-2021 only  
**Confirmation:** 2022-2024  
**2025/2026:** report-only transport/stress

## Error-risk + gate metrics

| Period | Coverage | Full A1 acc | Accepted acc | Accepted BA | Rejected acc | Gap | Error AUC | Error Brier |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SELECT_2019_2021 | 30.04% | 54.81% | 57.89% | 57.62% | 53.48% | 4.41 pp | 0.515 | 0.2557 |
| CONFIRM_2022_2024 | 12.19% | 56.16% | 44.57% | 45.11% | 57.77% | -13.20 pp | 0.460 | 0.2539 |
| 2022 | 8.80% | 53.20% | 40.91% | 40.91% | 54.39% | -13.48 pp | 0.450 | 0.2586 |
| 2023 | 14.34% | 58.96% | 44.44% | 43.81% | 61.40% | -16.95 pp | 0.469 | 0.2504 |
| 2024 | 13.39% | 56.30% | 47.06% | 51.28% | 57.73% | -10.67 pp | 0.453 | 0.2527 |
| 2025 | 4.74% | 49.41% | 33.33% | 34.29% | 50.21% | -16.87 pp | 0.503 | 0.2547 |
| 2026 | 1.05% | 37.17% | 0.00% | 0.00% | 37.57% | -37.57 pp | 0.402 | 0.2618 |

## Directional capture of accepted calls

| Period | UP precision | DOWN precision | UP capture | DOWN capture | False-UP FPR | False-DOWN FPR |
|---|---:|---:|---:|---:|---:|---:|
| SELECT_2019_2021 | 58.91% | 56.57% | 18.77% | 15.82% | 14.97% | 10.62% |
| CONFIRM_2022_2024 | 52.38% | 38.00% | 5.57% | 5.28% | 5.56% | 7.85% |
| 2025 | 40.00% | 28.57% | 1.28% | 2.06% | 3.09% | 3.21% |
| 2026 | 0.00% | 0.00% | 0.00% | 0.00% | 2.00% | 0.00% |

## Error-risk separation

- SELECT_2019_2021: mean P(error) on correct calls **0.436**; on wrong calls **0.439**.
- CONFIRM_2022_2024: mean P(error) on correct calls **0.456**; on wrong calls **0.447**.
- 2025: mean P(error) on correct calls **0.468**; on wrong calls **0.468**.
- 2026: mean P(error) on correct calls **0.534**; on wrong calls **0.509**.

## Governance

No 2025/2026 outcome was used to select the model family or threshold. The selected meta-model is refit online only from already-matured prior H3 errors. A failed transport cannot modify FERG V1; any repair requires V2.
