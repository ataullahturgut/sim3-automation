# SESSION MODEL-07 — SAGE PATH_SESSION / S1.6 — FINAL AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / CANONICAL BASELINE NOT PROMOTED / FEATURE-SELECTED CHALLENGER LIMITED

## Canonical baseline

Authority:
- `GOLD_SESSION_MODEL07_SAGE_PATH_SESSION_IDENTITY_AUTHORITY_2026-10-07.md`

Canonical identity:
- `S16_PATH_SESSION`
- canonical hourly PATH block + canonical 14 SAGE SESSION_ALL variables
- StandardScaler + LogisticRegression(L2, C=1.0)
- threshold 0.50
- strict SAGE readiness `sage_ready_utc < target_start_utc`

Matched canonical comparator:
- `S16_PATH_GLOBAL_MATCHED`

## Baseline frozen 2025 verdict

Only preregistered eligible heads were opened.

### Sobti NY/London
- N = 144
- PATH_SESSION BA = 45.94%
- matched PATH_GLOBAL BA = 42.68%
- delta BA = +3.26 pp
- PATH_SESSION Brier = 0.2870
- matched PATH_GLOBAL Brier = 0.2740

Relative improvement remains, but absolute directional skill is below 50%.

### WGC US
- N = 140
- PATH_SESSION BA = 46.69%
- matched PATH_GLOBAL BA = 49.38%
- delta BA = -2.68 pp
- PATH_SESSION Brier = 0.2890
- matched PATH_GLOBAL Brier = 0.2825

No 2025 promotion.

## Model-07B feature-selection challenger

Authorities:
- `GOLD_SESSION_MODEL07B_SAGE_PATH_SESSION_FEATURE_SELECTION_PREREG_2026-10-07.md`
- `GOLD_SESSION_MODEL07B_SAGE_PATH_SESSION_FEATURE_SELECTION_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_MODEL07B_SAGE_PATH_SESSION_FEATURE_SELECTION_ELIGIBILITY_2026-10-07.csv`

Selection universe:
- canonical hourly PATH variables
- canonical 14 SAGE variables

Identity constraint:
- at least one PATH variable
- at least one SAGE variable

Fair comparator:
- `SELECTED_PATH_MATCHED`
- exact same selected PATH subset
- no SAGE variables

Thus selected PATH_SESSION is credited only for incremental SAGE value beyond its own selected PATH subset.

## Pre-2025 selected eligibility

Two selected heads passed:

### Sobti NY/London
- N = 297
- selected PATH_SESSION BA = 53.57%
- selected PATH comparator BA = 50.41%
- UP recall = 55.17%
- DOWN recall = 51.97%
- PASS

### WGC Asia
- N = 152
- selected PATH_SESSION BA = 55.72%
- selected PATH comparator BA = 51.37%
- UP recall = 66.34%
- DOWN recall = 45.10%
- candidate Brier = 0.2410
- comparator Brier = 0.2432
- PASS

All other selected heads failed the frozen paired gate before 2025.

## Frozen 2025 selected transport

### Sobti NY/London
- N = 144
- selected PATH_SESSION Accuracy = 47.22%
- BA = 47.62%
- UP recall = 44.44%
- DOWN recall = 50.79%
- Brier = 0.2731
- selected PATH comparator BA = 45.15%
- delta BA = +2.47 pp

Verdict: relative improvement but insufficient absolute skill; not promoted.

### WGC Asia
- N = 105
- selected PATH_SESSION Accuracy = 53.33%
- BA = 52.11%
- UP recall = 63.79%
- DOWN recall = 40.43%
- Brier = 0.2572
- selected PATH comparator BA = 50.09%
- delta BA = +2.02 pp

Verdict: clean modest SAGE increment over its matched sparse PATH comparator.

## Cross-model guardrail

The existing Model-04B selected PATH_GLOBAL WGC Asia challenger on the same N=105 transport population achieved approximately:
- BA = 59.21%
- Brier = 0.2461
- UP recall = 75.86%
- DOWN recall = 42.55%

Therefore selected Model-07B WGC Asia is **not the strongest WGC Asia direction head** despite passing its own paired gate.

It is retained only as:
- a secondary window-specific challenger;
- potential error-diversity input for a later router/consensus study.

It is not promoted as a replacement for the stronger selected PATH_GLOBAL WGC Asia head.

## Binding Model-07 decision

1. Canonical S16 PATH_SESSION is valid but not promoted after 2025 transport.
2. Feature selection does not produce a broadly superior PATH_SESSION engine.
3. Sobti NY/London selected PATH_SESSION is rejected for primary use because 2025 BA remains below 50%.
4. WGC Asia selected PATH_SESSION is retained as a secondary challenger only.
5. WGC US selected PATH_SESSION failed the pre-2025 selected gate and remains closed.
6. No 2025 tuning or rescue was performed.
7. 2026 remains unopened.
8. Next primary lineage item: SESSION Model-08 — SAGE A1_SESSION / S1.7.
