# SESSION MODEL-08 — SAGE A1_SESSION / S1.7 — IDENTITY AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / BASELINE IDENTITY ACCEPTED / PRE-2025 FAIL-CLOSED

## Canonical identity

SESSION Model-08 is:

`S17_A1_SESSION`

Inputs:
- mandatory fresh NOVA A1 structural logit: `a1_logit`
- canonical 14-variable SAGE `SESSION_ALL` block

Estimator:
- StandardScaler
- LogisticRegression(L2, C=1.0)
- threshold = 0.50
- same-window causal replay

Correct comparator:
- `S17_A1_DIRECT_MATCHED`
- this is the **direct fresh upstream A1 probability**
- no downstream logistic refit of the comparator

## Corrected implementation authority

Binding authority:
- `GOLD_SESSION_SAGE_V2_STAGE1_CORRECTED_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_SAGE_V2_STAGE1_CORRECTED_PAIRED_2026-10-07.csv`
- `GOLD_SESSION_SAGE_V2_STAGE1_CORRECTED_TRANSPORT_ELIGIBILITY_2026-10-07.csv`

V2 supersedes V1 specifically because V1 implemented the S1.7 comparator incorrectly. V2 uses fresh `p_A1_arcr` directly.

## Clock / source-ready contract

- fresh A1 uses only matured same-window history and source-ready daily metal information;
- SAGE cycle is complete at 16:15 America/New_York;
- require `sage_ready_utc < target_start_utc`;
- equality rejected;
- no target-window information.

## Chronology

- 2022: governed warm-up/training only
- 2023–2024: scored development
- 2025: may open only if paired pre-2025 gate passes
- 2026: unopened

## 2023–2024 combined evidence

| Session | N | S17 BA | Direct A1 BA | Delta BA | UP recall | DOWN recall | S17 Brier | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 191 | 52.21% | 46.05% | +6.16 pp | 53.85% | 50.57% | 0.2688 | FAIL — year sign |
| Sobti Asia Morning | 184 | 53.34% | 45.14% | +8.20 pp | 52.83% | 53.85% | 0.2751 | FAIL — Brier |
| Sobti Europe | 213 | 45.09% | 50.07% | -4.98 pp | 68.91% | 21.28% | 0.2655 | FAIL |
| Sobti NY/London | 215 | 48.48% | 48.54% | -0.06 pp | 37.50% | 59.46% | 0.2706 | FAIL |
| Sobti Late-US | 89 | 50.23% | 54.22% | -3.99 pp | 68.75% | 31.71% | 0.2667 | FAIL |
| WGC Asia | 102 | 48.22% | 38.93% | +9.29 pp | 78.26% | 18.18% | 0.2520 | FAIL — recall floor |
| WGC Europe | 215 | 48.45% | 51.82% | -3.36 pp | 78.23% | 18.68% | 0.2576 | FAIL |
| WGC US | 177 | 50.64% | 43.82% | +6.82 pp | 23.26% | 78.02% | 0.2789 | FAIL — recall/Brier |

## Pre-2025 gate result

No S17 head is eligible.

Reasons:
- Sobti Asia Afternoon: YEAR_SIGN_FAIL
- Sobti Asia Morning: BRIER_GATE
- Sobti Europe: RECALL_FLOOR | BA_BELOW_COMPARATOR | YEAR_SIGN_FAIL
- Sobti NY/London: BA_BELOW_COMPARATOR | BRIER_GATE | YEAR_SIGN_FAIL
- Sobti Late-US: BA_BELOW_COMPARATOR | BRIER_GATE
- WGC Asia: RECALL_FLOOR
- WGC Europe: RECALL_FLOOR | BA_BELOW_COMPARATOR | BRIER_GATE | YEAR_SIGN_FAIL
- WGC US: RECALL_FLOOR | BRIER_GATE

## Binding Model-08 baseline decision

1. S17 A1_SESSION identity is valid.
2. The corrected direct-A1 comparator is mandatory.
3. No canonical S17 head passed the pre-2025 paired gate.
4. Therefore canonical Model-08 2025 remains closed.
5. A model-specific feature-selection challenger may select only among the 14 SAGE variables while keeping `a1_logit` mandatory.
6. Any selected challenger must be compared against direct fresh A1 and pass the same paired gate before 2025 can be opened.
7. 2026 remains unopened.
