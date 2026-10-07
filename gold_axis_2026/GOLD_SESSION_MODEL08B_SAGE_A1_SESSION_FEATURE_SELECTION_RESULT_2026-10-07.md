# SESSION MODEL-08B — SAGE A1_SESSION FEATURE-SELECTION RESULT

> **2026-10-07 governance amendment:** selected 07B/08B/09B development replay used a final full-development feature subset backwards. Development role/gate inference involving those selected rows is superseded by [GOLD_SESSION_NESTED_ROLE_REPAIR_AUTHORITY_2026-10-07.md](GOLD_SESSION_NESTED_ROLE_REPAIR_AUTHORITY_2026-10-07.md). Other identities are unaffected. Original frozen 2025 numerical forecasts remain archived transport evidence, but prior eligibility and repaired-policy identity equivalence are not endorsed. Historical text below is preserved.

**Status:** complete.

## Frozen SAGE variables

| Partition | Window | SAGE variables |
|---|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | sess_asia, sess_us_pm, sess_east_west_conflict, sess_dispersion, sess_europe, sess_asia_us_interaction |
| SOBTI_5_ET | ASIA_MORNING_LIT | sess_europe, sess_asia, sess_asia_us_interaction, sess_us_conflict, sess_dominance, sess_sign_changes |
| SOBTI_5_ET | EUROPE_LIT | sess_asia, sess_east_west_conflict, sess_europe, sess_dominance, sess_sign_changes, sess_asia_us_interaction |
| SOBTI_5_ET | NY_LONDON_LIT | sess_asia, sess_europe, sess_us_conflict, sess_asia_us_interaction, sess_dispersion, sess_sign_changes |
| SOBTI_5_ET | US_LATE_LIT | sess_europe, sess_asia, sess_east_west_conflict, sess_dominance, sess_us_conflict, sess_sign_changes |
| WGC_2026_NY3 | ASIA | sess_asia, sess_europe, sess_dominance, sess_dispersion, sess_us_am, sess_us_conflict |
| WGC_2026_NY3 | EUROPE | sess_asia, sess_sign_changes, sess_europe, sess_us_reversal, sess_dominance, sess_west_total |
| WGC_2026_NY3 | US | sess_asia, sess_europe, sess_east_west_conflict, sess_dispersion, sess_sign_changes, sess_asia_us_interaction |

## Pre-2025 eligibility

| Partition | Window | N | Candidate BA | Direct A1 BA | UP | DOWN | Eligible | Reason |
|---|---|---:|---:|---:|---:|---:|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 383 | 52.09% | 50.32% | 45.13% | 59.04% | False | YEAR_SIGN_FAIL |
| SOBTI_5_ET | ASIA_MORNING_LIT | 383 | 49.17% | 50.42% | 44.93% | 53.41% | False | BA_BELOW_COMPARATOR|YEAR_SIGN_FAIL |
| SOBTI_5_ET | EUROPE_LIT | 418 | 55.95% | 50.61% | 65.78% | 46.11% | True | PASS |
| SOBTI_5_ET | NY_LONDON_LIT | 414 | 46.43% | 49.92% | 48.26% | 44.60% | False | BA_BELOW_COMPARATOR|YEAR_SIGN_FAIL |
| SOBTI_5_ET | US_LATE_LIT | 259 | 51.06% | 53.08% | 90.00% | 12.12% | False | RECALL_FLOOR|BA_BELOW_COMPARATOR|YEAR_SIGN_FAIL |
| WGC_2026_NY3 | ASIA | 416 | 51.22% | 50.13% | 69.10% | 33.33% | True | PASS |
| WGC_2026_NY3 | EUROPE | 417 | 54.86% | 51.58% | 70.26% | 39.46% | True | PASS |
| WGC_2026_NY3 | US | 371 | 52.18% | 47.85% | 39.44% | 64.92% | True | PASS |

## 2025 transport

| Partition | Window | N | Candidate BA | Direct A1 BA | Delta BA | Candidate Brier | Direct A1 Brier |
|---|---|---:|---:|---:|---:|---:|---:|
| SOBTI_5_ET | EUROPE_LIT | 247 | 48.99% | 45.37% | +3.63 pp | 0.2476 | 0.2619 |
| WGC_2026_NY3 | ASIA | 253 | 46.95% | 49.73% | -2.78 pp | 0.2496 | 0.2499 |
| WGC_2026_NY3 | EUROPE | 247 | 47.72% | 50.63% | -2.91 pp | 0.2565 | 0.2617 |
| WGC_2026_NY3 | US | 239 | 45.60% | 44.82% | +0.78 pp | 0.2602 | 0.2620 |
