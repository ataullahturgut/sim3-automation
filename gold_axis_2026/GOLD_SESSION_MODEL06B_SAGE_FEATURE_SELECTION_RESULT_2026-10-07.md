# SESSION MODEL-06B — SAGE SESSION_ONLY FEATURE SELECTION

**Status:** complete.

## Pre-2025 selected-SAGE eligibility

| Partition | Window | N | BA | UP recall | DOWN recall | Eligible | Reason |
|---|---|---:|---:|---:|---:|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 279 | 49.88% | 48.28% | 51.49% | False | BA_LT_52|YEAR_BA_LT_50 |
| SOBTI_5_ET | ASIA_MORNING_LIT | 272 | 44.01% | 34.48% | 53.54% | False | BA_LT_52|YEAR_BA_LT_50 |
| SOBTI_5_ET | EUROPE_LIT | 295 | 47.88% | 80.49% | 15.27% | False | RECALL_FLOOR|BA_LT_52|YEAR_BA_LT_50 |
| SOBTI_5_ET | NY_LONDON_LIT | 297 | 49.21% | 37.24% | 61.18% | False | BA_LT_52|YEAR_BA_LT_50 |
| SOBTI_5_ET | US_LATE_LIT | 170 | 50.50% | 91.00% | 10.00% | False | RECALL_FLOOR|BA_LT_52|YEAR_BA_LT_50 |
| WGC_2026_NY3 | ASIA | 152 | 49.83% | 66.34% | 33.33% | False | BA_LT_52|YEAR_BA_LT_50 |
| WGC_2026_NY3 | EUROPE | 297 | 46.08% | 79.76% | 12.40% | False | RECALL_FLOOR|BA_LT_52|YEAR_BA_LT_50 |
| WGC_2026_NY3 | US | 264 | 45.28% | 17.09% | 73.47% | False | RECALL_FLOOR|BA_LT_52|YEAR_BA_LT_50 |

## Frozen selected features

| Partition | Window | Features |
|---|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | sess_us_conflict, sess_us_total, sess_us_pm, sess_east_west_conflict, sess_asia, sess_europe, sess_sign_changes, sess_dispersion |
| SOBTI_5_ET | ASIA_MORNING_LIT | sess_europe, sess_asia, sess_dominance, sess_asia_us_interaction, sess_east_west, sess_east_west_conflict, sess_us_am, sess_us_conflict |
| SOBTI_5_ET | EUROPE_LIT | sess_sign_changes, sess_europe, sess_dispersion, sess_east_west_conflict, sess_us_reversal, sess_asia, sess_us_pm, sess_us_conflict |
| SOBTI_5_ET | NY_LONDON_LIT | sess_us_conflict, sess_europe, sess_asia, sess_dispersion, sess_east_west_conflict, sess_us_am, sess_us_pm, sess_dominance |
| SOBTI_5_ET | US_LATE_LIT | sess_asia, sess_europe, sess_us_am, sess_asia_us_interaction, sess_us_pm, sess_dispersion, sess_us_total, sess_dominance |
| WGC_2026_NY3 | ASIA | sess_us_conflict, sess_us_pm, sess_dominance, sess_us_reversal, sess_europe, sess_east_west_conflict, sess_asia_us_interaction, sess_asia |
| WGC_2026_NY3 | EUROPE | sess_europe, sess_sign_changes, sess_dispersion, sess_east_west_conflict, sess_asia, sess_us_conflict, sess_us_am, sess_asia_us_interaction |
| WGC_2026_NY3 | US | sess_asia, sess_europe, sess_us_am, sess_asia_us_interaction, sess_east_west_conflict, sess_dominance, sess_dispersion, sess_us_conflict |

## 2025 transport — only development-eligible selected heads

No selected-SAGE head passed the pre-2025 gate; 2025 remained closed.
