# SESSION SENTRY V1 — RESULT

## Pre-2025 eligibility

| Partition | Window | N | SENTRY BA | Structural BA | UP recall | DOWN recall | Switches | Eligible | Reason |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 175 | 52.76% | 52.76% | 50.53% | 55.00% | 0 | False | NO_SWITCH_BY_2024 |
| SOBTI_5_ET | ASIA_MORNING_LIT | 170 | 45.83% | 49.77% | 50.00% | 41.67% | 4 | False | 2024_ACC|DEV_BA |
| SOBTI_5_ET | EUROPE_LIT | 189 | 49.10% | 48.71% | 67.96% | 30.23% | 4 | True | PASS |
| SOBTI_5_ET | NY_LONDON_LIT | 190 | 51.65% | 53.26% | 48.45% | 54.84% | 2 | False | 2024_ACC|DEV_BA |
| SOBTI_5_ET | US_LATE_LIT | 89 | 50.05% | 50.05% | 70.83% | 29.27% | 0 | False | RECALL_FLOOR|NO_SWITCH_BY_2024 |
| WGC_2026_NY3 | ASIA | 102 | 47.36% | 47.36% | 82.61% | 12.12% | 0 | False | RECALL_FLOOR|NO_SWITCH_BY_2024 |
| WGC_2026_NY3 | EUROPE | 189 | 51.04% | 52.12% | 69.16% | 32.93% | 2 | False | 2024_ACC|2024_BRIER|DEV_BA |
| WGC_2026_NY3 | US | 162 | 47.73% | 47.97% | 39.76% | 55.70% | 2 | False | 2024_BRIER |

## Frozen 2025 transport

| Model | Partition | Window | N | Accuracy | BA | UP correct/actual | DOWN correct/actual | Brier |
|---|---|---|---:|---:|---:|---:|---:|---:|
| PATH_GLOBAL | SOBTI_5_ET | EUROPE_LIT | 144 | 54.17% | 51.12% | 59/83 | 19/61 | 0.2627 |
| SENTRY | SOBTI_5_ET | EUROPE_LIT | 144 | 53.47% | 49.43% | 63/83 | 14/61 | 0.2590 |
| STRUCTURAL_IRIS | SOBTI_5_ET | EUROPE_LIT | 144 | 50.69% | 45.71% | 65/83 | 8/61 | 0.2631 |
