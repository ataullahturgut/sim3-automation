# GOLD H3 — ARAC-H3-v1 RESULT

Adaptive Regime-Analog Consensus: global Elastic-Net + recent balanced Logistic + local analog + regime prior, with online Brier weighting.

Frozen reliability threshold from 2019-2021: **0.033375** (development coverage 30.04%).

## Full coverage

| Period | Model | N | Accuracy | Balanced acc | False calls | Brier | Log loss | UP recall | DOWN recall |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DEV_2019_2021 | EXPANDING_PRIOR | 759 | 53.36% | 50.00% | 46.64% | 0.2494 | 0.6920 | 100.00% | 0.00% |
| DEV_2019_2021 | CORE3_LOGIT_L2 | 759 | 52.31% | 51.86% | 47.69% | 0.2511 | 0.6955 | 58.52% | 45.20% |
| DEV_2019_2021 | CORE3_LOGIT_EN | 759 | 53.49% | 52.99% | 46.51% | 0.2507 | 0.6947 | 60.49% | 45.48% |
| DEV_2019_2021 | ARAC | 759 | 51.78% | 51.12% | 48.22% | 0.2510 | 0.6953 | 60.99% | 41.24% |
| CONFIRM_2022_2024 | EXPANDING_PRIOR | 755 | 52.32% | 50.00% | 47.68% | 0.2497 | 0.6925 | 100.00% | 0.00% |
| CONFIRM_2022_2024 | CORE3_LOGIT_L2 | 755 | 54.97% | 54.49% | 45.03% | 0.2466 | 0.6865 | 64.81% | 44.17% |
| CONFIRM_2022_2024 | CORE3_LOGIT_EN | 755 | 54.97% | 54.45% | 45.03% | 0.2468 | 0.6867 | 65.57% | 43.33% |
| CONFIRM_2022_2024 | ARAC | 755 | 55.63% | 55.29% | 44.37% | 0.2465 | 0.6862 | 62.53% | 48.06% |

## ARAC selective calls using the development-frozen reliability rule

| Period | Calls | Coverage | Accuracy | Balanced acc | False calls | UP recall | DOWN recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| DEV_2019_2021 | 228 | 30.04% | 53.95% | 53.95% | 46.05% | 74.56% | 33.33% |
| CONFIRM_2022_2024 | 243 | 32.19% | 61.73% | 59.73% | 38.27% | 76.47% | 42.99% |
| 2022 | 63 | 25.20% | 58.73% | 54.63% | 41.27% | 83.33% | 25.93% |
| 2023 | 79 | 31.47% | 68.35% | 68.33% | 31.65% | 70.00% | 66.67% |
| 2024 | 101 | 39.76% | 58.42% | 54.19% | 41.58% | 76.67% | 31.71% |

## Annual full-coverage ARAC

| Year | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |
|---:|---:|---:|---:|---:|---:|
| 2019 | 52.17% | 52.73% | 0.2499 | 44.44% | 61.02% |
| 2020 | 53.54% | 50.42% | 0.2497 | 68.46% | 32.38% |
| 2021 | 49.60% | 50.39% | 0.2535 | 70.25% | 30.53% |
| 2022 | 52.40% | 52.51% | 0.2470 | 66.13% | 38.89% |
| 2023 | 58.57% | 58.51% | 0.2451 | 60.00% | 57.02% |
| 2024 | 55.91% | 55.19% | 0.2474 | 61.70% | 48.67% |

2022-2024 is confirmation inside already-opened project history, not a pristine blind lockbox.
