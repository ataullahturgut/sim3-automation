# SESSION MODEL-07B — SAGE PATH_SESSION FEATURE-SELECTION RESULT

**Status:** complete.

## Frozen representations

| Partition | Window | PATH variables | SAGE variables |
|---|---|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | g1h_slope_6, g1h_rv_48, g1h_down_semivol_24, g1h_ret_48h | sess_us_conflict, sess_east_west_conflict, sess_dispersion, sess_sign_changes |
| SOBTI_5_ET | ASIA_MORNING_LIT | g1h_ret_3h, g1h_jump_concentration_24, g1h_age_max_pos_24, g1h_ret_1h, g1h_max_drawdown_24 | sess_asia, sess_europe, sess_east_west |
| SOBTI_5_ET | EUROPE_LIT | g1h_lag2, g1h_age_max_pos_24, g1h_jump_concentration_24, g1h_max_drawdown_24, g1h_ret_1h | sess_sign_changes, sess_east_west_conflict, sess_europe |
| SOBTI_5_ET | NY_LONDON_LIT | g1h_ret_1h, g1h_rv_24, g1h_upfrac_24, g1h_lag2 | sess_us_conflict, sess_asia, sess_east_west_conflict, sess_europe |
| SOBTI_5_ET | US_LATE_LIT | g1h_ret_1h, g1h_slope_6, g1h_age_max_neg_24, g1h_lag2, g1h_age_max_pos_24 | sess_asia, sess_asia_us_interaction, sess_dominance |
| WGC_2026_NY3 | ASIA | g1h_rv_48, g1h_ret_1h | sess_us_conflict, sess_us_pm, sess_dominance, sess_us_reversal, sess_europe, sess_east_west_conflict |
| WGC_2026_NY3 | EUROPE | g1h_jump_concentration_24, g1h_age_max_pos_24, g1h_ret_1h, g1h_ret_3h, g1h_upfrac_24 | sess_sign_changes, sess_asia, sess_europe |
| WGC_2026_NY3 | US | g1h_ret_1h, g1h_lag2, g1h_range_24, g1h_ret_48h, g1h_upfrac_24 | sess_asia, sess_asia_us_interaction, sess_europe |

## Pre-2025 eligibility

| Partition | Window | N | Candidate BA | Comparator BA | UP | DOWN | Eligible | Reason |
|---|---|---:|---:|---:|---:|---:|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 279 | 54.88% | 54.34% | 53.79% | 55.97% | False | YEAR_SIGN_FAIL |
| SOBTI_5_ET | ASIA_MORNING_LIT | 272 | 51.54% | 53.76% | 39.31% | 63.78% | False | BA_BELOW_COMPARATOR|YEAR_SIGN_FAIL |
| SOBTI_5_ET | EUROPE_LIT | 295 | 49.49% | 50.48% | 67.68% | 31.30% | False | BA_BELOW_COMPARATOR|YEAR_SIGN_FAIL |
| SOBTI_5_ET | NY_LONDON_LIT | 297 | 53.57% | 50.41% | 55.17% | 51.97% | True | PASS |
| SOBTI_5_ET | US_LATE_LIT | 170 | 48.00% | 50.00% | 66.00% | 30.00% | False | BA_BELOW_COMPARATOR|YEAR_SIGN_FAIL |
| WGC_2026_NY3 | ASIA | 152 | 55.72% | 51.37% | 66.34% | 45.10% | True | PASS |
| WGC_2026_NY3 | EUROPE | 297 | 54.11% | 53.43% | 70.24% | 37.98% | False | YEAR_SIGN_FAIL |
| WGC_2026_NY3 | US | 264 | 50.54% | 50.11% | 45.30% | 55.78% | False | YEAR_SIGN_FAIL |

## 2025 transport

| Partition | Window | N | Candidate BA | Comparator BA | Delta BA | Candidate Brier | Comparator Brier |
|---|---|---:|---:|---:|---:|---:|---:|
| SOBTI_5_ET | NY_LONDON_LIT | 144 | 47.62% | 45.15% | +2.47 pp | 0.2731 | 0.2681 |
| WGC_2026_NY3 | ASIA | 105 | 52.11% | 50.09% | +2.02 pp | 0.2572 | 0.2530 |
