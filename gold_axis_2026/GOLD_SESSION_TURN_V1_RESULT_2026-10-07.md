# SESSION TURN V1 — RESULT

## Development eligibility

| Partition | Window | N | AURORA BA | TURN BA | TURN UP | TURN DOWN | Overrides | Rescue | Break | Net | Both-tail | Eligible | Reason |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 175 | 52.76% | 54.74% | 49.47% | 60.00% | 9 | 6 | 3 | +3 | 19 | True | PASS |
| SOBTI_5_ET | ASIA_MORNING_LIT | 170 | 50.00% | 50.88% | 48.98% | 52.78% | 7 | 4 | 3 | +1 | 20 | True | PASS |
| SOBTI_5_ET | EUROPE_LIT | 189 | 50.45% | 48.21% | 53.40% | 43.02% | 9 | 2 | 7 | -5 | 22 | False | NET_RESCUE_NOT_POSITIVE|DEV_BA|2024_ACC |
| SOBTI_5_ET | NY_LONDON_LIT | 190 | 51.65% | 49.63% | 42.27% | 56.99% | 14 | 5 | 9 | -4 | 22 | False | NET_RESCUE_NOT_POSITIVE|DEV_BA|2024_ACC |
| SOBTI_5_ET | US_LATE_LIT | 89 | 50.05% | 50.23% | 68.75% | 31.71% | 6 | 3 | 3 | +0 | 10 | False | NET_RESCUE_NOT_POSITIVE|DEV_BRIER |
| WGC_2026_NY3 | ASIA | 102 | 47.36% | 52.77% | 78.26% | 27.27% | 8 | 5 | 3 | +2 | 17 | True | PASS |
| WGC_2026_NY3 | EUROPE | 189 | 49.78% | 48.81% | 59.81% | 37.80% | 11 | 4 | 7 | -3 | 21 | False | NET_RESCUE_NOT_POSITIVE|DEV_BA|2024_ACC |
| WGC_2026_NY3 | US | 162 | 43.90% | 42.12% | 36.14% | 48.10% | 17 | 7 | 10 | -3 | 17 | False | NET_RESCUE_NOT_POSITIVE|DEV_BA|DEV_BRIER|2023_ACC|2024_ACC |

## Frozen 2025 transport

| Partition | Window | N | AURORA BA | TURN BA | TURN UP | TURN DOWN | AURORA Brier | TURN Brier | Overrides | Rescue | Break | Net |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 137 | 48.92% | 49.66% | 52.94% | 46.38% | 0.2755 | 0.2735 | 1 | 1 | 0 | +1 |
| SOBTI_5_ET | ASIA_MORNING_LIT | 140 | 56.50% | 55.13% | 58.21% | 52.05% | 0.2698 | 0.2763 | 2 | 0 | 2 | -2 |
| WGC_2026_NY3 | ASIA | 104 | 55.32% | 55.96% | 79.31% | 32.61% | 0.2670 | 0.2690 | 3 | 2 | 1 | +1 |
