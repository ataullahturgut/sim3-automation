# SESSION MODEL-09 — SAGE A1_PATH_SESSION / S1.8 — IDENTITY AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / BASELINE IDENTITY ACCEPTED / PRE-2025 FAIL-CLOSED

## Canonical identity

SESSION Model-09 is:

`S18_A1_PATH_SESSION`

Inputs:
- mandatory fresh NOVA A1 structural logit: `a1_logit`
- canonical hourly XAU PATH/VOL/SHAPE block
- canonical 14-variable SAGE SESSION_ALL block

Estimator:
- StandardScaler
- LogisticRegression(L2, C=1.0)
- threshold = 0.50
- same-window causal replay

Matched comparator:
- `S18_A1_PATH_MATCHED`
- same fresh `a1_logit`
- same hourly PATH block
- no SAGE variables

Thus S1.8 measures the incremental contribution of SAGE after A1 + PATH are already present.

## Binding authority

- `GOLD_SESSION_SAGE_V2_STAGE1_CORRECTED_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_SAGE_V2_STAGE1_CORRECTED_PAIRED_2026-10-07.csv`
- `GOLD_SESSION_SAGE_V2_STAGE1_CORRECTED_TRANSPORT_ELIGIBILITY_2026-10-07.csv`

## Clock / chronology

- 2022: governed warm-up/training only
- 2023–2024: scored development
- 2025: may open only if paired pre-2025 gate passes
- 2026: unopened

Source-ready rules:
- fresh A1 uses only matured same-window history;
- hourly PATH uses completed pre-target information;
- SAGE requires `sage_ready_utc < target_start_utc`;
- no target-window data.

## 2023–2024 combined evidence

| Session | N | S18 BA | Matched A1+PATH BA | Delta BA | UP recall | DOWN recall | S18 Brier | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 191 | 47.99% | 50.67% | -2.69 pp | 50.00% | 45.98% | 0.3141 | FAIL |
| Sobti Asia Morning | 184 | 49.36% | 49.79% | -0.44 pp | 50.00% | 48.72% | 0.3048 | FAIL |
| Sobti Europe | 213 | 47.86% | 48.17% | -0.31 pp | 68.07% | 27.66% | 0.3000 | FAIL |
| Sobti NY/London | 215 | 49.50% | 53.26% | -3.76 pp | 41.35% | 57.66% | 0.2947 | FAIL |
| Sobti Late-US | 89 | 48.50% | 50.05% | -1.55 pp | 60.42% | 36.59% | 0.3190 | FAIL |
| WGC Asia | 102 | 48.88% | 47.36% | +1.52 pp | 82.61% | 15.15% | 0.2787 | FAIL |
| WGC Europe | 215 | 50.90% | 54.31% | -3.41 pp | 67.74% | 34.07% | 0.2779 | FAIL |
| WGC US | 177 | 50.89% | 50.28% | +0.61 pp | 32.56% | 69.23% | 0.3041 | FAIL |

## Pre-2025 gate reasons

- Sobti Asia Afternoon: BA_BELOW_COMPARATOR | BRIER_GATE | YEAR_SIGN_FAIL
- Sobti Asia Morning: BA_BELOW_COMPARATOR | BRIER_GATE | YEAR_SIGN_FAIL
- Sobti Europe: RECALL_FLOOR | BA_BELOW_COMPARATOR | BRIER_GATE | YEAR_SIGN_FAIL
- Sobti NY/London: BA_BELOW_COMPARATOR | BRIER_GATE | YEAR_SIGN_FAIL
- Sobti Late-US: BA_BELOW_COMPARATOR | BRIER_GATE
- WGC Asia: RECALL_FLOOR | BRIER_GATE
- WGC Europe: BA_BELOW_COMPARATOR | YEAR_SIGN_FAIL
- WGC US: BRIER_GATE

No canonical S18 head is eligible.

## Binding Model-09 baseline decision

1. S18 A1_PATH_SESSION identity is valid.
2. Comparator identity is matched A1+PATH without SAGE.
3. No canonical S18 head passed the pre-2025 paired gate.
4. Therefore canonical Model-09 2025 remains closed.
5. A feature-selection challenger may keep A1 mandatory and select within PATH + SAGE only.
6. Any selected challenger must preserve at least one PATH and one SAGE variable.
7. Its comparator must use the exact same selected PATH subset plus A1, but no SAGE.
8. 2026 remains unopened.
