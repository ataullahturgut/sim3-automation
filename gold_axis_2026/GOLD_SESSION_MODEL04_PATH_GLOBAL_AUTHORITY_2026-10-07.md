# SESSION MODEL-04 — PATH_GLOBAL — IDENTITY + FEATURE-SELECTION AUTHORITY

**Date:** 2026-10-07  
**Status:** BASELINE COMPLETE / FEATURE-SELECTED CHALLENGER COMPLETE

## Baseline

SESSION Model-04 baseline is the accepted IRIS HOURLY_ONLY / PATH_GLOBAL model.

Identity authority:
- `GOLD_SESSION_MODEL04_PATH_GLOBAL_IDENTITY_AUTHORITY_2026-10-07.md`

Baseline implementation:
- StandardScaler
- LogisticRegression(L2, C=1.0)
- threshold 0.50
- original 25 hourly PATH/VOL/SHAPE features
- hourly bar-close availability `<= target_start`
- five-row causal replay
- 2022 warm-up / 2023–2024 development / 2025 frozen transport / 2026 unopened

2025 independent identity audit:
- matched rows: 284
- maximum probability difference: 0.0

## Model-04B variable-selection challenger

Authorities:
- `GOLD_SESSION_MODEL04B_PATH_GLOBAL_FEATURE_SELECTION_PREREG_2026-10-07.md`
- `GOLD_SESSION_MODEL04B_PATH_GLOBAL_FEATURE_SELECTION_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_MODEL04B_PATH_GLOBAL_FEATURE_SELECTION_2025_METRICS_2026-10-07.csv`
- `GOLD_SESSION_MODEL04B_PATH_GLOBAL_FEATURE_SELECTION_FROZEN_FEATURES_2026-10-07.json`

Selection is confined to the original PATH_GLOBAL hourly feature family. No 15m, cross-metal, macro, GVZ, COT or model-output feature was added.

## Exact-common-row 2025 comparison

| Session | Baseline BA | Selected BA | ΔBA | Baseline Brier | Selected Brier | UP recall selected | DOWN recall selected | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 50.35% | 47.49% | -2.87 pp | 0.2705 | 0.2653 | 52.94% | 42.03% | reject selected |
| Sobti Asia Morning | 53.52% | 53.52% | +0.00 pp | 0.2656 | **0.2556** | 52.24% | 54.79% | retain as calibration-only challenger |
| Sobti Europe | 51.12% | 49.21% | -1.91 pp | 0.2627 | 0.2529 | 77.11% | 21.31% | reject selected; class floor fails |
| Sobti NY/London | 42.68% | 41.98% | -0.70 pp | 0.2740 | 0.2672 | 39.51% | 44.44% | reject selected |
| Sobti Late-US | 53.30% | 52.05% | -1.25 pp | 0.2559 | 0.2531 | 79.10% | 25.00% | reject selected; class floor fails |
| WGC Asia | 58.14% | **59.21%** | **+1.06 pp** | 0.2608 | **0.2461** | 75.86% | **42.55%** | **retain / promotable challenger** |
| WGC Europe | 51.59% | 51.68% | +0.10 pp | 0.2676 | 0.2552 | 78.75% | 24.62% | reject selected; class floor fails |
| WGC US | 49.38% | 40.55% | -8.82 pp | 0.2825 | 0.2740 | 33.73% | 47.37% | reject selected |

## WGC Asia selected PATH_GLOBAL

Frozen variables:
- g1h_rv_48
- g1h_ret_3h
- g1h_max_drawdown_24
- g1h_slope_6
- g1h_lag2
- g1h_ret_1h
- g1h_ret_12h
- g1h_jump_concentration_24

2025 exact common-row result:
- N = 105
- Accuracy = 60.95%
- Balanced Accuracy = 59.21%
- UP recall = 75.86%
- DOWN recall = 42.55%
- Brier = 0.2461

Baseline on the same 105 rows:
- Accuracy = 60.00%
- Balanced Accuracy = 58.14%
- UP recall = 75.86%
- DOWN recall = 40.43%
- Brier = 0.2608

This is a clean same-coverage improvement in both balanced directional skill and probability quality.

## Binding Model-04 decision

1. The full 25-feature PATH_GLOBAL remains the canonical baseline identity.
2. The selected representation does not replace PATH_GLOBAL globally.
3. **WGC Asia selected PATH_GLOBAL is retained as a promotable window-specific challenger.**
4. Sobti Asia Morning selected PATH is retained only as a calibration-only challenger because discrete direction metrics are unchanged while Brier improves.
5. All other selected PATH variants are rejected.
6. The 30% minimum class-recall floor remains binding; this explicitly rejects selected WGC Europe despite a tiny BA increase and improved Brier.
7. No 2025 tuning occurred; the subsets were frozen from 2023–2024 development.
8. 2026 remains unopened.
9. The next primary lineage item is SESSION Model-05 — STRUCTURAL_IRIS / A1_PLUS_PATH.
