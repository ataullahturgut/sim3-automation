# GOLD MONTHLY ELMFIS — Stage 0 Canonical Baseline

Date: 2026-09-25

## Implementation
- Model: VW_MIDAS_ELMFIS_BASELINE_V1
- Workflow: .github/workflows/gold-midas-elmfis-baseline-v1.yml
- Run: 36161681793 — SUCCESS / OUTPUT_GATE=PASS
- Artifact: 10876525569
- Script: gold_axis_2026/tools/vw_midas_elmfis_baseline_v1.py

## Canonical structure
- 8 governed VW-MIDAS inputs.
- 4 return outputs jointly.
- 5 fuzzy rules.
- Bell/Gaussian membership.
- Product AND, normalized rule firing.
- First-order TSK consequents.
- Consequents solved analytically with ridge alpha 0.001.
- Rule centers initialized by training-only deterministic k-means.
- Rule spreads estimated from training-only within-rule standard deviations.
- No random split.
- DB READ_ONLY.
- 2025/2026 not used for model selection.

## Active-metric results

| Period | n | Sum absolute error USD | Direction | MAE | MAPE % | Relative MAE vs RW |
|---|---:|---:|---:|---:|---:|---:|
| DEV 2022-04..2024-12 | 33 | **1996.2933** | **20/33 = 60.61%** | 60.4937 | 2.95477 | 1.13555 |
| 2025 transport | 12 | **1032.7313** | **9/12 = 75.00%** | 86.0609 | 2.49825 | 0.61217 |
| 2026 Jan-Jul stress | 7 | **1997.7390** | **3/7 = 42.86%** | 285.3913 | 6.20731 | 1.20491 |

## Decision
- Baseline implementation is technically valid and governance checks pass.
- Baseline is weak on DEV cumulative absolute error and worse than RW MAE on DEV.
- Baseline weakness does **not** close the ELMFIS family.
- Proceed to the predeclared full Stage-1 optimizer parity screen because optimized ELMFIS is the actual research question.
- 2025/2026 remain descriptive only and do not affect continuation/optimizer selection.
