# GOLD MONTHLY FORECAST — NEW CHAT HANDOFF / CNN-LSTM START CHECKPOINT

Date: 2026-09-28
Status: **READY TO MOVE FROM PAUSED SVR TO CNN/LSTM STAGE 0**
Branch: `gold-midas-headswap-v1-20260925`

## 1. Project objective and binding contract

Target:
- H=1, next-calendar-month average XAU/USD.
- Forecast origin = previous completed month-end.
- Internal modeling target may be next-month Gold log return; reconstruct price from previous completed-month Gold average.

Selection authority:
- DEV = 2022-04..2024-12, n=33.
- 2025 = locked one-shot/final transport period; must not select or tune models.
- 2026 = quarantined/reporting only; must not select or tune models.

Governance:
- no random split;
- rolling/expanding chronology only;
- no target-month actual/features in fitting, scaling, tuning, decomposition, early stopping or model selection;
- DB READ_ONLY;
- primary selection metric = reconstructed-price DEV SigmaAE;
- direction is complementary principal criterion;
- supporting metrics = MAE, RMSE, MAPE/WAPE, relative MAE vs RW, worst month, yearly stability;
- same-sample optimized ensemble weights are diagnostic only unless a prequential protocol was frozen beforehand.

## 2. Completed / established model families

### ELM
Completed.
Important retained reference:
- AOA-ELM: DEV SigmaAE **1474.1021**, direction **20/33**.

### ANN
Completed and frozen.
Retained ensembles:
- FULL7 ANN: DEV SigmaAE **1428.8590**, direction **22/33**.
- REDUCED4 ANN: DEV SigmaAE **1431.4587**, direction **24/33**.

### ELMFIS
Completed.
Retained family reference:
- SMA-ELMFIS: DEV SigmaAE **1651.4482**, direction **25/33**.

### ANFIS
Completed.
Primary family champion:
- ChHHO-ANFIS: DEV SigmaAE **1413.029779**, direction **23/33**.
- Current strongest point-estimate price reference among the fully documented families in the retained cross-family audit.

### RBFNN
Completed and frozen.
Primary:
- DE-ABC-RBFNN: DEV SigmaAE **1415.8371**, direction **25/33**.
- Strongest documented direction result among the leading price models in the retained cross-family audit.

### GPR
Completed.
Canonical authority and staged development are recorded under:
- `GOLD_MONTHLY_GPR_AUTHORITY_AND_STAGE_PLAN_2026-09-26.md`
- `GOLD_MONTHLY_GPR_EXECUTION_CHECKPOINT_2026-09-26.json`
- `GOLD_MONTHLY_GPR_STAGE3C_AUTHORITY_2026-09-26.md`

Do not rerun completed GPR stages without checking those checkpoints first.

### DMA / DMS / IDMA
Canonical Gold-only family was tested enough to conclude that the current frozen 8-feature information set did not justify further small parameter tweaking.
Recorded checkpoint:
- Canonical DMA 0.99/0.99: DEV SigmaAE **1486.2561**, direction **19/33**.
- Canonical DMS 0.99/0.99: DEV SigmaAE **1489.8247**, direction **20/33**.
- Best 108-month sample-size diagnostic DMS: DEV SigmaAE **1483.8794**, direction **20/33**.

Status:
**DEFERRED_REVISIT_LAST / NOT REJECTED.**
Reopen only as a more literature-faithful replication track with a broader origin-safe predictor panel.

### Boosting
Completed / closed.
Primary price model:
- CATBOOST_PRICE: DEV SigmaAE **1460.4339353**, direction **20/33**.

Balance/direction:
- FULL5_MEDIAN: DEV SigmaAE **1484.7313306**, direction **23/33**.

2025 final holdout after freeze:
- CATBOOST_PRICE: SigmaAE 1020.686135, direction 11/12.
- FULL5_MEDIAN: SigmaAE 993.980271, direction 11/12.

No further Boosting tuning is authorized under the current evidence.

## 3. SVR / DWT-SVR — current paused checkpoint

Authoritative ledger:
`GOLD_MONTHLY_SVR_DWT_FAMILY_LEDGER_2026-09-28.md`

Authority:
`GOLD_MONTHLY_SVR_DWT_AUTHORITY_AND_STAGE_PLAN_2026-09-28.md`

Status:
**PAUSED / HANDOFF TO NEXT MODEL FAMILY.**

### Best verified SVR result
`EPSILON_RBF_DAILY12`
- DEV SigmaAE **1449.187363**
- direction **19/33**
- RBF epsilon-SVR
- DAILY_SUMMARY12 representation
- C=1.0
- epsilon=0.1
- gamma=scale
- train-only standardization

No deterministic tuning, authoritative Stage-4 metaheuristic, or completed Stage-5 refinement beat this SigmaAE.

### Key SVR outcomes
- Stage 1 RBF CURRENT8: **1524.500568 / 21/33**
- Stage 2 DAILY_SUMMARY12 parent: **1449.187363 / 19/33**
- Stage 3A coarse tuning: **1580.901050 / 20/33** — not promoted
- Stage 3B local tuning: **1592.590456 / 22/33** — not promoted
- best authoritative Stage-4 meta = ALO: **1494.808085 / 20/33** — not promoted
- FA technical completion: **1583.810635 / 19/33**, scientific gate PASS, but user-excluded from authoritative Stage-4 ranking because the user had already instructed to leave/stop FA
- Stage 5A.1 Adaptive PSO: **1748.655741 / 16/33** — not promoted
- Stage 5A.2 TLBO-tuned PSO: **1871.806182 / 17/33** — not promoted and worse than RW on relative MAE

