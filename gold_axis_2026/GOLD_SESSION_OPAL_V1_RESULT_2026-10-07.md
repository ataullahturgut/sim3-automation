# SESSION OPAL V1 — RESULT

## Pre-2025 eligibility

| Partition | Window | N | AURORA BA | OPAL BA | UP recall | DOWN recall | Overrides | Net rescue | Eligible | Reason |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 84 | 49.04% | 49.04% | 39.53% | 58.54% | 0 | +0 | False | NET_RESCUE_NOT_POSITIVE|NO_OVERRIDE |
| SOBTI_5_ET | ASIA_MORNING_LIT | 81 | 56.08% | 58.73% | 60.78% | 56.67% | 2 | +2 | True | PASS |
| SOBTI_5_ET | EUROPE_LIT | 99 | 49.50% | 48.31% | 56.14% | 40.48% | 1 | -1 | False | 2024_ACC|2024_BRIER|DEV_BA|NET_RESCUE_NOT_POSITIVE |
| SOBTI_5_ET | NY_LONDON_LIT | 102 | 57.97% | 56.08% | 61.22% | 50.94% | 2 | -2 | False | 2024_ACC|2024_BRIER|DEV_BA|NET_RESCUE_NOT_POSITIVE |
| SOBTI_5_ET | US_LATE_LIT | 6 | 25.00% | 50.00% | 100.00% | 0.00% | 1 | +1 | False | RECALL_FLOOR |
| WGC_2026_NY3 | ASIA | 13 | 43.75% | 53.75% | 87.50% | 20.00% | 1 | +1 | False | RECALL_FLOOR |
| WGC_2026_NY3 | EUROPE | 99 | 45.24% | 47.93% | 64.91% | 30.95% | 6 | +2 | True | PASS |
| WGC_2026_NY3 | US | 72 | 42.01% | 40.50% | 48.57% | 32.43% | 3 | -1 | False | 2024_ACC|2024_BRIER|DEV_BA|NET_RESCUE_NOT_POSITIVE |

## Frozen 2025 transport

| Partition | Window | N | AURORA BA | OPAL BA | OPAL UP | OPAL DOWN | AURORA Brier | OPAL Brier | Overrides | Net rescue |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SOBTI_5_ET | ASIA_MORNING_LIT | 140 | 56.50% | 55.76% | 56.72% | 54.79% | 0.2698 | 0.2727 | 5 | -1 |
| WGC_2026_NY3 | EUROPE | 145 | 51.59% | 52.64% | 63.75% | 41.54% | 0.2676 | 0.2676 | 13 | +1 |
