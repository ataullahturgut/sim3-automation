# GOLD MONTHLY H=1 — Original Periods Dual-Model Replay (23 Oct 2026)

**Status:** COMPLETED. 108/108 monthly forecasts, both original solvers, all 12 independent jobs and aggregation PASS.
**Reproducible run:** https://github.com/ataullahturgut/sim3-automation/actions/runs/39969094669
**Workflow:** `.github/workflows/gold-monthly-h1-historical-dual-model-20261023.yml`
**Research branch:** `gold-midas-headswap-v1-20260925`
**Data contract:** `NEON_STAKTRAKR_GPR_V2` (existing frozen/pinned inputs; no source rework)
**Full per-month data:** run artifact `monthly-h1-original-periods-54x2-comparison`, artifact ID `12508512122`, 90-day retention, includes 108 prediction rows, provenance, and phase metrics.

## Exact original window contract

- DEV: **2022-04..2024-12**, 33 targets. Internal chronological train/validation routines unchanged.
- TEST: **2025-01..2025-12**, 12 targets.
- STRESS: **2026-01..2026-07**, 7 targets.
- EXTRA (kept separate from old test): **2026-08..2026-09**, 2 targets.
- 54 targets per original model; expanding historical training samples from 2010 onward, completed prior-month labels only. No 2025/2026 outcomes used to select solver configurations.
- Original unchanged ChHHO-ANFIS solver `vw_midas_anfis_stage3c_literature_v1.py` and DE-ABC-RBFNN solver `vw_midas_rbfnn_stage1_v1.py`. Their optimizer state was isolated with a fresh process for each model/target.

## Verified result (USD/oz monthly average)

| Period | Targets | CHHHO sum abs $ | CHHHO MAPE | CHHHO correct direction | DE-ABC sum abs $ | DE-ABC MAPE | DE-ABC correct direction |
|---|---:|---:|---:|---:|---:|---:|---:|
| DEV 2022-24 | 33 | 1365.00 | 2.0335% | 24/33 | 1371.66 | 1.9956% | 26/33 |
| TEST 2025 | 12 | 1248.19 | 2.9666% | 9/12 | 1074.44 | 2.5493% | 9/12 |
| STRESS Jan-Jul 2026 | 7 | 1405.16 | 4.3077% | 6/7 | 1222.50 | 3.8442% | 6/7 |
| EXTRA Aug-Sep 2026 | 2 | 692.43 | 7.9333% | 1/2 | 519.47 | 5.9424% | 1/2 |

Combined original 52 targets (excluding extra):
- ChHHO sum abs **4018.36 $/oz**, MAPE **2.5550%**, direction **39/52=75.00%**.
- DE-ABC sum abs **3668.60 $/oz**, MAPE **2.3722%**, direction **41/52=78.85%**.

Combined 54 targets:
- ChHHO sum abs **4710.79 $/oz**, MAPE **2.7542%**, direction **40/54=74.07%**, 18 errors exceed 3%.
- DE-ABC sum abs **4188.07 $/oz**, MAPE **2.5045%**, direction **42/54=77.78%**, 19 errors exceed 3%.
- Both improve over previous-month-average no-change reference on DEV, TEST, and STRESS by sum absolute error; both underperform this reference on Aug-Sep 2026.
- DEV: ChHHO has marginally smaller summed absolute error (6.65 $/oz), while DE-ABC has lower MAPE and 2 more correct directions. On untouched TEST 2025 and STRESS 2026, DE-ABC has smaller summed absolute error and lower MAPE.
- Accuracy deteriorates markedly in 2026 even with improved direction consistency.

## Evidence / interpretation

- 12 source-gated job runs PASS; aggregate job PASS. Outputs were checked for every expected target, model family, input provenance SHA, valid finite estimates, and source contract. Full 108-row JSON is retained with the GitHub Actions run.
- In TEST 2025 both models have 9/12 direction, but DE-ABC error improvement is material (absolute error sum 1074.44 vs 1248.19).
- On STRESS Jan-Jul 2026 both are 6/7 correct direction, but percentage forecast errors are larger. This **does not** establish either model's prospective investment reliability.
- These are retrospective **research-only** forecasts; the 2026 price observations were reconstructed from a later Git data snapshot rather than certified original firstprints. This limitation was already accepted/recorded in source contract; source work was not reopened.
- This run did not change algorithms, fitting hyperparameter selection, data sources, Neon forecasts, the existing 262 archived forecasts, or production.
