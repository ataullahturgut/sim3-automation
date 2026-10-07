# SESSION MODEL-06 — SAGE SESSION_ONLY — IDENTITY AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / BASELINE IDENTITY ACCEPTED

## Canonical identity

SESSION Model-06 is SAGE Stage-1 S1.5:

`S15_SESSION_ONLY`

Estimator:
- StandardScaler
- LogisticRegression(L2, C=1.0)
- threshold = 0.50
- block size = 5
- minimum matured same-window training rows = 120

## Binding SAGE clock

The SAGE decomposition is New-York-local and fixed:

- Asia: previous NY date 18:00 -> current NY date 03:00
- Europe: 03:00 -> 08:00
- US AM: 08:00 -> 12:00
- US PM: 12:00 -> 16:00

Boundary value is the exact XAU/USD 15-minute bar **OPEN** at the boundary.
Nearest-bar substitution is prohibited.

A complete SAGE cycle is source-ready only at:

`16:15 America/New_York`

For target start T, use only the latest cycle satisfying:

`sage_ready_utc < target_start_utc`

Equality is rejected.

## Canonical SESSION_ALL feature block

Primary phase returns:
- sess_asia
- sess_europe
- sess_us_am
- sess_us_pm

Derived:
- sess_us_total
- sess_west_total
- sess_east_west
- sess_us_reversal
- sess_dispersion
- sess_sign_changes
- sess_dominance
- sess_asia_us_interaction
- sess_east_west_conflict
- sess_us_conflict

Total: 14 features.

## Authority lineage

Preregistration:
- `GOLD_SESSION_SAGE_V1_PREREG_2026-10-07.md`

Binding corrected development authority:
- `GOLD_SESSION_SAGE_V2_STAGE1_CORRECTED_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_SAGE_V2_STAGE1_CORRECTED_RESULT_2026-10-07.md`

V2 supersedes V1 for:
- the S1.5 standalone eligibility gate implementation;
- the S1.7 direct-A1 comparator implementation.

No preregistered clock, feature, threshold or model rule was changed by those corrections.

Chronology:
- 2022 warm-up/training only
- 2023–2024 scored development
- 2025 frozen transport only for preregistered eligible heads
- 2026 unopened

## Development result

| Session | N | Accuracy | BA | UP recall | DOWN recall | Brier | Pre-2025 gate |
|---|---:|---:|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 279 | 49.82% | 50.03% | 44.83% | 55.22% | 0.2573 | FAIL |
| Sobti Asia Morning | 272 | 44.49% | 44.95% | 37.93% | 51.97% | 0.2674 | FAIL |
| Sobti Europe | 295 | 51.53% | 48.11% | 78.66% | 17.56% | 0.2592 | FAIL |
| Sobti NY/London | 297 | 51.85% | 51.67% | 44.14% | 59.21% | 0.2557 | FAIL |
| Sobti Late-US | 170 | 48.82% | 44.29% | 70.00% | 18.57% | 0.2665 | FAIL |
| WGC Asia | 152 | **59.87%** | **56.21%** | **67.33%** | **45.10%** | **0.2497** | **PASS** |
| WGC Europe | 297 | 50.17% | 46.23% | 76.19% | 16.28% | 0.2543 | FAIL |
| WGC US | 264 | 47.73% | 45.65% | 27.35% | 63.95% | 0.2565 | FAIL |

The preregistered SESSION_ONLY gate requires:
- combined N >= 80;
- both class recalls >= 30%;
- combined BA >= 52%;
- each year with N >= 40 must have BA >= 50%.

Only WGC Asia passed before 2025 was opened.

## Frozen 2025 transport

Binding continuous-block authority:
- `GOLD_SESSION_SAGE_FROZEN_2025_TRANSPORT_V2_CONTINUOUS_SUMMARY_2026-10-07.json`

Only preregistered eligible WGC Asia was opened:

- N = 105
- Accuracy = 49.52%
- Balanced Accuracy = 48.06%
- UP recall = 62.07%
- DOWN recall = 34.04%
- Brier = 0.2619

Thus S15 SESSION_ONLY did **not** transport successfully to 2025.

## Binding Model-06 baseline decision

1. Model identity is valid and accepted.
2. SAGE V2 corrected is the development authority; V1 gate output is superseded where documented.
3. S15 SESSION_ONLY is not promoted as a 2025 session engine.
4. Only WGC Asia was legitimately opened in 2025 under the frozen pre-2025 gate.
5. Rejected 2023–2024 heads remain closed in 2025 for the baseline.
6. A model-specific feature-selection challenger may now be tested using only the 14 canonical SESSION_ALL variables.
7. Any selected representation must pass the same preregistered development gate **before** its corresponding 2025 head may be opened.
8. 2026 remains unopened.
