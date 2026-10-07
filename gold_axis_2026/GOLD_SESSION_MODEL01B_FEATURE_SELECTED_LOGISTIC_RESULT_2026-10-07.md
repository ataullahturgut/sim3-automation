# SESSION MODEL-01B — FEATURE-SELECTED CLASSICAL LOGISTIC

**Status:** complete.

Final estimator remains the same Classical Logistic as Model-01; only the feature representation changes.

## Frozen session-specific features

| Partition | Window | Frozen features |
|---|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | gold_r3, g_rv_48, g_jump_concentration_24, g_down_semivol_24, g_down_up_semivol_ratio_24, g_recovery_24, sigma20, g_age_max_pos_24 |
| SOBTI_5_ET | ASIA_MORNING_LIT | gold_r1, g_ret_3h, g_age_max_neg_24, g_down_up_semivol_ratio_24, gold_r5, g_ret_1h, platinum_r5, g_jump_concentration_24 |
| SOBTI_5_ET | EUROPE_LIT | gold_r3, gold_r1, gold_r5, g_slope_6, platinum_r21, g_age_max_pos_24, g_max_drawdown_24, silver_r1 |
| SOBTI_5_ET | NY_LONDON_LIT | gold_r5, gold_r3, gold_r1, g_ret_1h, g_slope_6, g_range_24, sigma20, g_lag2 |
| SOBTI_5_ET | US_LATE_LIT | g_slope_6, g_jump_concentration_24, g_lag2, g_rv_48, g_upfrac_24, sigma20, platinum_r21, g_age_max_neg_24 |
| WGC_2026_NY3 | ASIA | g_max_drawdown_24, g_ret_3h, g_rv_48, gold_r1, g_upfrac_24, gold_r10, gold_r21, g_ret_1h |
| WGC_2026_NY3 | EUROPE | platinum_r21, gold_r5, g_lag2, gold_r3, silver_r1, gold_r1, g_max_drawdown_24, g_ret_48h |
| WGC_2026_NY3 | US | g_slope_6, sigma20, gold_r5, gold_r3, g_range_24, gold_r1, g_ret_1h, platinum_r21 |

## 2025 frozen-specification transport

| Partition | Window | N | Accuracy | BA | UP recall | DOWN recall | Brier |
|---|---|---:|---:|---:|---:|---:|---:|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 141 | 58.87% | 59.09% | 69.57% | 48.61% | 0.2528 |
| SOBTI_5_ET | ASIA_MORNING_LIT | 141 | 46.10% | 46.53% | 55.22% | 37.84% | 0.2769 |
| SOBTI_5_ET | EUROPE_LIT | 147 | 48.30% | 46.43% | 59.52% | 33.33% | 0.2570 |
| SOBTI_5_ET | NY_LONDON_LIT | 146 | 47.95% | 46.18% | 59.04% | 33.33% | 0.2679 |
| SOBTI_5_ET | US_LATE_LIT | 108 | 55.56% | 48.75% | 75.00% | 22.50% | 0.2589 |
| WGC_2026_NY3 | ASIA | 107 | 54.21% | 52.53% | 72.41% | 32.65% | 0.2589 |
| WGC_2026_NY3 | EUROPE | 146 | 51.37% | 50.98% | 55.00% | 46.97% | 0.2650 |
| WGC_2026_NY3 | US | 141 | 43.97% | 44.80% | 40.48% | 49.12% | 0.2710 |

All XAU15 variables are computed from observations available strictly before each specific session start.
