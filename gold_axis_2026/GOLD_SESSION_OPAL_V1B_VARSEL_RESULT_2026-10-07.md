# SESSION OPAL V1B — VARIABLE-SELECTION RESULT

## Frozen features

| Partition | Window | Features |
|---|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | trend_x_opt_mm, opt_mm_net, opt_prod_net |
| SOBTI_5_ET | ASIA_MORNING_LIT | trend_x_opt_mm, d_opt_prod_net, opt_other_z52 |
| SOBTI_5_ET | EUROPE_LIT | opt_mm_net, opt_prod_z52, d_opt_mm_net, trend_strength |
| SOBTI_5_ET | NY_LONDON_LIT | opt_swap_net, d_opt_prod_net, opt_prod_z52, trend_strength |
| SOBTI_5_ET | US_LATE_LIT | spec_swap_gap, trend_x_opt_prod, opt_swap_net |
| WGC_2026_NY3 | ASIA | opt_mm_net, trend_x_opt_mm, opt_prod_net |
| WGC_2026_NY3 | EUROPE | d_opt_mm_net, d_opt_prod_net, trend_x_opt_mm |
| WGC_2026_NY3 | US | opt_prod_net, opt_mm_net, trend_x_opt_prod |

## Pre-2025 nested eligibility

| Partition | Window | N | AURORA BA | Selected OPAL BA | UP | DOWN | Overrides | Net rescue | Eligible | Reason |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 84 | 49.04% | 49.04% | 39.53% | 58.54% | 0 | +0 | False | NET_RESCUE_NOT_POSITIVE|NO_OVERRIDE |
| SOBTI_5_ET | ASIA_MORNING_LIT | 81 | 56.08% | 55.39% | 60.78% | 50.00% | 4 | +0 | False | 2024_BRIER|DEV_BA|NET_RESCUE_NOT_POSITIVE |
| SOBTI_5_ET | EUROPE_LIT | 99 | 49.50% | 48.31% | 56.14% | 40.48% | 1 | -1 | False | 2024_ACC|2024_BRIER|DEV_BA|NET_RESCUE_NOT_POSITIVE |
| SOBTI_5_ET | NY_LONDON_LIT | 102 | 57.97% | 57.97% | 61.22% | 54.72% | 0 | +0 | False | NET_RESCUE_NOT_POSITIVE|NO_OVERRIDE |
| SOBTI_5_ET | US_LATE_LIT | 6 | 25.00% | 50.00% | 100.00% | 0.00% | 1 | +1 | False | RECALL_FLOOR |
| WGC_2026_NY3 | ASIA | 13 | 43.75% | 43.75% | 87.50% | 0.00% | 0 | +0 | False | RECALL_FLOOR|NET_RESCUE_NOT_POSITIVE|NO_OVERRIDE |
| WGC_2026_NY3 | EUROPE | 99 | 45.24% | 47.93% | 64.91% | 30.95% | 4 | +2 | True | PASS |
| WGC_2026_NY3 | US | 72 | 42.01% | 42.01% | 54.29% | 29.73% | 0 | +0 | False | RECALL_FLOOR|NET_RESCUE_NOT_POSITIVE|NO_OVERRIDE |

## Frozen 2025 transport

| Model | Partition | Window | N | OPAL BA | UP | DOWN | Brier | Overrides | Net rescue |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| CANONICAL_OPAL | WGC_2026_NY3 | EUROPE | 145 | 52.64% | 63.75% | 41.54% | 0.2676 | 13 | +1 |
| SELECTED_OPAL | WGC_2026_NY3 | EUROPE | 145 | 50.96% | 65.00% | 36.92% | 0.2713 | 1 | -1 |
