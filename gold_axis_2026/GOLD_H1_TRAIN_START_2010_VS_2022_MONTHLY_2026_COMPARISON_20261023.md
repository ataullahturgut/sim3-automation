# GOLD H1 — 2010 vs 2022 initial training window; 2026 month-by-month

**Date:** 2026-10-23. **No database write; original unchanged CHHHO-ANFIS and DE-ABC-RBFNN solvers.**

**Existing 2010-trained reference**: [Actions 39969094669](https://github.com/ataullahturgut/sim3-automation/actions/runs/39969094669) (2010-03 onward), 54 monthly targets per family. **New 2022-trained test**: [Actions 39974655540](https://github.com/ataullahturgut/sim3-automation/actions/runs/39974655540) (2022-04 onward), 9 monthly targets per family. Both include January–September 2026. New workflow 3/3 jobs PASS.

This **newly added research experiment** is different from the prior outer evaluation starting in 2022. Both use the same Neon V2 price/GPR contract and origin-specific official GPR vintage. Only the completed-target training sample cutoff differs, resulting in 145–198 past rows for 2010, vs 45–53 for 2022.

### Absolute percentage errors (lower is better)

| Month 2026 | CHHHO trained 2010 | CHHHO trained 2022 | DE-ABC trained 2010 | DE-ABC trained 2022 |
|---|---:|---:|---:|---:|
| Jan | 9.72% | 7.72% | 8.33% | 7.94% |
| Feb | 2.53% | 6.20% | 1.61% | 2.82% |
| Mar | 8.39% | **22900.82% (INVALID-PLAUSIBILITY, solver uncapped)** | 3.87% | 3.32% |
| Apr | 0.63% | 11.67% | 0.65% | 4.82% |
| May | 1.04% | 2.89% | 1.61% | 2.81% |
| Jun | 7.45% | 13.55% | 7.59% | 7.80% |
| Jul | 0.38% | 4.87% | 3.24% | 4.73% |
| Aug | 7.23% | 5.30% | 6.43% | 3.44% |
| Sep | 8.64% | 9.23% | 5.45% | 6.70% |

### Aggregate 2026 January–September

| Model | Start | Mean APE | Correct directions | Σ absolute error USD/oz |
|---|---|---:|---:|---:|
| CHHHO-ANFIS | 2010-03 | **5.1134%** | **7/9** | 2097.5971 |
| CHHHO-ANFIS | 2022-04 | **2551.3600%** | 5/9 | 1120252.0564 |
| DE-ABC-RBFNN | 2010-03 | **4.3105%** | **7/9** | **1741.9717** |
| DE-ABC-RBFNN | 2022-04 | 4.9308% | 5/9 | 1999.3982 |

For a robustness comparison, excluding the March outlier in CHHHO: 2010-start MAPE 4.7032% (other eight months), 2022-start MAPE 7.6778% (same eight). 2010 start still better.

### Scientific / reproducibility caveat

March 2026 CHHHO with 2022-only training predicted USD **1,122,370.1372/oz** vs realized USD **4,879.6968/oz**. This is a mathematically finite but **obviously unusable** optimizer extrapolation, not a plausible investment forecast. Model lacks an upper plausible-return abstention gate. Retain raw output to show failure; do not silently replace/clamp.

Independent consistency audit on both runs: same actual prices and prior-month origin gold prices for all 9 targets; same official GPR source commit for all 9 target months. Feature hash equals the 2010 baseline for **7/9 month-targets within each model**, Jan–Jul. August and September feature SHA differs at exact byte level between runs, so this experiment does **not** certify identical feature bytes on those 2 origins, although both use the same approved source contract and output price levels. Jan–Jul strict seven-month subset still supports the 2010 advantage:
- CHHHO 2010 MAPE **4.3077%**, 2022 MAPE **3278.2449%** (due to March failure); 6/7 vs 4/7 directions.
- DE-ABC 2010 MAPE **3.8442%**, 2022 MAPE **4.8918%**; 6/7 vs 4/7 directions.

This is retrospective controlled historical research using subsequently captured market price snapshots, **not** a prospective original 2026 firstprint certification. This comparison does not change previous 54×2 results, the October label-free replays, or production.
