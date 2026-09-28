# GOLD MONTHLY FORECAST — BOOSTING FAMILY LEDGER / FINAL MANIFEST

Date originally opened: 2026-09-27  
Final consolidation date: 2026-09-28  
Status: **COMPLETE / FAMILY CLOSED**  
Branch: `gold-midas-headswap-v1-20260925`

> Supersession note: the prior version of this ledger ended while Stage 6C and ensemble work were still open. That status is superseded. This document is the current Boosting-family research memory and closure record.

## 1. Frozen project contract

- Objective: H=1 next-calendar-month average XAU/USD price.
- Forecast origin: previous completed calendar month-end.
- Development/selection authority: DEV 2022-04..2024-12, n=33.
- Primary DEV selection metric: cumulative absolute reconstructed-price error, SigmaAE.
- Direction accuracy is the principal complementary criterion.
- No random split.
- Chronological / expanding-origin information discipline.
- Target-month actual unavailable to model fitting / feature construction.
- DB READ_ONLY; authority invariants checked.
- 2025 role: final locked one-shot holdout, opened only after final Boosting architecture freeze.
- 2026 role: retrospective stress/reporting only; never selection/tuning authority.

## 2. Data / representation contract

The canonical Boosting price forecast is produced by predicting next-month Gold log return and reconstructing price from the previous completed-month Gold average.

Frozen principal representation for the final PRICE model:
- CURRENT8
- governed monthly VW-MIDAS-style origin-safe feature contract
- Gold/Silver/Platinum/Palladium information available at the forecast origin
- next-month Gold log-return target
- reconstructed price = previous completed-month Gold average * exp(predicted log return)

Other frozen lane representations explored and retained for audit:
- GBRT: DAILY_SUMMARY12
- XGBoost price lane: RAW_LEVEL_LAGS8
- XGBoost direction lane: CURRENT8
- LightGBM: MIXED20
- RF comparator: DAILY_SUMMARY12

## 3. Stage ledger

### Stage 0 — Authority / protocol freeze
**COMPLETE.**

Governance, chronology, target, DEV scope, metrics, random-split prohibition and DB read-only rules frozen before model development.

### Stage 1 — Canonical baselines
**COMPLETE.**

Initial canonical baseline screen:
- CatBoost Ordered CURRENT8: SigmaAE 1460.4339353 / 20 of 33 directions.
- RF anchor: initial canonical screen retained as historical comparator.
- XGBoost, GBRT and LightGBM canonical baselines were subsequently refined through representation/target/capacity stages.

CatBoost already established the strongest canonical price anchor and remained the final family price leader after all later stages.

### Stage 2 — Feature-representation ablation
**COMPLETE.**

Promoted representations:
- CatBoost -> CURRENT8
- GBRT -> DAILY_SUMMARY12
- XGBoost -> RAW_LEVEL_LAGS8 price lane; CURRENT8 direction lane
- LightGBM -> MIXED20
- RF comparator -> DAILY_SUMMARY12

### Stage 3 — Target / loss ablation
**COMPLETE.**

- LOGRET -> price reconstruction retained.
- DIRECT_PRICE closed.
- CatBoost -> RMSE.
- GBRT -> absolute_error.
- XGBoost -> squared-error variants.
- LightGBM -> L1.

### Stage 4 — Capacity scan
**COMPLETE.**

Key frozen frontier after capacity work:
- CatBoost PRICE: 1460.4339353 / 20/33
- GBRT: 1500.4294686 / 22/33
- LightGBM: 1534.6087211 / 22/33
- XGBoost lanes weaker on primary price error but direction lane retained for complementarity.

### Stage 5 — Regularization / subsampling
**COMPLETE.**

Frozen components later used in ensemble work:

| Component | Frozen identity | DEV SigmaAE | Direction |
|---|---|---:|---:|
| CATBOOST_PRICE | CB_R0_BASELINE / CURRENT8 | **1460.4339353** | 20/33 |
| CATBOOST_BALANCED | CB_R0_BASELINE | 1481.2619377 | 22/33 |
| GBRT | G_R0_BASELINE / DAILY_SUMMARY12 | 1500.4294686 | 22/33 |
| LIGHTGBM | L_R0_BASELINE / MIXED20 | 1534.6087211 | 22/33 |
| XGB_DIRECTION | X_R1_L2_5 / CURRENT8 | 1679.8371518 | 23/33 |
| RF comparator | comparator only | 1491.5506937 | 20/33 |

RF remained a comparator and was not admitted to the final Boosting ensemble pool.

## 4. Stage 6A — Broad CatBoost metaheuristic screen

**COMPLETE.**

