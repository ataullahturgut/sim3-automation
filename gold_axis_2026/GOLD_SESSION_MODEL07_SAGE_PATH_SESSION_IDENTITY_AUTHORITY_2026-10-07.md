# SESSION MODEL-07 — SAGE PATH_SESSION / S1.6 — IDENTITY AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / BASELINE IDENTITY ACCEPTED

## Canonical identity

SESSION Model-07 is SAGE Stage-1 S1.6:

`S16_PATH_SESSION`

Estimator:
- StandardScaler
- LogisticRegression(L2, C=1.0)
- threshold = 0.50
- block size = 5
- minimum matured same-window training rows inherited from S1.5-6

Inputs:
- canonical clock-safe XAU 1h PATH/VOL/SHAPE block from `res1h.feature_names("g1h")`;
- canonical 14-variable SAGE `SESSION_ALL` block.

Exact comparator:
`S16_PATH_GLOBAL_MATCHED`

The comparator uses the same rows and same hourly PATH block but excludes SAGE variables.

## Clock / source-ready contract

SAGE clock:
- Asia: previous NY date 18:00 -> current NY date 03:00
- Europe: 03:00 -> 08:00
- US AM: 08:00 -> 12:00
- US PM: 12:00 -> 16:00
- complete SAGE cycle ready at 16:15 America/New_York
- required: `sage_ready_utc < target_start_utc`
- equality rejected.

Hourly PATH:
- derived from governed XAU intraday source through the canonical resolution-matched helper;
- only completed pre-target hourly state is used.

No target-window information, nearest-bar substitution, archived H3 prediction, or downstream model output is consumed.

## Chronology

- 2022: governed warm-up/training only
- 2023–2024: scored development
- 2025: opened only for preregistered eligible S1.6 heads
- 2026: unopened

Binding development authority:
- `GOLD_SESSION_SAGE_V2_STAGE1_CORRECTED_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_SAGE_V2_STAGE1_CORRECTED_PAIRED_2026-10-07.csv`

Binding frozen transport:
- `GOLD_SESSION_SAGE_FROZEN_2025_TRANSPORT_V2_CONTINUOUS_SUMMARY_2026-10-07.json`

## Pre-2025 S1.6 gate

Two PATH_SESSION heads passed the preregistered development gate.

### Sobti NY/London

2023–2024:
- N = 297
- PATH_SESSION BA = 52.21%
- matched PATH_GLOBAL BA = 48.25%
- delta BA = +3.96 pp
- PATH_SESSION UP recall = 53.10%
- PATH_SESSION DOWN recall = 51.32%
- PATH_SESSION Brier = 0.2773
- matched PATH_GLOBAL Brier = 0.2677

Year detail:
- 2023 PATH_SESSION BA = 50.25%
- 2024 PATH_SESSION BA = 53.90%

Pre-2025 verdict: PASS.

### WGC US

2023–2024:
- N = 264
- PATH_SESSION BA = 47.46%
- matched PATH_GLOBAL BA = 45.75%
- delta BA = +1.71 pp
- PATH_SESSION UP recall = 38.46%
- PATH_SESSION DOWN recall = 56.46%
- PATH_SESSION Brier = 0.2794
- matched PATH_GLOBAL Brier = 0.2708

Year detail:
- 2023 delta BA vs PATH_GLOBAL = +2.75 pp
- 2024 delta BA vs PATH_GLOBAL = +2.21 pp

Pre-2025 verdict: PASS under the preregistered paired gate.

All other S1.6 heads failed closed before 2025.

## Frozen 2025 transport

The original 5-row replay phase is preserved continuously through 2023 -> 2024 -> 2025.

### Sobti NY/London

N = 144

PATH_SESSION:
- Accuracy = 45.14%
- Balanced Accuracy = 45.94%
- UP recall = 39.51%
- DOWN recall = 52.38%
- Brier = 0.2870

Matched PATH_GLOBAL:
- Balanced Accuracy = 42.68%
- Brier = 0.2740

2025 delta BA remains +3.26 pp versus matched PATH_GLOBAL, but absolute BA is below 50% and probability quality is worse.

### WGC US

N = 140

PATH_SESSION:
- Accuracy = 44.29%
- Balanced Accuracy = 46.69%
- UP recall = 33.73%
- DOWN recall = 59.65%
- Brier = 0.2890

Matched PATH_GLOBAL:
- Balanced Accuracy = 49.38%
- Brier = 0.2825

2025 delta BA = -2.68 pp.

## Binding Model-07 identity decision

1. `S16_PATH_SESSION` identity is accepted.
2. No duplicate baseline rerun is required.
3. Only Sobti NY/London and WGC US were legitimately opened in 2025.
4. Neither transports as a strong 2025 direction engine.
5. Sobti NY/London preserves relative BA improvement versus its matched PATH_GLOBAL comparator but remains below useful absolute directional skill.
6. WGC US loses both relative and absolute directional quality in 2025.
7. Model-specific feature selection may be tested only inside the canonical PATH + SAGE universe and must use development-only selection.
8. 2026 remains unopened.
