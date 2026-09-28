# GOLD MONTHLY FORECAST — CNN/LSTM STAGE 1A LOOKBACK FREEZE

Date: 2026-09-28
Status: **FROZEN BEFORE STAGE-1A OUTCOME**

Parent authority:
- `gold_axis_2026/GOLD_MONTHLY_CNN_LSTM_AUTHORITY_AND_STAGE_PLAN_2026-09-28.md`
- authority commit `c5a9f3ce83e916f634db1e27ac47294a9fd43de3`

Stage-0 canonical result:
- `gold_axis_2026/GOLD_MONTHLY_CNN_LSTM_STAGE0_CANONICAL_RESULT_2026-09-28.md`
- result commit `89476d9269665b059a6b1a5869780d07dbb7aca6`

## Purpose

Stage 1A isolates **lookback sensitivity only**.

No other architecture or training parameter may change.

## Frozen candidates

For each canonical architecture:
- LSTM
- 1D CNN
- CNN-LSTM

Evaluate:
- lookback = 3 completed months
- lookback = 6 completed months
- lookback = 12 completed months = existing Stage-0 parent result, not rerun

Thus exactly six new challenger runs are authorized.

## All non-lookback settings remain frozen

- feature panel: frozen VW-MIDAS CURRENT8
- target: next-month Gold log return
- DEV: 2022-04..2024-12, n=33
- width / filters: 32
- dropout: 0.10 where applicable
- CNN kernel: 3
- stride: 1
- padding: valid
- optimizer: Adam
- learning rate: 0.001
- loss: MAE
- batch size: 16
- max epochs: 300
- patience: 25
- seeds: 1701, 2903, 4111
- chronological inner validation
- no shuffle
- train-only X/Y scaling
- seed selection by inner validation Gold log-return MAE
- final refit on all pre-target sequences at selected best epoch

## Selection rule

Within each architecture, compare lookback 3, 6 and 12 on:
1. DEV reconstructed-price SigmaAE (primary)
2. direction correct / 33
3. relative MAE vs RW
4. yearly stability
5. seed dispersion

No cross-architecture hyperparameter interaction is tested in Stage 1A.

The best lookback within each architecture becomes that architecture's Stage-1A parent for Stage 1B.

## Scientific gate

Each new run must independently PASS:
- train_last < target
- sequence endpoint = forecast origin
- train-only scaling invariance
- future-feature perturbation invariance
- target-label perturbation invariance
- deterministic replay
- 3/3 seed outputs per origin
- finite forecasts
- abs(predicted log return) < 1
- DB invariants unchanged
- exactly 33 DEV origins
- 2025/2026 modeling rows loaded = 0

## Governance

- No rescue tuning.
- No width/dropout/LR/batch/kernel changes.
- No Cartesian search.
- No 2025 opening.
- No 2026 selection/tuning.
- DB READ_ONLY.
