# GOLD MONTHLY FORECAST — TIMEXER V1 FREEZE

**Freeze date:** 2026-09-28
**Branch:** `gold-midas-headswap-v1-20260925`
**Status:** PRE-RUN METHOD FREEZE

## Provenance
Official implementation:
- `thuml/TimeXer`
- pinned source commit: `76011909357972bd55a27adba2e1be994d81b327`
- paper: TimeXer, NeurIPS 2024

TimeXer is designed specifically for forecasting an endogenous target with exogenous time-series inputs. In the official `features='MS'` path, the last input column is treated as the endogenous target and preceding columns as exogenous series.

## Frozen Gold V1 representation
Input order:
1. Silver monthly average
2. Platinum monthly average
3. Palladium monthly average
4. Gold monthly average — endogenous target, deliberately last

No GPR/macro inputs in V1.
No CURRENT8 engineered MR/VW features in V1.
No future exogenous values are supplied.
Only historical exogenous observations through the forecast origin are used.

## Chronology
- training history starts 2010-05
- lookback = 48 completed months
- H=1
- rolling 48->1 supervised windows
- latest 12 matured pre-target target months = explicit chronological validation
- earlier windows = training
- random split = NONE
- outer target month is never present in training/validation inputs or labels

## Frozen architecture
The official EPF example uses roughly seven patches per context (seq_len=168, patch_len=24).
For monthly Gold V1:
- seq_len=48
- patch_len=6 -> 8 patches
- features='MS'
- enc_in=4
- c_out=1
- pred_len=1
- e_layers=2
- d_model=64
- d_ff=128
- n_heads=4
- factor=1
- dropout=0.1
- activation='gelu'
- use_norm=1

The smaller hidden width is frozen before results because the governed Gold sample has only ~80-130 train windows per origin, far below the official high-frequency EPF sample scale. V1 tests the TimeXer architecture rather than reproducing the capacity of a large hourly benchmark.

## Training
- seed=20260928 reset per origin
- Adam
- learning_rate=1e-4
- batch_size=16
- max_epochs=20
- patience=4
- loss=MSE on Gold H=1
- validation=MSE on explicit latest-12 matured target months
- best validation state restored before outer forecast
- device=CPU
- no architecture or hyperparameter tuning inside V1

## Evaluation
- DEV 2022-04..2024-12, n=33: sole scientific comparison authority
- 2025: LOCKED_REPORT_ONLY
- 2026-01..2026-07: QUARANTINED_REPORT_ONLY
- primary metric: DEV SigmaAE
- secondary: Gold direction accuracy
- support: MAE, RMSE, MAPE, WAPE, relative MAE vs Random Walk, worst month

## Governance
- DB READ_ONLY
- no random split
- no target-month leakage
- no future exogenous data
- existing Challenger-A/B paths unchanged
- no post-result V1 tuning
