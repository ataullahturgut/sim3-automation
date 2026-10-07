# SESSION MODEL-05 — STRUCTURAL_IRIS / A1_PLUS_PATH — FINAL AUTHORITY

**Date:** 2026-10-07  
**Status:** CANONICAL BASELINE ACCEPTED / FEATURE-SELECTED CHALLENGER REJECTED

## Canonical baseline

Authority:
- `GOLD_SESSION_MODEL05_STRUCTURAL_IRIS_IDENTITY_AUTHORITY_2026-10-07.md`

Canonical model:
- `S14_A1_PLUS_1H_FULL`
- mandatory fresh `a1_logit`
- full canonical 1h PATH/VOL/SHAPE block
- StandardScaler + LogisticRegression(L2, C=1.0)
- threshold 0.50

## Feature-selected challenger

Authority:
- `GOLD_SESSION_MODEL05B_STRUCTURAL_IRIS_1H_FEATURE_SELECTION_PREREG_2026-10-07.md`
- `GOLD_SESSION_MODEL05B_STRUCTURAL_IRIS_1H_FEATURE_SELECTION_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_MODEL05B_STRUCTURAL_IRIS_1H_FEATURE_SELECTION_2025_METRICS_2026-10-07.csv`

A1 structural signal was mandatory in every challenger fit. Only the canonical 1h PATH block was selectable. No 15m, cross-metal, macro, GVZ, COT, or downstream model feature was added.

## 2025 exact common-row comparison

| Session | Canonical BA | Selected BA | Delta BA | Canonical Brier | Selected Brier | Selected UP recall | Selected DOWN recall | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 48.92% | 43.81% | -5.12 pp | 0.2777 | 0.2643 | 45.59% | 42.03% | reject |
| Sobti Asia Morning | **60.86%** | 57.49% | -3.36 pp | 0.2557 | 0.2555 | 65.67% | 49.32% | reject; canonical remains stronger |
| Sobti Europe | 45.71% | 44.63% | -1.09 pp | 0.2631 | 0.2572 | 84.34% | 4.92% | reject; class collapse |
| Sobti NY/London | 51.15% | 50.53% | -0.62 pp | 0.2726 | 0.2714 | 40.74% | 60.32% | reject |
| Sobti Late-US | 53.30% | 51.27% | -2.03 pp | 0.2478 | 0.2329 | 92.54% | 10.00% | reject; severe UP bias |
| WGC Asia | 51.80% | 47.04% | -4.76 pp | 0.2792 | 0.2664 | 81.03% | 13.04% | reject |
| WGC Europe | 49.90% | 51.06% | +1.15 pp | 0.2686 | 0.2578 | 77.50% | 24.62% | reject; 30% recall floor fails |
| WGC US | 44.83% | 42.09% | -2.74 pp | 0.2998 | 0.2933 | 19.28% | 64.91% | reject |

## Binding decision

1. `S14_A1_PLUS_1H_FULL` remains the canonical SESSION Model-05.
2. The feature-selected 1h PATH representation does **not** replace the canonical model in any session.
3. Even WGC Europe, where BA improves by 1.15pp, is rejected because DOWN recall falls to 24.62%, below the binding 30% minimum-class-recall floor.
4. Sobti Asia Morning remains the strongest clean Model-05 transport head at 60.86% BA with 64.18% UP recall and 57.53% DOWN recall.
5. Feature reduction improves probability calibration in several windows but systematically weakens directional robustness; calibration-only gains are insufficient for promotion.
6. No 2025 tuning occurred; subsets were frozen from development only.
7. 2026 remains unopened.
8. Next primary model: SESSION Model-06 SAGE SESSION_ONLY.
