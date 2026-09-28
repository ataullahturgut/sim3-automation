# GOLD MONTHLY FORECAST — BOOSTING STAGE 6C-C CAUSAL CEEMDAN–XGBOOST PRE-OUTCOME FREEZE

Date: 2026-09-28
Status: FROZEN BEFORE OUTCOME

## Authority

Primary gold-specific structural source:
- Xin Xie (2025), "Research on Gold Price Prediction Model Based on CEEMDAN-XGBoost",
  Academic Journal of Science and Technology, 18(2), 88–95.
  DOI: 10.54097/27p05m50.
- Source design: daily gold opening prices, 2012-10-31..2022-10-28, 8:1:1 train/validation/test.
- Source reports CEEMDAN-XGBoost test MAE 21.0753 and RMSE 26.4743 versus standalone XGBoost test MAE 31.7936 and RMSE 38.8063.
- Source describes four interpretable IMF bands (IMF1..IMF4) and feeds decomposed IMF components to XGBoost.
- Exact XGBoost hyperparameters are NOT_FOUND in the paper text and therefore are not imported or guessed.

CEEMDAN implementation authority:
- PyEMD / EMD-signal.
- CEEMDAN default trials=100, epsilon=0.005.
- Reproducibility requires fixed noise seed and parallel=False.
- Torres et al. (2011) CEEMDAN; Colominas et al. (2014) improved CEEMDAN.

Leakage-control authority:
- Conventional one-time decomposition can leak future information into historical components.
- This experiment uses a moving-front / point-in-time construction: every target month's CEEMDAN feature is generated from a prefix ending at the previous completed month only.
- No global full-sample decomposition is permitted.

## Scientific question

Does a strictly causal CEEMDAN multiscale representation of Gold improve the already-frozen XGBoost learner under the GOLD MONTHLY H=1 protocol?

Only the representation changes.
The XGBoost learner and forecasting target remain frozen.

## Frozen project contract

- Forecast target: H=1 next-calendar-month average XAU/USD.
- Model training target: next-month Gold log return.
- Price reconstruction: previous completed-month Gold average * exp(predicted log return).
- DEV: 2022-04..2024-12, n=33.
- 2025: BLOCKED / NOT OPENED.
- 2026: QUARANTINED / NOT USED IN DEVELOPMENT.
- Random split: NONE.
- Database: READ_ONLY.
- Primary metric: DEV price SigmaAE.
- Secondary metrics: direction accuracy, MAE, RMSE, MAPE/WAPE, relative MAE vs RW, yearly stability, worst month.

## Frozen XGBoost learner

Use the Stage-5 CURRENT8 price/balance challenger X_R4_COMBO unchanged:

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
- DEV SigmaAE = 1583.8534959 (rounded report value; runner must reproduce exact stored computation from the same code/data)
- direction = 20/33.

No XGBoost hyperparameter optimization is authorized in Stage 6C-C.

## Causal CEEMDAN representation

### Input signal
- Authoritative monthly Gold average price series from the project database.
- Fixed decomposition history starts at 2010-01.
- A feature is created only after at least 60 completed monthly observations are available.

### For target month t
1. origin = t-1.
2. Build Gold level signal using only 2010-01..origin.
3. Run CEEMDAN only on this prefix.
4. Extract up to four IMF series, IMF1..IMF4.
5. Discard the residual/trend term, matching the source paper's IMF-feature design.
6. Feature vector for t = the endpoint values of IMF1..IMF4 at origin.
7. If fewer than four IMFs are returned, missing higher-order IMF slots are zero-padded and the IMF count is recorded.
8. Historical training row k must use its own independently generated prefix ending at k-1. It may NOT reuse a decomposition fitted through a later outer origin.

This produces a fixed 4-dimensional CAUSAL_CEEMDAN_IMF4_ENDPOINT representation.

## CEEMDAN parameters

Implementation package: EMD-signal==1.6.4 / PyEMD.

- trials = 100
- epsilon = 0.005
- max_imf = 4
- parallel = False
- noise seed = 1701
- default noise_kind = normal
- default noise_scale = 1
- default range_thr = 0.01
- default total_power_thr = 0.05
- beta_progress = True

No CEEMDAN parameter tuning is authorized.

## Integrity checks

The run must fail if:
- any outer target is outside DEV,
- 2025 or 2026 enters development,
- DB authority invariants change,
- any feature prefix extends past t-1,
- any training target is >= outer target,
- feature dimension is not 4,
- CEEMDAN output is non-finite,
- CEEMDAN reconstruction error exceeds tolerance,
- CURRENT8 XGBoost comparator does not reconcile to the Stage-5 frozen result,
- deterministic repeat decomposition of a smoke target differs beyond floating tolerance.

## Comparator and decision

Primary comparator:
- frozen XGBoost CURRENT8 X_R4_COMBO.

Context only:
- Vanilla CatBoost family leader: SigmaAE 1460.433935309605, direction 20/33.

Decision rule:
- Promote CEEMDAN-XGBoost only if it improves full 33-month DEV SigmaAE under the frozen causal protocol.
- Direction and stability are secondary diagnostics and cannot rescue a worse primary score after seeing outcomes.

## Stop rule

Stage 6C-C evaluates the single canonical causal CEEMDAN-XGBoost structural challenger only.
It does NOT authorize:
- CEEMDAN parameter tuning,
- VMD,
- residual CEEMDAN,
- WOA-XGBoost,
- ensembles,
- 2025 holdout evaluation.
