# SESSION AURORA V1 — RESULT

## Pre-2025 eligibility

| Partition | Window | N | AURORA BA | Structural BA | UP recall | DOWN recall | Switches | Eligible | Reason |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 175 | 52.76% | 52.76% | 50.53% | 55.00% | 0 | False | NO_SWITCH_BY_2024 |
| SOBTI_5_ET | ASIA_MORNING_LIT | 170 | 50.00% | 49.77% | 50.00% | 50.00% | 1 | True | PASS |
| SOBTI_5_ET | EUROPE_LIT | 189 | 50.45% | 48.71% | 60.19% | 40.70% | 1 | True | PASS |
| SOBTI_5_ET | NY_LONDON_LIT | 190 | 51.65% | 53.26% | 48.45% | 54.84% | 2 | False | 2024_ACC|DEV_BA |
| SOBTI_5_ET | US_LATE_LIT | 89 | 50.05% | 50.05% | 70.83% | 29.27% | 0 | False | RECALL_FLOOR|NO_SWITCH_BY_2024 |
| WGC_2026_NY3 | ASIA | 102 | 47.36% | 47.36% | 82.61% | 12.12% | 0 | False | RECALL_FLOOR|NO_SWITCH_BY_2024 |
| WGC_2026_NY3 | EUROPE | 189 | 49.78% | 52.12% | 65.42% | 34.15% | 1 | False | 2024_ACC|2024_BRIER|DEV_BA |
| WGC_2026_NY3 | US | 162 | 43.90% | 47.97% | 40.96% | 46.84% | 2 | False | 2024_ACC|2024_BRIER|DEV_BA |

## Frozen 2025 transport

| Model | Partition | Window | N | Accuracy | BA | UP correct/actual | DOWN correct/actual | Brier |
|---|---|---|---:|---:|---:|---:|---:|---:|
| AURORA | SOBTI_5_ET | ASIA_MORNING_LIT | 140 | 56.43% | 56.50% | 39/67 | 40/73 | 0.2698 |
| PATH_GLOBAL | SOBTI_5_ET | ASIA_MORNING_LIT | 140 | 53.57% | 53.52% | 35/67 | 40/73 | 0.2656 |
| STRUCTURAL_IRIS | SOBTI_5_ET | ASIA_MORNING_LIT | 140 | 60.71% | 60.86% | 43/67 | 42/73 | 0.2557 |
| AURORA | SOBTI_5_ET | EUROPE_LIT | 144 | 54.17% | 51.12% | 59/83 | 19/61 | 0.2627 |
| PATH_GLOBAL | SOBTI_5_ET | EUROPE_LIT | 144 | 54.17% | 51.12% | 59/83 | 19/61 | 0.2627 |
| STRUCTURAL_IRIS | SOBTI_5_ET | EUROPE_LIT | 144 | 50.69% | 45.71% | 65/83 | 8/61 | 0.2631 |
