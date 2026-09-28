# GOLD MONTHLY FORECAST — CNN/LSTM STAGE 1B CAPACITY/WIDTH FREEZE

Date: 2026-09-28
Status: **FROZEN BEFORE STAGE-1B OUTCOME**

Parent authority:
- `gold_axis_2026/GOLD_MONTHLY_CNN_LSTM_AUTHORITY_AND_STAGE_PLAN_2026-09-28.md`
- authority commit `c5a9f3ce83e916f634db1e27ac47294a9fd43de3`

Stage-1A checkpoint:
- `gold_axis_2026/GOLD_MONTHLY_CNN_LSTM_STAGE1A_LOOKBACK_RESULT_2026-09-28.md`
- checkpoint commits `6a63ccd034c42e9608c2c7fa7729e05a2cba41a1`, `7072cdd67bb0c3004399617fe46f0ead2b8f43a3`

## Purpose

Stage 1B isolates **capacity / width only**.

No other architecture or training parameter may change.

## Frozen parents from Stage 1A

- LSTM parent: lookback 3, width 32
- CNN parent: lookback 3, filters 32
- CNN-LSTM parent: lookback 6, CNN filters 32 + LSTM units 32

## Authorized challengers

For each architecture, evaluate only:
- width 16
- width 64

Width 32 is the existing parent and must not be rerun.

Thus exactly six new challenger runs are authorized:
- LSTM LB3 W16
- LSTM LB3 W64
- CNN LB3 W16
- CNN LB3 W64
- CNN-LSTM LB6 W16
- CNN-LSTM LB6 W64

For CNN-LSTM, width changes jointly:
- Conv1D filters = width
- LSTM hidden units = width

No asymmetric 16/32, 32/64, 64/32 combinations are allowed in Stage 1B.

## All non-width settings remain frozen

- feature panel: frozen VW-MIDAS CURRENT8
- target: next-month Gold log return
- DEV: 2022-04..2024-12, n=33
- selected lookbacks from Stage 1A
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

Within each architecture, compare width 16, 32 and 64 on:
1. DEV reconstructed-price SigmaAE (primary)
2. direction correct / 33
3. relative MAE vs RW
4. yearly stability
5. seed dispersion

The best width within each architecture becomes that architecture's Stage-1B parent for Stage 1C.

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
- No lookback/dropout/LR/batch/kernel changes.
- No Cartesian search.
- No 2025 opening.
- No 2026 selection/tuning.
- DB READ_ONLY.
