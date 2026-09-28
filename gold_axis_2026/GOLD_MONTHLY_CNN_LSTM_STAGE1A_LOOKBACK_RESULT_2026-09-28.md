# GOLD MONTHLY FORECAST — CNN/LSTM STAGE 1A LOOKBACK RESULT

Date: 2026-09-28
Status: **STAGE 1A COMPLETE / ALL SCIENTIFIC GATES PASS**

Authority:
- `gold_axis_2026/GOLD_MONTHLY_CNN_LSTM_AUTHORITY_AND_STAGE_PLAN_2026-09-28.md`
- `gold_axis_2026/GOLD_MONTHLY_CNN_LSTM_STAGE1A_LOOKBACK_FREEZE_2026-09-28.md`

Workflow:
- run id: `36439589026`
- workflow commit: `2733449eadab0c17f0b87af6c3804b635182412d`

## Scope

Stage 1A changed **lookback only**.

Frozen alternatives:
- 3 months
- 6 months
- 12 months = canonical Stage-0 parent result

All other architecture/training settings remained frozen.

## Full Stage-1A comparison

| Architecture | Lookback | DEV SigmaAE | Direction | Relative MAE vs RW | Scientific gate |
|---|---:|---:|---:|---:|---|
| LSTM | 3 | 1589.982720 | 19/33 | 0.904427 | PASS |
| LSTM | 6 | 1594.166828 | 15/33 | 0.906807 | PASS |
| LSTM | 12 | 1738.059520 | 15/33 | 0.988657 | PASS |
| CNN | 3 | 1641.827499 | 21/33 | 0.933918 | PASS |
| CNN | 6 | 1735.729785 | 16/33 | 0.987332 | PASS |
| CNN | 12 | 1906.942562 | 13/33 | 1.084723 | PASS |
| CNN-LSTM | 3 | 1588.107858 | 19/33 | 0.903361 | PASS |
| CNN-LSTM | 6 | **1528.569851** | **20/33** | **0.869494** | PASS |
| CNN-LSTM | 12 | 1554.308208 | 18/33 | 0.884134 | PASS |

## Stage-1A architecture leaders

### LSTM
Winner: **lookback 3**
- SigmaAE: 1589.982720
- direction: 19/33
- relative MAE vs RW: 0.904427
- parent LB12 SigmaAE: 1738.059520

### CNN
Winner: **lookback 3**
- SigmaAE: 1641.827499
- direction: 21/33
- relative MAE vs RW: 0.933918
- parent LB12 SigmaAE: 1906.942562

### CNN-LSTM
Winner: **lookback 6**
- SigmaAE: **1528.569851**
- direction: **20/33**
- relative MAE vs RW: **0.869494**
- parent LB12 SigmaAE: 1554.308208
- improvement vs Stage-0 CNN-LSTM parent: 25.738357 SigmaAE, approximately 1.656%.

## CNN-LSTM LB6 yearly blocks

### 2022
- n=9
- SigmaAE 440.379016
- MAE 48.931002
- direction 5/9
- relative MAE vs RW 0.913649

### 2023
- n=12
- SigmaAE 501.419608
- MAE 41.784967
- direction 6/12
- relative MAE vs RW 1.006867

### 2024
- n=12
- SigmaAE 586.771227
- MAE 48.897602
- direction 9/12
- relative MAE vs RW 0.754205

Worst month:
- target 2024-03
- actual 2158.0
- forecast 2027.842728
- absolute error 130.157272

Seed behavior:
- selected seed 1701: 1 origin
- selected seed 2903: 23 origins
- selected seed 4111: 9 origins
- mean validation-MAE seed spread: 0.002110449
- max validation-MAE seed spread: 0.004857024

## Scientific gate

All six new Stage-1A jobs separately PASS:
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

All six result artifacts were uploaded successfully.

## Cross-family context

Stage-1A family leader CNN-LSTM LB6 remains behind retained cross-family price references:
- ChHHO-ANFIS: 1413.029779 / 23/33
- DE-ABC-RBFNN: 1415.8371 / 25/33
- ANN FULL7: 1428.8590 / 22/33
- ANN REDUCED4: 1431.4587 / 24/33
- SVR EPSILON_RBF_DAILY12: 1449.187363 / 19/33
- CatBoost price: 1460.4339353 / 20/33

Therefore Stage 1A improves the CNN/LSTM family but does not yet produce the overall project leader.

## Decision

- Stage 1A COMPLETE.
- LSTM Stage-1A parent: LB3.
- CNN Stage-1A parent: LB3.
- CNN-LSTM Stage-1A parent: LB6.
- Overall family leader after Stage 1A: **CNN-LSTM LB6**.
- Stage 1B next authorized factor: **capacity / width**, varying only width/filter count while preserving the selected lookback for each architecture.
- 2025 remains locked.
- 2026 remains excluded from tuning/selection.

## Kontrol ve Uyum Özeti

- Only lookback changed: PASS.
- Blind Cartesian search: NONE.
- Random split: NONE.
- DEV only: PASS.
- 2025 opened: NO.
- 2026 used for tuning/selection: NO.
- DB writes: NONE / READ_ONLY.
- Six new challengers completed: YES.
- Scientific gate: PASS for all six.
- Stage 1B started: NO.
