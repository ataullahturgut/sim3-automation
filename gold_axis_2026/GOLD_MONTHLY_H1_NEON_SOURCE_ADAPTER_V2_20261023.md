# GOLD Monthly H=1 – Neon Source Adapter V2

Date: 2026-10-23. Project: next calendar month XAU/USD average.
Feature contract: **CURRENT8 = AU, AG, PT, PD × (MR1, VW-GPR)**.
Historical DEV: Apr 2022–Dec 2024. Retrospective 2025 and Jan–Sep 2026 must not be used for model selection.

## What changed
- Added `gold_axis_2026/tools/gold_monthly_h1_neon_source_v2.py`, which builds and verifies the SAME aligned four-metal daily prices as Neon view `gold_monthly_h1.staktrakr_single_repository_monthly_research_v1`.
- 2010–2025 days: `public.observations`, the pinned old StakTrakr Git historical file. Jan–Sep 2026: the pinned `staktrakr_2026_git_snapshot_daily_v1`. No attempt to mix `CORE5_CANONICAL` with new targets.
- Every one of 804 metal-month means must match the approved Neon monthly view, including the common-weekday observation counts. On missing, duplicate, unexpected revision or mismatched price the program **halts**.
- Every forecast origin Mar 2022–Sep 2026 must have its own official origin-dated GPR archive. For Mar 2022–Aug 2026, values from `GPR_OFFICIAL_GIT_PIT`, checked against `gold_monthly_h1.gpr_origin_safe_model_v1`; Sep 2026 from the cross-validated official Sep 2026 GPR archive.
- The full monthly GPR history is taken from **the same dated origin-specific source version** as the required lagged GPR value. This is critical for the original GPR normalization; a single monthly GPR scalar is insufficient.
- Added optional environment gate `GOLD_MONTHLY_H1_DATA_CONTRACT=NEON_STAKTRAKR_GPR_V2` to the ORIGINAL `vw_midas_msvr_successor_v1.py` loader. Historical frozen scripts remain unchanged unless this explicit mode is selected.
- Added `gold_monthly_h1_retrain_v2.py` to run the ORIGINAL ChHHO-ANFIS and DE-ABC-RBFNN solvers against this replacement DataBundle, with strict source checks and no database mutations.
- Added `test_gold_monthly_h1_neon_source_v2.py` and source-gated GitHub Actions workflow.

## Scientific limitations (do not suppress)
The 2026 StakTrakr Git records were captured in October 2026; they are not independently verified historical first-print/as-of prices. **The data adapter is authorized for retrospective research only**, not live trading or prospectively proven backtests. Old CORE5 prices and old forecast scores were a different target authority; direct score comparability is invalid.
The 2010–Feb 2022 GPR values in retrospective feature windows are sourced from the archive available at each later (2022+) forecast origin. This does not constitute a prospective 2010 forecast.
No optimizer/ANFIS/RBFNN equations or hyperparameter selections were modified. Retuning on 2025–2026 outcomes is forbidden.

## Execution
1. Set the Neon read-only secret `NEON_DATABASE_URL` in the execution environment. Keep it out of logs and files.
2. Validate real inputs, no model retraining:
   `python gold_axis_2026/tools/gold_monthly_h1_retrain_v2.py --mode inputs --targets 2022-04,2025-01,2026-08,2026-09`
3. Full real historical replay, explicit targets:
   `python gold_axis_2026/tools/gold_monthly_h1_retrain_v2.py --mode replay --models CHHHO,DE_ABC --targets 2026-08,2026-09`
4. Store results as **new research-version** results. Do not overwrite frozen historical results or the main application registry without separate acceptance testing.

## Verification state
- Unit tests prove 201-month source parity on synthetic aligned daily data, exact eight-feature invariance to target-month label, and fail-closed wrong provider, wrong GPR vintage and future-release handling.
- Real Neon input audit 2026-10-23: 4/4 checked targets (2022-04, 2025-01, 2026-08, 2026-09) produced eight features using the strict source loader.
- A training/inference replay requires its own successful execution record; unit tests and input audits are **not** proof of model forecasting performance.
