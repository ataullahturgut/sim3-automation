# GOLD MONTHLY FORECAST — CNN/LSTM STAGE 0 RESULT REPORT

Date: 2026-09-28  
Status: **STAGE 0 COMPLETE / SCIENTIFIC GATE PASS / STAGE 1 AUTHORIZED**  
Branch: `gold-midas-headswap-v1-20260925`

## 1. Authority and implementation freeze

Parent authority:
- `gold_axis_2026/GOLD_MONTHLY_CNN_LSTM_AUTHORITY_AND_STAGE_PLAN_2026-09-28.md`
- authority commit: `c5a9f3ce83e916f634db1e27ac47294a9fd43de3`

Stage-0 implementation freeze:
- `gold_axis_2026/GOLD_MONTHLY_CNN_LSTM_STAGE0_IMPLEMENTATION_FREEZE_2026-09-28.md`
- commit: `f4ebb7c112a60a31c65874677947b3d1a02f1011`

Shared governed runner:
- `gold_axis_2026/tools/gold_monthly_cnn_lstm_stage0_v1.py`
- commit: `8687666c0c29087eb433643af414fc15a297d969`

Frozen model contract:
- DEV only = 2022-04..2024-12, n=33
- frozen VW-MIDAS CURRENT8 predictor contract
- lookback = 12
- target = next-month Gold log return
- reconstructed-price DEV SigmaAE is primary
- train-only X/Y scaling
- chronological inner validation
- deterministic seeds = 1701, 2903, 4111
- Adam, lr=0.001, batch=16, MAE, max 300 epochs, patience=25
- no shuffle
- 2025 locked and not queried/loaded
- 2026 quarantined and not queried/loaded
- DB READ_ONLY

## 2. Operational correction before valid model runs

The first workflow attempts failed **before model training** because the workflow environment omitted `scikit-learn`, which is imported by the existing metrics helper.

Classification:
- **TECHNICAL_PRE_MODEL_FAILURE**
- no model score was produced
- no hyperparameter or scientific-contract change was made

Correction:
- added the missing runtime dependency to all three workflows
- exposed full audit summaries in the workflow output
- model architecture, data, seeds, tuning and validation contract remained unchanged

Valid workflow-fix commits:
- LSTM: `dd8f39130c99e4d2e9c94579f9ec9e500c0bea1f`
- CNN: `b2da8e685d3b929e599c00a4d193d6b9a779062c`
- CNN-LSTM: `371dcbfa381e9ba6106683dce44d618cdcd9704a`

## 3. Stage-0 canonical results

| Rank in Stage 0 | Model | DEV SigmaAE | Direction | MAE | RMSE | WAPE % | Rel.MAE vs RW | Scientific gate |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | CNN-LSTM | **1554.308208** | **18/33** | 47.100249 | 59.753580 | 2.287336 | **0.884134** | PASS |
| 2 | LSTM | 1738.059520 | 15/33 | 52.668470 | 63.468334 | 2.557746 | 0.988657 | PASS |
| 3 | 1D CNN | 1906.942562 | 13/33 | 57.786138 | 69.951987 | 2.806276 | 1.084723 | PASS |

Interpretation:
- **CNN-LSTM is the canonical Stage-0 family leader** on both primary SigmaAE and direction.
- LSTM is slightly better than random walk in aggregate relative MAE.
- CNN is worse than random walk in aggregate relative MAE.
- None of the three canonical Stage-0 models beats the retained cross-family leaders.

## 4. Year-by-year DEV blocks

### CNN-LSTM

| Year | n | SigmaAE | Direction | Rel.MAE vs RW |
|---|---:|---:|---:|---:|
| 2022 | 9 | 455.293466 | 4/9 | 0.944592 |
| 2023 | 12 | 505.672021 | 6/12 | 1.015406 |
| 2024 | 12 | 593.342721 | 8/12 | 0.762651 |

Worst month:
- target = 2024-03
- actual = 2158.0
- forecast = 2030.857352
- absolute error = 127.142648

### LSTM

| Year | n | SigmaAE | Direction | Rel.MAE vs RW |
|---|---:|---:|---:|---:|
| 2022 | 9 | 461.911436 | 4/9 | 0.958322 |
| 2023 | 12 | 606.744753 | 5/12 | 1.218363 |
| 2024 | 12 | 669.403330 | 6/12 | 0.860416 |

Worst month:
- target = 2024-04
- actual = 2331.0
- forecast = 2187.802017
- absolute error = 143.197983

### 1D CNN

| Year | n | SigmaAE | Direction | Rel.MAE vs RW |
|---|---:|---:|---:|---:|
| 2022 | 9 | 591.995576 | 2/9 | 1.228207 |
| 2023 | 12 | 550.323672 | 4/12 | 1.105068 |
| 2024 | 12 | 764.623314 | 7/12 | 0.982806 |

