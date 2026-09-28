# GOLD MONTHLY FORECAST — CNN/LSTM STAGE 1C DROPOUT FREEZE

Date: 2026-09-28
Status: **FROZEN BEFORE STAGE-1C OUTCOME**

Parent authority:
- `gold_axis_2026/GOLD_MONTHLY_CNN_LSTM_AUTHORITY_AND_STAGE_PLAN_2026-09-28.md`

Stage-1B checkpoint:
- `gold_axis_2026/GOLD_MONTHLY_CNN_LSTM_STAGE1B_WIDTH_RESULT_2026-09-28.md`
- checkpoint commits `4194d3864a88dd1e3c23fa5cc0a541ecf15347e8`, `6f52ffb8e652a95be2667a5ea5694c2d62e827fd`

## Purpose

Stage 1C isolates **dropout regularization only**.

No other architecture or training parameter may change.

## Frozen parents

- LSTM: lookback 3, width 32, dropout 0.10
- CNN-LSTM: lookback 6, width 32, dropout 0.10

Pure CNN is **not part of Stage 1C** because the canonical CNN architecture has no dropout layer. Adding a dropout layer would be a structural architecture change, not a clean dropout-factor ablation.

## Authorized challengers

For LSTM and CNN-LSTM evaluate:
- dropout 0.00
- dropout 0.20

Dropout 0.10 is the existing parent and must not be rerun.

Thus exactly four new challenger runs are authorized:
- LSTM LB3 W32 D0.00
- LSTM LB3 W32 D0.20
- CNN-LSTM LB6 W32 D0.00
- CNN-LSTM LB6 W32 D0.20

## All non-dropout settings remain frozen

- feature panel: frozen VW-MIDAS CURRENT8
- target: next-month Gold log return
- DEV: 2022-04..2024-12, n=33
- LSTM lookback 3 / width 32
- CNN-LSTM lookback 6 / width 32
- CNN kernel 3
- stride 1
- padding valid
- optimizer Adam
- learning rate 0.001
- loss MAE
- batch size 16
- max epochs 300
- patience 25
- seeds 1701, 2903, 4111
- chronological inner validation
- no shuffle
- train-only X/Y scaling
- seed selection by inner validation Gold log-return MAE
- final refit on all pre-target sequences at selected best epoch

## Selection rule

Within each applicable architecture compare dropout 0.00, 0.10, 0.20 on:
1. DEV reconstructed-price SigmaAE (primary)
2. direction correct / 33
3. relative MAE vs RW
4. yearly stability
5. seed dispersion

The best dropout becomes that architecture's Stage-1C parent for Stage 1D.

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
- No lookback/width/LR/batch/kernel changes.
- No Cartesian search.
- No 2025 opening.
- No 2026 selection/tuning.
- DB READ_ONLY.
