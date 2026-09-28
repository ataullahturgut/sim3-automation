# GOLD MONTHLY FORECAST — CNN/LSTM STAGE 1D LEARNING RATE FREEZE

Date: 2026-09-28
Status: **FROZEN BEFORE STAGE-1D OUTCOME**

Parent authority:
- `gold_axis_2026/GOLD_MONTHLY_CNN_LSTM_AUTHORITY_AND_STAGE_PLAN_2026-09-28.md`

Stage checkpoints:
- Stage 1A lookback result
- Stage 1B width result
- Stage 1C dropout result

## Purpose

Stage 1D is the **final local micro-tuning gate** before structural challengers.

It isolates **Adam learning rate only**.

## Frozen parents

### LSTM
- lookback 3
- width 32
- dropout 0.10
- Adam lr 0.001 parent
- DEV SigmaAE 1589.982720
- direction 19/33

### CNN
- lookback 3
- filters 16
- canonical CNN has no dropout layer
- Adam lr 0.001 parent
- DEV SigmaAE 1641.506529
- direction 20/33

### CNN-LSTM
- lookback 6
- Conv1D filters 32
- LSTM units 32
- dropout 0.10
- Adam lr 0.001 parent
- DEV SigmaAE 1528.569851
- direction 20/33

## Authorized challengers

Exactly three new runs:
- LSTM parent + Adam lr 0.0003
- CNN parent + Adam lr 0.0003
- CNN-LSTM parent + Adam lr 0.0003

The lr 0.001 parents are existing frozen results and must not be rerun.

## All non-LR settings remain frozen

- feature panel: frozen VW-MIDAS CURRENT8
- target: next-month Gold log return
- DEV: 2022-04..2024-12, n=33
- parent lookback / width / dropout as above
- CNN kernel 3
- stride 1
- padding valid
- optimizer Adam
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

Within each architecture compare lr 0.0003 vs parent lr 0.001 on:
1. DEV reconstructed-price SigmaAE (primary)
2. direction correct / 33
3. relative MAE vs RW
4. yearly stability
5. seed dispersion

## Pre-frozen stop rule

Stage 1D closes local micro-tuning unless a challenger shows **meaningful evidence** of benefit.

Meaningful evidence is defined before outcome as either:
- at least **1.0% lower DEV SigmaAE** than that architecture's parent, or
- at least **+2 direction-correct origins** with no more than **0.5% deterioration in DEV SigmaAE**.

If no challenger meets either condition:
- Stage 1E batch-size sweep is skipped;
- Stage 1F CNN-kernel micro-sweep is skipped;
- no local Cartesian interaction grid is opened;
- proceed directly to structural challengers:
  1. BiLSTM
  2. CNN-BiLSTM
  3. controlled CNN-BiLSTM refinement only if justified.

A small numerical win below the threshold may still replace the architecture parent under the frozen primary-metric rule, but it does **not** justify further micro-tuning.

## Scientific gate

Each challenger must independently PASS:
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
- No lookback/width/dropout/batch/kernel changes.
- No random split.
- No 2025 opening.
- No 2026 selection/tuning.
- DB READ_ONLY.
