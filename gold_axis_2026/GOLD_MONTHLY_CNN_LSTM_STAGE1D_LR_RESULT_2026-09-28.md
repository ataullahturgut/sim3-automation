# GOLD MONTHLY FORECAST — CNN/LSTM STAGE 1D LEARNING RATE RESULT

Date: 2026-09-28
Status: **STAGE 1D COMPLETE / MICRO-TUNING CLOSED**

Authority:
- `gold_axis_2026/GOLD_MONTHLY_CNN_LSTM_STAGE1D_LR_FREEZE_2026-09-28.md`
- freeze commit `6b633642c18eb2b6e99c9d55f5659c4d4b300b5f`

Workflow:
- run id: `36453143598`
- workflow commit: `ac220c4ff642d921bc1e7486f2a1bf0fc2aadab5`

## Results

| Architecture | Parent LR | Parent SigmaAE | Parent Dir | Challenger LR | Challenger SigmaAE | Challenger Dir | Meaningful-evidence gate |
|---|---:|---:|---:|---:|---:|---:|---|
| LSTM LB3 W32 D0.10 | 0.001 | 1589.982720 | 19/33 | 0.0003 | 1648.503201 | 20/33 | FAIL |
| CNN LB3 W16 | 0.001 | 1641.506529 | 20/33 | 0.0003 | 1637.176965 | 21/33 | FAIL |
| CNN-LSTM LB6 W32 D0.10 | 0.001 | 1528.569851 | 20/33 | 0.0003 | 1583.467570 | 18/33 | FAIL |

## Pre-frozen stop-rule evaluation

Meaningful evidence required either:
1. >=1.0% lower DEV SigmaAE, or
2. >=2 direction-correct origins with no more than 0.5% SigmaAE deterioration.

None of the three challengers meets either condition.

CNN LR=0.0003 has a small local numerical price win:
- improvement: 4.329564 SigmaAE
- approximately 0.264%
- direction: +1 origin

This is below the pre-frozen meaningful-evidence threshold. It may be retained as a local CNN diagnostic/technical parent under the primary metric, but it does **not** justify more micro-tuning.

LSTM LR=0.0003 materially worsens price error.
CNN-LSTM LR=0.0003 materially worsens both price error and direction.

## Decision

- Stage 1D COMPLETE.
- Pre-frozen stop rule TRIGGERED.
- Stage 1E batch-size sweep: SKIPPED.
- Stage 1F kernel micro-sweep: SKIPPED.
- local Cartesian interaction tuning: CLOSED.
- overall family leader remains:
  - CNN-LSTM
  - lookback 6
  - width 32
  - dropout 0.10
  - Adam LR 0.001
  - DEV SigmaAE 1528.569851
  - direction 20/33
- next modeling phase after snapshot parity:
  1. BiLSTM structural challenger
  2. CNN-BiLSTM structural challenger
  3. controlled structural refinement only if justified.

## Kontrol ve Uyum Özeti

- Only learning rate changed: PASS.
- Three challengers completed: YES.
- Scientific gate: PASS for all three.
- Random split: NONE.
- 2025 opened: NO.
- 2026 used for tuning/selection: NO.
- DB writes: NONE / READ_ONLY.
- Stop rule defined before outcome: YES.
- Micro-tuning closed according to frozen rule: YES.
