# GOLD CONTROL — UP-2 REGIME-CONDITIONED FAILURE DETECTOR V1

**Status:** `FORWARD_RETENTION_OK_TRANSPORT_NOT_SUPPORTED`

## Model

Features: ['last_hour_trend_r2', 'sqrt_score', 'late_downside_intensity']  
Training: 2022 UP-2 calls only. Veto if p_fail >= 0.50. Veto -> ABSTAIN.

| Period | Calls | False UP removed | True UP retained | Precision before | Precision after |
|---|---:|---:|---:|---:|---:|
| 2022 train | 7 | 1/3 | 3/4 | 57.1% | 60.0% |
| 2023 | 1 | 0/0 | 1/1 | 100.0% | 100.0% |
| 2024 | 3 | 0/0 | 3/3 | 100.0% | 100.0% |
| 2023-24 guard | 4 | 0/0 | 4/4 | 100.0% | 100.0% |
| 2025 locked | 25 | 4/12 | 6/13 | 52.0% | 42.9% |

Standardized coefficients: `{"last_hour_trend_r2": 0.6794260108183809, "late_downside_intensity": 0.21335833563278786, "sqrt_score": 0.3533986989207096}`

Sample-limited research only. The pre-2025 forward guard has no false-UP cases, so this experiment cannot certify a failure detector.
