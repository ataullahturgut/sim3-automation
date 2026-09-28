# GOLD MONTHLY FORECAST — VANILLA BiLSTM STRUCTURAL RESULT

Date: 2026-09-28
Status: **COMPLETE / SCIENTIFIC GATE PASS / NOT PROMOTED**

Freeze:
- `gold_axis_2026/GOLD_MONTHLY_BILSTM_STRUCTURAL_FREEZE_2026-09-28.md`
- freeze commit `1b111e953b8c7cd83e2e5e0509a1f53316d73dfc`

Workflow:
- run id: `36458681241`
- workflow commit: `f912e9a31e5342f4db9663837e8d5dac1be71c97`

Execution:
- authorized DEV Snapshot V1 only
- snapshot payload SHA-256: `2111e394f60d131995273789fc014dc339db4e1b7672095c89117c133879a3eb`
- Neon connection: NONE
- artifact id: `10987310997`

## Frozen architecture

- input: 3 x 8
- Bidirectional(LSTM(32)), merge=concat
- Dropout 0.10
- Dense(1)
- Adam 0.001
- batch 16
- seeds 1701 / 2903 / 4111

## DEV result

- n: 33
- SigmaAE: **1638.0967950069746**
- MAE: 49.63929681839317
- RMSE: 61.26234861228702
- MAPE: 2.4583149554049166%
- WAPE: 2.410639851683735%
- direction: **19/33**
- relative MAE vs RW: **0.9317956740654008**
- monthly win rate vs RW: 0.5151515151515151
- median AE: 45.4018900419735
- worst month: 2024-11
  - actual: 2651.0
  - forecast: 2790.468996864613
  - absolute error: 139.46899686461302

## Yearly

### 2022
- SigmaAE: 483.1305445655739
- direction: 5/9
- relative MAE vs RW: 1.0023455281443443

### 2023
- SigmaAE: 531.2748970391663
- direction: 5/12
- relative MAE vs RW: 1.0668170623276432

### 2024
- SigmaAE: 623.6913534022344
- direction: 9/12
- relative MAE vs RW: 0.8016598372779363

## Seed behavior

Selected seed counts:
- 1701: 13 origins
- 2903: 0 origins
- 4111: 20 origins

Mean validation-MAE seed spread:
- 0.0014791747369424602

Max validation-MAE seed spread:
- 0.0028397994309840684

## Structural comparison

### Versus LSTM structural parent
LSTM:
- SigmaAE 1589.9827200167367
- direction 19/33
- relative MAE vs RW 0.9044270307262439

BiLSTM:
- SigmaAE 1638.0967950069746
- direction 19/33
- relative MAE vs RW 0.9317956740654008

Difference:
- SigmaAE: **+48.114075** (BiLSTM worse)
- approximately **+3.026%**
- direction: no improvement

### Versus current CNN/LSTM family leader
CNN-LSTM LB6/W32/D0.10/LR0.001:
- SigmaAE 1528.5698506560245
- direction 20/33

BiLSTM:
- SigmaAE 1638.0967950069746
- direction 19/33

Difference:
- SigmaAE: **+109.526944** (BiLSTM worse)
- approximately **+7.165%**
- direction: -1 origin

## Interpretation

Vanilla bidirectionality does not improve this small-sample H=1 monthly setup when applied to the LSTM parent window.

The 2024 block is reasonably strong directionally (9/12), but 2022 is essentially equal to RW and 2023 is worse than RW. The aggregate result is therefore inferior to the unidirectional LSTM parent and clearly inferior to the CNN-LSTM family leader.

Per the pre-outcome freeze:
- do **not** open a BiLSTM micro-hyperparameter grid;
- do **not** rescue-tune this BiLSTM;
- retain result as a completed negative structural challenger;
- proceed to **CNN-BiLSTM**, which tests bidirectionality after convolutional feature extraction rather than as a standalone recurrent replacement.

## Scientific gate

All PASS:
- snapshot hash verified
- no DB connection
- train_last < target
- sequence endpoint = origin
- train-only scaling invariance
- future-feature perturbation invariance
- target-label perturbation invariance
- same-seed deterministic replay
- 3/3 seed outputs
- finite predictions
- abs(pred log return) < 1
- exactly 33 DEV origins
- no 2025/2026 rows

## Decision

- Vanilla BiLSTM: **NOT PROMOTED**
- BiLSTM micro-grid: **NOT AUTHORIZED**
- current family leader unchanged: CNN-LSTM LB6/W32/D0.10/LR0.001
- next structural challenger: **CNN-BiLSTM**

## Kontrol ve Uyum Özeti

- Neon queried: NO
- Snapshot V1 used: YES
- Snapshot hash verified: PASS
- Scientific gate: PASS
- Random split: NONE
- 2025 opened: NO
- 2026 used: NO
- Rescue tuning: NONE
