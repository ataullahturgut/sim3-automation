# SESSION OPAL V1 — FINAL AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / WGC EUROPE SPECIALIST RETAINED / VARIABLE-SELECTED CHALLENGER REJECTED

## Identity

SESSION OPAL V1 is a corrected COT/options-positioning reversal specialist layered on fresh SESSION AURORA.

Upstream:
- fresh causal SESSION AURORA;
- canonical pre-target XAU 1h momentum state.

COT:
- governed corrected publication-time authority;
- only reports with `cot_available_at_utc <= session_start_utc`;
- official delayed releases override default timing;
- no old date-only +7 shortcut.

Canonical feature set: 18 variables.

Estimator:
- StandardScaler
- LogisticRegression(C=1.0, class_weight=balanced)
- reversal threshold = 0.70
- minimum matured same-window training rows = 80

Correction:
- only when AURORA follows momentum and OPAL reversal probability >= 0.70;
- otherwise preserve AURORA.

## Baseline development gate

Two canonical OPAL heads passed:

### Sobti Asia Morning
Development:
- N = 81
- AURORA BA = 56.08%
- OPAL BA = 58.73%
- OPAL UP recall = 60.78%
- OPAL DOWN recall = 56.67%
- Brier: 0.2457 -> 0.2387
- overrides = 2
- net rescue = +2

### WGC Europe
Development:
- N = 99
- AURORA BA = 45.24%
- OPAL BA = 47.93%
- OPAL UP recall = 64.91%
- OPAL DOWN recall = 30.95%
- Brier: 0.2744 -> 0.2692
- overrides = 6
- net rescue = +2

All other canonical heads failed closed before 2025.

## Frozen 2025 canonical transport

### Sobti Asia Morning
N = 140

AURORA:
- Accuracy = 56.43%
- BA = 56.50%
- UP recall = 58.21%
- DOWN recall = 54.79%
- Brier = 0.2698

OPAL:
- Accuracy = 55.71%
- BA = 55.76%
- UP recall = 56.72%
- DOWN recall = 54.79%
- Brier = 0.2727
- overrides = 5
- rescued = 2
- broken = 3
- net rescue = -1

Verdict:
- transport deteriorates;
- reject Sobti Asia Morning OPAL.

### WGC Europe
N = 145

AURORA:
- Accuracy = 53.10%
- BA = 51.59%
- UP recall = 66.25%
- DOWN recall = 36.92%
- Brier = 0.26764

Canonical OPAL:
- Accuracy = 53.79%
- BA = 52.64%
- UP recall = 63.75%
- DOWN recall = 41.54%
- Brier = 0.26762
- overrides = 13
- rescued = 7
- broken = 6
- net rescue = +1

Verdict:
- same full 145-row coverage;
- BA improves +1.06 pp;
- DOWN recall improves +4.62 pp;
- Brier improves marginally;
- class-recall floor is satisfied.

Canonical OPAL is retained as a **WGC Europe window-specific specialist challenger**.

It is not promoted as a universal session engine.

## OPAL V1B variable-selection diagnostic

Authority:
- `GOLD_SESSION_OPAL_V1B_VARSEL_PREREG_2026-10-07.md`
- `GOLD_SESSION_OPAL_V1B_VARSEL_RESULT_2026-10-07.md`
- `GOLD_SESSION_OPAL_V1B_VARSEL_FROZEN_FEATURES_2026-10-07.json`

Variable selection was restricted to the original 18 OPAL variables and used development only.

Only WGC Europe passed the nested pre-2025 selected gate.

Frozen WGC Europe selected set:
- d_opt_mm_net
- d_opt_prod_net
- trend_x_opt_mm

2025:
- canonical OPAL BA = 52.64%
- selected OPAL BA = 50.96%
- canonical DOWN recall = 41.54%
- selected DOWN recall = 36.92%
- canonical Brier = 0.2676
- selected Brier = 0.2713
- canonical net rescue = +1
- selected net rescue = -1

Therefore the selected representation is rejected.

## Binding decision

1. SESSION OPAL V1 identity is valid and corrected-PIT clean.
2. Sobti Asia Morning OPAL is rejected after 2025 transport deterioration.
3. **WGC Europe canonical OPAL is retained as a window-specific specialist challenger.**
4. Canonical 18-feature OPAL remains superior to its selected-feature variant.
5. OPAL V1B feature-selection challenger is rejected.
6. OPAL is not a universal primary session model.
7. No 2025 tuning or rescue was performed.
8. 2026 remains unopened.
9. Fresh OPAL output now exists for downstream specialist-combination work.
10. Next downstream dependency, if following the historical specialist stack, is HELIOS; however HELIOS must be rebuilt from fresh session-native inputs rather than historical H3 artifacts.
