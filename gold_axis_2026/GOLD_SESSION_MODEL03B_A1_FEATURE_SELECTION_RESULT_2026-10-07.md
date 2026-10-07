# SESSION MODEL-03B — NOVA A1 / ARCR FEATURE-SELECTED CHALLENGER

**Status:** complete.

## Frozen session-specific features

| Partition | Window | Frozen features |
|---|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | gold_r3, g_rv_48, g_lag2, g_down_semivol_24, g_ret_6h, g_jump_concentration_24, platinum_r1, gold_r5 |
| SOBTI_5_ET | ASIA_MORNING_LIT | gold_r1, gold_r5, g_ret_3h, g_age_max_neg_24, g_down_up_semivol_ratio_24, g_jump_concentration_24, g_up_semivol_24, silver_r1 |
| SOBTI_5_ET | EUROPE_LIT | gold_r3, g_slope_6, g_age_max_pos_24, platinum_r21, g_max_drawdown_24, silver_r1, g_close_location_24, g_age_max_neg_24 |
| SOBTI_5_ET | NY_LONDON_LIT | gold_r5, gold_r3, gold_r1, g_ret_1h, g_slope_6, sigma20, g_range_24, g_lag2 |
| SOBTI_5_ET | US_LATE_LIT | g_lag2, g_ret_3h, g_slope_6 |
| WGC_2026_NY3 | ASIA | g_rv_48, g_ret_3h, g_max_drawdown_24 |
| WGC_2026_NY3 | EUROPE | platinum_r21, g_lag2, silver_r1, g_age_max_neg_24, gold_r3, gold_r5, g_max_drawdown_24, g_ret_48h |
| WGC_2026_NY3 | US | gold_r5, gold_r1, g_slope_6, sigma20, g_range_24, g_upfrac_24, g_lag2, platinum_r5 |

## 2025 exact common-row transport

| Model | Partition | Window | N | Accuracy | BA | UP recall | DOWN recall | Brier |
|---|---|---|---:|---:|---:|---:|---:|---:|
| BASELINE_A1_ARCR | SOBTI_5_ET | ASIA_AFTERNOON_LIT | 141 | 56.74% | 56.70% | 55.07% | 58.33% | 0.2453 |
| SELECTED_A1_ARCR | SOBTI_5_ET | ASIA_AFTERNOON_LIT | 141 | 50.35% | 50.54% | 59.42% | 41.67% | 0.2621 |
| BASELINE_A1_ARCR | SOBTI_5_ET | ASIA_MORNING_LIT | 141 | 53.19% | 53.29% | 55.22% | 51.35% | 0.2606 |
| SELECTED_A1_ARCR | SOBTI_5_ET | ASIA_MORNING_LIT | 141 | 49.65% | 49.49% | 46.27% | 52.70% | 0.2662 |
| BASELINE_A1_ARCR | SOBTI_5_ET | EUROPE_LIT | 147 | 50.34% | 50.40% | 50.00% | 50.79% | 0.2600 |
| SELECTED_A1_ARCR | SOBTI_5_ET | EUROPE_LIT | 147 | 44.22% | 43.85% | 46.43% | 41.27% | 0.2616 |
| BASELINE_A1_ARCR | SOBTI_5_ET | NY_LONDON_LIT | 146 | 48.63% | 49.08% | 45.78% | 52.38% | 0.2616 |
| SELECTED_A1_ARCR | SOBTI_5_ET | NY_LONDON_LIT | 146 | 47.95% | 46.95% | 54.22% | 39.68% | 0.2668 |
| BASELINE_A1_ARCR | SOBTI_5_ET | US_LATE_LIT | 108 | 58.33% | 51.99% | 76.47% | 27.50% | 0.2590 |
| SELECTED_A1_ARCR | SOBTI_5_ET | US_LATE_LIT | 108 | 58.33% | 50.44% | 80.88% | 20.00% | 0.2405 |
| BASELINE_A1_ARCR | WGC_2026_NY3 | ASIA | 107 | 52.34% | 50.97% | 67.24% | 34.69% | 0.2654 |
| SELECTED_A1_ARCR | WGC_2026_NY3 | ASIA | 107 | 55.14% | 54.03% | 67.24% | 40.82% | 0.2572 |
| BASELINE_A1_ARCR | WGC_2026_NY3 | EUROPE | 146 | 51.37% | 51.78% | 47.50% | 56.06% | 0.2623 |
| SELECTED_A1_ARCR | WGC_2026_NY3 | EUROPE | 146 | 50.68% | 50.62% | 51.25% | 50.00% | 0.2642 |
| BASELINE_A1_ARCR | WGC_2026_NY3 | US | 141 | 41.84% | 44.42% | 30.95% | 57.89% | 0.2748 |
| SELECTED_A1_ARCR | WGC_2026_NY3 | US | 141 | 40.43% | 39.57% | 44.05% | 35.09% | 0.2668 |

All candidate inputs are available strictly before the relevant session start.
