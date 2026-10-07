# SESSION PRISM V1 — RESULT

## Development lambda selection

| Partition | Window | Lambda | N | AURORA BA | PRISM BA | PRISM UP | PRISM DOWN | Changed | Rescue | Break | Net | Eligible |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 1.0 | 84 | 49.04% | 51.25% | 48.84% | 53.66% | 30 | 16 | 14 | +2 | False |
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 10.0 | 84 | 49.04% | 51.36% | 44.19% | 58.54% | 22 | 12 | 10 | +2 | False |
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 50.0 | 84 | 49.04% | 50.03% | 48.84% | 51.22% | 13 | 7 | 6 | +1 | True |
| SOBTI_5_ET | ASIA_MORNING_LIT | 1.0 | 81 | 56.08% | 53.73% | 60.78% | 46.67% | 27 | 13 | 14 | -1 | False |
| SOBTI_5_ET | ASIA_MORNING_LIT | 10.0 | 81 | 56.08% | 55.78% | 54.90% | 56.67% | 19 | 9 | 10 | -1 | False |
| SOBTI_5_ET | ASIA_MORNING_LIT | 50.0 | 81 | 56.08% | 53.14% | 52.94% | 53.33% | 13 | 5 | 8 | -3 | False |
| SOBTI_5_ET | EUROPE_LIT | 1.0 | 99 | 49.50% | 49.50% | 56.14% | 42.86% | 36 | 18 | 18 | +0 | False |
| SOBTI_5_ET | EUROPE_LIT | 10.0 | 99 | 49.50% | 48.93% | 52.63% | 45.24% | 31 | 15 | 16 | -1 | False |
| SOBTI_5_ET | EUROPE_LIT | 50.0 | 99 | 49.50% | 45.68% | 50.88% | 40.48% | 24 | 10 | 14 | -4 | False |
| SOBTI_5_ET | NY_LONDON_LIT | 1.0 | 102 | 57.97% | 59.93% | 63.27% | 56.60% | 28 | 15 | 13 | +2 | False |
| SOBTI_5_ET | NY_LONDON_LIT | 10.0 | 102 | 57.97% | 59.07% | 65.31% | 52.83% | 27 | 14 | 13 | +1 | True |
| SOBTI_5_ET | NY_LONDON_LIT | 50.0 | 102 | 57.97% | 60.95% | 65.31% | 56.60% | 13 | 8 | 5 | +3 | True |
| SOBTI_5_ET | US_LATE_LIT | 1.0 | 6 | 25.00% | 25.00% | 50.00% | 0.00% | 0 | 0 | 0 | +0 | False |
| SOBTI_5_ET | US_LATE_LIT | 10.0 | 6 | 25.00% | 25.00% | 50.00% | 0.00% | 0 | 0 | 0 | +0 | False |
| SOBTI_5_ET | US_LATE_LIT | 50.0 | 6 | 25.00% | 25.00% | 50.00% | 0.00% | 0 | 0 | 0 | +0 | False |
| WGC_2026_NY3 | ASIA | 1.0 | 13 | 43.75% | 31.25% | 62.50% | 0.00% | 2 | 0 | 2 | -2 | False |
| WGC_2026_NY3 | ASIA | 10.0 | 13 | 43.75% | 43.75% | 87.50% | 0.00% | 0 | 0 | 0 | +0 | False |
| WGC_2026_NY3 | ASIA | 50.0 | 13 | 43.75% | 43.75% | 87.50% | 0.00% | 0 | 0 | 0 | +0 | False |
| WGC_2026_NY3 | EUROPE | 1.0 | 99 | 45.24% | 41.73% | 59.65% | 23.81% | 30 | 13 | 17 | -4 | False |
| WGC_2026_NY3 | EUROPE | 10.0 | 99 | 45.24% | 45.55% | 64.91% | 26.19% | 24 | 12 | 12 | +0 | False |
| WGC_2026_NY3 | EUROPE | 50.0 | 99 | 45.24% | 45.24% | 66.67% | 23.81% | 16 | 8 | 8 | +0 | False |
| WGC_2026_NY3 | US | 1.0 | 72 | 42.01% | 45.75% | 42.86% | 48.65% | 25 | 14 | 11 | +3 | False |
| WGC_2026_NY3 | US | 10.0 | 72 | 42.01% | 42.97% | 40.00% | 45.95% | 19 | 10 | 9 | +1 | False |
| WGC_2026_NY3 | US | 50.0 | 72 | 42.01% | 41.78% | 45.71% | 37.84% | 8 | 4 | 4 | +0 | False |

## Frozen 2025 transport

| Partition | Window | Lambda | N | AURORA BA | PRISM BA | PRISM UP | PRISM DOWN | AURORA Brier | PRISM Brier | Changed | Net rescue |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 50.0 | 137 | 48.92% | 43.04% | 39.71% | 46.38% | 0.2755 | 0.2855 | 20 | -8 |
| SOBTI_5_ET | NY_LONDON_LIT | 50.0 | 144 | 51.15% | 50.35% | 41.98% | 58.73% | 0.2726 | 0.2771 | 25 | -1 |
