# SESSION MODEL-05 — STRUCTURAL_IRIS / A1_PLUS_PATH — FINAL AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / CANONICAL BASELINE RETAINED / 1H FEATURE-SELECTION CHALLENGER REJECTED

## Canonical baseline

Model-05 canonical identity:

`S14_A1_PLUS_1H_FULL`

Inputs:
- mandatory fresh NOVA A1 structural logit;
- full canonical 1h XAU PATH/VOL/SHAPE block.

Estimator:
- StandardScaler
- LogisticRegression(L2, C=1.0)
- threshold = 0.50

Chronology:
- 2022 upstream warm-up
- 2023–2024 development
- 2025 one-time frozen transport
- 2026 unopened

Identity authority:
- `GOLD_SESSION_MODEL05_STRUCTURAL_IRIS_IDENTITY_AUTHORITY_2026-10-07.md`
- `GOLD_SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP22_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_S14_FROZEN_2025_TRANSPORT_SUMMARY_2026-10-07.json`

## Model-05B feature analysis

Authorities:
- `GOLD_SESSION_MODEL05B_STRUCTURAL_IRIS_1H_FEATURE_SELECTION_PREREG_2026-10-07.md`
- `GOLD_SESSION_MODEL05B_STRUCTURAL_IRIS_1H_FEATURE_SELECTION_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_MODEL05B_STRUCTURAL_IRIS_1H_FEATURE_SELECTION_2025_METRICS_2026-10-07.csv`
- `GOLD_SESSION_MODEL05B_STRUCTURAL_IRIS_1H_FEATURE_SELECTION_FROZEN_FEATURES_2026-10-07.json`

A1 structural logit is mandatory in every challenger model. Only the canonical 1h PATH variables may be selected.

### Identity correction during audit

The first Model-05B run used a 1h-only ready-row population. This did not preserve the canonical S1.4 common-row population, because the original S1.4 replay requires both 15m-ready and 1h-ready rows before all S1.4 branches are compared.

That first run is **SUPERSEDED / NON-AUTHORITATIVE**.

The corrected run restores the original S1.4 common-row identity and block phase. Its baseline metrics match the frozen S1.4 authority.

## Corrected exact-common-row 2025 comparison

| Session | Canonical BA | Selected BA | Delta BA | Canonical Brier | Selected Brier | Selected UP | Selected DOWN | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 48.92% | 43.81% | -5.12 pp | 0.2777 | 0.2643 | 45.59% | 42.03% | reject |
| Sobti Asia Morning | **60.86%** | 57.49% | -3.36 pp | 0.2557 | 0.2555 | 65.67% | 49.32% | reject; canonical direction stronger |
| Sobti Europe | 45.71% | 44.63% | -1.09 pp | 0.2631 | 0.2572 | 84.34% | 4.92% | reject; severe class collapse |
| Sobti NY/London | 51.15% | 50.53% | -0.62 pp | 0.2726 | 0.2714 | 40.74% | 60.32% | reject |
| Sobti Late-US | 53.30% | 51.27% | -2.03 pp | 0.2478 | 0.2329 | 92.54% | 10.00% | reject; severe class collapse |
| WGC Asia | 51.80% | 47.04% | -4.76 pp | 0.2792 | 0.2664 | 81.03% | 13.04% | reject |
| WGC Europe | 49.90% | **51.06%** | +1.15 pp | 0.2686 | **0.2578** | 77.50% | **24.62%** | reject; 30% class-recall floor fails |
| WGC US | 44.83% | 42.09% | -2.74 pp | 0.2998 | 0.2933 | 19.28% | 64.91% | reject |

## Binding decision

1. **Canonical Model-05 remains S14_A1_PLUS_1H_FULL.**
2. The 1h PATH feature-selection hypothesis is not validated for promotion.
3. No selected 1h Structural-IRIS variant is promoted.
4. WGC Europe is explicitly rejected despite better BA/Brier because DOWN recall falls to 24.62%, below the frozen 30% floor.
5. Sobti Asia Morning remains the strongest canonical 2025 Model-05 head:
   - N 140
   - Accuracy 60.71%
   - Balanced Accuracy 60.86%
   - UP recall 64.18%
   - DOWN recall 57.53%
   - Brier 0.2557
6. Existing 15m S1.4 variants remain separate historical/window-specific frozen candidates; this Model-05B test neither deletes nor promotes them.
7. No 2025 parameter/feature tuning was performed.
8. 2026 remains unopened.
