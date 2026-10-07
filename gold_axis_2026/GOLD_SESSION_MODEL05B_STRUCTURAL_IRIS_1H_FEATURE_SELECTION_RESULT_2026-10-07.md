# SESSION MODEL-05B — STRUCTURAL_IRIS 1H FEATURE-SELECTION CHALLENGER

**Status:** complete.

A1 structural logit is mandatory; only the canonical 1h PATH block is reduced.

## Frozen path variables

| Partition | Window | Frozen path features |
|---|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | g1h_age_max_pos_24, g1h_ret_6h, g1h_rv_6, g1h_lag2, g1h_ret_1h, g1h_ret_12h, g1h_jump_concentration_24, g1h_ret_3h |
| SOBTI_5_ET | ASIA_MORNING_LIT | g1h_ret_3h, g1h_ret_1h, g1h_slope_24, g1h_jump_concentration_24, g1h_rv_48, g1h_rv_6, g1h_up_semivol_24, g1h_close_location_24 |
| SOBTI_5_ET | EUROPE_LIT | g1h_ret_6h, g1h_ret_1h, g1h_ret_3h, g1h_ret_12h, g1h_age_max_neg_24, g1h_jump_concentration_24, g1h_ret_48h, g1h_rv_12 |
| SOBTI_5_ET | NY_LONDON_LIT | g1h_ret_3h, g1h_down_semivol_24, g1h_ret_1h, g1h_rv_12, g1h_jump_concentration_24, g1h_range_24, g1h_ret_6h, g1h_slope_24 |
| SOBTI_5_ET | US_LATE_LIT | g1h_ret_1h, g1h_ret_3h, g1h_ret_6h |
| WGC_2026_NY3 | ASIA | g1h_ret_3h, g1h_ret_1h, g1h_upfrac_24, g1h_ret_12h, g1h_ret_6h, g1h_range_24, g1h_ret_48h, g1h_rv_48 |
| WGC_2026_NY3 | EUROPE | g1h_jump_concentration_24, g1h_ret_3h, g1h_ret_6h, g1h_close_location_24, g1h_upfrac_24, g1h_ret_48h, g1h_lag2, g1h_ret_1h |
| WGC_2026_NY3 | US | g1h_ret_3h, g1h_ret_1h, g1h_ret_6h, g1h_jump_concentration_24, g1h_slope_24, g1h_down_up_semivol_ratio_24, g1h_range_24, g1h_age_max_pos_24 |

## 2025 exact common-row transport

| Model | Partition | Window | N | Accuracy | BA | UP recall | DOWN recall | Brier |
|---|---|---|---:|---:|---:|---:|---:|---:|
| S14_A1_PLUS_1H_FULL | SOBTI_5_ET | ASIA_AFTERNOON_LIT | 137 | 48.91% | 48.92% | 51.47% | 46.38% | 0.2771 |
| S14_A1_PLUS_1H_SELECTED | SOBTI_5_ET | ASIA_AFTERNOON_LIT | 137 | 47.45% | 47.46% | 50.00% | 44.93% | 0.2654 |
| S14_A1_PLUS_1H_FULL | SOBTI_5_ET | ASIA_MORNING_LIT | 140 | 61.43% | 61.60% | 65.67% | 57.53% | 0.2521 |
| S14_A1_PLUS_1H_SELECTED | SOBTI_5_ET | ASIA_MORNING_LIT | 140 | 60.00% | 60.05% | 61.19% | 58.90% | 0.2458 |
| S14_A1_PLUS_1H_FULL | SOBTI_5_ET | EUROPE_LIT | 144 | 50.69% | 45.71% | 78.31% | 13.11% | 0.2631 |
| S14_A1_PLUS_1H_SELECTED | SOBTI_5_ET | EUROPE_LIT | 144 | 50.69% | 44.63% | 84.34% | 4.92% | 0.2572 |
| S14_A1_PLUS_1H_FULL | SOBTI_5_ET | NY_LONDON_LIT | 144 | 50.00% | 51.15% | 41.98% | 60.32% | 0.2726 |
| S14_A1_PLUS_1H_SELECTED | SOBTI_5_ET | NY_LONDON_LIT | 144 | 49.31% | 50.53% | 40.74% | 60.32% | 0.2714 |
| S14_A1_PLUS_1H_FULL | SOBTI_5_ET | US_LATE_LIT | 107 | 59.81% | 53.30% | 79.10% | 27.50% | 0.2478 |
| S14_A1_PLUS_1H_SELECTED | SOBTI_5_ET | US_LATE_LIT | 107 | 61.68% | 51.27% | 92.54% | 10.00% | 0.2329 |
| S14_A1_PLUS_1H_FULL | WGC_2026_NY3 | ASIA | 105 | 55.24% | 51.61% | 86.21% | 17.02% | 0.2811 |
| S14_A1_PLUS_1H_SELECTED | WGC_2026_NY3 | ASIA | 105 | 49.52% | 46.04% | 79.31% | 12.77% | 0.2663 |
| S14_A1_PLUS_1H_FULL | WGC_2026_NY3 | EUROPE | 145 | 51.03% | 49.28% | 66.25% | 32.31% | 0.2710 |
| S14_A1_PLUS_1H_SELECTED | WGC_2026_NY3 | EUROPE | 145 | 54.48% | 51.68% | 78.75% | 24.62% | 0.2594 |
| S14_A1_PLUS_1H_FULL | WGC_2026_NY3 | US | 140 | 41.43% | 44.83% | 26.51% | 63.16% | 0.2998 |
| S14_A1_PLUS_1H_SELECTED | WGC_2026_NY3 | US | 140 | 37.86% | 42.09% | 19.28% | 64.91% | 0.2933 |
