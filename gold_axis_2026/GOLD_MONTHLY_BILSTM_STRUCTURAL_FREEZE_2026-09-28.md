# GOLD MONTHLY FORECAST — BiLSTM STRUCTURAL CHALLENGER FREEZE

Date: 2026-09-28
Status: **FROZEN BEFORE OUTCOME**

## Position in roadmap

- Stage 1A lookback: complete
- Stage 1B width: complete
- Stage 1C dropout: complete
- Stage 1D learning rate: complete
- Micro-tuning stop rule: triggered
- Stage 1E batch sweep: skipped
- Stage 1F kernel sweep: skipped
- DEV Snapshot V1: authorized with exact offline parity
- Next structural challenger: **Vanilla BiLSTM**

## Execution source

Use only authorized DEV Snapshot V1:
- schema: `GOLD_MONTHLY_DEV_SNAPSHOT_V1_2026-09-28`
- source workflow run: `36456042954`
- snapshot artifact id: `10985453248`
- payload SHA-256: `2111e394f60d131995273789fc014dc339db4e1b7672095c89117c133879a3eb`

Neon access in the BiLSTM job is forbidden.

## Frozen architecture

Structural parent: Stage-1C/1D LSTM parent.

- input shape: lookback 3 x 8 frozen VW-MIDAS predictors
- layer: `Bidirectional(LSTM(32))`
  - 32 units in forward direction
  - 32 units in backward direction
  - merge mode: concat
- Dropout(0.10)
- Dense(1)

The backward pass operates **only inside the completed historical lookback window**. It does not access any timestamp after forecast origin.

## Frozen training

- target: next-month Gold log return
- DEV: 2022-04..2024-12, n=33
- lookback: 3 completed months
- width: 32 per LSTM direction
- dropout: 0.10
- optimizer: Adam
- learning rate: 0.001
- loss: MAE
- batch size: 16
- max epochs: 300
- early stopping patience: 25
- seeds: 1701, 2903, 4111
- chronological inner validation
- no shuffle
- train-only X/Y scaling
- seed selection: inner validation natural-scale Gold log-return MAE
- final refit: selected seed + best epoch on all pre-target sequences

## Comparison references

Primary structural parent — LSTM:
- SigmaAE: 1589.9827200167367
- direction: 19/33
- relative MAE vs RW: 0.9044270307262439

Current CNN/LSTM family leader — CNN-LSTM:
- SigmaAE: 1528.5698506560245
- direction: 20/33
- relative MAE vs RW: 0.8694936579385805

Cross-family reference leaders remain unchanged and are contextual only.

## Promotion interpretation

BiLSTM is considered structurally promising if it provides meaningful evidence under the already-established structural-development philosophy:
- clearly lower DEV SigmaAE than LSTM parent, and/or
- material direction improvement without material price-error degradation.

No rescue tuning is allowed from this run.

If Vanilla BiLSTM is weak, do not open a BiLSTM micro-grid.
If it is promising, only a small predeclared structural refinement may follow.

## Scientific gate

Must independently PASS:
- snapshot payload hash verified
- no database connection present
- train_last < target
- sequence endpoint = forecast origin
- train-only scaling invariance
- future-feature perturbation invariance
- target-label perturbation invariance
- deterministic replay
- 3/3 seed outputs per origin
- finite forecasts
- abs(predicted log return) < 1
- exactly 33 DEV origins
- 2025/2026 rows absent

## Governance

- Snapshot is execution cache only; Neon remains authority.
- Random split: forbidden.
- 2025: locked.
- 2026: excluded from tuning/selection.
- No DB writes.
- No parameter search in this run.
