# GOLD NEXT-DAY DIRECTION — HOURLY LAG V3 SELECTION

2023 = lag selection/development. 2024 = frozen-subset confirmation.

Selected lags: **hr_ret_lag2**.

## One-at-a-time 2023 leaders

| Lag | Δ accuracy | Δ balanced acc | Δ Brier | Δ log loss |
|---|---:|---:|---:|---:|
| hr_ret_lag2 | +0.89 pp | +0.90 pp | +0.0002 | +0.0004 |
| hr_ret_lag19 | +0.45 pp | +0.47 pp | -0.0014 | -0.0031 |
| hr_ret_lag8 | +0.45 pp | +0.45 pp | -0.0008 | -0.0015 |
| hr_ret_lag3 | +0.00 pp | +0.03 pp | -0.0013 | -0.0023 |
| hr_ret_lag15 | +0.00 pp | +0.02 pp | -0.0003 | +0.0004 |
| hr_ret_lag0 | +0.00 pp | +0.00 pp | +0.0001 | +0.0001 |
| hr_ret_lag1 | +0.00 pp | +0.00 pp | +0.0003 | +0.0005 |
| hr_ret_lag10 | +0.00 pp | +0.00 pp | +0.0012 | +0.0033 |
| hr_ret_lag22 | +0.00 pp | -0.01 pp | -0.0038 | -0.0130 |
| hr_ret_lag4 | -0.45 pp | -0.42 pp | -0.0010 | -0.0019 |

## Frozen comparison

| Model | Period | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall | False calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BASE_V1 | 2023 | 224 | 55.36% | 55.47% | 0.2591 | 0.7180 | 67.57% | 43.36% | 44.64% |
| V3_SELECTED | 2023 | 224 | 56.25% | 56.37% | 0.2593 | 0.7184 | 69.37% | 43.36% | 43.75% |
| BASE_V1 | 2024 | 244 | 53.69% | 52.76% | 0.2609 | 0.7184 | 61.48% | 44.04% | 46.31% |
| V3_SELECTED | 2024 | 244 | 54.51% | 53.59% | 0.2606 | 0.7181 | 62.22% | 44.95% | 45.49% |
| BASE_V1 | 2023-2024 | 468 | 54.49% | 53.96% | 0.2600 | 0.7182 | 64.23% | 43.69% | 45.51% |
| V3_SELECTED | 2023-2024 | 468 | 55.34% | 54.80% | 0.2600 | 0.7183 | 65.45% | 44.14% | 44.66% |

All 24 hourly lags were tested individually. The final subset was chosen only from 2023 under the frozen greedy rule.