- Vanilla + 33 optimizer methods screened.
- PSO strongest primary inner-validation leader.
- DE_ABC strongest 6-anchor outer diagnostic.
- MFO also strong on inner validation.
- Six finalists advanced to full DEV: Vanilla, PSO, MFO, DE_ABC, HHO, TLBO.

Broad-screen results were screening evidence only, not final DEV selection evidence.

## 5. Stage 6B — Full DEV CatBoost finalists

**COMPLETE.**

| Candidate | DEV SigmaAE | Direction | Decision |
|---|---:|---:|---|
| Vanilla CatBoost | **1460.4339** | 20/33 | RETAINED |
| DE_ABC | 1594.2708 | 21/33 | NOT PROMOTED |
| PSO | 1612.0424 | 18/33 | NOT PROMOTED |
| MFO | 1649.1963 | 18/33 | NOT PROMOTED |
| HHO | 1673.8990 | 19/33 | NOT PROMOTED |
| TLBO | 1714.3877 | 16/33 | NOT PROMOTED |

Decision:
- CatBoost metaheuristic tuning did not improve the frozen Vanilla price frontier.
- Vanilla CatBoost remained the family PRICE center.

## 6. Stage 6C — Boosting-specific literature / structural challengers

### 6C-A — CMA-ES–GBRT
**COMPLETE / NOT PROMOTED.**

Authority:
- Suan et al. (2026), Emerging Science Journal, DOI 10.28991/ESJ-2026-010-03-016.

Results:
- frozen GBRT: 1500.4294686 / 22/33
- CMA-ES–GBRT: 1650.1984961 / 18/33

Finding:
- inner validation improved in most origins, but outer chronological DEV transport deteriorated.

Decision:
- NOT PROMOTED.
- Same CMA-ES search under the frozen lane should not be repeated without a genuinely new scientific hypothesis.

### 6C-B — TPE / Optuna–GBRT
**COMPLETE / NOT PROMOTED.**

Authority:
- same gold-forecasting hyperparameter-optimization line used for the CMA-ES control.

Protocol:
- DAILY_SUMMARY12
- next-month Gold log return
- GBRT absolute_error
- nested chronological last-12-month inner validation
- Optuna TPESampler
- 80 trials/origin, 2640 total

Results:
- GBRT baseline: **1500.4294686 / 22/33**
- TPE/Optuna–GBRT: **1576.9728631 / 18/33**

Finding:
- inner validation improved in 31/33 origins;
- outer DEV still degraded.

Decision:
- scientifically valid, NOT PROMOTED.
- run 36348652770, job 108702856918.

### 6C-C — causal CEEMDAN–XGBoost
**COMPLETE / NOT PROMOTED.**

Authority:
- Xin Xie (2025), CEEMDAN-XGBoost gold prediction.
- PyEMD / EMD-signal causal moving-front implementation.

Leakage control:
- every historical feature created from its own prefix ending at t-1;
- no global full-series decomposition;
- four IMF endpoint slots;
- frozen Stage-5 XGBoost learner;
- no CEEMDAN or XGBoost tuning.

Results:
- frozen XGBoost CURRENT8 comparator: **1583.8534959 / 20/33**
- causal CEEMDAN-XGBoost: **1820.4745553 / 17/33**
- relative MAE vs RW: 1.03554

Decision:
- NOT PROMOTED.
- causal adaptation did not reproduce the source-paper-style gain under this monthly H=1 contract.
- run 36382346934, job 108800529082.

### 6C-D authority review
**COMPLETE.**

Planned gated sequence:
- D0 causal VMD-XGB
- only if D0 promising: D1 VMD + residual CEEMDAN
- only if D1 successful: D2 WOA optimization

### 6C-D0 — causal VMD–XGBoost
**COMPLETE / NOT PROMOTED.**

Authority:
- Guo et al. (2025), Computational Economics.
- Dragomiretskiy & Zosso (2014), VMD.
- vmdpy 0.2.

Frozen VMD:
- alpha=2000
- tau=0
- K=3
- DC=0
- init=1
- tol=1e-7

Results:
- frozen XGBoost comparator: **1583.8534959 / 20/33**
- causal VMD-XGBoost: **2019.0623882 / 15/33**
- relative MAE vs RW: 1.14850

Pre-outcome D1 gates both failed.

Decision:
- D0 NOT PROMOTED.
- D1 VMD + residual CEEMDAN = **CLOSED_NOT_OPENED**.
- D2 WOA = **NOT AUTHORIZED**.
- decomposition structural branch CLOSED.
- run 36383935285, job 108805248611.

