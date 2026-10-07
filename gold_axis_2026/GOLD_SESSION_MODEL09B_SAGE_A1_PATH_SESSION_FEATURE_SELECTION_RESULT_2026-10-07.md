# SESSION MODEL-09B — SAGE A1_PATH_SESSION FEATURE-SELECTION RESULT

**Status:** complete.

## Frozen representations

| Partition | Window | PATH variables | SAGE variables |
|---|---|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | g1h_age_max_pos_24, g1h_rv_6, g1h_ret_1h, g1h_lag2 | sess_asia, sess_east_west_conflict, sess_sign_changes, sess_asia_us_interaction |
| SOBTI_5_ET | ASIA_MORNING_LIT | g1h_ret_3h, g1h_jump_concentration_24, g1h_ret_1h, g1h_rv_6 | sess_asia_us_interaction, sess_sign_changes, sess_asia, sess_europe |
| SOBTI_5_ET | EUROPE_LIT | g1h_ret_1h, g1h_ret_6h, g1h_ret_3h, g1h_ret_12h, g1h_jump_concentration_24, g1h_ret_48h | sess_asia, sess_europe |
| SOBTI_5_ET | NY_LONDON_LIT | g1h_ret_3h, g1h_ret_1h, g1h_ret_6h, g1h_jump_concentration_24, g1h_down_semivol_24 | sess_us_conflict, sess_asia, sess_asia_us_interaction |
| SOBTI_5_ET | US_LATE_LIT | g1h_ret_3h, g1h_ret_1h, g1h_rv_48 | sess_asia |
| WGC_2026_NY3 | ASIA | g1h_ret_1h, g1h_ret_3h, g1h_upfrac_24, g1h_ret_48h, g1h_rv_6, g1h_slope_24 | sess_us_conflict, sess_dominance |
| WGC_2026_NY3 | EUROPE | g1h_ret_1h, g1h_ret_3h, g1h_jump_concentration_24, g1h_ret_6h, g1h_upfrac_24 | sess_sign_changes, sess_asia, sess_us_pm |
| WGC_2026_NY3 | US | g1h_ret_3h, g1h_ret_1h, g1h_ret_6h, g1h_jump_concentration_24 | sess_asia, sess_asia_us_interaction, sess_us_conflict, sess_sign_changes |

## Pre-2025 eligibility

| Partition | Window | N | Candidate BA | Matched A1+PATH BA | UP | DOWN | Eligible | Reason |
|---|---|---:|---:|---:|---:|---:|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 191 | 56.14% | 54.51% | 54.81% | 57.47% | False | YEAR_SIGN_FAIL |
| SOBTI_5_ET | ASIA_MORNING_LIT | 184 | 49.19% | 49.96% | 50.94% | 47.44% | False | BA_BELOW_COMPARATOR|YEAR_SIGN_FAIL |
| SOBTI_5_ET | EUROPE_LIT | 213 | 45.09% | 45.51% | 68.91% | 21.28% | False | RECALL_FLOOR|BA_BELOW_COMPARATOR|YEAR_SIGN_FAIL |
| SOBTI_5_ET | NY_LONDON_LIT | 215 | 56.41% | 53.50% | 46.15% | 66.67% | True | PASS |
| SOBTI_5_ET | US_LATE_LIT | 89 | 54.40% | 50.38% | 77.08% | 31.71% | True | PASS |
| WGC_2026_NY3 | ASIA | 102 | 51.91% | 49.54% | 82.61% | 21.21% | False | RECALL_FLOOR |
| WGC_2026_NY3 | EUROPE | 215 | 51.79% | 53.14% | 75.00% | 28.57% | False | RECALL_FLOOR|BA_BELOW_COMPARATOR|YEAR_SIGN_FAIL |
| WGC_2026_NY3 | US | 177 | 59.94% | 55.13% | 41.86% | 78.02% | True | PASS |

## 2025 transport

| Partition | Window | N | Candidate BA | Matched A1+PATH BA | Delta BA | Candidate Brier | Comparator Brier |
|---|---|---:|---:|---:|---:|---:|---:|
| SOBTI_5_ET | NY_LONDON_LIT | 144 | 52.73% | 45.86% | +6.88 pp | 0.2681 | 0.2655 |
| SOBTI_5_ET | US_LATE_LIT | 107 | 44.79% | 44.79% | +0.00 pp | 0.2613 | 0.2619 |
| WGC_2026_NY3 | US | 140 | 45.38% | 40.89% | +4.49 pp | 0.2928 | 0.2861 |
