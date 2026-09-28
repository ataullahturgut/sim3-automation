# GOLD MONTHLY FORECAST — CNN/LSTM STAGE 1B WIDTH RESULT

Date: 2026-09-28
Status: **STAGE 1B COMPLETE / ALL SCIENTIFIC GATES PASS**

Authority:
- `gold_axis_2026/GOLD_MONTHLY_CNN_LSTM_AUTHORITY_AND_STAGE_PLAN_2026-09-28.md`
- `gold_axis_2026/GOLD_MONTHLY_CNN_LSTM_STAGE1B_WIDTH_FREEZE_2026-09-28.md`

Stage-1A parents:
- LSTM: lookback 3, width 32
- CNN: lookback 3, width 32
- CNN-LSTM: lookback 6, width 32

Workflow:
- run id: `36444509542`
- workflow commit: `24d2597e3af21088044c4d63c3e775705bd030f2`

## Scope

Stage 1B changed **capacity / width only**.

Frozen width alternatives:
- 16
- 32 = existing Stage-1A parent, not rerun
- 64

All other architecture/training settings remained frozen.

## Full Stage-1B comparison

| Architecture | Lookback | Width | DEV SigmaAE | Direction | Relative MAE vs RW | Gate |
|---|---:|---:|---:|---:|---:|---|
| LSTM | 3 | 16 | 1781.506869 | 18/33 | 1.013371 | PASS |
| LSTM | 3 | **32** | **1589.982720** | 19/33 | **0.904427** | PASS |
| LSTM | 3 | 64 | 1622.268592 | **20/33** | 0.922792 | PASS |
| CNN | 3 | **16** | **1641.506529** | 20/33 | **0.933735** | PASS |
| CNN | 3 | 32 | 1641.827499 | **21/33** | 0.933918 | PASS |
| CNN | 3 | 64 | 1650.274754 | 18/33 | 0.938723 | PASS |
| CNN-LSTM | 6 | 16 | 1536.953447 | 18/33 | 0.874262 | PASS |
| CNN-LSTM | 6 | **32** | **1528.569851** | **20/33** | **0.869494** | PASS |
| CNN-LSTM | 6 | 64 | 1532.628331 | 18/33 | 0.871802 | PASS |

## Stage-1B architecture decisions

### LSTM
Winner under the frozen primary criterion: **width 32**
- SigmaAE 1589.982720
- direction 19/33
- relative MAE vs RW 0.904427

Width 64 improved direction to 20/33 but worsened primary SigmaAE to 1622.268592.
Width 16 materially degraded performance and was worse than RW on aggregate relative MAE.

### CNN
Technical primary-criterion winner: **width 16**
- SigmaAE 1641.506529
- direction 20/33
- relative MAE vs RW 0.933735

Width 32:
- SigmaAE 1641.827499
- direction 21/33
- relative MAE vs RW 0.933918

The price-error advantage of width 16 over width 32 is only **0.320970 SigmaAE**, approximately **0.0196%**. Therefore this is a technical primary-metric win, not evidence of a meaningful capacity effect. Width 32 remains direction-superior by one origin.

Width 64 is inferior on both primary price error and direction versus width 32.

### CNN-LSTM
Winner: **width 32**
- SigmaAE 1528.569851
- direction 20/33
- relative MAE vs RW 0.869494

Width 16:
- SigmaAE 1536.953447
- direction 18/33

Width 64:
- SigmaAE 1532.628331
- direction 18/33

Width 64 has a very strong 2024 block:
- direction 10/12
- relative MAE vs RW 0.638867

However its weaker 2022 and 2023 blocks make its total DEV result inferior to width 32.

## Overall family leader after Stage 1B

Unchanged:
- **CNN-LSTM**
- lookback **6**
- width **32**
- DEV SigmaAE **1528.569851**
- direction **20/33**
- relative MAE vs RW **0.869494**

Stage 1B did **not** improve the CNN/LSTM family-wide price leader.

Interpretation:
- LSTM appears underfit at width 16 and does not benefit enough from width 64.
- CNN is largely width-insensitive between 16 and 32; the difference is negligible.
- CNN-LSTM has a clear local optimum at width 32 among the frozen 16/32/64 candidates.
- Capacity is therefore unlikely to be the main bottleneck behind the gap to cross-family leaders.

## Cross-family context

Family leader still trails:
- ChHHO-ANFIS: 1413.029779 / 23/33
- DE-ABC-RBFNN: 1415.8371 / 25/33
- ANN FULL7: 1428.8590 / 22/33
- ANN REDUCED4: 1431.4587 / 24/33
- SVR EPSILON_RBF_DAILY12: 1449.187363 / 19/33
- CatBoost price: 1460.4339353 / 20/33

## Scientific gate

All six new Stage-1B jobs separately PASS:
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

## Decision

- Stage 1B COMPLETE.
- LSTM Stage-1B parent: LB3 / W32.
- CNN Stage-1B parent: LB3 / W16 under the frozen primary SigmaAE rule, with W32 retained as a near-tie direction-superior diagnostic reference.
- CNN-LSTM Stage-1B parent: LB6 / W32.
- Overall family leader remains CNN-LSTM LB6 / W32.
- Next authorized factor: Stage 1C dropout regularization.
- 2025 remains locked.
- 2026 remains excluded from tuning/selection.

## Kontrol ve Uyum Özeti

- Only width changed: PASS.
- Parent lookbacks preserved: PASS.
- Blind Cartesian search: NONE.
- Random split: NONE.
- DEV only: PASS.
- 2025 opened: NO.
- 2026 used for tuning/selection: NO.
- DB writes: NONE / READ_ONLY.
- Six new challengers completed: YES.
- Scientific gate: PASS for all six.
- Stage 1C started: NO.
