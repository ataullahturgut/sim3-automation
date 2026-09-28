# GOLD MONTHLY FORECAST — BOOSTING STAGE 6C-D0 CAUSAL VMD–XGBOOST PRE-OUTCOME FREEZE

Date: 2026-09-28
Status: FROZEN BEFORE OUTCOME

## Authority

Primary gold-specific structural source:
Guo, Y.; Li, C.; Wang, X.; Duan, Y. (2025).
"Gold Price Prediction Using Two-layer Decomposition and XGboost Optimized by the Whale Optimization Algorithm."
Computational Economics 66(2), 1157-1189.
DOI: 10.1007/s10614-024-10736-9.

The source uses VMD as the first decomposition layer before residual CEEMDAN and WOA-XGBoost.

VMD method authority:
Dragomiretskiy, K.; Zosso, D. (2014).
"Variational Mode Decomposition."
IEEE Transactions on Signal Processing 62(3), 531-544.
DOI: 10.1109/TSP.2013.2288675.

Reference Python implementation:
vmdpy / sktime.libs.vmdpy.

The gold paper's exact standalone D0 VMD parameterization is NOT_FOUND.
Therefore Stage 6C-D0 uses the canonical reference-example parameters, frozen before any outcome:
- alpha = 2000
- tau = 0.0
- K = 3
- DC = 0
- init = 1 (uniform center-frequency initialization)
- tol = 1e-7

No VMD parameter tuning is authorized in D0.

## Scientific question

Does causal VMD itself provide useful multiscale information to the already-frozen XGBoost learner under the GOLD MONTHLY H=1 protocol?

Only the representation changes.
The XGBoost learner remains frozen.

## Frozen forecasting contract

- Forecast target: H=1 next-calendar-month average XAU/USD.
- Training target: next-month Gold log return.
- Price reconstruction: previous completed-month Gold average * exp(predicted log return).
- DEV: 2022-04..2024-12, n=33.
- 2025: BLOCKED / NOT OPENED.
- 2026: QUARANTINED / NOT USED IN DEVELOPMENT.
- Random split: NONE.
- DB: READ_ONLY.
- Primary metric: DEV price SigmaAE.
- Secondary: direction, MAE, RMSE, MAPE/WAPE, relative MAE vs RW, yearly stability, worst month.

## Frozen XGBoost learner

Use Stage-5 CURRENT8 X_R4_COMBO unchanged:
- objective = reg:squarederror
- n_estimators = 200
- learning_rate = 0.05
- max_depth = 4
- min_child_weight = 1
- gamma = 0.001
- subsample = 0.80
- colsample_bytree = 0.80
- reg_alpha = 0.01
- reg_lambda = 5.0
- tree_method = hist
- random_state = 1701
- n_jobs = 1

Frozen CURRENT8 reference:
- DEV SigmaAE = 1583.8534958594905
- direction = 20/33.

## Causal VMD representation

Input signal:
- authoritative monthly Gold average levels from the project database.
- decomposition history starts at 2010-01.
- feature generation begins only after 60 completed monthly observations.

For target t:
1. origin = t-1.
2. Build the Gold level prefix 2010-01..origin only.
3. Run VMD on this prefix only.
4. Recover K=3 modes.
5. Define residual = original signal - sum(three VMD modes).
6. Feature vector for t:
   [mode1_endpoint, mode2_endpoint, mode3_endpoint, residual_endpoint].
7. Every historical training row k must be generated from its own independent prefix ending at k-1.
8. A later outer-origin decomposition may never be reused for an earlier training row.

Representation name:
CAUSAL_VMD_K3_MODES_PLUS_RESIDUAL_ENDPOINT

Feature dimension = 4.

## Leakage and integrity gates

The run must fail if:
- any decomposition prefix extends past t-1,
- any training target is >= outer target,
- 2025/2026 enters development,
- feature dimension != 4,
- any VMD output is non-finite,
- mode count != 3,
- reconstruction using modes + residual differs from the input beyond floating tolerance,
- deterministic smoke replay differs,
- DB authority invariants change,
- frozen CURRENT8 comparator does not reconcile exactly.

## Decision rule

Primary comparator:
Frozen Stage-5 XGBoost CURRENT8 X_R4_COMBO.

Proceed to Stage 6C-D1 only if D0 meets at least one pre-outcome criterion:
A. primary improvement: DEV SigmaAE < 1583.8534958594905; OR
B. complementarity signal: direction >= 22/33 AND DEV SigmaAE <= 1.05 * 1583.8534958594905.

Otherwise D1 is CLOSED_NOT_OPENED.

Context only:
Vanilla CatBoost family leader = SigmaAE 1460.433935309605.

## Stop rule

Stage 6C-D0 evaluates causal VMD-XGBoost only.
It does NOT authorize:
- CEEMDAN residual decomposition,
- WOA,
- VMD tuning,
- ensemble,
- 2025 holdout.
