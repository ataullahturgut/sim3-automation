# GOLD MONTHLY FORECAST — CNN/LSTM STAGE 0 IMPLEMENTATION FREEZE

Date: 2026-09-28
Status: FROZEN BEFORE STAGE-0 OUTCOME
Parent authority: `gold_axis_2026/GOLD_MONTHLY_CNN_LSTM_AUTHORITY_AND_STAGE_PLAN_2026-09-28.md`
Parent authority commit: `c5a9f3ce83e916f634db1e27ac47294a9fd43de3`

## Purpose

Freeze implementation details that were intentionally not specified at framework level in the parent authority before any CNN/LSTM Stage-0 result is observed.

## Binding scope

Stage 0 only:
- 0A LSTM
- 0B 1D CNN
- 0C CNN-LSTM

No Stage-1 tuning is authorized by this file.

## Framework/runtime

- Python 3.11
- TensorFlow CPU 2.20.0
- deterministic TensorFlow operations enabled
- one CPU thread for intra/inter-op execution
- CUDA disabled
- `shuffle=False`

## Data boundary

- DB access is READ_ONLY.
- DEV targets only: 2022-04..2024-12, n=33.
- No 2025 target actual, feature, predictor or score may be queried or loaded.
- No 2026 target actual, feature, predictor or score may be queried or loaded.
- Gold and daily-metal source queries are hard-cut at 2025-01-01.
- GPR PIT vintages are restricted to DEV forecast origins through 2024-11.
- Feature engineering remains the existing frozen VW-MIDAS CURRENT8 contract.

## Sequence construction

- lookback = 12 completed monthly feature rows.
- Each feature row is the frozen 8-dimensional VW-MIDAS predictor vector already used by prior monthly neural families.
- For target month T, the prediction sequence contains 12 feature rows whose final feature timestamp is origin T-1.
- Training labels must satisfy label_month < T.
- Gold log return only is the Stage-0 target.

## Scaling

Inner seed-selection fit:
- feature scaler fit only on inner-training sequences, flattened over sequence/time while preserving feature columns;
- target scaler fit only on inner-training Gold log-return labels;
- validation sequence/labels never influence scaler parameters.

Final origin fit:
- after seed selection, scalers are refit only on all pre-target training sequences/labels;
- current target input sequence never influences scaler parameters;
- target-month label never influences fit/scaling.

Standardization:
- mean/std;
- std < 1e-9 replaced with 1.0.

## Chronological inner validation

- final 20% of pre-target training sequences;
- minimum 12 validation rows where feasible;
- if fewer than 24 total sequences exist, use the final max(1, ceil(20%)) rows;
- no random split.

## Deterministic repeats

Frozen seeds:
- 1701
- 2903
- 4111

For each DEV origin:
1. train the frozen architecture independently under each seed;
2. use early stopping on chronological validation MAE;
3. record best epoch and natural-scale Gold log-return validation MAE;
4. select the seed with the lowest validation MAE, tie-break by seed value;
5. refit the selected seed once on all pre-target sequences for its selected best-epoch count;
6. use that refit for the forecast.

Determinism replay is a scientific diagnostic only and does not replace the canonical forecast refit. It is run on fixed boundary origins to verify same-seed reproducibility.

## Frozen architecture/training

Common:
- optimizer Adam
- learning rate 0.001
- MAE loss
- batch size 16
- max 300 epochs
- early stopping patience 25
- restore best validation weights

0A LSTM:
- LSTM(32)
- Dropout(0.10)
- Dense(1)

0B CNN:
- Conv1D(filters=32, kernel=3, stride=1, padding=valid, ReLU)
- GlobalAveragePooling1D
- Dense(1)

0C CNN-LSTM:
- Conv1D(filters=32, kernel=3, stride=1, padding=valid, ReLU)
- LSTM(32)
- Dropout(0.10)
- Dense(1)

## Mandatory scientific gate

Each model must separately PASS:
1. train_last < target for every DEV origin;
2. prediction sequence last timestamp = forecast origin;
3. train-only scaling invariance;
4. future-feature perturbation invariance;
5. target-label perturbation invariance before scoring;
6. same-seed deterministic replay;
7. exactly 3/3 seed-selection outputs per DEV origin;
8. all predictions finite;
9. |predicted Gold log return| < 1;
10. DB authority invariants unchanged.

Additional boundary gate:
- 2025/2026 modeling rows loaded = 0.

## Required Stage-0 report fields

Per model:
- DEV sum absolute error on reconstructed price
- MAE/RMSE/MAPE/WAPE
- direction correct / 33
- relative MAE vs random walk
- yearly 2022/2023/2024 blocks
- worst month
- selected-seed counts
- seed validation dispersion
- scientific gate details
- exact runtime/dependency metadata

## Governance

- No rescue tuning.
- No Stage-1 parameter change based on partial Stage-0 outcomes.
- No 2025 opening.
- No 2026 tuning/selection.
- No DB writes.
