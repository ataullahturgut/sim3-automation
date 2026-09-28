# GOLD MONTHLY FORECAST — CNN/LSTM STAGE 0 CANONICAL RESULT

Date: 2026-09-28
Status: **STAGE 0 COMPLETE / SCIENTIFIC GATE PASS**
Parent authority: `GOLD_MONTHLY_CNN_LSTM_AUTHORITY_AND_STAGE_PLAN_2026-09-28.md`
Implementation freeze: `GOLD_MONTHLY_CNN_LSTM_STAGE0_IMPLEMENTATION_FREEZE_2026-09-28.md`

## Canonical Stage-0 results — DEV 2022-04..2024-12, n=33

| Model | DEV SigmaAE | MAE | Direction | Relative MAE vs RW | Gate |
|---|---:|---:|---:|---:|---|
| CNN-LSTM | 1554.308208 | 47.100249 | 18/33 | 0.884134 | PASS |
| LSTM | 1738.059520 | 52.668470 | 15/33 | 0.988657 | PASS |
| 1D CNN | 1906.942562 | 57.786138 | 13/33 | 1.084723 | PASS |

Stage-0 family leader: **CNN-LSTM**.

## CNN-LSTM yearly blocks

- 2022 (9 origins): SigmaAE 455.293466; MAE 50.588163; direction 4/9; relative MAE vs RW 0.944592.
- 2023 (12 origins): SigmaAE 505.672021; MAE 42.139335; direction 6/12; relative MAE vs RW 1.015406.
- 2024 (12 origins): SigmaAE 593.342721; MAE 49.445227; direction 8/12; relative MAE vs RW 0.762651.

Worst month:
- target 2024-03
- actual 2158.0
- forecast 2030.857352
- absolute error 127.142648

Seed behavior:
- selected seed 4111 at all 33 DEV origins.
- mean validation-MAE seed spread 0.002324750.
- max validation-MAE seed spread 0.005508843.

A duplicate CNN-LSTM workflow run was triggered from the same commit. It reproduced the canonical CNN-LSTM metrics exactly and is treated as a duplicate determinism confirmation, not a separate model result.

## LSTM diagnostic

- SigmaAE 1738.059520
- direction 15/33
- relative MAE vs RW 0.988657
- worst target 2024-04; AE 143.197983
- selected seeds: 1701 at 32 origins, 4111 at 1 origin.

## CNN diagnostic

- SigmaAE 1906.942562
- direction 13/33
- relative MAE vs RW 1.084723
- worst target 2024-04; AE 164.220705
- selected seeds: 2903 at 30 origins, 1701 at 2, 4111 at 1.

## Scientific gate

All three canonical models PASS all required checks:
- train_last < target;
- sequence ends at forecast origin;
- train-only scaling invariance;
- future-feature perturbation invariance;
- target-label perturbation invariance;
- deterministic replay;
- 3/3 seed outputs at every DEV origin;
- finite predictions;
- abs(predicted Gold log return) < 1;
- DB authority invariants unchanged;
- exactly 33 DEV origins;
- 2025/2026 modeling rows loaded = 0.

## Cross-family context

The Stage-0 CNN-LSTM baseline does not yet beat retained cross-family leaders:
- ChHHO-ANFIS: 1413.029779 / 23 of 33 direction
- DE-ABC-RBFNN: 1415.8371 / 25 of 33
- ANN FULL7: 1428.8590 / 22 of 33
- ANN REDUCED4: 1431.4587 / 24 of 33
- SVR EPSILON_RBF_DAILY12: 1449.187363 / 19 of 33
- CatBoost price: 1460.4339353 / 20 of 33

Therefore Stage 0 is technically successful but not cross-family champion evidence.

## Decision

- Stage 0 COMPLETE.
- CNN-LSTM is the Stage-0 family leader.
- LSTM retained as baseline.
- CNN retained as weak baseline; it is worse than RW on aggregate relative MAE.
- Stage 1 is authorized because the mandatory Stage-0 gate passed.
- Next exact step: Stage 1A controlled lookback sensitivity under the already frozen family plan.
- 2025 remains locked.
- 2026 remains excluded from tuning/selection.

## Kontrol ve Uyum Özeti

- DEV-only selection: PASS.
- Random split: NONE.
- DB writes: NONE / READ_ONLY.
- 2025 queried/loaded for CNN/LSTM modeling: NO.
- 2026 queried/loaded for CNN/LSTM modeling: NO.
- Scientific gate: PASS for 0A/0B/0C.
- Stage 0 complete: YES.
- Stage 1 started: NO.
