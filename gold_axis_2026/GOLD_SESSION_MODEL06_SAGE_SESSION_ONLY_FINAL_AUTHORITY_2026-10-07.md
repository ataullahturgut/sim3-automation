# SESSION MODEL-06 — SAGE SESSION_ONLY — FINAL AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / BASELINE NOT PROMOTED / FEATURE-SELECTED CHALLENGER FAIL-CLOSED

## Canonical baseline

Model-06:
`S15_SESSION_ONLY`

Authority:
- `GOLD_SESSION_MODEL06_SAGE_SESSION_ONLY_IDENTITY_AUTHORITY_2026-10-07.md`
- `GOLD_SESSION_SAGE_V2_STAGE1_CORRECTED_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_SAGE_FROZEN_2025_TRANSPORT_V2_CONTINUOUS_SUMMARY_2026-10-07.json`

Canonical feature block:
14 SAGE phase/decomposition variables, with the cycle source-ready at 16:15 America/New_York and strict `sage_ready_utc < target_start_utc`.

## Baseline pre-2025 result

Only WGC Asia passed the preregistered S1.5 development gate:

- N = 152
- Accuracy = 59.87%
- Balanced Accuracy = 56.21%
- UP recall = 67.33%
- DOWN recall = 45.10%
- Brier = 0.2497

All other S1.5 heads failed closed before 2025.

## Baseline frozen 2025 transport

Only WGC Asia was legitimately opened:

- N = 105
- Accuracy = 49.52%
- Balanced Accuracy = 48.06%
- UP recall = 62.07%
- DOWN recall = 34.04%
- Brier = 0.2619

Therefore canonical SESSION_ONLY did not transport successfully.

## Model-06B feature-selection challenger

Authorities:
- `GOLD_SESSION_MODEL06B_SAGE_SESSION_ONLY_FEATURE_SELECTION_PREREG_2026-10-07.md`
- `GOLD_SESSION_MODEL06B_SAGE_FEATURE_SELECTION_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_MODEL06B_SAGE_FEATURE_SELECTION_ELIGIBILITY_2026-10-07.csv`

Only the canonical 14 SAGE variables were selectable.
No external feature family was added.

### Honest 2023–2024 selected-SAGE gate

| Session | N | BA | UP recall | DOWN recall | Eligibility |
|---|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 279 | 49.88% | 48.28% | 51.49% | FAIL |
| Sobti Asia Morning | 272 | 44.01% | 34.48% | 53.54% | FAIL |
| Sobti Europe | 295 | 47.88% | 80.49% | 15.27% | FAIL |
| Sobti NY/London | 297 | 49.21% | 37.24% | 61.18% | FAIL |
| Sobti Late-US | 170 | 50.50% | 91.00% | 10.00% | FAIL |
| WGC Asia | 152 | 49.83% | 66.34% | 33.33% | FAIL |
| WGC Europe | 297 | 46.08% | 79.76% | 12.40% | FAIL |
| WGC US | 264 | 45.28% | 17.09% | 73.47% | FAIL |

Every selected-SAGE head fails the frozen development gate.

## 2025 selected-SAGE status

**CLOSED / NOT OPENED.**

Because no selected-SAGE head passed the pre-2025 eligibility gate, no selected-SAGE 2025 outcome was produced.

This is intentional fail-closed governance, not missing data.

## Binding Model-06 decision

1. Canonical SAGE SESSION_ONLY identity is accepted.
2. Canonical SAGE SESSION_ONLY is not promoted after its eligible WGC Asia head fails 2025 transport.
3. Feature selection does not rescue SESSION_ONLY.
4. No selected-SAGE head is eligible for 2025; 2025 remains closed for all Model-06B variants.
5. No selected feature subset is carried forward as a promoted direction engine.
6. 2026 remains unopened.
7. The next Stage-1 lineage item is SAGE PATH_SESSION / S1.6.
