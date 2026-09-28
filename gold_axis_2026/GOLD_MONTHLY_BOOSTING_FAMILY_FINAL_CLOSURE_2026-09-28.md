# GOLD MONTHLY FORECAST — BOOSTING FAMILY FINAL CLOSURE

Date: 2026-09-28  
Status: **COMPLETE / CLOSED**  
Branch: `gold-midas-headswap-v1-20260925`

Canonical detailed family memory:
- `GOLD_MONTHLY_BOOSTING_FAMILY_LEDGER_2026-09-27.md`
- finalized through E6 by commit `6eb71dc469c878030f656443857026e7ba65a62c`

## 1. Frozen authority
- H=1 next-calendar-month average XAU/USD.
- Origin: previous completed month-end.
- DEV selection/tuning authority: 2022-04..2024-12, n=33.
- Primary metric: DEV price SigmaAE.
- Direction: complementary principal criterion.
- 2025: one-shot final holdout after final architecture freeze.
- 2026: retrospective stress/reporting only.
- Random split: NONE.
- Target-month leakage: NONE under recorded gates.
- DB: READ_ONLY.

## 2. Final Boosting roles

### PRICE — CATBOOST_PRICE
Frozen identity:
- CURRENT8
- next-month Gold log return
- CatBoost Ordered
- iterations 100
- depth 6
- learning_rate 0.03
- l2_leaf_reg 3
- random_strength 1
- seed 1701

DEV:
- SigmaAE **1460.4339353**
- MAE 44.255574
- direction **20/33**
- relative MAE vs RW ~0.830736

### BALANCE / DIRECTION — FULL5_MEDIAN
Components:
- CATBOOST_PRICE
- CATBOOST_BALANCED
- GBRT
- LIGHTGBM
- XGB_DIRECTION

Rule:
- row-wise median
- no learned weights
- no subset search
- no post-hoc component deletion

DEV:
- SigmaAE **1484.7313306**
- MAE 44.991859
- direction **23/33**

Direction relation vs CATBOOST_PRICE:
- rescues 3
- losses 0
- both correct 20
- both wrong 10

## 3. Completed challenger lines

### CatBoost metaheuristics
Full DEV finalists:
- Vanilla 1460.4339 / 20
- DE_ABC 1594.2708 / 21
- PSO 1612.0424 / 18
- MFO 1649.1963 / 18
- HHO 1673.8990 / 19
- TLBO 1714.3877 / 16

No metaheuristic finalist beat Vanilla.

### GBRT optimization
- CMA-ES–GBRT: 1650.1985 / 18 — NOT PROMOTED.
- TPE/Optuna–GBRT: 1576.9729 / 18 — NOT PROMOTED.
- frozen GBRT comparator: 1500.4295 / 22.

### Structural decomposition challengers
- causal CEEMDAN–XGB: 1820.4746 / 17 — NOT PROMOTED.
- causal VMD–XGB: 2019.0624 / 15 — NOT PROMOTED.
- residual CEEMDAN continuation: CLOSED_NOT_OPENED.
- WOA continuation: NOT AUTHORIZED.

## 4. Ensemble closure

E1:
- FULL5 Median: **1484.7313 / 23**
- REDUCED4 Median: 1490.6523 / 22
- equal and inverse-MAE variants weaker.

E2 expanding-prequential constrained simplex:
- FULL5: 1532.4585 / 19
- REDUCED4: 1524.2580 / 18
- NOT PROMOTED.
- full-DEV same-sample optimum 1458.3767 is DIAGNOSTIC ONLY.

E3 controlled shrinkage:
- best learned FULL5 alpha 0.10: 1506.3582 / 21
- best learned REDUCED4 alpha 0.10: 1514.0033 / 20
- neither beats the frozen medians.
- learned-weight line CLOSED.

## 5. Final robustness
E4:
- CATBOOST_PRICE monthly AE wins vs FULL5 Median: 14
- FULL5 Median wins: 7
- ties: 12
- CATBOOST_PRICE preferred in **33/33** common leave-one-origin aggregate comparisons.
- robustness did not trigger post-hoc reselection.

## 6. 2025 one-shot final holdout
E5 froze architecture before 2025.

E6:

| Role | 2025 SigmaAE | MAE | RMSE | Direction |
|---|---:|---:|---:|---:|
| CATBOOST_PRICE | 1020.686135 | 85.057178 | 116.133793 | **11/12** |
| FULL5_MEDIAN | **993.980271** | **82.831689** | **111.625270** | **11/12** |

2025 is final transport evidence only and did not change the frozen roles.

## 7. 2026 retrospective stress
Only the frozen CATBOOST_PRICE 2026 Jan-Jul stress series is established in the current Boosting record.

Aggregate:
- SigmaAE **1581.7823984**
- MAE 225.9689141
- RMSE 260.0716609
- relative MAE vs RW 0.9540304
- direction **6/7**

Monthly:
- Jan actual 4753 / forecast 4315.7336
- Feb 5020 / 4874.4531
- Mar 4856 / 5165.8332
- Apr 4721 / 4806.5931
- May 4587 / 4699.9312
- Jun 4228 / 4584.3215
- Jul 4073 / 4207.2901

FULL5_MEDIAN 2026 Jan-Jul in this family record:
- **NOT_RUN / NOT_PROVEN**

## 8. Closed research directions
Under the current evidence set, do not reopen without a new scientific rationale or new untouched validation authority:
- additional CatBoost metaheuristic enumeration
- same CMA-ES/TPE GBRT search
- causal CEEMDAN/VMD branch
- residual decomposition continuation
- WOA continuation
- arbitrary ensemble subsets
- simplex/shrinkage retuning
- learned stacking/meta-learner
- post-hoc 2025/2026 model switching

## 9. Provenance
Key runs:
- 2026 CatBoost stress: 36343917345
- TPE/Optuna–GBRT: 36348652770
- CEEMDAN–XGB: 36382346934
- VMD–XGB: 36383935285
- E1 ensemble: 36384759464
- E2 simplex: 36385723320
- E3 shrinkage: 36388959039
- E4 robustness: 36389540195
- E6 holdout: 36390663634

Final architecture freeze commit:
- `0baec13a4fd2f28e181513400b3b1aa7bbaaa477`

Final family-manifest consolidation commit:
- `6eb71dc469c878030f656443857026e7ba65a62c`

## 10. Family decision
- PRICE = **CATBOOST_PRICE**
- BALANCE / DIRECTION = **FULL5_MEDIAN**
- Boosting family = **COMPLETE / CLOSED**
- next planned family = **SVR / DWT-SVR**

Existing older cross-family audit documents remain historical snapshots and are not silently rewritten. A new cross-family audit should be generated when the intended next set of families is ready.

## Kontrol ve Uyum Özeti
- Other-family final-closure structure checked: PASS.
- Detailed Boosting manifest updated through E6: PASS.
- Final closure artifact created: PASS.
- All major tried methods + outcomes + decisions recorded: PASS.
- Final model identities/configurations recorded: PASS.
- DEV robustness recorded: PASS.
- 2025 one-shot holdout recorded: PASS.
- 2026 CatBoost stress recorded and quarantined: PASS.
- Missing 2026 FULL5 series labeled NOT_RUN / NOT_PROVEN: PASS.
- Random split: NONE.
- DB writes: NONE.
- Post-holdout tuning/reselection: NONE.
