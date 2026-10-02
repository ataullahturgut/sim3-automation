# GOLD FORECASTING CHALLENGE V1 — VALIDATION SELECTION

Validation only: **2019-2020**. The selection program loaded no post-2020 rows.

| Rank | Feature block | Model | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | CORE3 | LOGIT_EN | 507 | 54.83% | 54.63% | 0.2498 | 0.6930 | 56.34% | 52.91% |
| 2 | CORE3 | LOGIT_L2 | 507 | 54.04% | 53.83% | 0.2502 | 0.6938 | 55.63% | 52.02% |
| 3 | CORE4 | LOGIT_EN | 507 | 54.24% | 53.81% | 0.2502 | 0.6937 | 57.39% | 50.22% |
| 4 | CORE3 | LDA_SHRINK | 507 | 53.85% | 53.60% | 0.2501 | 0.6935 | 55.63% | 51.57% |
| 5 | CORE4 | LDA_SHRINK | 507 | 53.85% | 53.46% | 0.2506 | 0.6945 | 56.69% | 50.22% |
| 6 | CORE4 | LOGIT_L2 | 507 | 53.65% | 53.18% | 0.2508 | 0.6948 | 57.04% | 49.33% |
| 7 | CORE3_SAFE_EXTERNAL | LOGIT_EN | 507 | 51.48% | 52.02% | 0.2549 | 0.7032 | 47.54% | 56.50% |
| 8 | CORE3_SAFE_EXTERNAL | LDA_SHRINK | 507 | 51.08% | 51.76% | 0.2562 | 0.7059 | 46.13% | 57.40% |
| 9 | CORE3_SAFE_EXTERNAL | EXTRA_TREES | 507 | 50.30% | 51.11% | 0.2507 | 0.6946 | 44.37% | 57.85% |
| 10 | GOLD_ONLY | LOGIT_EN | 507 | 53.06% | 50.68% | 0.2490 | 0.6911 | 70.42% | 30.94% |

Champion to lock: **CORE3 + LOGIT_EN**.
Validation confidence cutoffs: 60% coverage ≈ **0.020218**, 40% coverage ≈ **0.032632**.

No 2021 target was inspected by this selection script.
