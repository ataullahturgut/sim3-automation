# SESSION MODEL-09 — SAGE A1_PATH_SESSION / S1.8 — FINAL AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / CANONICAL FAIL-CLOSED / SELECTED SOBTI NY-LONDON CHALLENGER RETAINED

## Canonical baseline

Authority:
- `GOLD_SESSION_MODEL09_SAGE_A1_PATH_SESSION_IDENTITY_AUTHORITY_2026-10-07.md`

Canonical identity:
- `S18_A1_PATH_SESSION`
- mandatory fresh `a1_logit`
- canonical hourly PATH block
- canonical 14-variable SAGE block
- StandardScaler + LogisticRegression(L2, C=1.0)
- threshold 0.50

Matched comparator:
- `S18_A1_PATH_MATCHED`
- same fresh A1 + same PATH, no SAGE.

No canonical S18 head passed the pre-2025 paired gate; canonical 2025 remained closed.

## Model-09B selected challenger

Authorities:
- `GOLD_SESSION_MODEL09B_SAGE_A1_PATH_SESSION_FEATURE_SELECTION_PREREG_2026-10-07.md`
- `GOLD_SESSION_MODEL09B_SAGE_A1_PATH_SESSION_FEATURE_SELECTION_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_MODEL09B_SAGE_A1_PATH_SESSION_FEATURE_SELECTION_ELIGIBILITY_2026-10-07.csv`
- `GOLD_SESSION_MODEL09B_SAGE_A1_PATH_SESSION_FEATURE_SELECTION_2025_PAIRED_2026-10-07.csv`

Identity:
- fresh A1 is mandatory;
- at least one PATH and one SAGE variable are retained;
- comparator uses the exact same selected PATH subset + A1 but no SAGE.

## Pre-2025 selected eligibility

Three heads passed.

### Sobti NY/London
- N = 215
- selected A1_PATH_SESSION BA = 56.41%
- matched selected A1+PATH BA = 53.50%
- UP recall = 46.15%
- DOWN recall = 66.67%
- Brier = 0.2581
- PASS

Frozen selected representation:
- PATH: g1h_ret_3h, g1h_ret_1h, g1h_ret_6h, g1h_jump_concentration_24, g1h_down_semivol_24
- SAGE: sess_us_conflict, sess_asia, sess_asia_us_interaction
- plus mandatory a1_logit

### Sobti Late-US
- N = 89
- BA = 54.40%
- matched comparator BA = 50.38%
- UP recall = 77.08%
- DOWN recall = 31.71%
- PASS

### WGC US
- N = 177
- BA = 59.94%
- matched comparator BA = 55.13%
- UP recall = 41.86%
- DOWN recall = 78.02%
- Brier = 0.2493
- PASS

All other selected heads failed the frozen pre-2025 gate.

## Frozen 2025 selected transport

### Sobti NY/London
- N = 144
- Accuracy = 51.39%
- Balanced Accuracy = **52.73%**
- UP recall = **41.98%**
- DOWN recall = **63.49%**
- Brier = 0.2681
- matched selected A1+PATH BA = 45.86%
- matched comparator Brier = 0.2655
- delta BA = **+6.88 pp**
- delta Brier = +0.0026

Verdict:
- preserves acceptable two-class recall;
- provides a large incremental BA gain over its exact matched A1+PATH comparator;
- absolute BA remains modest rather than dominant;
- probability calibration is slightly worse.

**Retain as a window-specific Sobti NY/London challenger for later expert/router/consensus analysis.**

### Sobti Late-US
- N = 107
- BA = 44.79%
- UP recall = 82.09%
- DOWN recall = 7.50%
- matched comparator BA = 44.79%
- Brier = 0.2613

Verdict: reject; severe one-sided collapse.

### WGC US
- N = 140
- BA = 45.38%
- UP recall = 24.10%
- DOWN recall = 66.67%
- matched comparator BA = 40.89%
- Brier = 0.2928

Verdict: reject; absolute skill weak and UP recall below the 30% floor.

## Binding Model-09 decision

1. Canonical S18 A1_PATH_SESSION remains fail-closed.
2. Feature selection rescues one useful window-specific candidate: **Sobti NY/London selected A1_PATH_SESSION**.
3. The Sobti NY/London challenger is retained, but not declared a universal primary model.
4. Sobti Late-US and WGC US selected variants are rejected after frozen 2025 transport.
5. No other selected session opened 2025.
6. No 2025 feature reselection, threshold tuning, C tuning or eligibility rescue occurred.
7. 2026 remains unopened.
8. The next lineage item must be taken from the binding post-Stage-1 execution order in the project manifest; do not infer it from historical H3 naming.
