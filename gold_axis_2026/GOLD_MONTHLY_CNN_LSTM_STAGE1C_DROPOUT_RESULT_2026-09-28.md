# GOLD MONTHLY FORECAST — CNN/LSTM STAGE 1C DROPOUT RESULT

Date: 2026-09-28
Status: **STAGE 1C COMPLETE / ALL SCIENTIFIC GATES PASS**

Authority:
- `gold_axis_2026/GOLD_MONTHLY_CNN_LSTM_AUTHORITY_AND_STAGE_PLAN_2026-09-28.md`
- `gold_axis_2026/GOLD_MONTHLY_CNN_LSTM_STAGE1C_DROPOUT_FREEZE_2026-09-28.md`

Stage-1B parents:
- LSTM: lookback 3, width 32, dropout 0.10
- CNN-LSTM: lookback 6, width 32, dropout 0.10

Workflow:
- run id: `36449230158`
- workflow commit: `c598b0362248807d148c0e9e6259e797abb36068`

## Scope

Stage 1C changed **dropout only**.

Frozen alternatives:
- 0.00
- 0.10 = existing parent, not rerun
- 0.20

Pure CNN was not included because its canonical architecture has no dropout layer. Adding one would be a structural architecture change rather than a clean dropout-factor ablation.

## Full Stage-1C comparison

| Architecture | Lookback | Width | Dropout | DEV SigmaAE | Direction | Relative MAE vs RW | Gate |
|---|---:|---:|---:|---:|---:|---:|---|
| LSTM | 3 | 32 | 0.00 | 1642.260829 | 19/33 | 0.934164 | PASS |
| LSTM | 3 | 32 | **0.10** | **1589.982720** | **19/33** | **0.904427** | PASS |
| LSTM | 3 | 32 | 0.20 | 1591.571554 | 18/33 | 0.905331 | PASS |
| CNN-LSTM | 6 | 32 | 0.00 | 1664.049364 | 15/33 | 0.946558 | PASS |
| CNN-LSTM | 6 | 32 | **0.10** | **1528.569851** | **20/33** | **0.869494** | PASS |
| CNN-LSTM | 6 | 32 | 0.20 | 1607.029670 | 19/33 | 0.914124 | PASS |

## Stage-1C decisions

### LSTM
Winner: **dropout 0.10**
- SigmaAE 1589.982720
- direction 19/33
- relative MAE vs RW 0.904427

Dropout 0.20 is very close on primary price error:
- SigmaAE 1591.571554
- difference vs 0.10 = +1.588834
- approximately +0.10% worse

But it is also one direction origin worse (18/33), so 0.10 remains the clean winner.

Dropout 0.00 materially worsened price error:
- SigmaAE 1642.260829
- direction 19/33
- relative MAE vs RW 0.934164

### CNN-LSTM
Winner: **dropout 0.10**
- SigmaAE 1528.569851
- direction 20/33
- relative MAE vs RW 0.869494

Dropout 0.00:
- SigmaAE 1664.049364
- direction 15/33
- relative MAE vs RW 0.946558

Dropout 0.20:
- SigmaAE 1607.029670
- direction 19/33
- relative MAE vs RW 0.914124

Thus CNN-LSTM shows a clear interior optimum at dropout 0.10 among the frozen 0.00/0.10/0.20 candidates.

## Interpretation

- Removing dropout entirely hurts both recurrent architectures.
- Increasing dropout from 0.10 to 0.20 does not improve the primary DEV objective.
- CNN-LSTM is especially sensitive: no-dropout degrades both price error and direction sharply.
- For LSTM, 0.20 is near-tied on price but not better and loses one direction origin.
- Dropout is therefore not the current bottleneck behind the cross-family performance gap.

## Overall family leader after Stage 1C

Unchanged:
- **CNN-LSTM**
- lookback **6**
- width **32**
- dropout **0.10**
- DEV SigmaAE **1528.569851**
- direction **20/33**
- relative MAE vs RW **0.869494**

## Cross-family context

Family leader still trails retained cross-family references:
- ChHHO-ANFIS: 1413.029779 / 23/33
- DE-ABC-RBFNN: 1415.8371 / 25/33
- ANN FULL7: 1428.8590 / 22/33
- ANN REDUCED4: 1431.4587 / 24/33
- SVR EPSILON_RBF_DAILY12: 1449.187363 / 19/33
- CatBoost price: 1460.4339353 / 20/33

## Scientific gate

All four new Stage-1C jobs separately PASS:
- train_last < target
- sequence ends at forecast origin
- train-only scaling invariance
- future-feature perturbation invariance
- target-label perturbation invariance
- same-seed deterministic replay
- exactly 3/3 seed outputs at every DEV origin
- finite predictions
- abs(predicted log return) < 1
- DB authority invariants unchanged
- exactly 33 DEV origins
- no 2025/2026 modeling rows loaded

All four result artifacts were uploaded successfully.

## Decision

- Stage 1C COMPLETE.
- LSTM Stage-1C parent: LB3 / W32 / D0.10.
- CNN-LSTM Stage-1C parent: LB6 / W32 / D0.10.
- Pure CNN unchanged from Stage 1B.
- Overall family leader remains CNN-LSTM LB6 / W32 / D0.10.
- Next authorized factor: **Stage 1D learning-rate sensitivity**.
- 2025 remains locked.
- 2026 remains excluded from tuning/selection.

## Kontrol ve Uyum Özeti

- Only dropout changed: PASS.
- Parent lookback/width preserved: PASS.
- Pure CNN excluded because dropout is not part of its canonical architecture: PASS.
- Blind Cartesian search: NONE.
- Random split: NONE.
- DEV only: PASS.
- 2025 opened: NO.
- 2026 used for tuning/selection: NO.
- DB writes: NONE / READ_ONLY.
- Four new challengers completed: YES.
- Scientific gate: PASS for all four.
- Stage 1D started: NO.