### Exact SVR resume point
If/when SVR is reopened:
1. Stage 5A.3 — DE-tuned PSO-SVR
2. Stage 5A.4 — Adaptive / Improved TLBO-SVR
3. Stage 5A.5 — Adaptive Crow Search-SVR
4. Stage 5A.6 — PSO-TLBO Hybrid SVR
5. Stage 5B — conditional hybrids only if evidence warrants
6. Stage 6 — causal DWT/MODWT-SVR
7. Stage 7 — controlled ensemble
8. Stage 8 — robustness
9. Stage 9 — family freeze
10. Stage 10 — 2025 one-shot holdout

At handoff there are **no active SVR GitHub jobs**.

## 4. Next model family — CNN / LSTM

New authority/freeze file:
`GOLD_MONTHLY_CNN_LSTM_AUTHORITY_AND_STAGE_PLAN_2026-09-28.md`

Authority commit:
`c5a9f3ce83e916f634db1e27ac47294a9fd43de3`

Status:
**AUTHORIZED / STAGE 0 FROZEN BEFORE OUTCOME**

Research authority:
- Hochreiter & Schmidhuber (1997), LSTM, DOI 10.1162/neco.1997.9.8.1735.
- Amini & Kalantari (2024), Gold CNN-BiLSTM, PLOS ONE, DOI 10.1371/journal.pone.0298426.
- Li (2024), Gold CNN-LSTM, DOI 10.23977/ferm.2024.070216.
- Lahmiri (2026), CNN-LSTM-GRU-WOA Gold/Brent, DOI 10.1016/j.finr.2026.100100; reserved for later hybrid authority, not Stage 0.

Important adaptation limit:
published Gold DNN studies generally use daily price sequences and much larger sample counts. Their reported errors must **not** be compared directly with this project's monthly H=1 DEV scores.

## 5. CNN/LSTM Stage 0 — exact next execution

Common contract:
- frozen 8 origin-safe VW-MIDAS monthly predictors;
- causal sequence ending at forecast origin;
- lookback = 12 completed months;
- next-month Gold log-return target;
- train-only X/Y scaling;
- no shuffling;
- chronological inner validation = final 20%, minimum 12 validation rows where feasible;
- 3 deterministic seed repeats;
- inner validation MAE selects repeat;
- fit selected configuration on all pre-target sequences;
- Adam lr 0.001;
- batch 16;
- MAE loss;
- max 300 epochs;
- early stopping patience 25;
- restore best validation weights.

### Stage 0A — LSTM
- 1 LSTM layer
- 32 hidden units
- dropout 0.10
- Dense(1)

### Stage 0B — 1D CNN
- Conv1D 32 filters
- kernel 3
- stride 1
- ReLU
- global average pooling
- Dense(1)

### Stage 0C — CNN-LSTM
- Conv1D 32 filters, kernel 3
- ReLU
- LSTM 32
- dropout 0.10
- Dense(1)

Mandatory implementation gates:
- train_last < target
- sequence ends at origin
- future-feature perturbation invariance
- target-label perturbation invariance before scoring
- train-only scaling
- deterministic replay
- 3/3 seed outputs
- finite predictions
- no pathological |predicted log return| >= 1
- DB invariants unchanged

No rescue tuning in Stage 0.

## 6. CNN/LSTM later stages

Stage 1:
- controlled lookback/capacity/training ablations
- lookback {3,6,12}
- widths {16,32,64}
- dropout {0,.1,.2}
- learning rate {.0003,.001}
- batch {8,16,32}
- compact ablation only, not blind Cartesian search

Stage 2:
- targeted deterministic training refinement
- optional AdamW / gradient clipping / depth / seed robustness only if frozen before outcome
- no automatic 32-metaheuristic screen

Stage 3:
- CNN-BiLSTM structural challenger
- same origin-safe historical window only
- bidirectional processing cannot see beyond forecast origin

Stage 4:
- controlled ensemble

Stage 5:
- robustness

Stage 6:
- family freeze

Stage 7:
- 2025 one-shot holdout

## 7. Broader roadmap after CNN/LSTM

Current intended sequence after the canonical CNN/LSTM block:
1. CNN-BiLSTM within the CNN/LSTM family
2. ICEEMDAN-LSTM-CNN-CBAM
3. GRU / Attention-GRU / MA-GRUS
4. Transformer / PatchTST / DPformer
5. LSTM-Transformer
6. DMA/DMS/IDMA literature-replication revisit last

Each new family must receive its own authority / leakage / stage freeze before production execution.

## 8. Immediate instruction for the next chat

First action:
**Run CNN/LSTM Stage 0A, 0B and 0C under the newly frozen authority.**

Execution preference:
- independent models may run as separate parallel GitHub jobs;
- every model must expose its own job status/logs;
- no shell-background `&` batching;
- scientific gate per model;
- do not move to Stage 1 until all Stage-0 artifacts are audited.

After completion report:
- LSTM SigmaAE / direction
- CNN SigmaAE / direction
- CNN-LSTM SigmaAE / direction
- yearly blocks
- RW-relative MAE
- worst month
- seed dispersion
- scientific-gate result
- direct comparison against ChHHO-ANFIS, DE-ABC-RBFNN, ANN ensembles, Boosting and SVR parent using DEV only.

## 9. Kontrol ve Uyum Özeti

- Current target contract preserved: PASS.
- DEV-only selection: PASS / binding.
- 2025 locked for new CNN/LSTM family: YES.
- 2026 excluded from tuning/selection: YES.
- Random split: NONE.
- DB writes: NONE / READ_ONLY.
- SVR active jobs at handoff: NONE.
- SVR exact resume point recorded: YES.
- CNN/LSTM authority frozen before outcome: YES.
- Next executable stage unambiguous: **Stage 0A/0B/0C**.