## 7. Ensemble complementarity and E1 baseline ensembles

**COMPLETE.**

Frozen before outcome:

FULL5:
1. CATBOOST_PRICE
2. CATBOOST_BALANCED
3. GBRT
4. LIGHTGBM
5. XGB_DIRECTION

REDUCED4:
1. CATBOOST_PRICE
2. GBRT
3. LIGHTGBM
4. XGB_DIRECTION

No arbitrary subset search.

E1 results:

| Rank | Pool | Variant | DEV SigmaAE | Direction |
|---:|---|---|---:|---:|
| 1 | FULL5 | MEDIAN | **1484.7313306** | **23/33** |
| 2 | REDUCED4 | MEDIAN | 1490.6522620 | 22/33 |
| 3 | FULL5 | Equal mean | 1503.4581154 | 21/33 |
| 4 | FULL5 | Prequential inverse-MAE | 1503.7173745 | 21/33 |
| 5 | REDUCED4 | Equal mean | 1512.8638608 | 20/33 |
| 6 | REDUCED4 | Prequential inverse-MAE | 1513.3072989 | 20/33 |

Interpretation:
- FULL5 Median does not beat CATBOOST_PRICE on SigmaAE.
- It gains +3 correct directions versus CATBOOST_PRICE.
- It becomes the BALANCE / DIRECTION challenger.

Provenance:
- run 36384759464
- job 108807711065
- E1 scientific gate PASS

## 8. E2 — constrained simplex

**COMPLETE / RAW SIMPLEX NOT PROMOTED.**

Constraints:
- nonnegative weights
- weights sum to 1
- no intercept
- exact LP via scipy.optimize.linprog(method="highs")
- first 6 DEV origins equal-weight fallback
- later weights fit on strictly prior DEV origins only

Honest expanding-prequential results:

| Pool | E2 SigmaAE | Direction | Frozen E1 median |
|---|---:|---:|---:|
| FULL5 | 1532.4585226 | 19/33 | 1484.7313306 / 23 |
| REDUCED4 | 1524.2579549 | 18/33 | 1490.6522620 / 22 |

Same-sample full-DEV optimum:
- CATBOOST_PRICE 85.3928%
- GBRT 14.6072%
- others 0%
- diagnostic SigmaAE 1458.3766698

This same-sample value is **DIAGNOSTIC ONLY**, not selection evidence.

Decision:
- raw simplex NOT PROMOTED.
- run 36385723320
- job 108810569825
- scientific gate PASS.

## 9. E3 — controlled shrinkage

**COMPLETE / LEARNED-WEIGHT LINE CLOSED.**

Frozen alpha grid:
- 0.00
- 0.10
- 0.25
- 0.50
- 0.75
- 1.00

Shrinkage:
- w_alpha(t) = (1-alpha) * equal + alpha * prior-only simplex(t)
- E1 median retained as separate comparator.

Best learned candidates:
- FULL5 alpha 0.10: **1506.358156 / 21/33**
- REDUCED4 alpha 0.10: **1514.003270 / 20/33**

Neither beats its frozen E1 median.

Decision:
- learned shrinkage NOT PROMOTED.
- learned-weight ensemble optimization CLOSED.
- run 36388959039
- scientific gate PASS.

## 10. E4 — final robustness

**COMPLETE / SCIENTIFIC GATE PASS.**

Principal frozen candidates:

| Role | Candidate | DEV SigmaAE | Direction |
|---|---|---:|---:|
| PRICE | CATBOOST_PRICE | **1460.4339353** | 20/33 |
| BALANCE / DIRECTION | FULL5_MEDIAN | 1484.7313306 | **23/33** |

Year blocks:

CATBOOST_PRICE:
- 2022 Apr-Dec: 381.562198 / 7 of 9
- 2023: 419.833524 / 6 of 12
- 2024: 659.038214 / 7 of 12

FULL5_MEDIAN:
- 2022 Apr-Dec: 400.891095 / 7 of 9
- 2023: 423.484569 / 6 of 12
- 2024: 660.355667 / 10 of 12

Pairwise monthly AE:
- CATBOOST_PRICE wins 14
- FULL5_MEDIAN wins 7
- ties 12

Direction relation:
- Median rescues 3 CatBoost misses
- Median losses 0 CatBoost hits
- both correct 20
- both wrong 10

Common leave-one-origin aggregate SigmaAE:
- CATBOOST_PRICE preferred in **33/33** omissions
- FULL5_MEDIAN preferred in 0/33

Leave-one-component-out median tests were diagnostic only and were not used to redesign the pool.

Decision:
- E4 PASS.
- roles proceed unchanged to final freeze.
- run 36389540195.

