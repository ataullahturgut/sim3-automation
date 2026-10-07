# SESSION MODEL-08 — SAGE A1_SESSION / S1.7 — FINAL AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / CANONICAL FAIL-CLOSED / FEATURE-SELECTED CHALLENGER NOT PROMOTED

## Canonical baseline

Authority:
- `GOLD_SESSION_MODEL08_SAGE_A1_SESSION_IDENTITY_AUTHORITY_2026-10-07.md`

Canonical identity:
- `S17_A1_SESSION`
- mandatory fresh `a1_logit`
- full 14-variable SAGE SESSION_ALL block
- StandardScaler + LogisticRegression(L2, C=1.0)
- threshold 0.50

Correct comparator:
- direct fresh `p_A1_arcr`
- no downstream comparator refit

Canonical pre-2025 result:
- no session passed the corrected paired gate
- canonical 2025 remained closed.

## Model-08B feature-selection challenger

Authorities:
- `GOLD_SESSION_MODEL08B_SAGE_A1_SESSION_FEATURE_SELECTION_PREREG_2026-10-07.md`
- `GOLD_SESSION_MODEL08B_SAGE_A1_SESSION_FEATURE_SELECTION_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_MODEL08B_SAGE_A1_SESSION_FEATURE_SELECTION_ELIGIBILITY_2026-10-07.csv`

Model-08B keeps `a1_logit` mandatory and selects only among the 14 canonical SAGE variables.

### Pre-2025 eligible selected heads

Four heads passed:
- Sobti Europe: BA 55.95% vs direct A1 50.61%, UP 65.78%, DOWN 46.11%
- WGC Asia: BA 51.22% vs direct A1 50.13%, UP 69.10%, DOWN 33.33%
- WGC Europe: BA 54.86% vs direct A1 51.58%, UP 70.26%, DOWN 39.46%
- WGC US: BA 52.18% vs direct A1 47.85%, UP 39.44%, DOWN 64.92%

All other selected heads failed closed before 2025.

## Frozen 2025 selected transport

### Sobti Europe
- N = 247
- selected BA = 48.99%
- direct A1 BA = 45.37%
- delta BA = +3.63 pp
- selected UP recall = 72.03%
- selected DOWN recall = 25.96%
- selected Brier = 0.2476
- direct A1 Brier = 0.2619

Verdict: not promoted; absolute BA < 50% and DOWN recall < 30%.

### WGC Asia
- N = 253
- selected BA = 46.95%
- direct A1 BA = 49.73%
- selected UP recall = 83.10%
- selected DOWN recall = 10.81%
- Brier = 0.2496

Verdict: reject.

### WGC Europe
- N = 247
- selected BA = 47.72%
- direct A1 BA = 50.63%
- selected UP recall = 69.72%
- selected DOWN recall = 25.71%
- Brier = 0.2565

Verdict: reject.

### WGC US
- N = 239
- selected BA = 45.60%
- direct A1 BA = 44.82%
- selected UP recall = 48.89%
- selected DOWN recall = 42.31%
- Brier = 0.2602

Verdict: class balance is acceptable but absolute directional skill is too weak; reject.

## Binding Model-08 decision

1. Canonical S17 A1_SESSION remains fail-closed.
2. Feature selection creates development-eligible heads but none transports strongly in 2025.
3. No selected A1_SESSION head is promoted.
4. No Model-08 representation is carried forward as a primary direction engine.
5. Selected heads may remain only as negative/diagnostic evidence.
6. No 2025 retuning or rescue was performed.
7. 2026 remains unopened.
8. Next primary lineage item: SESSION Model-09 — SAGE A1_PATH_SESSION / S1.8.
