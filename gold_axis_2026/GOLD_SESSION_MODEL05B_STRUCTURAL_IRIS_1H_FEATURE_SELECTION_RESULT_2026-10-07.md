# SESSION MODEL-05B — STRUCTURAL_IRIS 1H FEATURE-SELECTION CHALLENGER

**Status:** complete.

A1 structural logit is mandatory; only the canonical 1h PATH block is reduced.

## Frozen path variables

| Partition | Window | Frozen path features |
|---|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | g1h_age_max_pos_24, g1h_rv_6, g1h_ret_6h, g1h_lag2, g1h_ret_1h, g1h_ret_12h, g1h_jump_concentration_24, g1h_down_semivol_24 |
| SOBTI_5_ET | ASIA_MORNING_LIT | g1h_ret_3h, g1h_ret_1h, g1h_jump_concentration_24, g1h_rv_48, g1h_slope_24, g1h_ret_6h, g1h_rv_6, g1h_age_max_pos_24 |
| SOBTI_5_ET | EUROPE_LIT | g1h_ret_6h, g1h_ret_1h, g1h_ret_3h, g1h_ret_12h, g1h_age_max_neg_24, g1h_jump_concentration_24, g1h_ret_48h, g1h_rv_12 |
| SOBTI_5_ET | NY_LONDON_LIT | g1h_ret_3h, g1h_down_semivol_24, g1h_ret_1h, g1h_rv_12, g1h_jump_concentration_24, g1h_range_24, g1h_ret_6h, g1h_slope_24 |
| SOBTI_5_ET | US_LATE_LIT | g1h_ret_1h, g1h_ret_3h, g1h_ret_6h |
| WGC_2026_NY3 | ASIA | g1h_ret_3h, g1h_ret_1h, g1h_upfrac_24, g1h_ret_12h, g1h_ret_6h, g1h_range_24, g1h_ret_48h, g1h_rv_48 |
| WGC_2026_NY3 | EUROPE | g1h_ret_3h, g1h_ret_6h, g1h_ret_1h, g1h_jump_concentration_24, g1h_upfrac_24, g1h_ret_48h, g1h_close_location_24, g1h_lag2 |
| WGC_2026_NY3 | US | g1h_ret_3h, g1h_ret_1h, g1h_ret_6h, g1h_jump_concentration_24, g1h_slope_24, g1h_down_up_semivol_ratio_24, g1h_range_24, g1h_age_max_pos_24 |

## 2025 exact common-row transport

| Model | Partition | Window | N | Accuracy | BA | UP recall | DOWN recall | Brier |
|---|---|---|---:|---:|---:|---:|---:|---:|
| S14_A1_PLUS_1H_FULL | SOBTI_5_ET | ASIA_AFTERNOON_LIT | 137 | 48.91% | 48.92% | 51.47% | 46.38% | 0.2777 |
| S14_A1_PLUS_1H_SELECTED | SOBTI_5_ET | ASIA_AFTERNOON_LIT | 137 | 43.80% | 43.81% | 45.59% | 42.03% | 0.2643 |
| S14_A1_PLUS_1H_FULL | SOBTI_5_ET | ASIA_MORNING_LIT | 140 | 60.71% | 60.86% | 64.18% | 57.53% | 0.2557 |
| S14_A1_PLUS_1H_SELECTED | SOBTI_5_ET | ASIA_MORNING_LIT | 140 | 57.14% | 57.49% | 65.67% | 49.32% | 0.2555 |
| S14_A1_PLUS_1H_FULL | SOBTI_5_ET | EUROPE_LIT | 144 | 50.69% | 45.71% | 78.31% | 13.11% | 0.2631 |
| S14_A1_PLUS_1H_SELECTED | SOBTI_5_ET | EUROPE_LIT | 144 | 50.69% | 44.63% | 84.34% | 4.92% | 0.2572 |
| S14_A1_PLUS_1H_FULL | SOBTI_5_ET | NY_LONDON_LIT | 144 | 50.00% | 51.15% | 41.98% | 60.32% | 0.2726 |
| S14_A1_PLUS_1H_SELECTED | SOBTI_5_ET | NY_LONDON_LIT | 144 | 49.31% | 50.53% | 40.74% | 60.32% | 0.2714 |
| S14_A1_PLUS_1H_FULL | SOBTI_5_ET | US_LATE_LIT | 107 | 59.81% | 53.30% | 79.10% | 27.50% | 0.2478 |
| S14_A1_PLUS_1H_SELECTED | SOBTI_5_ET | US_LATE_LIT | 107 | 61.68% | 51.27% | 92.54% | 10.00% | 0.2329 |
| S14_A1_PLUS_1H_FULL | WGC_2026_NY3 | ASIA | 104 | 55.77% | 51.80% | 86.21% | 17.39% | 0.2792 |
| S14_A1_PLUS_1H_SELECTED | WGC_2026_NY3 | ASIA | 104 | 50.96% | 47.04% | 81.03% | 13.04% | 0.2664 |
| S14_A1_PLUS_1H_FULL | WGC_2026_NY3 | EUROPE | 145 | 51.72% | 49.90% | 67.50% | 32.31% | 0.2686 |
| S14_A1_PLUS_1H_SELECTED | WGC_2026_NY3 | EUROPE | 145 | 53.79% | 51.06% | 77.50% | 24.62% | 0.2578 |
| S14_A1_PLUS_1H_FULL | WGC_2026_NY3 | US | 140 | 41.43% | 44.83% | 26.51% | 63.16% | 0.2998 |
| S14_A1_PLUS_1H_SELECTED | WGC_2026_NY3 | US | 140 | 37.86% | 42.09% | 19.28% | 64.91% | 0.2933 |