## 11. E5 — final architecture freeze

**COMPLETE.**

Frozen before 2025 holdout.

### Final PRICE role
**CATBOOST_PRICE**

Identity:
- lane CATBOOST_PRICE
- profile CB_R0_BASELINE
- representation CURRENT8
- target next-month Gold log-return
- CatBoost Ordered
- iterations 100
- depth 6
- learning_rate 0.03
- l2_leaf_reg 3
- random_strength 1
- seed 1701

DEV:
- SigmaAE 1460.4339353
- MAE 44.255574
- RMSE ~57.8094
- direction 20/33
- relative MAE vs RW ~0.830736

### Final BALANCE / DIRECTION role
**FULL5_MEDIAN**

Combination:
- row-wise median of the five frozen component reconstructed-price forecasts
- no learned weights
- no subset search
- no post-hoc component deletion

DEV:
- SigmaAE 1484.7313306
- MAE 44.991859
- direction 23/33
- relative MAE vs RW ~0.84456

Freeze commit:
- `0baec13a4fd2f28e181513400b3b1aa7bbaaa477`

After E5, 2025 was allowed to open once. No model/feature/weight/role could change based on holdout performance.

## 12. E6 — 2025 final one-shot holdout

**COMPLETE / SCIENTIFIC GATE PASS / FAMILY CLOSED.**

2025 was evaluated once under the frozen E5 identities.

| Role | 2025 SigmaAE | MAE | RMSE | Rel.MAE vs RW | Direction | Worst month |
|---|---:|---:|---:|---:|---:|---|
| CATBOOST_PRICE | 1020.686135 | 85.057178 | 116.133793 | 0.605030 | **11/12** | 2025-10 |
| FULL5_MEDIAN | **993.980271** | **82.831689** | **111.625270** | **0.589200** | **11/12** | 2025-10 |

Interpretation:
- FULL5 Median transported with lower 2025 price error than CatBoost PRICE.
- Both achieved 11/12 direction.
- This does **not** retroactively replace or retune the frozen E5 role definitions.
- 2025 is transport evidence only after architecture freeze.

Provenance:
- run 36390663634
- workflow success
- E6 scientific gate PASS
- final holdout report committed to branch
- payload SHA256 34193a4d696542e2ec57dbef82ed683b9222eacf28baa630f9c1be763738e5c1

## 13. 2026 retrospective stress — CATBOOST_PRICE only

The CatBoost PRICE identity was frozen before this stress run.

2026 role:
- RETROSPECTIVE_STRESS_REPORT_ONLY
- no model selection, tuning, pool design, shrinkage, rescue or reopening authority

Available authoritative monthly actuals at the stress-run time: Jan-Jul 2026.

| Month | Actual | Forecast | AE | Direction correct |
|---|---:|---:|---:|---|
| 2026-01 | 4753.00 | 4315.733590 | 437.266410 | YES |
| 2026-02 | 5020.00 | 4874.453097 | 145.546903 | YES |
| 2026-03 | 4856.00 | 5165.833177 | 309.833177 | NO |
| 2026-04 | 4721.00 | 4806.593140 | 85.593140 | YES |
| 2026-05 | 4587.00 | 4699.931201 | 112.931201 | YES |
| 2026-06 | 4228.00 | 4584.321488 | 356.321488 | YES |
| 2026-07 | 4073.00 | 4207.290079 | 134.290079 | YES |

Aggregate:
- n=7
- SigmaAE **1581.7823984**
- MAE 225.9689141
- RMSE 260.0716609
- MAPE 4.92562%
- relative MAE vs RW 0.9540304
- direction **6/7 = 85.71%**

Provenance:
- run 36343917345
- job 108689194910
- scientific gate PASS
- artifact 10939947745
- payload SHA256 6f6c4ba1bbc3840f416ba8214a7b49c4d91be1abfa2208fb4baada2e4901200e

Important:
- a comparable frozen FULL5_MEDIAN 2026 Jan-Jul stress series has **not** been established in the current Boosting record.
- therefore do not invent or infer a 2026 FULL5 result from the CatBoost series.
- status for FULL5_MEDIAN 2026 Jan-Jul within this family record: **NOT_RUN / NOT_PROVEN**.

## 14. Final family decision

### PRICE
**CATBOOST_PRICE**

Reason:
- lowest honest DEV SigmaAE among completed Boosting candidates;
- survives all 33 common leave-one-origin removals against FULL5 Median;
- all CatBoost metaheuristic, GBRT optimizer and decomposition challengers failed to improve its DEV price frontier.

