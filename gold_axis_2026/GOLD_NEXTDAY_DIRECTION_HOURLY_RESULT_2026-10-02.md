# GOLD NEXT-DAY DIRECTION — XAU 1H V1

Raw hourly rows: **17,644**. Daily 16:00 NY issue rows after feature/target maturity: **705**.
Strict expanding OOS: 2022 initial history; 2023-2024 scored.

| Model | Period | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| LOGIT_L2 | 2023-2024 | 468 | 54.91% | 54.41% | 0.2598 | 0.7178 | 64.23% | 44.59% |
| LOGIT_L2 | 2023 | 224 | 56.25% | 56.35% | 0.2584 | 0.7170 | 67.57% | 45.13% |
| LOGIT_L2 | 2024 | 244 | 53.69% | 52.76% | 0.2610 | 0.7186 | 61.48% | 44.04% |
| HGB | 2023-2024 | 468 | 48.29% | 47.98% | 0.2807 | 0.7625 | 54.07% | 41.89% |
| HGB | 2023 | 224 | 48.66% | 48.68% | 0.2812 | 0.7645 | 50.45% | 46.90% |
| HGB | 2024 | 244 | 47.95% | 46.87% | 0.2802 | 0.7606 | 57.04% | 36.70% |
| MAJORITY_PROB | 2023-2024 | 468 | 52.56% | 50.00% | 0.2497 | 0.6925 | 100.00% | 0.00% |
| MAJORITY_PROB | 2023 | 224 | 49.55% | 50.00% | 0.2510 | 0.6951 | 100.00% | 0.00% |
| MAJORITY_PROB | 2024 | 244 | 55.33% | 50.00% | 0.2485 | 0.6902 | 100.00% | 0.00% |
| SESSION_MOMENTUM | 2023-2024 | 468 | 47.86% | 47.81% | 0.5214 | 7.2030 | 48.78% | 46.85% |
| SESSION_MOMENTUM | 2023 | 224 | 50.89% | 50.87% | 0.4911 | 6.7844 | 48.65% | 53.10% |
| SESSION_MOMENTUM | 2024 | 244 | 45.08% | 44.63% | 0.5492 | 7.5872 | 48.89% | 40.37% |

Prediction ledger, monthly metrics, fit logs and standardized Logistic coefficients were saved.
