# GOLD MONTHLY FORECAST — CNN / LSTM FAMILY AUTHORITY AND STAGE PLAN

Date: 2026-09-28
Status: **AUTHORIZED / STAGE 0 FROZEN BEFORE OUTCOME**
Branch: `gold-midas-headswap-v1-20260925`

## 1. Purpose

Open the next GOLD MONTHLY model family after pausing SVR / DWT-SVR.

Family scope:
- canonical LSTM;
- canonical 1D CNN;
- canonical CNN-LSTM;
- later CNN-BiLSTM structural challenger;
- controlled ensemble only after family-level evidence exists.

This family remains separate from later roadmap families:
- ICEEMDAN-LSTM-CNN-CBAM;
- GRU / Attention-GRU / MA-GRUS;
- Transformer / PatchTST / DPformer;
- LSTM-Transformer.

## 2. Authority

### Foundational LSTM authority
Hochreiter & Schmidhuber (1997), "Long Short-Term Memory", Neural Computation 9(8):1735-1780.
DOI: 10.1162/neco.1997.9.8.1735.

Transfer:
- recurrent memory with input/forget/output gating;
- long-range temporal dependency modeling.

### Gold-specific CNN/LSTM authority
Amini & Kalantari (2024), "Gold price prediction by a CNN-Bi-LSTM model along with automatic parameter tuning", PLOS ONE 19(3):e0298426.
DOI: 10.1371/journal.pone.0298426.

Verified study scope:
- daily closing Gold forecasting;
- compares CNN, LSTM, CNN-LSTM, Conv-LSTM, Stacked LSTM and CNN-Bi-LSTM;
- CNN is used for local feature extraction and recurrent layers for sequence modeling;
- grid search / sensitivity analysis includes lookback, learning rate and mini-batch size;
- CNN-BiLSTM reported as strongest model in that study.

Additional direct Gold evidence:
Li (2024), "Gold Price Prediction Based on CNN-LSTM".
DOI: 10.23977/ferm.2024.070216.
Reports a CNN-LSTM Gold model compared with SVM, LSTM and Ridge.

Recent hybrid evidence:
Lahmiri (2026), "A hybrid CNN-LSTM-GRU system tuned by whale optimization algorithm for enhanced gold and brent price prediction".
DOI: 10.1016/j.finr.2026.100100.
This is authority for later hybrid research only; it does not authorize metaheuristic wrapping in Stage 0.

## 3. Project adaptation and limitations

Published Gold DNN studies commonly use daily closing-price sequences and much larger sample counts than the current monthly H=1 evaluation block.

Therefore:
- published Gold performance numbers are **not directly comparable** with this project's monthly H=1 results;
- no literature result is treated as evidence that LSTM/CNN must outperform ANN, RBFNN, ANFIS, GPR, Boosting or SVR here;
- this project retains its own target, chronology, origin-safe feature contract and DEV authority.

The family is a project-specific monthly adaptation of literature-supported sequence architectures.

## 4. Binding project contract

Target:
- H=1 next-calendar-month average XAU/USD.
- Forecast origin = previous completed month-end.
- Internal target = next-month Gold log return.
- Price reconstruction = previous completed-month Gold average × exp(predicted log return).

Selection authority:
- DEV = 2022-04..2024-12, n=33.
- 2025 = LOCKED one-shot final holdout; not opened before family freeze.
- 2026 = QUARANTINED / reporting only; never tuning or selection.

Data:
- first canonical lane uses the frozen **8 origin-safe VW-MIDAS predictors** already used in prior monthly neural families;
- input to sequence models is a causal monthly sequence ending at the forecast origin;
- no target-month features;
- no global full-sample scaling;
- DB READ_ONLY;
- random split prohibited.

Primary selection metric:
- DEV ΣAE on reconstructed monthly Gold price.

Complementary:
- direction correct / 33;
- MAE, RMSE, MAPE, WAPE;
- relative MAE vs random walk;
- worst month;
- year stability;
- seed dispersion.

## 5. Stage 0 — canonical architecture freeze

Stage 0 is frozen before outcome.

### Common data contract
- input representation: frozen VW-MIDAS CURRENT8 monthly features;
- lookback: **12 completed months**;
- target: standardized next-month Gold log return;
- target sequence ends at origin month;
- training sample only if all 12 historical steps are available;
- train-only feature scaling per forecast origin;
- train-only target scaling per forecast origin;
- chronological inner validation = final 20% of pre-target training sequences, minimum 12 validation rows where feasible;
- no shuffling;
- deterministic seeds = 3 repeats;
- repeat selected only by inner chronological validation MAE;
- final chosen configuration refit once on all pre-target sequences;
- target-month actual never enters fit, scaling, early stopping or repeat selection.

### 0A — LSTM baseline
Architecture:
- one LSTM layer, 32 hidden units;
- tanh recurrent cell / sigmoid gates as framework default;
- dropout = 0.10;
- Dense(1) output.

Training:
- Adam;
- learning rate = 0.001;
- loss = MAE on standardized Gold return;
- batch size = 16;
- max epochs = 300;
- early stopping on chronological validation MAE;
- patience = 25;
- restore best validation weights.