### BALANCE / DIRECTION
**FULL5_MEDIAN**

Reason:
- +3 DEV direction rescues and 0 direction losses relative to CatBoost PRICE;
- 23/33 DEV direction;
- strong 2025 one-shot transport: 993.98 SigmaAE and 11/12 direction.

### Closed lines
Do not reopen under the current evidence set without a genuinely new hypothesis / new untouched validation authority:
- CatBoost broad metaheuristic tuning
- PSO/MFO/DE_ABC/HHO/TLBO finalist search
- CMA-ES–GBRT
- TPE/Optuna–GBRT
- causal CEEMDAN–XGBoost
- causal VMD–XGBoost
- residual CEEMDAN continuation
- WOA continuation
- E2 simplex
- E3 shrinkage
- arbitrary ensemble subset search
- learned stacking/meta-learner
- post-hoc 2025/2026 model switching

## 15. Family status and roadmap

Boosting family development: **COMPLETE / CLOSED**.

All planned Boosting model-development stages, structural challengers, controlled ensemble stages, robustness, final freeze and one-shot 2025 holdout are complete.

Next planned family in the governed monthly roadmap:
- **SVR / DWT-SVR**

Global cross-family ranking is **not** rewritten inside this family manifest. Existing cross-family audit files are historical snapshots from before Boosting closure. A new cross-family audit should be created only when the intended family set for that audit is ready, rather than silently editing older dated audits.

## 16. Artifact / provenance anchors

Primary evidence files:
- `GOLD_MONTHLY_BOOSTING_STAGE5_REGULARIZATION_REPORT_2026-09-27.md`
- `GOLD_MONTHLY_BOOSTING_STAGE6B_FINALIST_FREEZE_2026-09-27.md`
- `GOLD_MONTHLY_BOOSTING_STAGE6C_A_CMAES_GBRT_RESULT_2026-09-27.md`
- `GOLD_MONTHLY_BOOSTING_STAGE6C_B_TPE_GBRT_RESULT_2026-09-28.md`
- `GOLD_MONTHLY_BOOSTING_STAGE6C_C_CAUSAL_CEEMDAN_XGB_RESULT_2026-09-28.md`
- `GOLD_MONTHLY_BOOSTING_STAGE6C_D0_CAUSAL_VMD_XGB_RESULT_2026-09-28.md`
- `GOLD_MONTHLY_BOOSTING_ENSEMBLE_E1_RESULT_2026-09-28.md`
- `GOLD_MONTHLY_BOOSTING_ENSEMBLE_E2_RESULT_2026-09-28.md`
- `GOLD_MONTHLY_BOOSTING_ENSEMBLE_E3_SHRINKAGE_RESULT_2026-09-28.md`
- `GOLD_MONTHLY_BOOSTING_E4_FINAL_ROBUSTNESS_RESULT_2026-09-28.md`
- `GOLD_MONTHLY_BOOSTING_E5_FINAL_FREEZE_2026-09-28.md`
- `GOLD_MONTHLY_BOOSTING_E6_2025_FINAL_HOLDOUT_RESULT_2026-09-28.md`
- `GOLD_MONTHLY_BOOSTING_CATBOOST_VANILLA_FREEZE_BEFORE_2026_2026-09-27.json`

Key workflow runs:
- 2026 CatBoost stress: 36343917345
- TPE/Optuna–GBRT: 36348652770
- CEEMDAN–XGB: 36382346934
- VMD–XGB: 36383935285
- E1 ensemble: 36384759464
- E2 simplex: 36385723320
- E3 shrinkage: 36388959039
- E4 robustness: 36389540195
- E6 2025 holdout: 36390663634

## 17. Kontrol ve Uyum Özeti

- Family ledger updated through final closure: **PASS**.
- Final status COMPLETE/CLOSED: **PASS**.
- Stage 6C-B/C/D results recorded: **PASS**.
- E1/E2/E3 ensemble results recorded: **PASS**.
- E4 robustness recorded: **PASS**.
- E5 freeze recorded: **PASS**.
- E6 one-shot 2025 holdout recorded: **PASS**.
- 2026 CatBoost stress explicitly quarantined from selection: **PASS**.
- 2026 FULL5 result not invented: **PASS / NOT_RUN-NOT_PROVEN**.
- Random split: NONE.
- DEV selection authority: 2022-04..2024-12 only.
- Target-period leakage: NONE under recorded scientific gates.
- DB writes: NONE / READ_ONLY.
- Post-holdout tuning/reselection: PROHIBITED / NONE.
- Learned weights: CLOSED.
- Structural decomposition branch: CLOSED.
- Boosting family: **CLOSED**.