Worst month:
- target = 2024-04
- actual = 2331.0
- forecast = 2166.779295
- absolute error = 164.220705

## 5. Seed behavior

CNN-LSTM:
- seed 4111 selected at **33/33** origins
- mean validation-MAE seed spread = 0.00232475
- max validation-MAE seed spread = 0.00550884

LSTM:
- seed 1701 selected at 32/33 origins
- seed 4111 selected at 1/33
- mean validation-MAE seed spread = 0.00165321
- max validation-MAE seed spread = 0.00334846

CNN:
- seed 2903 selected at 30/33 origins
- seed 1701 selected at 2/33
- seed 4111 selected at 1/33
- mean validation-MAE seed spread = 0.00091773
- max validation-MAE seed spread = 0.00297506

These concentrations are recorded as diagnostics; they are not used to alter Stage-0 outcomes.

## 6. Scientific gate

All three valid canonical models passed every required gate:

- train_last < target: PASS
- sequence ends at forecast origin: PASS
- train-only scaling invariance: PASS
- future-feature perturbation invariance: PASS
- target-label perturbation invariance: PASS
- same-seed deterministic replay: PASS
- exactly 3/3 seed outputs at all 33 origins: PASS
- finite predictions: PASS
- |predicted Gold log return| < 1: PASS
- DB authority invariants unchanged: PASS
- no 2025/2026 modeling rows queried/loaded: PASS
- DEV origin count = 33: PASS

## 7. Independent CNN-LSTM replay

A duplicate GitHub push caused two independent CNN-LSTM jobs for the same frozen commit.

Canonical run:
- run id: `36435087769`

Duplicate replay:
- run id: `36435087029`

Both completed successfully and produced **identical**:
- DEV SigmaAE = 1554.3082078115099
- direction = 18/33
- all aggregate metrics
- all yearly metrics
- seed selection counts
- worst month
- scientific-gate results

Decision:
- `36435087769` is retained as the canonical Stage-0C run.
- `36435087029` is retained only as an additional independent determinism audit, not as a second experiment.

## 8. Cross-family DEV comparison

| Model | DEV SigmaAE | Direction |
|---|---:|---:|
| ChHHO-ANFIS | **1413.029779** | 23/33 |
| DE-ABC-RBFNN | 1415.837100 | **25/33** |
| ANN FULL7 | 1428.859000 | 22/33 |
| ANN REDUCED4 | 1431.458700 | 24/33 |
| EPSILON_RBF_DAILY12 SVR | 1449.187363 | 19/33 |
| CATBOOST_PRICE | 1460.433935 | 20/33 |
| AOA-ELM | 1474.102100 | 20/33 |
| **CNN-LSTM Stage 0** | **1554.308208** | **18/33** |
| LSTM Stage 0 | 1738.059520 | 15/33 |
| CNN Stage 0 | 1906.942562 | 13/33 |

Stage-0 conclusion:
- CNN-LSTM is the only canonical model in this family with a clearly useful aggregate improvement over RW, but it is **not** a cross-family promotion candidate at its current canonical specification.
- Stage 0 is a baseline stage, not the family-final decision.
- Stage 1 controlled ablation remains authorized because all three scientific gates passed.

## 9. Valid GitHub runs

- Stage 0A LSTM: `36435073019` — SUCCESS
- Stage 0B CNN: `36435077515` — SUCCESS
- Stage 0C CNN-LSTM canonical: `36435087769` — SUCCESS
- Stage 0C duplicate determinism replay: `36435087029` — SUCCESS / audit-only

## 10. Exact next checkpoint

**Stage 1 — controlled sequence/capacity/training ablation.**

Per frozen family authority:
1. Stage 1A — lookback {3,6,12}
2. Stage 1B — width {16,32,64}
3. Stage 1C — dropout {0,.1,.2}
4. Stage 1D — learning rate {.0003,.001}
5. Stage 1E — batch {8,16,32}
6. Stage 1F — CNN-specific kernel refinement where applicable
7. Stage 1G — locked Stage-1 leader reconstruction

No blind Cartesian search.
No 2025.
No 2026 tuning/selection.
No rescue tuning of Stage-0 results.

## Kontrol ve Uyum Özeti

- Stage 0A/0B/0C completed: **YES**
- Valid workflows successful: **YES**
- Scientific gate all canonical models: **PASS**
- 2025 opened: **NO**
- 2025 queried/loaded by Stage 0: **NO**
- 2026 used: **NO**
- Random split: **NONE**
- DB writes: **NONE / READ_ONLY**
- Stage-0 family leader: **CNN-LSTM, SigmaAE 1554.308208, direction 18/33**
- Cross-family champion changed: **NO**
- Stage 1 authorized: **YES**