### 0B — 1D CNN baseline
Architecture:
- Conv1D filters = 32;
- kernel size = 3;
- stride = 1;
- activation = ReLU;
- global average pooling;
- Dense(1).

Training contract identical to 0A.

### 0C — CNN-LSTM baseline
Architecture:
- Conv1D filters = 32;
- kernel size = 3;
- stride = 1;
- activation = ReLU;
- no future padding / causal sequence only;
- one LSTM layer, 32 hidden units;
- dropout = 0.10;
- Dense(1).

Training contract identical to 0A.

### Stage-0 implementation gates
All three must pass:
1. train_last < target for every DEV origin;
2. sequence last timestamp = origin, never target;
3. train-only scaling invariance;
4. future-feature perturbation leaves current-origin prediction unchanged;
5. target-label perturbation leaves fitted current-origin model unchanged until scoring;
6. deterministic replay under the same seed;
7. 3/3 seed results present at every origin;
8. finite predictions;
9. no forecast absolute log return >= 1;
10. DB invariants unchanged.

No rescue hyperparameter tuning in Stage 0.

## 6. Stage 1 — controlled sequence / capacity ablation

Only after Stage 0 gate PASS.

Predeclared factors:
- lookback in {3, 6, 12};
- hidden/filter width in {16, 32, 64};
- dropout in {0.00, 0.10, 0.20};
- learning rate in {0.0003, 0.001};
- batch size in {8, 16, 32}.

Rules:
- do not run the Cartesian product blindly;
- use a compact, predeclared ablation design;
- one factor class at a time around the canonical baseline;
- all selection remains nested/prequential within DEV;
- same-DEV full grid minima are diagnostic only if not nested.

Outputs:
- LSTM leader;
- CNN leader;
- CNN-LSTM leader;
- price / direction / stability roles.

## 7. Stage 2 — targeted training refinement

Permitted:
- Adam vs AdamW if implementation authority is frozen before outcome;
- gradient clipping diagnostic;
- one-vs-two recurrent layers;
- recurrent width refinement;
- early-stopping / epoch-budget robustness;
- seed robustness.

Not automatically permitted:
- 32-method metaheuristic screen;
- arbitrary optimizer cross-products;
- external 2025/2026 tuning.

Open any metaheuristic only through a separate pre-outcome amendment after deterministic training evidence.

## 8. Stage 3 — CNN-BiLSTM structural challenger

Authority-backed by Amini & Kalantari (2024).

Run only after Stage 0-2 canonical evidence:
- CNN-BiLSTM with the same origin-safe sequence data;
- compare against the frozen LSTM, CNN and CNN-LSTM leaders;
- BiLSTM may operate only within the **historical input window** ending at the origin;
- it must never consume observations after the forecast origin.

If tested:
- architecture and tuning range frozen before outcomes;
- no use of 2025/2026.

## 9. Stage 4 — controlled ensemble

Pool frozen before ensemble evaluation.

Permitted:
- equal mean;
- median;
- prequential inverse-error weights;
- optional constrained simplex fitted only on prior DEV history;
- shrinkage toward equal weights.

Prohibited:
- arbitrary subset search;
- same-sample optimized weights presented as honest evidence;
- using 2025/2026 to choose pool or weights.

## 10. Stage 5 — robustness

Required:
- year-by-year DEV;
- pairwise monthly AE wins;
- direction rescue/loss;
- worst-month removal;
- leave-one-origin diagnostic;
- seed dispersion;
- architecture sensitivity;
- ensemble component leave-one-out diagnostic;
- failure / numerical pathology audit.

## 11. Stage 6 — family freeze

Freeze:
- price leader;
- direction leader;
- balanced challenger;
- ensemble if earned.

Write exact:
- architecture;
- lookback;
- features;
- scaling;
- optimizer/training settings;
- seeds;
- selection path;
- payload hashes.

No family reopening after seeing 2025 without a new, explicitly separate research identity.

## 12. Stage 7 — 2025 one-shot holdout

Only after Stage 6 freeze.

Report:
- 12 monthly predictions;
- ΣAE;
- direction;
- MAE/RMSE/MAPE/WAPE;
- RW-relative MAE;
- worst month.

2025 cannot change architecture, hyperparameters, ensemble composition or family selection.

## 13. Handoff / immediate next action

Next authorized execution:
**Stage 0A/0B/0C canonical LSTM + CNN + CNN-LSTM technical gate on DEV only.**

Do not start CNN-BiLSTM, ICEEMDAN, GRU or Transformer before the canonical Stage-0 family evidence is recorded.

## Kontrol ve Uyum Özeti

- Foundational LSTM authority: VERIFIED.
- Direct Gold CNN/LSTM authority: VERIFIED.
- Monthly H=1 adaptation: PROJECT-SPECIFIC / clearly separated from published daily results.
- Stage 0 frozen before outcome: YES.
- DEV-only selection: REQUIRED.
- 2025 opened: NO.
- 2026 used for tuning/selection: NO.
- Random split: PROHIBITED.
- DB: READ_ONLY.
- Same frozen monthly target contract: YES.
