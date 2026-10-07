# SESSION MODEL-04B — PATH_GLOBAL FEATURE-SELECTION CHALLENGER

**Status:** complete.

## Frozen session-specific features

| Partition | Window | Frozen features |
|---|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | g1h_slope_6, g1h_ret_3h, g1h_rv_48, g1h_down_semivol_24, g1h_ret_1h, g1h_ret_48h, g1h_age_max_pos_24, g1h_lag2 |
| SOBTI_5_ET | ASIA_MORNING_LIT | g1h_ret_3h, g1h_jump_concentration_24, g1h_age_max_pos_24, g1h_ret_6h, g1h_ret_1h, g1h_up_semivol_24, g1h_rv_6, g1h_age_max_neg_24 |
| SOBTI_5_ET | EUROPE_LIT | g1h_jump_concentration_24, g1h_lag2, g1h_age_max_pos_24, g1h_ret_3h, g1h_ret_1h, g1h_ret_6h, g1h_up_semivol_24, g1h_max_drawdown_24 |
| SOBTI_5_ET | NY_LONDON_LIT | g1h_ret_1h, g1h_ret_3h, g1h_ret_6h, g1h_rv_24, g1h_range_24, g1h_lag2, g1h_upfrac_24, g1h_rv_12 |
| SOBTI_5_ET | US_LATE_LIT | g1h_ret_3h, g1h_slope_6, g1h_lag2, g1h_rv_48, g1h_age_max_pos_24, g1h_age_max_neg_24, g1h_jump_concentration_24, g1h_down_up_semivol_ratio_24 |
| WGC_2026_NY3 | ASIA | g1h_rv_48, g1h_ret_3h, g1h_max_drawdown_24, g1h_slope_6, g1h_lag2, g1h_ret_1h, g1h_ret_12h, g1h_jump_concentration_24 |
| WGC_2026_NY3 | EUROPE | g1h_jump_concentration_24, g1h_ret_3h, g1h_ret_6h, g1h_age_max_pos_24, g1h_ret_1h, g1h_upfrac_24, g1h_slope_6, g1h_max_drawdown_24 |
| WGC_2026_NY3 | US | g1h_ret_1h, g1h_ret_3h, g1h_lag2, g1h_range_24, g1h_ret_6h, g1h_ret_48h, g1h_down_up_semivol_ratio_24, g1h_upfrac_24 |

## 2025 exact common-row transport

| Model | Partition | Window | N | Accuracy | BA | UP recall | DOWN recall | Brier |
|---|---|---|---:|---:|---:|---:|---:|---:|
| BASELINE_PATH_GLOBAL | SOBTI_5_ET | ASIA_AFTERNOON_LIT | 137 | 50.36% | 50.35% | 48.53% | 52.17% | 0.2705 |
| SELECTED_PATH_GLOBAL | SOBTI_5_ET | ASIA_AFTERNOON_LIT | 137 | 47.45% | 47.49% | 52.94% | 42.03% | 0.2653 |
| BASELINE_PATH_GLOBAL | SOBTI_5_ET | ASIA_MORNING_LIT | 140 | 53.57% | 53.52% | 52.24% | 54.79% | 0.2656 |
| SELECTED_PATH_GLOBAL | SOBTI_5_ET | ASIA_MORNING_LIT | 140 | 53.57% | 53.52% | 52.24% | 54.79% | 0.2556 |
| BASELINE_PATH_GLOBAL | SOBTI_5_ET | EUROPE_LIT | 144 | 54.17% | 51.12% | 71.08% | 31.15% | 0.2627 |
| SELECTED_PATH_GLOBAL | SOBTI_5_ET | EUROPE_LIT | 144 | 53.47% | 49.21% | 77.11% | 21.31% | 0.2529 |
| BASELINE_PATH_GLOBAL | SOBTI_5_ET | NY_LONDON_LIT | 144 | 41.67% | 42.68% | 34.57% | 50.79% | 0.2740 |
| SELECTED_PATH_GLOBAL | SOBTI_5_ET | NY_LONDON_LIT | 144 | 41.67% | 41.98% | 39.51% | 44.44% | 0.2672 |
| BASELINE_PATH_GLOBAL | SOBTI_5_ET | US_LATE_LIT | 107 | 59.81% | 53.30% | 79.10% | 27.50% | 0.2559 |
| SELECTED_PATH_GLOBAL | SOBTI_5_ET | US_LATE_LIT | 107 | 58.88% | 52.05% | 79.10% | 25.00% | 0.2531 |
| BASELINE_PATH_GLOBAL | WGC_2026_NY3 | ASIA | 105 | 60.00% | 58.14% | 75.86% | 40.43% | 0.2608 |
| SELECTED_PATH_GLOBAL | WGC_2026_NY3 | ASIA | 105 | 60.95% | 59.21% | 75.86% | 42.55% | 0.2461 |
| BASELINE_PATH_GLOBAL | WGC_2026_NY3 | EUROPE | 145 | 53.10% | 51.59% | 66.25% | 36.92% | 0.2676 |
| SELECTED_PATH_GLOBAL | WGC_2026_NY3 | EUROPE | 145 | 54.48% | 51.68% | 78.75% | 24.62% | 0.2552 |
| BASELINE_PATH_GLOBAL | WGC_2026_NY3 | US | 140 | 47.14% | 49.38% | 37.35% | 61.40% | 0.2825 |
| SELECTED_PATH_GLOBAL | WGC_2026_NY3 | US | 140 | 39.29% | 40.55% | 33.73% | 47.37% | 0.2740 |
