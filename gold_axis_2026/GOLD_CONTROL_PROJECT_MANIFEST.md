# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.82  
**Issue date:** 2026-09-21  
**Repository:** `ataullahturgut/sim3-automation`  
**Canonical branch:** `gold-r4-direction-engine`  
**Current research branch:** `gold-direction-vlmc-bs-family-v2-20260918`  
**Project root:** `gold_axis_2026/`

---

## 1. Sole authority

This file is the **only current Gold Control project manifest**.

`gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md` is the sole project-level authority for Gold Control architecture, model roles, data chronology, validation governance, research sequencing, frozen challenge definitions and promotion rules.

Contracts, preregistrations, design notes, checkpoints, reports, event inventories, run artifacts, historical handovers and audit outputs are subordinate to this manifest. If a subordinate artifact conflicts with this manifest, the current manifest wins once the corresponding manifest change is accepted on the governed branch.

Authority split:

- **GitHub:** current code, frozen model/feature/source contracts, reproducibility and this manifest.
- **Production Neon:** mutable source observations, point-in-time lineage, append-only runtime/context state and legitimately issued forecast/decision records.

Historical implementation detail may remain in Git history or immutable audit storage, but historical model scores do not define current project authority.

Gold Control is a **decision-support and research system, not an autonomous trading system**.

---

## 2. Current top-level architecture

Gold Control has **two parallel primary lines**. They may exchange role-preserving context but they are not one homogeneous model-selection pool.

### 2.1 Monthly H=1 price-level forecasting — ACTIVE AND INDEPENDENT

The monthly programme forecasts the next calendar month's XAU/USD price level from the previous completed month-end information boundary.

Current monthly H=1 expert identities:

- `CAUSAL_PATCH`
- `VW_MIDAS_MSVR_SUCCESSOR_V1`
- `MOMENTUM_3M`
- `RANDOM_WALK`

`MONTHLY_DIRECTION_3M` remains a strategic monthly direction/prior context.

The monthly H=1 line remains a standalone forecast output regardless of GC-BREAK research progress.

### 2.2 Short-term GC-BREAK — SEQUENTIAL TREND-HEALTH / BREAK EARLY WARNING

The current short-term problem is **not fixed-horizon 1D/3D direction prediction**.

Binding state ontology:

`STABLE -> WEAKENING -> BREAK_ALERT -> CONFIRMED_BREAK -> NEW_REGIME`

Recovery transitions are permitted, including `WEAKENING -> STABLE`, `BREAK_ALERT -> STABLE` or a lower warning state, and later stabilization of a new regime.

Primary short-term questions are warning lead time, false-warning burden, missed breaks, confirmation delay, regime stabilization and recovery behavior.

`NEXT_NY17_1D`, `NEXT_NY17_3D`, standalone 1D/3D directional accuracy and fixed-horizon break-risk are historical research targets only and may not silently re-enter the architecture.

---

## 3. Governed runtime registry versus current research activity

The governed runtime registry contains exactly **11 identities**. Runtime registration does **not** mean every identity is currently active in the GC-BREAK research sequence.

### 3.1 Governed runtime registry

1. `CAUSAL_PATCH`
2. `VW_MIDAS_MSVR_SUCCESSOR_V1`
3. `MOMENTUM_3M`
4. `RANDOM_WALK`
5. `MONTHLY_DIRECTION_3M`
6. `FAST`
7. `SLOW`
8. `MACRO_EVENT_SUCCESSOR_V2`
9. `EMERGENCY_LEVEL`
10. `EMERGENCY_REVERSAL`
11. `GVZ_RISK`

No additional research channel becomes a governed runtime identity without explicit promotion and manifest change control.

### 3.2 Current GC-BREAK research activity status

The current research-status layer is binding for work sequencing and must not be confused with the runtime registry above.

| Identity / lane | Current research status | Binding interpretation |
|---|---|---|
| `FAST` | `EVALUATED / RETAINED_TACTICAL_CONTEXT` | 2025 full-timeline replay complete; not proven standalone volatility-warning engine |
| `GVZ_RISK` | `EVALUATED / RETAINED_RISK_CONTEXT` | 2025 full-timeline historical replay complete; risk/severity only, no direction vote |
| `BOCPD` research lane | `EVALUATED / RETAINED_RESEARCH_REFERENCE` | only V5 + R2 remain authoritative; BOCPD is retained as regime/change context, not as the next standalone future-change-time predictor |
| RSM / ERSM family | `TERMINATED / FAILED_METHOD_FAMILY / DO_NOT_REVISIT` | closed by explicit user decision on 2026-09-18; historical artifacts are audit-only and the family must not re-enter research sequencing unless the user explicitly reverses the closure. |
| `DIRECTION_VLMC_BS_V1_RESEARCH` | `AUDIT_ONLY / SUPERSEDED_FOR_FAMILY_SCOPE` | original custom-Python rolling-52 experiment is retained only for lineage; corrected V2 uses source weekly-return construction and pinned R VLMC reference semantics. |
| `DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH` | `EVALUATED / NO_PROMOTION / SOURCE_FAITHFUL_REFERENCE_REPLICATION_COMPLETE / 2025_GENERALIZATION_WEAK / FAMILY_CLOSED_CURRENT_SEQUENCE` | rolling 26/52/104 reference-family replay complete; k=52 validated strongly in 2024 but failed to generalize in 2025, while k=104 was more balanced in 2025 but had weaker pre-2025 evidence. Subsequent Fixed-Share, COVLMC-X3 and VLMC-C 104 successors did not rescue stable direction discrimination; the VLMC family is closed for the current direction-research sequence unless explicitly reopened by the user. |
| `DIRECTION_VLMC_BS_FIXED_SHARE_V1_RESEARCH` | `REJECTED / NO_PROMOTION / 2025_GENERALIZATION_FAILED` | literature-grounded adaptive expert weighting of VLMC-26/52 improved 2023-2024 but collapsed in locked 2025; do not rescue by retuning this same grid against 2025. |
| `DIRECTION_COVLMC_X3_V1_RESEARCH` | `EVALUATED / NO_PROMOTION / PRE2025_COLLAPSE_TO_NEUTRAL / NOT_RUNTIME` | direct VLMCX exogenous-covariate successor using rolling 104-week Gold signs plus PIT DGS10, USD/CNY and GPR; 2024 produced P(UP)=0.5 at all 44 origins and 44/44 UP forecasts, and unchanged 2025 replay produced 52/52 UP; do not rescue by post-result parameter tuning. |
| `DIRECTION_VLMC_C_104_V1_RESEARCH` | `EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED / 2025_COLLAPSE_TO_ALWAYS_UP / NOT_RUNTIME` | governed run 35453387137 completed after a comparison-only column-reference bug fix that did not change model semantics. On identical 2024 support, balanced accuracy fell to 0.4417 versus parent VLMC-BS-104 at 0.5583 and DOWN sensitivity fell to 0.05 versus 0.45. Unchanged 2025 replay forecast 52/52 UP, balanced accuracy 0.50 and DOWN sensitivity 0. |
| `DIRECTION_BCT_CTW_V1_RESEARCH` | `EVALUATED / NO_PROMOTION / WEAK_DIRECTIONAL_DISCRIMINATION` | exact BCT/CTW-52 replay complete through 2025; probability quality improved materially versus VLMC-BS but 2025 produced 52/52 UP forecasts, balanced accuracy 50%, and 0/5 DOWN volatility-event agreement |
| `DIRECTION_BCTX_AR_V1_RESEARCH` | `EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED / BCT_FAMILY_CLOSED_CURRENT_SEQUENCE / NOT_RUNTIME` | frozen BCT-X/AR successor selected p=1 and ternary thresholds only by 2022-2023 GCTW evidence. 2024 accuracy 0.5660 and balanced accuracy 0.5584 beat trivial raw baselines, but DOWN sensitivity was only 0.1538 so the preregistered gate failed. Unchanged 2025 replay fell to balanced accuracy 0.4865 with DOWN sensitivity 0 and 51/52 UP forecasts. |
| `DIRECTION_BCARS_V1_RESEARCH` | `BLOCKED_PRE2025_BOUNDARY_SUPPORT / NOT_SCORED / NOT_RUNTIME` | source-form ordinary-Beta B-CARS(1,1) is blocked by genuine pre-2025 weekly up-ratios equal to 0; no silent clipping permitted |
| `DIRECTION_BCARS_SV_V1_RESEARCH` | `EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED / WEAK_DIRECTIONAL_DISCRIMINATION` | separately preregistered Smithson-Verkuilen boundary-safe B-CARS(1,1) successor; 2024 validation failed and 2025 produced 51 UP / 1 DOWN with 0% DOWN sensitivity |
| `DIRECTION_REALP_CARR_V1_RESEARCH` | `EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED / REALP_BCARS_FAMILY_CLOSED_CURRENT_SEQUENCE / NOT_RUNTIME` | exact CARB specification was not proven and was not invented. Source-verifiable Realized Probability + asymmetric CARR/QMLE + linear RealP forecasting was preregistered and executed. 2024 balanced accuracy 0.4651, DOWN sensitivity 0.1154 and accuracy 0.4717 failed the frozen gate; unchanged 2025 balanced accuracy 0.4444 with 0 DOWN sensitivity. |
| `DIRECTION_SADORSKY_TREE_TECH_V1_RESEARCH` | `REGISTERED_LITERATURE_CANDIDATE / SOURCE_FAITHFUL_2025_TEST_BLOCKED_GLD_OHLCV / NOT_IMPLEMENTED` | Sadorsky (2021) GLD/SLV direction classification with logit, 500-tree bagging, 3000-tree stochastic gradient boosting and 500-tree RF over 1..20 trading-day horizons using 13 technical indicators. Exact source-faithful test needs GLD ETF OHLCV, including volume-dependent OBV/MFI; current Gold Control does not hold that source panel. |
| `DIRECTION_BASHER_SADORSKY_RF_MACRO_V1_RESEARCH` | `REGISTERED_LITERATURE_CANDIDATE / SOURCE_FAITHFUL_2025_TEST_BLOCKED_INPUT_PANEL / NOT_IMPLEMENTED` | Basher & Sadorsky (2022) RF/bagging/logit direction family over 1..20 trading-day horizons with technical indicators plus rates, inflation/term structure, VIX/OVX, EPU/EMU and EMV inputs. Current project lacks the complete pre-2025 source-faithful predictor panel and GLD-volume inputs. |
| `DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_V1_RESEARCH` | `REGISTERED_LITERATURE_CANDIDATE / SPOT_XAU_2025_ADAPTATION_READY_CURRENT_INTRADAY / EXACT_FUTURES_REPLICATION_BLOCKED / NOT_IMPLEMENTED` | Bonato et al. (2018) recursively estimated quantile boosting with intraday realized volatility/skewness and market/sentiment controls. Gold Control has 5-minute XAU/USD cache from 2020-04-06 through 2026-08-31, sufficient for a pre-2025 spot-XAU adaptation and locked 2025 challenge; exact paper replication remains blocked because the paper targets gold futures and a broader control panel. |
| `DIRECTION_PARISI_ROLLING_WARD_V1_RESEARCH` | `METHOD_RECOVERY_AND_DATA_AUDIT_STARTED / CURRENT_DATA_SUFFICIENT / NO_MODEL_FIT / NO_2025_SCORE` | First literature-backed candidate opened after explicit user authorization. Read-only audit confirms 436 pre-2025 and 52 2025 common XAU/DJIA weekly buckets, with 431 pre-2025 eligible four-lag origins. Core source inputs are available. Exact rolling-window sizes, Ward layer allocation, activation/scaling and training/stopping details remain to be proven before fitting; do not guess them. Start checkpoint: `GOLD_CONTROL_DIRECTION_PARISI_ROLLING_WARD_V1_START_2026-09-21.md`. |
| `DIRECTION_PARISI_ROLLING_WARD_GC_V1_RESEARCH` | `PREREGISTERED / SOURCE_GROUNDED_GOLD_CONTROL_ADAPTATION / FROZEN_BEFORE_2025_SCORE / NOT_RUNTIME` | Executable adaptation separated from the literature identity because the exact 2008 proprietary Ward layer allocation/training settings are not fully recoverable. Preserves ΔGold/ΔDJIA four-lag core, period-by-period rolling retraining, 21 hidden neurons and same-author Ward activation family. XAU/DJIA are synchronized on latest common date in each Monday-start week. Rolling window is selected only from {50,75,100} on common 2024 support, then frozen before 2025. Exact source replication is NOT claimed. |
| `DIRECTION_ALTUNTAS_ALEXNET_CANDLE_V1_RESEARCH` | `REGISTERED_LITERATURE_CANDIDATE / 2025_TEST_REQUIRES_DAILY_OHLC_COMPLETION / NOT_IMPLEMENTED` | Altuntaş, Okumuş & Kocamaz (2022): next-day UP/DOWN from 11-day candlestick images with SMA7, SMA50 and Bollinger(20,2), fine-tuned AlexNet at 227x227x3; source uses chronological 9y/3y/3y train/validation/test, max 100 epochs and mini-batch 32. Current long XAU history is not stored as a complete governed daily OHLC panel, so image construction is not yet input-complete. |
| `DIRECTION_YADAV_TECH_ML_V1_RESEARCH` | `REGISTERED_LITERATURE_CANDIDATE / WORKING_PAPER / 2025_TEST_REQUIRES_DAILY_OHLC_COMPLETION / EXTERNAL_2025_EXPOSURE / NOT_IMPLEMENTED` | Yadav (2026 working paper): next-day XAU/USD binary direction with technical indicators and logistic regression, decision tree, RF, gradient boosting and SVM under time-series OOS evaluation. Indicators include RSI, ATR, MACD, moving averages and Bollinger features; ATR requires OHLC. Because the source study itself uses data through 2025, any 2025 replay here is transport/reproduction evidence, not an independent blind holdout. |
| `DIRECTION_SULMAN_DL_ENSEMBLE_V1_RESEARCH` | `REGISTERED_LITERATURE_CANDIDATE / SOURCE_FAITHFUL_2025_TEST_BLOCKED_OHLCV_DATASET / EXTERNAL_2025_EXPOSURE / NOT_IMPLEMENTED` | Sulman et al. (2026): next-day gold return forecasting from daily OHLCV plus lagged price/return features using RF, XGBoost, tuned RBF-SVR, LSTM, BiLSTM, GRU, CNN-LSTM, ML ensemble and CNN-LSTM/GRU DL ensemble. Source deep-learning setup uses Adam 0.001, MSE, batch 32, <=100 epochs, early-stopping patience 12 and ReduceLROnPlateau patience 6/factor 0.5. Current project lacks a source-equivalent governed daily gold volume series; source study itself uses 2020-2025, so 2025 cannot be called independent blind OOS. |
| `DIRECTION_MAHATO_ATTAR_ENSEMBLE_V1_RESEARCH` | `REGISTERED_LITERATURE_CANDIDATE / METHOD_SPEC_NOT_PROVEN / 2025_TEST_BLOCKED / NOT_IMPLEMENTED` | Mahato & Attar (2014) reports next-day increase/decrease prediction with ensemble methods and 85% gold accuracy from stacking, but accessible authoritative material does not expose enough exact feature, base-learner and split details for a source-faithful implementation. Do not reconstruct the method by guesswork; obtain the full method specification first. |
| `DIRECTION_ZHANG_RETURN_ML_V1_RESEARCH` | `REGISTERED_LITERATURE_CANDIDATE / 2025_TEST_BLOCKED_EXTERNAL_PREDICTORS / NOT_IMPLEMENTED` | Zhang (DAML 2024 proceedings): relative-return regression with XGBoost, SVR and RF using oil, VIX, S&P 500, USD index plus MACD difference, RSI and Bollinger %B; grid search and trend accuracy are reported. Current Gold Control does not hold a complete pre-2025 governed panel for the exact oil/VIX/S&P500/USD-index predictors. |
| Post-BOCPD future-change-time lane | `NEXT_RESEARCH_LANE / PREREGISTRATION_REQUIRED` | separately named residual-time / explicit-duration / Bayesian online changepoint-prediction challenger; exact identity and parameters must be frozen before implementation |
| `MACRO_EVENT_SUCCESSOR_V2` | `SUSPENDED_FOR_CURRENT_GC_BREAK_RESEARCH_SEQUENCE` | governed runtime identity remains registered, but it is **not the next motor** and no new Macro Event tuning/evaluation is authorized in the current sequence |
| `MACRO_EVENT_SUCCESSOR_V4_RELIABILITY_GATE` | `FROZEN_RESEARCH_CHALLENGER / NOT_RUNTIME_AUTHORITY` | historical preregistration remains audit lineage; not promoted and not the current workstream |
| `EMERGENCY_LEVEL` | `SUSPENDED / REDESIGN_REQUIRED` | do not treat as next motor until separately redesigned/preregistered |
| `EMERGENCY_REVERSAL` | `SUSPENDED` | do not treat as next motor until separately re-authorized |
| `SLOW` | `LOW_PRIORITY / NOT_NEXT` | valid confirmation/new-regime context but not the immediate research priority |
| Monthly H=1 line | `ACTIVE_INDEPENDENT` | continues separately from GC-BREAK motor sequencing |

**Important:** suspension here is a research-sequencing status. It does not erase historical runtime identities, old contracts or Git history, and it does not promote a replacement automatically.

The binding post-BOCPD scientific direction is **not another ordinary BOCPD threshold/hazard retune** and is not Macro Event, GVZ, Emergency or SLOW. The next research lane is a separately named **future change-time prediction** motor in the residual-time / explicit-duration / Bayesian online prediction of changepoints family. Its exact implementation is not pre-approved; it requires preregistration using pre-2025 chronology before any new outcome inspection.

---

## 4. BOCPD research authority — exactly two retained identities

The active BOCPD research authority contains exactly **two** identities:

1. `BOCPD_HOURLY_B2_ADAPTIVE_HAZARD_V5_RESEARCH` — **primary BOCPD research model**.
2. `BOCPD_HOURLY_B2_PRE2025_BASELINE_R2_RESEARCH` — **frozen comparison baseline only**.

No other BOCPD identity is active authority. Raw hourly Candidate B, earlier optimized B2 identities, daily Candidate A, monthly `BOCPD_RETURN_SUCCESSOR_V1`, duration/residual V2, robust-clipped V3, duration+robust V4 and other superseded BOCPD experiments are historical only. Their active model-code/result/workflow surfaces are removed from the current research branch; Git history may retain them solely for audit traceability.

The **only authoritative BOCPD model surfaces** on the active research branch are:

- code: `gold_axis_2026/tools/bocpd_hourly_b2_adaptive_hazard_pre2025.py`;
- code: `gold_axis_2026/tools/bocpd_hourly_b2_baseline_r2_pre2025.py`;
- result: `gold_axis_2026/GOLD_CONTROL_BOCPD_B2_ADAPTIVE_HAZARD_V5_PRE2025_RESULT_2026-09-16.md`;
- result: `gold_axis_2026/GOLD_CONTROL_BOCPD_B2_BASELINE_R2_PRE2025_RESULT_2026-09-17.md`;
- reproducibility workflow: `.github/workflows/gold-bocpd-b2-adaptive-hazard-pre2025-20260916.yml`;
- reproducibility workflow: `.github/workflows/gold-bocpd-b2-baseline-r2-pre2025.yml`.

Any other BOCPD-named model code, model result or model workflow present on the active research branch is non-authoritative and must be removed or separately re-authorized by manifest change control.

The retained hourly input series is `XAU_USD_TWELVE_1H_RESEARCH_V1`. It is **research-only** and does not replace canonical `XAU_EOD_TWELVE_NY17` runtime semantics.

Neither retained BOCPD identity is a governed runtime or production engine. V5 is the active research reference; R2 is its benchmark. Neither emits an equal-weight direction vote.

### 4.1 BOCPD chronology

Binding chronology for both retained BOCPD identities:

- **2022:** research formation, hour-of-day normalization and prior formation;
- **2023:** development and parameter selection;
- **2024:** pre-2025 chronological retrospective comparison, not a pristine untouched holdout because BOCPD programme-level 2024 evidence had already been seen;
- **2025:** prohibited for tuning/model selection in the retained line and not queried/accessed by the V5/R2 pre-2025 model scripts.

The 2022 hourly history is accepted as **sufficient high-coverage research formation data for this phase**. This manifest does not claim that every theoretically expected 2022 market-hour slot has been independently completeness-certified.

### 4.2 BOCPD pre-2025 auxiliary comparison

`BOCPD_HOURLY_B2_PRE2025_BASELINE_R2_RESEARCH` on the 2024 auxiliary abnormal-volatility comparison:

- 57 episodes;
- 12 matched episodes;
- 45 unmatched episodes;
- 11 / 17 events captured;
- precision `0.210526`;
- recall `0.647059`;
- F0.5 `0.243363`.

`BOCPD_HOURLY_B2_ADAPTIVE_HAZARD_V5_RESEARCH` on the same 2024 comparison:

- 65 episodes;
- 15 matched episodes;
- 50 unmatched episodes;
- 14 / 17 events captured;
- precision `0.230769`;
- recall `0.823529`;
- F0.5 `0.269576`.

These are **auxiliary abnormal-daily-volatility metrics**, not structural GC-BREAK precision/recall. V5 improves event coverage, precision, recall and F0.5 relative to R2 under the same comparison, but false-warning burden remains material. No runtime/production promotion is authorized.

Any future BOCPD successor requires a separately named preregistration/change-control step. The next future-change-time lane is a **separate model identity**, not a silent V6 retune of V5.


### 4.3 Direction-forecast research authority — evaluated four-motor set and VLMC successors

The original four-motor direction-research set has now been evaluated, blocked, or closed as documented below; it is no longer a merely planned set. None of these research identities is a governed runtime or production authority, and none may silently replace the GC-BREAK state ontology.

Subsequent VLMC-family successors are also governed in this section so that completed, rejected, blocked and incomplete VLMC work cannot be mistaken for untried ideas. All evaluations must remain time-ordered and point-in-time safe.

The previously discussed higher-moment direction-probability method remains NOT SELECTED for this research set.

#### 4.3.1 RSM / ERSM family — CLOSED

The RSM/ERSM family was fully evaluated for the source-feasible variants and is now permanently closed for the current project by explicit user decision dated 2026-09-18.

Binding status:

`TERMINATED / FAILED_METHOD_FAMILY / DO_NOT_REVISIT / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`.

Do not reopen, extend, retune, augment, ensemble, or propose successors from this family unless the user explicitly reverses the closure. Detailed historical evidence remains in repository audit files, especially `GOLD_CONTROL_DIRECTION_RSM_FAMILY_CLOSURE_2026-09-18.md`, and is intentionally not repeated in this manifest.

#### 4.3.2 VLMC-BS family — corrected reference replication

The original `DIRECTION_VLMC_BS_V1_RESEARCH` is retained only as historical audit evidence and is superseded for family-level interpretation.

The authoritative corrected identity is:

`DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH`.

V2 follows Liu, Papailias & Quinn (2021) and the Mächler-Bühlmann R reference implementation more closely:

- governed daily simple percentage returns are summed into Monday-start weekly returns before binary UP/DOWN conversion;
- rolling windows k=26, 52 and 104 are evaluated because these are the source-feasible windows with same-source pre-2025 history;
- direct reference implementation uses R 4.4.1 and pinned `VLMC` 1.4-4;
- `K0=0.30`;
- candidate cutoff grid `0.40..2.50` by 0.02;
- `B=1000` bootstrap replications;
- `n.start=10000`;
- bootstrap one-step classification uses `VLMC::predict(type="class")`;
- each window-specific cutoff is calibrated once pre-OOS and frozen for the rolling replay;
- final direction is UP iff `P(UP)>=0.5`;
- no smoothing, NO_SIGNAL band, provider splice, external/context input or post-2025 rescue is present.

Frozen cutoff calibration:
- k=26: K*=0.40, bootstrap loss 0.304;
- k=52: K*=0.54, bootstrap loss 0.287;
- k=104: K*=0.40, bootstrap loss 0.243.

Fair 2024 common support begins 2024-03-04, n=44:
- k=26: accuracy 0.5909, balanced accuracy 0.5833;
- k=52: accuracy 0.6364, balanced accuracy 0.6292;
- k=104: accuracy 0.5682, balanced accuracy 0.5583.

On its full 2024 support, k=52 reaches accuracy 0.6792 and balanced accuracy 0.6781, providing materially stronger pre-2025 validation than the superseded V1.

Locked 2025 replay:
- k=26: accuracy 0.5769, balanced accuracy 0.5045, DOWN sensitivity 0.3333;
- k=52: accuracy 0.5769, balanced accuracy 0.4450, DOWN sensitivity 0.1333;
- k=104: accuracy 0.6154, balanced accuracy 0.5514, DOWN sensitivity 0.4000;
- corrected always-UP raw-accuracy baseline = 0.7115.

Frozen 19-event overlay:
- k=26: raw 12/19, balanced 0.4286, DOWN 0/5;
- k=52: raw 12/19, balanced 0.4929, DOWN 1/5;
- k=104: raw 14/19, balanced 0.6929, DOWN 3/5.

The event overlay is diagnostic only. k=104's event-subset result does not override its weaker pre-2025 evidence or the absence of stable pre-2025-to-2025 generalization.

Binding status:

`DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH = EVALUATED / NO_PROMOTION / SOURCE_FAITHFUL_REFERENCE_REPLICATION_COMPLETE / 2025_GENERALIZATION_WEAK / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`.

Fixed-Share adaptive weighting was subsequently tested as `DIRECTION_VLMC_BS_FIXED_SHARE_V1_RESEARCH`; it is `REJECTED / NO_PROMOTION / 2025_GENERALIZATION_FAILED`. Detailed evidence remains in `GOLD_CONTROL_DIRECTION_VLMC_BS_FIXED_SHARE_V1_RESULT_2026-09-19.md`.

Two additional VLMC-family successors must also remain explicit in project authority:

- `DIRECTION_COVLMC_X3_V1_RESEARCH`: direct exogenous-covariate extension using R `VLMCX` 1.0, rolling 104 weeks and exactly PIT DGS10, USD/CNY and GPR. On the identical 44-week 2024 VLMC-104 support it collapsed to `P(UP)=0.5` at every origin, forecast 44/44 UP, balanced accuracy 0.50 and DOWN sensitivity 0. The unchanged post-diagnostic 2025 replay forecast 52/52 UP with balanced accuracy 0.50. Binding status: `EVALUATED / NO_PROMOTION / PRE2025_COLLAPSE_TO_NEUTRAL / NOT_RUNTIME`. No parameter rescue is authorized under this identity.
- `DIRECTION_VLMC_C_104_V1_RESEARCH`: branch-specific consistent-pruning successor following the An et al. VLMC-C approach. The frozen 104-week experiment (`alpha0=0.05`, 100000 Monte Carlo draws per branch, pinned reference commit `8195ee16dedbb3a89c288869ee9c0b856ea2ed4f`) completed in governed workflow run `35453387137`. On identical 2024 support it produced accuracy 0.4773, balanced accuracy 0.4417 and DOWN sensitivity 0.05, versus parent VLMC-BS-104 at 0.5682 / 0.5583 / 0.45. The unchanged 2025 replay forecast 52/52 UP, yielding balanced accuracy 0.50 and DOWN sensitivity 0. Binding status: `EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED / 2025_COLLAPSE_TO_ALWAYS_UP / NOT_RUNTIME`.

**VLMC family closure for the current direction-research sequence:** the source-faithful 26/52/104 family contained a real but unstable signal, but Fixed-Share did not solve regime instability, COVLMC-X3 collapsed to neutral, and VLMC-C 104 failed the pre-2025 successor test before collapsing to all-UP in 2025. The family is therefore `CLOSED_FOR_CURRENT_DIRECTION_RESEARCH_SEQUENCE / NO_PROMOTION`. Do not open discounted/forgetting VLMC, new fixed-window searches, Fixed-Share rescue, COVLMC rescue or VLMC-specific smoothing successors unless the user explicitly reopens the family. No 2025 outcome may be used for rescue tuning.

Authoritative V2 audit surfaces:
- `GOLD_CONTROL_DIRECTION_VLMC_BS_FAMILY_V2_PREREG_2026-09-18.md`;
- `tools/direction_vlmc_bs_family_v2_reference.R`;
- `GOLD_CONTROL_DIRECTION_VLMC_BS_FAMILY_V2_CALIBRATION_2026-09-18.csv`;
- `GOLD_CONTROL_DIRECTION_VLMC_BS_FAMILY_V2_PRE2025_RESULT_2026-09-18.md`;
- `GOLD_CONTROL_DIRECTION_VLMC_BS_FAMILY_V2_2025_RESULT_2026-09-18.md`;
- `GOLD_CONTROL_DIRECTION_VLMC_BS_FAMILY_V2_2025_VOLATILITY_RESULT_2026-09-18.md`.

Additional VLMC successor authority surfaces:
- Fixed-Share result: `GOLD_CONTROL_DIRECTION_VLMC_BS_FIXED_SHARE_V1_RESULT_2026-09-19.md`;
- COVLMC preregistration: `GOLD_CONTROL_DIRECTION_COVLMC_X3_V1_PREREG_2026-09-18.md`;
- COVLMC result: `GOLD_CONTROL_DIRECTION_COVLMC_X3_V1_RESULT_2026-09-18.md`;
- COVLMC implementation: `tools/direction_covlmc_x3_v1_reference.R`;
- COVLMC workflow: `.github/workflows/gold-control-covlmc-x3-v1.yml`;
- VLMC-C preregistration: `GOLD_CONTROL_DIRECTION_VLMC_C_104_V1_PREREG_2026-09-18.md`;
- VLMC-C implementation: `tools/direction_vlmc_c_104_v1_reference.R`;
- VLMC-C workflow: `.github/workflows/gold-control-vlmc-c-104-v1.yml`;
- VLMC-C final result: `GOLD_CONTROL_DIRECTION_VLMC_C_104_V1_RESULT_2026-09-19.md`.

#### 4.3.3 DIRECTION_BCT_CTW_V1_RESEARCH — Bayesian Context Tree / Context Tree Weighting

Primary literature basis: Kontoyiannis, Mertzanis, Panotopoulou, Papageorgiou & Skoularidou (2022), JRSS Series B, DOI 10.1111/rssb.12511.

Let T(D) be the set of proper context trees with maximal depth D over alphabet size m. The BCT model prior is

pi_D(T;beta) = alpha^(|T|-1) * beta^(|T|-L_D(T)),

where alpha = (1-beta)^(1/(m-1)), |T| is the number of leaves and L_D(T) is the number of leaves at depth D. For the planned binary direction motor, m=2.

At each leaf/context s, the transition vector has independent Jeffreys-Dirichlet prior

theta_s ~ Dirichlet(1/2,1/2).

With context counts a_s(j), the posterior becomes

theta_s | x,T ~ Dirichlet(a_s(0)+1/2, a_s(1)+1/2).

Unlike a single selected VLMC, BCT/CTW averages over tree-model and parameter uncertainty. The exact prior predictive likelihood is

P*_D(x) = sum_T pi_D(T;beta) * integral P(x|theta,T) pi(theta|T) dtheta.

CTW computes it recursively. At a leaf, P_w,s = P_e,s. At an internal node,

P_w,s = beta*P_e,s + (1-beta)*product_j P_w,sj.

The exact next-symbol posterior predictive distribution is

P*_D(x_(n+1)|x_1^n) = P*_D(x_1^(n+1)) / P*_D(x_1^n).

For binary UP/DOWN data, the native output is therefore the exact posterior predictive P(UP next | sign history), not merely a MAP-tree class. The source framework suggests beta near 1-2^(-m+1); for m=2 this is about 0.5.

**Current BCT/CTW V1 evaluation checkpoint (2026-09-18):** V1 froze `D=10`, `beta=0.5`, `Dirichlet(1/2,1/2)`, a rolling 52-week binary window, first 10 signs as the fixed initial context, and the exact CTW posterior predictive with UP iff `P(UP)>=0.5`. No depth grid, threshold tuning or randomization was used.

Pre-2025:
- 2023 accuracy 0.5581395, balanced accuracy 0.5877193;
- 2024 fixed validation accuracy 0.4905660, balanced accuracy 0.4829060;
- combined pre-2025 Brier 0.2628675 and log loss 0.7224324;
- pre-2025 P(UP) range 0.4250141..0.8670874 with no exact 0/1 probabilities.

The probability layer is materially better behaved than the superseded VLMC-BS V1 audit run, whose pre-2025 replay produced exact 0/1 probabilities at 70/96 origins. This confirms the intended Bayesian smoothing/model-averaging benefit but does not establish a direction edge.

Locked 2025 historical replay:
- accuracy 0.6923077;
- balanced accuracy 0.5000000;
- actual UP/DOWN 36/16;
- forecast UP/DOWN 52/0;
- UP sensitivity 1.0;
- DOWN sensitivity 0.0;
- Brier 0.2320852;
- log loss 0.6578098;
- P(UP) range 0.5195496..0.7344673.

Thus the 69.23% raw accuracy exactly equals the always-UP baseline and is non-discriminative. On the frozen 19-event volatility overlay, raw direction agreement is 14/19 but event-direction balanced accuracy is 0.50, DOWN-event agreement 0/5 and EXTREME-event agreement 2/5.

Binding status: `EVALUATED / NO_PROMOTION / WEAK_DIRECTIONAL_DISCRIMINATION`. No post-2025 threshold shift, alternate D, NO_SIGNAL band or context augmentation is authorized under V1.

**Authoritative BCT/CTW V1 research surfaces on the current branch:**
- preregistration: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCT_CTW_V1_PREREG_2026-09-18.md`;
- implementation: `gold_axis_2026/tools/direction_bct_ctw_v1_research.py`;
- pre-2025 checkpoint: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCT_CTW_V1_PRE2025_RESULT_2026-09-18.md`;
- frozen 2025 weekly forecast table: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCT_CTW_V1_2025_WEEKLY_FORECASTS_2026-09-18.csv`;
- locked 2025 result: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCT_CTW_V1_2025_RESULT_2026-09-18.md`;
- frozen 19-event overlay table: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCT_CTW_V1_2025_VOLATILITY_OVERLAY_2026-09-18.csv`;
- volatility-overlay result: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCT_CTW_V1_2025_VOLATILITY_RESULT_2026-09-18.md`.

##### 4.3.3.1 DIRECTION_BCTX_AR_V1_RESEARCH — final BCT-family successor

A final literature-grounded successor tested the published BCT-X/BCT-AR extension on the corrected real-valued weekly-return surface rather than a binary-only sign sequence.

Frozen before replay:
- source: `XAU_WEEKLY_SIGN_SOURCE_METHOD_V2_2022_2025.csv` continuous `weekly_return`;
- development selection sample: 2022-03-07 through 2023-12-25 only;
- m=3, D=10, beta=0.75;
- source-default priors mu0=0, Sigma0=I, tau=lambda=1;
- p in {1,2,3,4,5};
- ternary quantiser candidate thresholds from development-sample q10..q90 values;
- quantiser pair and p selected only by exact GCTW evidence;
- fixed 2024 validation gate required balanced accuracy >=0.55, both class sensitivities >=0.40, and raw accuracy strictly above always-UP and previous-sign baselines.

Frozen selected configuration:
- p=1;
- c1_z=-0.8267251397;
- c2_z=1.0789919159;
- development log evidence=-124.9520496812.

2024 fixed validation:
- n=53;
- accuracy=0.5660377;
- balanced accuracy=0.5584046;
- UP sensitivity=0.9629630;
- DOWN sensitivity=0.1538462;
- TP/TN/FP/FN=26/4/22/1;
- forecast UP/DOWN=48/5;
- always-UP accuracy=0.5094340;
- previous-sign accuracy=0.5094340.

The pre-registered gate failed because DOWN sensitivity was below 0.40. This failure was established before 2025 replay and cannot be rescued by 2025.

Unchanged 2025 post-diagnostic replay:
- n=52;
- accuracy=0.6923077;
- balanced accuracy=0.4864865;
- UP sensitivity=0.9729730;
- DOWN sensitivity=0.0;
- forecast UP/DOWN=51/1;
- always-UP accuracy=0.7115385.

Binding status:
`EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED / BCT_FAMILY_CLOSED_CURRENT_SEQUENCE / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`.

The BCT direction family is closed for the current research sequence after binary BCT/CTW V1 and the real-valued BCT-X/AR successor. No D/beta/window/direction-threshold/quantiser rescue, ACTW extension or additional BCT-family tuning is authorized unless the user explicitly reopens the family.

Authoritative BCT-X/AR surfaces:
- preregistration: `GOLD_CONTROL_DIRECTION_BCTX_AR_V1_PREREG_2026-09-19.md`;
- implementation: `tools/direction_bctx_ar_v1_research.py`;
- frozen evidence grid: `GOLD_CONTROL_DIRECTION_BCTX_AR_V1_EVIDENCE_GRID_2026-09-19.csv`;
- frozen selected configuration: `GOLD_CONTROL_DIRECTION_BCTX_AR_V1_FROZEN_CONFIG_2026-09-19.json`;
- frozen 2024 forecasts: `GOLD_CONTROL_DIRECTION_BCTX_AR_V1_PRE2025_FORECASTS_2026-09-19.csv`;
- pre-2025 result: `GOLD_CONTROL_DIRECTION_BCTX_AR_V1_PRE2025_RESULT_2026-09-19.json`;
- unchanged 2025 forecasts: `GOLD_CONTROL_DIRECTION_BCTX_AR_V1_2025_FORECASTS_2026-09-19.csv`;
- 2025 result: `GOLD_CONTROL_DIRECTION_BCTX_AR_V1_2025_RESULT_2026-09-19.json`;
- final result: `GOLD_CONTROL_DIRECTION_BCTX_AR_V1_RESULT_2026-09-19.md`.

#### 4.3.4 DIRECTION_BCARS_V1_RESEARCH — Beta Conditional Autoregressive Shape

Primary literature basis: Xie, Sun & Fan (2023), Financial Innovation, DOI 10.1186/s40854-023-00489-z.

Let p_t be log close and h_t the maximum log price over interval [t-1,t]. Define

u_t = h_t - p_(t-1),
d_t = h_t - p_t,
R_t = u_t + d_t,
ur_t = u_t / R_t.

Then

r_t = p_t - p_(t-1) = R_t * (2*ur_t - 1).

Since R_t > 0, r_t > 0 if and only if ur_t > 0.5. Thus direction forecasting is transformed into forecasting a continuous up-ratio in [0,1].

B-CARS assumes

ur_t ~ Beta(alpha_t,beta),

with conditional mean

k_t = E(ur_t | Omega_t) = alpha_t/(alpha_t+beta).

The source benchmark B-CARS(1,1) uses

k_t = omega + gamma*k_(t-1) + tau*ur_(t-1),

subject to omega>0, gamma>=0, tau>=0 and omega+gamma+tau<=1. The time-varying shape parameter is

alpha_t = k_t*beta/(1-k_t).

Parameters are estimated by maximum likelihood from the Beta conditional likelihood. The native direction rule follows from whether the forecasted up-ratio is above or below 0.5. A Gold adaptation may additionally report `1-F_Beta(0.5;alpha_t,beta)` only as a derived probability diagnostic, not as the source paper's native direction rule.

The source high adjustment is preserved as `H_t^a=max(H_t,C_(t-1))`.

**True-OHLC data audit (2026-09-18):** a research-only Twelve Data `XAU/USD` 1h OHLC artifact was retrieved with no production database write. It contains 23,965 validated hourly bars, 205 weekly close anchors and 204 weekly up-ratio rows. Weekly HIGH is the maximum provider `high` field between consecutive governed weekly close anchors; it is not the maximum hourly close. Weekly close-axis checks against `XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1` passed at the investigated boundary dates. The weekly decomposition identity holds to machine precision (maximum absolute error approximately 6.94e-18).

The ordinary-Beta parent V1 is **blocked before 2025 scoring** because the true pre-2025 sample contains exact `ur=0` observations at target weeks 2022-08-15 and 2024-04-22. These are genuine gap/down interval geometries rather than extraction errors. Ordinary Beta density has open support `(0,1)`; the parent preregistration prohibited silent clipping. Therefore:

`DIRECTION_BCARS_V1_RESEARCH = BLOCKED_PRE2025_BOUNDARY_SUPPORT / NOT_SCORED / NOT_PROMOTED`.

No 2025 score exists for the unmodified parent identity.

#### 4.3.4a DIRECTION_BCARS_SV_V1_RESEARCH — boundary-safe preregistered successor

Because the support blocker was discovered using pre-2025 data only, a separately named successor was frozen before 2025 replay.

The successor preserves B-CARS(1,1), source/high semantics, expanding-window OOS, initial 52 modeled weekly up-ratios, deterministic five-start constrained L-BFGS-B fitting and the native 0.5 direction boundary, but applies the standard Smithson-Verkuilen transformation at each origin with n training observations:

`y_i^* = (y_i*(n-1)+0.5)/n`.

The transform maps [0,1] into (0,1) while leaving the 0.5 classification boundary invariant. Continuous forecast diagnostics are mapped back to raw up-ratio scale via

`k_raw=(n*k^*-0.5)/(n-1)`.

No epsilon/clipping parameter is tuned.

**Pre-2025 frozen evidence:**

2023 development/audit:
- n=43;
- accuracy 0.4418605;
- balanced accuracy 0.5000000;
- forecasts 0 UP / 43 DOWN;
- UP sensitivity 0.0000; DOWN sensitivity 1.0000;
- source-style up-ratio R2_oos = -0.0032779.

2024 fixed validation:
- n=53;
- accuracy 0.4716981;
- balanced accuracy 0.4729345;
- forecasts 23 UP / 30 DOWN;
- UP sensitivity 0.4074074; DOWN sensitivity 0.5384615;
- source-style up-ratio R2_oos = -0.0325649.

Combined 2023-2024:
- n=96;
- accuracy 0.4583333;
- balanced accuracy 0.4745098;
- forecasts 23 UP / 73 DOWN;
- source-style up-ratio R2_oos = -0.0208597.

This is a failed pre-2025 validation checkpoint; the model was nevertheless carried unchanged into 2025 to preserve the preregistered test sequence.

**Locked 2025 historical replay:**
- n=52;
- accuracy 0.6730769 versus always-UP 0.6923077;
- balanced accuracy 0.4861111;
- actual UP/DOWN 36/16;
- forecasts 51 UP / 1 DOWN;
- UP sensitivity 0.9722222;
- DOWN sensitivity 0.0000000;
- TP/TN/FP/FN = 35/0/16/1;
- the only DOWN forecast targeted 2025-03-03 and was wrong;
- up-ratio MSE 0.0807706 versus expanding historical-mean MSE 0.0819350;
- source-style up-ratio R2_oos = +0.0142111;
- derived Beta-tail Brier 0.2367432 and log loss 0.6669116.

Thus the small positive 2025 continuous up-ratio R2_oos does not translate into two-sided direction discrimination.

**Frozen 19-event volatility overlay:**
- raw event-direction agreement 14/19 = 73.68%;
- balanced event-direction accuracy 0.5000;
- UP event agreement 14/14;
- DOWN event agreement 0/5;
- EXTREME event agreement 2/5;
- MAJOR-only agreement 12/14.

The raw event hit rate is class-balance driven because B-CARS-SV forecasts UP on every event week.

Binding successor status:

`DIRECTION_BCARS_SV_V1_RESEARCH = EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED / WEAK_DIRECTIONAL_DISCRIMINATION / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`.

**Authoritative B-CARS research surfaces on the current branch:**
- parent preregistration: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCARS_V1_PREREG_2026-09-18.md`;
- true-OHLC data audit: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCARS_V1_DATA_AUDIT_2026-09-18.md`;
- parent pre-2025 blocker: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCARS_V1_PRE2025_BLOCKER_2026-09-18.md`;
- boundary-safe successor preregistration: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCARS_SV_V1_PREREG_2026-09-18.md`;
- successor implementation: `gold_axis_2026/tools/direction_bcars_sv_v1_research.py`;
- successor pre-2025 checkpoint: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCARS_SV_V1_PRE2025_RESULT_2026-09-18.md`;
- frozen 2025 forecast table: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCARS_SV_V1_2025_WEEKLY_FORECASTS_2026-09-18.csv`;
- locked 2025 result: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCARS_SV_V1_2025_RESULT_2026-09-18.md`;
- frozen 19-event overlay: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCARS_SV_V1_2025_VOLATILITY_OVERLAY_2026-09-18.csv`;
- volatility-overlay result: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCARS_SV_V1_2025_VOLATILITY_RESULT_2026-09-18.md`.

No post-2025 threshold, model-order, boundary treatment, frequency, optimizer or feature rescue is authorized under either B-CARS identity.

#### 4.3.4b DIRECTION_REALP_CARR_V1_RESEARCH — source-verifiable Realized Probability successor

A final Realized-Probability successor was opened only after an authority scan.

Authority boundary:
- a 2022 Academy of Mathematics and Systems Science seminar describes a CARB (Conditional AutoRegressive Beta-distribution) model for Realized Probability direction forecasting;
- however, the exact CARB recursion, likelihood, initialization and reproducible implementation were not found in an accessible primary source;
- therefore `CARB_EXACT_SPECIFICATION = NOT_PROVEN / DO_NOT_IMPLEMENT_BY_GUESSING`.

The experiment instead uses only source-verifiable components from Xie, Wu, Sun & Wang, *Realized Probability Index is a Better Market Timing Indicator*:
- hourly log-price changes between consecutive governed weekly close anchors;
- `CPR=sum positive intraperiod log returns`;
- `CNR=sum negative intraperiod log returns`;
- `CAR=CPR-CNR=sum |r_i|`;
- `RealP=CPR/CAR`;
- exact direction identity `return>0 <=> RealP>0.5`;
- asymmetric CARR conditional-mean filter `lambda_(t+1)=omega+a*lambda_t+b*CAR_t+g*CAR_t*I(r_t<0)`;
- exponential-density QMLE;
- linear historical relation `RealP_t=theta+psi*lambda_t+e_t`;
- next-week direction UP iff forecast RealP exceeds 0.5.

This is a weekly Gold adaptation of the published daily-to-monthly empirical design, not CARB and not an exact frequency replication.

Data audit:
- provider Twelve Data, XAU/USD, 1h, America/New_York;
- 23,642 validated hourly bars;
- 202 governed weekly close anchors;
- 201 weekly RealP rows from 2022-02-28 through 2025-12-29;
- no RealP boundary values at 0 or 1;
- maximum RealP decomposition identity error about 1.39e-15;
- weekly derived-input SHA-256 `3c9abbcc33e3bfba14404b6f9393bf7ed2ace663157b2b4322bd778bc9a1c941`;
- raw hourly payload not persisted;
- production database writes NONE.

Frozen 2024 validation:
- n=53;
- accuracy 0.4716981;
- balanced accuracy 0.4650997;
- UP sensitivity 0.8148148;
- DOWN sensitivity 0.1153846;
- TP/TN/FP/FN = 22/3/23/5;
- forecasts 45 UP / 8 DOWN;
- always-UP = previous-sign = historical-mean-RealP direction accuracy = 0.5094340;
- continuous RealP R2_oos versus expanding historical mean = +0.0078421.

The preregistered gate failed before 2025 replay because balanced accuracy, DOWN sensitivity and raw-baseline conditions failed.

Unchanged 2025 post-diagnostic replay:
- n=52;
- accuracy 0.6153846;
- balanced accuracy 0.4444444;
- UP sensitivity 0.8888889;
- DOWN sensitivity 0.0000000;
- forecasts 48 UP / 4 DOWN;
- always-UP accuracy 0.6923077;
- RealP R2_oos = -0.0559187.

Binding status:
`DIRECTION_REALP_CARR_V1_RESEARCH = EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED / REALP_BCARS_FAMILY_CLOSED_CURRENT_SEQUENCE / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`.

The B-CARS / Realized-Probability direction family is closed for the current research sequence. No CARB invention, threshold rescue, alternate CARR order, exogenous augmentation or 2025-driven tuning is authorized unless the user explicitly reopens the family.

Authoritative RealP-CARR surfaces:
- preregistration: `GOLD_CONTROL_DIRECTION_REALP_CARR_V1_PREREG_2026-09-20.md`;
- hourly derivation: `data_pipeline/twelve_xau_realp_research_v1.py`;
- model implementation: `tools/direction_realp_carr_v1_research.py`;
- data audit: `GOLD_CONTROL_DIRECTION_REALP_CARR_V1_DATA_AUDIT_2026-09-20.json`;
- pre-2025 forecasts: `GOLD_CONTROL_DIRECTION_REALP_CARR_V1_PRE2025_FORECASTS_2026-09-20.csv`;
- pre-2025 result: `GOLD_CONTROL_DIRECTION_REALP_CARR_V1_PRE2025_RESULT_2026-09-20.json`;
- 2025 forecasts: `GOLD_CONTROL_DIRECTION_REALP_CARR_V1_2025_FORECASTS_2026-09-20.csv`;
- 2025 result: `GOLD_CONTROL_DIRECTION_REALP_CARR_V1_2025_RESULT_2026-09-20.json`;
- final result: `GOLD_CONTROL_DIRECTION_REALP_CARR_V1_RESULT_2026-09-20.md`.

### 4.3.5 Literature-backed direction-engine queue registered 2026-09-21

The earlier RSM/ERSM, VLMC, BCT and B-CARS/Realized-Probability families remain closed under their existing decisions. The following literature-backed candidates are **new research identities**, not rescues or retunes of those closed families.

Registration in this manifest is **not implementation authorization**. No code, workflow, model fitting, 2025 scoring or result selection is authorized until the user explicitly instructs the project to proceed with a named candidate. Missing inputs are to be collected only after that instruction and source semantics are frozen.

#### 4.3.5.1 DIRECTION_SADORSKY_TREE_TECH_V1_RESEARCH

Primary authority: Perry Sadorsky (2021), *Predicting Gold and Silver Price Direction Using Tree-Based Classifiers*, Journal of Risk and Financial Management 14(5):198, DOI 10.3390/jrfm14050198.

Source method:
- target asset is GLD (and separately SLV), not spot XAU/USD;
- binary target at horizons h=1..20 trading days: UP if future ETF price change is positive, DOWN otherwise;
- 13 technical-indicator feature space including RSI, stochastic slow/fast components, ADX, MACD/MACD signal, ROC, OBV, MFI, WAD, MA50 and MA200;
- comparison models: logit, decision-tree bagging, stochastic gradient boosting and random forests;
- bagging: 500 trees;
- RF: 500 trees and mtry=3 (=floor(sqrt(13)));
- stochastic gradient boosting: 3000 trees, shrinkage 0.20, interaction depth 8, minimum node size 10, bag fraction 0.5;
- paper reports 80/20 testing plus sensitivity analysis with repeated 10-fold CV, and additionally a time-series CV experiment in which the training sample is refit sequentially.

Gold Control implementation rule:
- random splitting/repeated random CV is **not** permitted for the project decision surface even though reported in the source;
- source model identities/hyperparameters may be replicated, but all project selection/tuning must be time-ordered and frozen before 2025;
- h=1..20 may be reproduced, with h=5/10/20 explicitly reported; overlapping-horizon metrics must be accompanied by non-overlapping-origin robustness;
- exact GLD replication and any spot-XAU adaptation must be reported as different evidence classes and may not be silently conflated.

2025 testability audit:
- exact source-faithful status: `BLOCKED_GLD_OHLCV`;
- Gold Control currently has no governed GLD ETF series;
- volume-dependent OBV and MFI prevent exact substitution with the current close-centric XAU history;
- a spot-XAU technical-indicator adaptation is possible only under a separately frozen adaptation contract after OHLC/volume semantics are resolved.

#### 4.3.5.2 DIRECTION_BASHER_SADORSKY_RF_MACRO_V1_RESEARCH

Primary authority: Syed A. Basher & Perry Sadorsky (2022), *Forecasting Bitcoin price direction with random forests: How important are interest rates, inflation, and market volatility?*, Machine Learning with Applications 9:100355, DOI 10.1016/j.mlwa.2022.100355. The paper contains a parallel gold/GLD direction experiment.

Source method:
- multistep direction horizons h=1..20 trading days;
- logit, tree bagging and random forests, with tuned-RF comparisons;
- technical-indicator block overlaps the Sadorsky family (RSI, stochastic indicators, ADX, MACD/MACD signal, ROC, OBV, MFI, WAD, MA50, MA200);
- macro/market block includes EPU, EMU, 10-year Treasury yield, 3-month T-bill, term spread, break-even inflation, 5-year inflation expectations, VIX, OVX and EMV_IDT;
- RF/tree bagging use 500 trees; paper's RF feature count implies mtry=floor(sqrt(p));
- paper reports both ordinary CV and time-series CV; for gold, reported tsCV accuracy is 0.8189 at h=10 and 0.8778 at h=20.

Gold Control implementation rule:
- only time-ordered formation/validation is authorized; no random CV may determine project promotion;
- all feature release lags/PIT semantics must be origin-safe;
- 2025 may not determine horizon, feature subset, mtry, threshold or any tuned parameter;
- h=10 and h=20 must receive non-overlapping-origin robustness checks because overlapping multiday targets can inflate apparent sample size.

2025 testability audit:
- status `BLOCKED_INPUT_PANEL`;
- current project has some relevant rates/macro context but not the complete source-faithful pre-2025 daily/availability-aware EPU/EMU/EMV_IDT/VIX/OVX/3m-T-bill/break-even/5y-inflation panel;
- current VIX registry coverage begins in 2026, so it does not support a 2025 source-faithful challenge;
- GLD and volume-dependent indicators are also not currently input-complete.

#### 4.3.5.3 DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_V1_RESEARCH

Primary authority: Bonato, Demirer, Gupta & Pierdzioch (2018), *Gold futures returns and realized moments: A forecasting experiment using a quantile-boosting approach*, Resources Policy 57:196-212, DOI 10.1016/j.resourpol.2018.03.004.

Source method:
- target is gold futures return, not spot XAU/USD;
- realized volatility and realized skewness are computed from intraday gold-futures returns;
- recursively expanding quantile boosting jointly performs iterative model building and predictor selection;
- forecasting models compare: boosted AR(1), boosted market/sentiment controls without realized moments, and boosted controls plus realized volatility/skewness;
- source control set includes 3m T-bill, 10y-minus-3m term spread, USD/GBP and JPY/USD returns, S&P 500 return, VXO, WTI return, daily EPU and EMU, plus lagged gold-futures return;
- baseline experiment uses 75% (1222 observations) to initialize and then recursively produces OOS forecasts;
- source evidence emphasizes incremental predictive value at intermediate horizons/lower quantiles and reports directional-accuracy tests.

Gold Control implementation rule:
- first executable identity is explicitly a **spot-XAU adaptation**, not a claim of exact futures replication;
- realized moments must be built only from intraday bars completed by the forecast origin;
- the source's recursive quantile-boosting procedure and comparator structure must be reproduced as closely as source details permit;
- all quantile set, boosting stopping rule, predictor list and horizon set must be frozen from pre-2025 information before 2025 scoring;
- direction metrics are mandatory in addition to quantile-loss/return-forecast metrics.

2025 testability audit:
- `SPOT_XAU_ADAPTATION_READY_CURRENT_INTRADAY`;
- Gold Control Neon read-only audit on 2026-09-21 shows XAU 5m cache 2020-04-06..2026-08-31 (482,734 rows) and XAU 1m cache 2023-01-02..2026-06-30 (1,330,943 rows), so 2023-2024 formation and all 2025 realized-moment construction are available;
- `EXACT_FUTURES_REPLICATION_BLOCKED` because the paper uses gold futures and a broader control panel not currently complete;
- no 2025 score is authorized yet.

#### 4.3.5.4 DIRECTION_PARISI_ROLLING_WARD_V1_RESEARCH

Primary authority: Parisi, Parisi & Díaz (2008), *Forecasting gold price changes: Rolling and recursive neural network models*, Journal of Multinational Financial Management 18(5):477-487, DOI 10.1016/j.mulfin.2007.12.002.

Source method:
- one-step-ahead sign variation in gold price;
- predictors are four lags of gold first differences and four lags of DJIA first differences;
- feed-forward and Ward neural networks are compared under recursive and rolling updating;
- rolling networks recalculate weights period-by-period; rolling Ward is the source's strongest family;
- source reports block-bootstrap validation and mean rolling-Ward sign prediction 60.68% (sd 2.82%);
- a Ward specification with two hidden layers / 21 neurons is reported among the best architectural combinations.

Gold Control implementation rule:
- exact weekly/period aggregation and rolling sample-size rule must be recovered/frozen from the paper before execution; where the source detail is not recoverable, do not invent it;
- Gold and DJIA first differences must be synchronized to the same completed-period clock;
- network training at every origin must use only prior observations;
- architecture/sample-size alternatives may be compared only inside pre-2025 chronology, never on 2025.

2025 testability audit:
- `READY_CURRENT_DATA_FOR_GOLD_ADAPTATION`;
- current Gold Control holds DJIA daily closes from 2016-08-29 onward and long XAU daily research history, sufficient to construct several years of pre-2025 lagged weekly inputs and a locked 2025 retrospective challenge;
- source price/weekly semantics still require a preregistered bridge before scoring.

#### 4.3.5.4a DIRECTION_PARISI_ROLLING_WARD_GC_V1_RESEARCH — executable Gold-Control adaptation

The 2008 Parisi gold paper is sufficiently clear about the scientific core but not sufficiently transparent to support a claim of exact software replication. The primary source proves one-step-ahead `ΔG_t` forecasting from four lags of gold first differences plus four lags of DJIA first differences, repeated retraining, rolling recent-information updating, a best reported Ward architecture with two hidden layers / 21 neurons, exploration of activation/scaling/sample-size combinations, and superior rolling-Ward direction performance. It does **not** expose enough accessible detail to recover the exact 21-neuron layer allocation, winning activation/scaling assignment, tested rolling sample sizes or proprietary optimizer/stopping settings.

Accordingly, the executable identity is separately named `DIRECTION_PARISI_ROLLING_WARD_GC_V1_RESEARCH` and may not be described as an exact replication.

Frozen source-grounded adaptation:
- XAU: `XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`;
- DJIA: `DJIA_FRED`;
- weekly anchor: latest completed date in each Monday-start week on which both XAU and DJIA exist;
- no interpolation / forward fill / asynchronous weekly endpoint;
- first differences in levels, not log returns;
- inputs exactly `ΔG[t-1..t-4]` and `ΔDJI[t-1..t-4]`;
- target exactly next `ΔG_t`;
- UP iff predicted `ΔG_t>0`.

Ward mechanism where the gold paper is silent is taken only from the same authors' explicit 2006 Ward implementation:
- supervised back-propagation;
- input min/max scaling to [-1,1];
- Ward activation families Gaussian / Gaussian-complement / tanh;
- logistic output with inverse target scaling.

GC_V1 hidden bank:
- 21 hidden neurons total from the gold-paper count;
- 7 Gaussian + 7 Gaussian-complement + 7 tanh neurons;
- this equal-slab allocation is an explicit adaptation and is **not** represented as the unrecovered 2008 two-hidden-layer allocation.

Frozen numerical training:
- target scaled to [0.1,0.9];
- full-batch Adam lr=0.01;
- <=2000 epochs;
- training-MSE patience 200, min improvement 1e-10;
- starts 11/29/47/71/101;
- choose the single lowest-training-MSE start at each origin; no seed vote or ensemble.

Frozen pre-2025 window selection:
- candidate fixed rolling windows {50,75,100} weeks;
- compare on identical common 2024 forecast support only;
- select by balanced accuracy, then raw accuracy, then ΔG RMSE, then smaller window;
- freeze selected window before any 2025 model score.

2025 evidence class:
- `LOCKED_RETROSPECTIVE_CHALLENGE`, not pristine/prospective;
- full 2025 replay only after pre-2025 configuration is persisted;
- no 2025 rescue tuning.

Authority surface:
- `GOLD_CONTROL_DIRECTION_PARISI_ROLLING_WARD_GC_V1_PREREG_2026-09-21.md`.

Current status:
`PREREGISTERED / FROZEN_BEFORE_2025_SCORE / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`.

#### 4.3.5.5 DIRECTION_ALTUNTAS_ALEXNET_CANDLE_V1_RESEARCH

Primary authority: Altuntaş, Okumuş & Kocamaz (2022), *Evrişimsel Sinir Ağları ve Transfer Öğrenme Yaklaşımı Kullanılarak Altın Fiyat Yönünün Tahmini*, Computer Science 7(2):124-131, DOI 10.53070/bbd.1205299.

Source method:
- daily ounce-gold OHLC;
- label at day T is UP if Close(T+1)>Close(T), DOWN if Close(T+1)<Close(T);
- each sample image contains an 11-day candlestick chart plus SMA7, SMA50 and Bollinger bands with SMA20 +/- 2*20-day standard deviation;
- PNG chart images are classified by fine-tuning pretrained AlexNet at 227x227x3;
- source split is chronological 3:1:1 by years (9 years train, 3 validation, 3 test);
- last fully connected layer is replaced by two outputs; max epochs 100; mini-batch 32;
- source reports 53.8% classification accuracy.

Gold Control implementation rule:
- preserve chronological train/validation/test; no shuffled image split;
- chart rendering must be deterministic and frozen (axis/scale/image geometry/indicator styling);
- ImageNet pretrained weights may be used as external prior, but all fine-tuning/early stopping must use <=2024 data;
- 2025 images/labels must be generated only after image pipeline and training choices are frozen.

2025 testability audit:
- `REQUIRES_DAILY_OHLC_COMPLETION`;
- current long-lived Gold Control XAU history is not stored as a complete governed daily OHLC panel for source-faithful candlestick generation;
- existing Twelve Data infrastructure can later be used to acquire/validate OHLC, but that collection is not authorized by this registration alone.

#### 4.3.5.6 DIRECTION_YADAV_TECH_ML_V1_RESEARCH

Primary authority: Kartikey Yadav (2026), *Comparative Evaluation of Machine Learning Classifiers for Short-Term Gold Price Direction: Statistical and Economic Evidence*, SSRN 6323238, DOI 10.2139/ssrn.6323238. This is a working paper, not a peer-reviewed journal result.

Source method:
- daily XAU/USD, next-day binary direction;
- classifier family: logistic regression, decision tree, random forest, gradient boosting and SVM;
- technical indicators include RSI, ATR, MACD, moving averages and Bollinger-band features;
- evaluation is time-series out-of-sample rather than ordinary random splitting;
- paper reports only modest near-chance accuracy and no statistically significant superiority to a naive benchmark.

Gold Control implementation rule:
- use a fully specified source-faithful indicator list only after the exact working-paper version is frozen;
- OHLC-dependent indicators such as ATR must use completed daily OHLC bars;
- preprocessing/scaling/model hyperparameters must be fit only on pre-2025 data;
- include confidence intervals and paired forecast-significance testing in addition to raw classification metrics.

2025 testability audit:
- `REQUIRES_DAILY_OHLC_COMPLETION`;
- importantly, the source paper itself uses 2000-2025 data. Therefore its architecture/feature choices are externally exposed to 2025;
- any Gold Control 2025 run is `EXTERNAL_LITERATURE_INFORMED_RETROSPECTIVE_TRANSPORT`, not a pristine independent holdout.

#### 4.3.5.7 DIRECTION_SULMAN_DL_ENSEMBLE_V1_RESEARCH

Primary authority: Sulman et al. (2026), *Forecasting Next-Day Gold Returns under Market Volatility: A Comparative Study of Machine Learning and Hybrid Deep Learning Ensembles*, IEEE ICMI 2026, DOI 10.1109/ICMI68585.2026.11539848.

Source method:
- daily gold OHLCV, 2020-2025, with lagged price/return features;
- target is next-day return; direction is evaluated from forecast-return sign;
- models include RF, XGBoost, tuned RBF-SVR, LSTM, BiLSTM, GRU, CNN-LSTM, equal-weight ML ensemble and CNN-LSTM/GRU deep ensemble;
- source uses chronological 80% train / 20% test and z-score scaling;
- deep-learning training: Adam lr=0.001, MSE loss, batch 32, <=100 epochs, early stopping patience 12 with best-weight restore, ReduceLROnPlateau patience 6/factor 0.5;
- source deep ensemble averages CNN-LSTM and GRU outputs and reports 60.45% directional accuracy.

Gold Control implementation rule:
- instrument/volume semantics for the source dataset must be identified before source-faithful replication;
- scaling must be fit on training data only;
- the paper's architecture/configuration may be treated as an external literature prior, but project tuning must use <=2024 chronology only;
- 2025 may not select architecture, SVR C/gamma, lag schema, ensemble weights or stopping rules.

2025 testability audit:
- `BLOCKED_SOURCE_EQUIVALENT_DAILY_OHLCV`;
- Gold Control does not currently hold a governed source-equivalent traded-volume series for spot XAU;
- the source study itself uses 2025; therefore a later 2025 run is transport/reproduction evidence, not independent blind OOS.

#### 4.3.5.8 DIRECTION_MAHATO_ATTAR_ENSEMBLE_V1_RESEARCH

Primary authority: Mahato & Attar (2014), *Prediction of gold and silver stock price using ensemble models*, ICAETR 2014, DOI 10.1109/ICAETR.2014.7012821.

Source-supported facts:
- next-day increase/decrease classification for gold and silver;
- ensemble-model comparison;
- abstract reports 85% gold accuracy with stacking and 79% silver accuracy with hybrid bagging.

Authority limitation:
- the accessible authoritative record does not expose enough exact feature definitions, base-learner composition, training/test chronology or hyperparameter details to reproduce the 85% result faithfully.

2025 testability audit:
- `METHOD_SPEC_NOT_PROVEN / BLOCKED`;
- do not invent missing method details;
- obtain the full paper/method specification before preregistration or implementation.

#### 4.3.5.9 DIRECTION_ZHANG_RETURN_ML_V1_RESEARCH

Primary authority: Runjie Zhang (DAML 2024 proceedings), *Gold Price Relative Return Prediction with Machine Learning Models*.

Source method:
- gold relative-return regression using XGBoost, SVR and Random Forest;
- market predictors: oil price, volatility index, S&P 500 index and USD index;
- technical predictors: MACD difference, RSI and Bollinger %B;
- grid search is used for model parameters;
- evaluation reports MSE, RMSE, MAE, R2 and trend accuracy; source reports RF/SVR R2 about 0.79 and XGBoost about 0.72.

Gold Control implementation rule:
- because the project objective here is direction, source return forecasts must first be generated exactly, then mapped to direction by sign; do not train a different classifier under the same identity;
- source grid-search ranges and training chronology must be recovered/frozen before execution;
- any grid search must occur entirely pre-2025 under time ordering;
- no Nasdaq/DJIA proxy may silently replace S&P 500, and no broad-dollar proxy may silently replace the source USD index without a separately named adaptation.

2025 testability audit:
- `BLOCKED_EXTERNAL_PREDICTORS`;
- current Gold Control does not hold the complete pre-2025 source-faithful oil/VIX/S&P500/USD-index daily panel; current governed VIX history begins in 2026;
- exact input gaps must be filled and source semantics frozen before a 2025 challenge.

#### 4.3.5.10 Common 2025 challenge contract for the registered literature queue

For every candidate above:

- **2025 is a locked retrospective challenge, not a fresh/pristine blind holdout.** Project researchers have already observed 2025 in prior work; no claim may relabel it as prospectively unseen evidence.
- all feature definitions, source semantics, model identity, horizon(s), hyperparameters, threshold/direction mapping, preprocessing, training-window policy and selection rule must be frozen using information available no later than 2024-12-31 before candidate-specific 2025 scoring;
- source papers that used random train/test splits do not override Gold Control governance: project evaluation is chronological only;
- source papers published in 2026 that themselves use 2025 (Yadav; Sulman et al.) carry explicit `EXTERNAL_2025_EXPOSURE`; their 2025 Gold Control replay can test transport/reproducibility but cannot be treated as independent confirmatory evidence;
- exact replication and Gold/XAU adaptation are separate evidence classes and must be labelled separately;
- no missing source may be silently replaced by a proxy. Any proxy/adaptation requires a separately named identity or an explicit preregistered adaptation surface;
- for h>1 overlapping targets, report standard origin-by-origin metrics **and** non-overlapping-origin robustness;
- mandatory direction metrics: accuracy, balanced accuracy, UP sensitivity, DOWN sensitivity, TP/TN/FP/FN, forecast UP/DOWN counts, always-UP, always-DOWN and previous-sign baselines; report probability calibration/Brier/log-loss whenever the native model emits probabilities;
- regression-native methods must also report their source-native regression/quantile metrics before forecast sign is scored;
- no candidate is promoted solely for raw accuracy; class balance, two-sided discrimination, stability across pre-2025 validation blocks and baseline improvement are required;
- no implementation begins until explicit user authorization after reviewing input gaps.

#### 4.3.5.11 Current data-readiness snapshot (read-only audit, 2026-09-21)

Available current project surfaces relevant to this queue:
- XAU intraday 1m cache: 2023-01-02 through 2026-06-30, 1,330,943 rows;
- XAU intraday 5m cache: 2020-04-06 through 2026-08-31, 482,734 rows;
- XAU daily research history: 2010-01-04 through 2026-07-31;
- DJIA daily close: 2016-08-29 through 2026-09-18;
- NASDAQ-100 daily close is available, but it is not an authorized substitute for S&P 500;
- existing XAU pipelines can retrieve daily Twelve Data OHLC later, but a complete governed long-history OHLC dataset is not yet frozen for this queue;
- no governed GLD ETF panel is currently registered;
- no source-equivalent traded-volume panel is currently registered for the GLD/OHLCV-dependent candidates;
- current VIX_CBOE registered history begins in 2026, so it cannot support pre-2025 formation;
- complete source-faithful OVX/EPU/EMU/EMV_IDT/3m-T-bill/break-even inflation/5y-inflation and Zhang oil/S&P500/USD-index panels are not currently complete for this queue.

**Binding implementation state:** `REGISTERED_ONLY / RESEARCHED / DATA_READINESS_CLASSIFIED / DO_NOT_IMPLEMENT_UNTIL_USER_AUTHORIZATION`.

### 4.4 Common governance for direction research motors

The original four direction motors and the literature-backed queue in Section 4.3.5 form a parallel research-only direction programme. Closed families remain closed; newly registered literature candidates do not alter the primary GC-BREAK sequential state output and do not reactivate the historical fixed NEXT_NY17_1D/3D programme.

Before implementation, a common preregistration must freeze target horizon/frequency, exact XAU source and close/OHLC semantics, rolling versus expanding formation, permitted training window(s), probability-to-direction mapping, abstention rule if any, evaluation metrics, and tie/missing handling.

Initial evaluation must report at minimum success rate, balanced accuracy where applicable, Brier score, log-loss, calibration and coverage. A model may not be selected solely because it has the highest raw hit rate.

The first implementation stage must reproduce each method's native mathematical identity WITHOUT FAST, GVZ, BOCPD, Macro or Emergency inputs. Only after standalone evidence is frozen may existing Gold Control motors be added one at a time through role-preserving ablation. Flat equal voting remains forbidden.

Current status is identity-specific: the RSM/ERSM family is `TERMINATED / FAILED_METHOD_FAMILY / DO_NOT_REVISIT`; the VLMC family is closed for the current sequence after its governed successors; the BCT family is closed for the current sequence after BCT/CTW V1 and BCT-X/AR V1; source-form B-CARS V1 is `BLOCKED_PRE2025_BOUNDARY_SUPPORT / NOT_SCORED`; `DIRECTION_BCARS_SV_V1_RESEARCH` is `NO_PROMOTION / PRE2025_VALIDATION_FAILED`; and `DIRECTION_REALP_CARR_V1_RESEARCH` closed the B-CARS/Realized-Probability family for the current sequence. Exact CARB remains `NOT_PROVEN / DO_NOT_IMPLEMENT_BY_GUESSING`. Separately, the nine Section 4.3.5 literature identities are `REGISTERED_ONLY / NOT_IMPLEMENTED`; their per-identity 2025-readiness/blocker status is binding until source/input gaps are resolved and the user authorizes implementation.

---

## 5. Role-preserving multi-clock architecture

Heterogeneous engines must not be flat-voted or ranked as though they solve the same task.

### Strategic block

- Monthly H=1 experts: independent price-level forecast plus strategic anchor/context.
- `MONTHLY_DIRECTION_3M`: slow strategic prior; not a daily trigger.

### Trend-structure block

- **FAST:** tactical daily trend state, flip, age and persistence; candidate early weakening evidence.
- **SLOW:** completed-week trend confirmation, alignment/conflict and state age; confirmation/new-regime evidence, currently low priority.

Frozen FAST rule:

- SMA20;
- current and previous completed daily state relative to SMA20;
- both UP -> `ROBUST_UP`;
- both DOWN -> `ROBUST_DOWN`;
- otherwise `MIXED`;
- exactly two-day persistence.

Frozen SLOW rule:

- completed W-FRI weekly closes;
- incomplete current week excluded;
- SMA4;
- previous and current completed week on same side -> `ROBUST_UP` / `ROBUST_DOWN`;
- otherwise `NOT_YET_ROBUST`;
- exactly two completed-week persistence.

### Regime / stress / risk block

- `BOCPD_HOURLY_B2_ADAPTIVE_HAZARD_V5_RESEARCH`: primary hourly BOCPD research context; causal adaptive hazard from run length and lagged volatility; no equal direction vote.
- `BOCPD_HOURLY_B2_PRE2025_BASELINE_R2_RESEARCH`: frozen constant-hazard benchmark only.
- `GVZ_RISK`: retained options-implied gold-market risk/severity context only; never an equal direction vote and never silently converted into UP/DOWN.
- post-BOCPD future-change-time challenger: next research lane; must model prospective time-to-change / residual-time or equivalent explicit-duration hazard without reusing 2025 for tuning.
- `EMERGENCY_LEVEL`: **suspended / redesign required**.
- `EMERGENCY_REVERSAL`: **suspended**.
- realized volatility: retrospective uncertainty/severity/event context; never a predictor of the same realized event.
- chronology-safe optional VIX: risk context only.

### Event / shock block

- `MACRO_EVENT_SUCCESSOR_V2`: governed release-aware event-surprise identity, but **suspended for the current GC-BREAK research sequence**.
- `MARKET_SHOCK_V3`: research-only realized intraday shock intensity/concordance around eligible events.

Historical Macro Event contracts remain audit lineage. Their existence does not make Macro Event the next work item.

### Reliability / meta block

Permitted evidence includes matured reliability, support count, evidence age, explicit missingness, missing reason, class-degeneracy flags and justified regime/event-conditional reliability.

`NO_SIGNAL` / abstention is valid when support is insufficient.

---

## 6. Native clocks, availability time and evidence age

The architecture is multi-clock by design:

- **GC-BREAK main origin:** daily completed reference origin;
- **FAST:** tactical completed-daily clock;
- **SLOW:** completed weekly clock;
- **BOCPD research (V5/R2):** eligible completed-hour XAU clock; output usable only after the corresponding one-hour bar is complete;
- **future change-time challenger:** native clock must be explicitly preregistered; no output may be credited before all inputs required at that origin are complete;
- **Monthly H=1 / Monthly Direction:** strategic monthly clock;
- **Macro Event / Market Shock:** event-triggered intraday clock when that research lane is active;
- **GVZ_RISK:** completed GVZ daily-close clock under the frozen R4.1 implementation.

A slower state may be carried forward only under its native-clock semantics and must carry explicit `age` / `state_age` information.

Missing channels may not be silently imputed as neutral or zero.

### 6.1 Binding signal-availability rule

A model output cannot be credited before the latest input needed to compute that output was actually available.

For completed-daily-close engines such as FAST and GVZ_RISK:

- a state calculated using date `t` close becomes usable only **after that close**;
- a volatility event realized during date `t` cannot be called an `EARLY_HIT` using a signal that itself requires date `t` close;
- same-date daily-close overlap is at most `SAME_EVENT_CONFIRM` / same-date diagnostic unless an earlier timestamp independently proves availability;
- genuine one-session-ahead warning comparison must use the latest completed engine origin strictly before the event session;
- no event date may be used to select which historical engine date is treated as the signal origin.

Each motor must declare its native decision time before outcome overlay.

---

## 7. Governance locks

Binding rules:

- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`
- `NOT_PROVEN_EXPERT_SELECTION_RULE`
- `NOT_PROVEN_POSITION_MAPPING`
- no automatic `BUY / SELL / HOLD / EXIT / REDUCE`
- no flat/equal-weight voting across heterogeneous engines
- no hindsight threshold tuning
- no random-split time-series validation
- no silent provider substitution
- no interpolation or forward-fill of missing canonical XAU session references
- no backdating of reconstruction/replay evidence
- no historical reconstruction relabelled as prospective evidence
- no target/future observation inserted into an earlier origin
- no challenge/stress result used to retune that locked challenge/stress evaluation
- no production forecast/decision authority write without explicit later authorization
- no stale context labelled fresh merely because an identity remains registered
- no fabricated state or feature when a historical channel is unavailable
- no rejected model family rescued by post-score tuning
- no same-day completed-close value labelled as a pre-event warning for an event already realized during that session
- no event-conditioned backward search presented as alarm precision, warning accuracy or false-warning performance
- no post-hoc warning horizon chosen because it makes 2025 results look better
- no suspended motor silently reactivated merely because historical code/contracts remain in GitHub
- no ordinary BOCPD retuning represented as future-change-time prediction without a separately named identity and preregistration

When evidence is absent or unproven, use `NOT_FOUND`, `NOT_PROVEN`, `UNRESOLVED`, `BLOCKED`, `NOT_TESTABLE` or `INSUFFICIENT_SUPPORT` as appropriate.

---

## 8. Evidence classes and point-in-time semantics

Evidence classes remain separate:

- `HISTORICAL_REPLAY`: reconstructed after the original origin using information bounded to that historical origin;
- `PROSPECTIVE_SHADOW`: issued after the governed mechanism is frozen/deployed and before the relevant future outcome is known;
- `LIVE_PRODUCTION`: only when separately authorized.

For every historical origin, all features, model states and reliability estimates must respect information available at that origin. Later target observations, future price paths and later revisions are forbidden from predictor construction or model selection.

Historical reconstruction is never proof that a signal was actually issued live at that historical time.

---

## 9. Canonical XAU / NY17 contract

Canonical tactical XAU series:

`XAU_EOD_TWELVE_NY17`

Provider/input contract:

- provider: Twelve Data;
- symbol: `XAU/USD`;
- interval: `1min`;
- requested timezone: `America/New_York`;
- accepted bar: unique exact `16:59:00` source bar;
- accepted value: `close` after positive/range-valid OHLC checks;
- stored timestamp: corresponding 17:00 ET session boundary converted to UTC;
- fallback: none;
- interpolation: forbidden;
- forward-fill: forbidden;
- alternate-provider substitution: forbidden;
- official CME/EBS settlement/fixing claim: forbidden.

The Twelve Data value is Gold Control's internal NY17 reference, not an official CME settlement/fixing price.

Exact historical provider gaps remain gaps; a different bar may not be inserted into the canonical series merely to improve coverage.

---

## 10. Frozen GC-BREAK structural event-label rule

The primary GC-BREAK ground-truth event definition is engine-independent.

Binding rule:

- family: volatility-normalized directional change;
- daily log return;
- volatility scale: trailing 20 governed observations;
- sigma lagged one observation;
- primary threshold: `k = 3.0`;
- current regime extreme updated causally;
- break timestamp: first governed observation whose adverse move from the regime extreme reaches the frozen threshold;
- after an event, regime direction flips and the extreme resets to the event close.

`k = 2.5` is sensitivity-only and may not replace `k = 3.0` because a downstream model scores better.

FAST, SLOW, Monthly Direction, Emergency, BOCPD, GVZ, Macro Event, Market Shock and learned models may not define this structural ground truth.

---

## 11. Frozen 2025 volatility challenge

Authority file:

`gold_axis_2026/GOLD_CONTROL_2025_VOLATILITY_CHALLENGE_CONTRACT_V1_2026-09-15.md`

Research event source:

`XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`

This source is research-only and does not replace canonical exact-16:59 NY17 runtime semantics.

Cross-check facts:

- 2025 governed research weekdays: **255**;
- same-day overlap with exact 16:59 one-minute cache: **197**;
- equal close values on same-day overlap: **197 / 197**;
- directly comparable daily-return pairs: **168**;
- return correlation: **1.000000**;
- mean absolute return difference: **0.000000 percentage points**;
- sign agreement: **168 / 168**.

Frozen event formula:

`r_t = 100 * ln(P_t / P_{t-1})`

`sigma20_t = sample standard deviation of the 20 immediately preceding governed daily log returns`

`z_t = r_t / sigma20_t`

Frozen tiers:

- **MAJOR:** `|z_t| >= 2.0`
- **EXTREME:** `|z_t| >= 3.0`

The frozen inventory contains **19 event-days**, of which **5 are EXTREME**, with **14 UP / 5 DOWN**:

1. `2025-02-10` UP `+2.3407`
2. `2025-02-14` DOWN `-2.2468`
3. `2025-02-18` UP `+2.1885`
4. `2025-03-13` UP `+2.1237`
5. `2025-04-04` DOWN `-3.3930` EXTREME
6. `2025-04-09` UP `+3.2185` EXTREME
7. `2025-04-10` UP `+2.3440`
8. `2025-07-21` UP `+2.0611`
9. `2025-08-01` UP `+2.5481`
10. `2025-09-02` UP `+2.6673`
11. `2025-09-22` UP `+2.6254`
12. `2025-09-29` UP `+2.3040`
13. `2025-10-06` UP `+2.7911`
14. `2025-10-13` UP `+2.5043`
15. `2025-10-16` UP `+2.9074`
16. `2025-10-17` DOWN `-2.0589`
17. `2025-10-21` DOWN `-4.1054` EXTREME
18. `2025-12-22` UP `+4.0174` EXTREME
19. `2025-12-29` DOWN `-6.6415` EXTREME

These dates are retrospective outcomes, not information available to a live motor before they occur.

### 11.1 Engine-first evaluation lock

The binding evaluation direction is **engine first, challenge overlay second**.

For every evaluated engine:

1. run/replay the engine across its complete eligible origin set on its native clock;
2. retain signals, abstentions, state transitions, episode onsets, persistence/age, missingness and blocked/not-testable states;
3. freeze the complete engine-output table before outcome overlay;
4. only then compute event coverage, false-warning burden, lead/lag, same-event confirmation and role-specific support;
5. do not choose warning horizon, carry window, threshold, score mapping or episode rule after viewing challenge outcomes;
6. retain exact engine signal dates even when no event is nearby.

Event-conditioned backward lookup alone is diagnostic and is not alarm-performance evidence.

---

## 12. Current validated motor evidence

### 12.1 FAST

Evidence class: `HISTORICAL_REPLAY / RETROSPECTIVE_DIAGNOSTIC`.

- complete 2025 governed timeline: **255 daily rows**;
- frozen rule: SMA20 + two completed-daily observations on the same side;
- new robust episode onsets: **22**;
- descriptive same-direction future-event incidence after onset: 1-day `1/22`, 3-day `2/22`, 5-day `3/22`, 10-day `5/22`;
- same-event day `1/22` is not early-warning credit under completed-close semantics.

FAST is retained as a **daily tactical trend-state engine** and is not proven as a standalone volatility-warning engine.

### 12.2 GVZ_RISK

Role: **RISK_ONLY**. No UP/DOWN direction vote.

Frozen R4.1 mapping:

- `GVZ <= 25.9795` -> `NORMAL`, cap `1.0`;
- `25.9795 < GVZ <= 30.5238` -> `ELEVATED`, cap `0.5`;
- `GVZ > 30.5238` -> `PANIC`, cap `0.25`.

2025 historical replay facts:

- source: `GVZ_CBOE_FRED_MIRROR_RESEARCH_V1`;
- valid daily observations/scored rows: **250 / 250**;
- frozen-score mismatch: **0**;
- FAST used in score: **false for all rows**;
- `NORMAL`: **237** days;
- `ELEVATED`: **10** days;
- `PANIC`: **3** days.

Same-date overlap with a completed GVZ daily close is not credited as pre-event warning for an event already realized that date.

GVZ_RISK is retained as a **selective market-stress / risk-context motor**. General volatility-day prediction performance is not proven; the PANIC sample is too small for promotion claims.

### 12.3 BOCPD

See Section 4. The retained BOCPD research authority is V5 + R2 only. BOCPD is retained as regime/change context; it is not to be further tuned on visible 2025 outcomes as the project’s future-change-time predictor.

### 12.4 Macro Event

`MACRO_EVENT_SUCCESSOR_V2` remains a governed runtime registry identity, and historical V3/V4 research contracts remain traceable, but the Macro Event lane is **suspended for the current GC-BREAK research sequence**.

Do not interpret old Macro Event preregistrations, workflows or runtime registration as an instruction to resume it next. Reactivation requires explicit new project direction/change control.

### 12.5 Emergency and SLOW

- `EMERGENCY_LEVEL`: suspended / redesign required.
- `EMERGENCY_REVERSAL`: suspended.
- `SLOW`: low-priority confirmation/new-regime context; not the immediate next motor.

### 12.6 Next motor / future-change-time challenger

The next research motor is a **new, separately named future-change-time prediction challenger**. Its scientific family is residual-time / explicit-duration / Bayesian online prediction of changepoints or a closely equivalent causally valid duration-hazard formulation.

Binding design boundary:

- objective: estimate whether / when a break or changepoint is approaching, rather than only detect that a regime change may already have occurred;
- BOCPD V5 remains complementary regime/change context and is not silently renamed into this motor;
- formation/development must use pre-2025 chronology; 2025 is not available for parameter tuning or model selection;
- no random split;
- native clock, warning horizon, episode formation, output semantics and evaluation rule must be preregistered before outcome overlay;
- exact model identity and parameterization remain `NOT_FROZEN` until that preregistration is created.

---

## 13. Frozen research split

### Formation / development

`2022-01-01 .. 2024-12-31`

Permitted use: label-quality inspection, baseline development, rolling/prequential internal validation, calibration/reliability estimation and architecture development under frozen governance.

### Retrospective Challenge

`2025-01-01 .. 2025-12-31`

Locked retrospective challenge. No threshold, feature or model choice may be derived from its outcomes and then claimed as untouched challenge evidence.

### Retrospective Stress / transport

`2026-01-01 .. 2026-08-31`

Researcher-visible retrospective stress/transport period; not fresh blind OOS evidence.

### Prospective Shadow

Begins only after final architecture/parameter freeze and before future outcomes are known.

Random splitting is forbidden.

---

## 14. Current work-package and sequencing status

1. **Coverage / PIT audit — COMPLETE**
2. **WP0 — State / break-label contract — COMPLETE / FROZEN**
3. **WP1 — PIT-safe formation panel — COMPLETE**
4. **WP2 — independent break-event inventory — COMPLETE WITH DATA-DENSITY WARNING**
5. **Split Freeze — COMPLETE / PRE-SCORE FROZEN**
6. **WP3 — preregistered simple formation baselines — COMPLETE WITH LIMITATIONS**
7. **2025 volatility challenge inventory — FROZEN**
8. **FAST full-timeline replay — COMPLETE**
9. **GVZ_RISK full-timeline historical replay — COMPLETE**
10. **BOCPD retained research comparison — COMPLETE FOR CURRENT V5/R2 CHECKPOINT**
11. **Macro Event — SUSPENDED FOR CURRENT SEQUENCE**
12. **Emergency Level/Reversal — SUSPENDED; Level requires redesign**
13. **SLOW — LOW PRIORITY / NOT NEXT**
14. **Post-BOCPD future change-time challenger — NEXT GC-BREAK RESEARCH LANE; exact identity/parameters require preregistration**
15. **Legacy parallel direction-research lane — RSM/ERSM CLOSED / DO_NOT_REVISIT; VLMC family CLOSED / NO_PROMOTION; BCT family CLOSED / NO_PROMOTION; B-CARS / Realized-Probability family CLOSED / NO_PROMOTION; exact CARB NOT_PROVEN and not implemented**
16. **Literature-backed direction-engine queue — REGISTERED / RESEARCHED / DATA-READINESS CLASSIFIED / NOT IMPLEMENTED: Sadorsky Tree-Tech; Basher-Sadorsky RF-Macro; Bonato QBoost Realized-Moments; Parisi Rolling-Ward; Altuntaş AlexNet-Candle; Yadav Tech-ML; Sulman DL-Ensemble; Mahato-Attar Ensemble; Zhang Return-ML. Implementation requires explicit user authorization; 2025 remains a locked retrospective challenge under Section 4.3.5.10.**
17. **WP4 role-preserving integration/state-transition work — AFTER the new GC-BREAK challenger has a frozen design/evidence checkpoint**
18. **Architecture/parameter freeze — PENDING**
19. **Prospective shadow — PENDING FINAL FREEZE**

The next **GC-BREAK** research lane is therefore not inferred from runtime-registry order: it remains the separately governed future-change-time challenger defined in Section 12.6. In parallel, the Section 4.3.5 direction-engine queue is registered for later standalone testing but is not yet authorized for implementation. Macro Event, Emergency and SLOW remain outside the immediate GC-BREAK next step unless explicitly reactivated.

---

## 15. Post-BOCPD future model-development rule

Ordinary BOCPD is primarily an online **change-detection / regime-context** mechanism: after new evidence arrives, it updates belief that a change may have occurred. The next scientific question is different: whether the system can estimate **time-to-change / residual time / approaching-break hazard before the break**.

Accordingly, the next motor must be a separately named and preregistered future-change-time challenger. Preferred research families include:

- residual-time prediction under non-geometric duration models;
- explicit-duration / semi-Markov or duration-hazard formulations;
- Bayesian online prediction of changepoints / learned or structured time-to-change models;
- another low-dimensional causal duration-hazard formulation only if its role and timing semantics are explicitly frozen.

An HMM/HSMM may be used as an implementation family **only if it serves this frozen future-change-time objective**; `HSMM` by itself is not the binding motor identity and is not automatically selected.

The exact identity, features, native clock, duration state, horizon/output definition, loss/objective, episode rule and evaluation metrics must be preregistered before the model is run against outcomes used for evaluation.

Chronology lock for the new challenger:

- use 2022–2024 as the pre-2025 research/design universe under time ordering;
- do not use 2025 to choose thresholds, duration family, features, warning horizon or parameterization;
- 2025 is researcher-visible and cannot be relabelled as pristine holdout after design choices informed by it;
- no random split;
- BOCPD V5/R2, FAST and GVZ may contribute only in role-preserving origin-safe form; no flat equal vote.

High-capacity boosting, mixture-of-experts and deep-learning escalation remain blocked until a simpler duration/hazard challenger justifies additional complexity under time-ordered evidence.

---

## 16. Historical research interpretation

Historical fixed-horizon, 1D/3D, V1.48/V1.49, HS-SDL-DMA and related studies remain historical/auxiliary research only.

Old result files or artifact names are not current project authority. Historical traceability belongs in Git history and/or immutable evidence storage.

Specific superseded interpretation locks:

- old event-conditioned FAST `11/19` is not current alarm performance;
- same-date GVZ daily-close overlap is not early-warning evidence;
- any result that hides full-year engine outputs by starting only from realized event dates is invalid for alarm-performance claims;
- old Macro Event research artifacts do not override the current Macro research suspension;
- superseded BOCPD identities do not re-enter because historical files or commits exist;
- an ordinary BOCPD retune is not the approved substitute for the new future-change-time challenger.

---

## 17. Neon / write authority

GC-BREAK currently has **no production forecast, decision or trading authority**.

Unless separately authorized later:

- no production decision-signal writes;
- no BUY/SELL/action mapping;
- no automatic selector/ensemble writes;
- no mutation of legitimately issued historical records;
- no speculative schema expansion solely for an unaccepted research challenger.

Research panels, labels, predictions and evaluations must remain logically separated and lineage-complete.

Historical research backfills must use explicit research series identities and truthful provenance. They may not silently overwrite direct-authority series identities.

---

## 18. Promotion and prospective-evidence rule

Binding scientific order:

`PIT-safe formation`

-> `independent event inventories`

-> `engine-first full native-clock replay`

-> `freeze exact engine outputs and signal timestamps`

-> `outcome overlay`

-> `role-preserving evaluation`

-> `BOCPD context freeze`

-> `separately preregistered future-change-time challenger`

-> `role-preserving integration / state-transition work`

-> `same-origin ablation / optional extensions`

-> `architecture + parameter freeze`

-> `prospective shadow`

A model is not promoted because it is theoretically elegant or retrospectively impressive. Promotion requires reproducible, time-ordered incremental evidence with adequate support and no leakage.

The strongest future claim comes only from outcomes first observed after final architecture/parameter freeze.

---

## 19. Final binding summary

Gold Control is a **role-preserving, multi-clock sequential early-warning / regime-transition research programme** running in parallel with an independent monthly H=1 price-level forecasting programme.

Two distinct retrospective event universes are explicit:

1. frozen GC-BREAK structural-break labels;
2. frozen 2025 volatility challenge of 19 abnormal daily moves.

Current validated motor checkpoint:

- FAST: replay complete, retained tactical context, standalone volatility warning not proven;
- GVZ_RISK: replay complete, retained risk context, no direction vote;
- BOCPD: V5 primary research reference + R2 frozen benchmark only; retained as regime/change context;
- Macro Event: runtime registry identity retained but **current research lane suspended**;
- Emergency Level/Reversal: suspended, with Level requiring redesign;
- SLOW: low priority, not next.

The **next GC-BREAK research motor/lane** is a new separately named **future-change-time prediction challenger** based on residual-time / explicit-duration / Bayesian online changepoint-prediction principles (or a causally equivalent preregistered duration-hazard formulation). Exact model identity and parameters are not yet frozen; the scientific lane is frozen. It must be designed with pre-2025 chronology and may not use visible 2025 outcomes for tuning.

In parallel, the direction-research families remain governed. RSM/ERSM is permanently closed as `TERMINATED / FAILED_METHOD_FAMILY / DO_NOT_REVISIT`. The VLMC family is now `CLOSED_FOR_CURRENT_DIRECTION_RESEARCH_SEQUENCE / NO_PROMOTION`: corrected VLMC-BS V2 found a real but unstable signal; Fixed-Share failed 2025 generalization; COVLMC-X3 collapsed to neutral; and the governed VLMC-C 104 successor failed pre-2025 direction validation (balanced 0.4417, DOWN sensitivity 0.05 versus parent 0.5583 / 0.45) and then forecast 52/52 UP in the unchanged 2025 replay. No further VLMC rescue/tuning is authorized unless the user explicitly reopens the family. BCT/CTW-52 is `NO_PROMOTION / WEAK_DIRECTIONAL_DISCRIMINATION`; it materially improves probability stability versus VLMC-BS but collapses to 52/52 UP forecasts in the 2025 replay. Its final published real-valued successor `DIRECTION_BCTX_AR_V1_RESEARCH` was evaluated under frozen pre-2024 evidence selection: 2024 balanced accuracy reached 0.5584 but DOWN sensitivity was only 0.1538, failing the preregistered gate; unchanged 2025 replay had balanced accuracy 0.4865, DOWN sensitivity 0 and 51/52 UP forecasts. The BCT direction family is therefore `CLOSED_FOR_CURRENT_DIRECTION_RESEARCH_SEQUENCE / NO_PROMOTION` unless explicitly reopened by the user. Source-form B-CARS V1 is blocked by genuine pre-2025 boundary up-ratios and was not scored. Its Smithson-Verkuilen successor failed pre-2025 direction validation. A final authority scan found the Realized Probability research line; exact CARB mathematics remained `NOT_PROVEN`, so no CARB was invented. The source-verifiable `DIRECTION_REALP_CARR_V1_RESEARCH` successor used hourly RealP plus the published asymmetric CARR/QMLE and RealP-on-lambda regression. It failed the frozen 2024 gate (balanced 0.4651, DOWN sensitivity 0.1154, accuracy 0.4717) and unchanged 2025 replay deteriorated to balanced 0.4444 with 0 DOWN sensitivity. The B-CARS / Realized-Probability direction family is therefore `CLOSED_FOR_CURRENT_DIRECTION_RESEARCH_SEQUENCE / NO_PROMOTION` unless explicitly reopened. None may override GC-BREAK. The higher-moment direction-probability method is not selected for this set.

A new literature-backed direction-engine queue was registered on 2026-09-21 without reopening those closed families: `DIRECTION_SADORSKY_TREE_TECH_V1_RESEARCH`, `DIRECTION_BASHER_SADORSKY_RF_MACRO_V1_RESEARCH`, `DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_V1_RESEARCH`, `DIRECTION_PARISI_ROLLING_WARD_V1_RESEARCH`, `DIRECTION_ALTUNTAS_ALEXNET_CANDLE_V1_RESEARCH`, `DIRECTION_YADAV_TECH_ML_V1_RESEARCH`, `DIRECTION_SULMAN_DL_ENSEMBLE_V1_RESEARCH`, `DIRECTION_MAHATO_ATTAR_ENSEMBLE_V1_RESEARCH` and `DIRECTION_ZHANG_RETURN_ML_V1_RESEARCH`. These identities are `REGISTERED_ONLY / NOT_IMPLEMENTED`. Bonato's spot-XAU realized-moment adaptation and Parisi's Gold/DJIA adaptation have current data sufficient for a preregistered 2025 retrospective challenge; Altuntaş and Yadav require daily OHLC completion; Sadorsky, Basher-Sadorsky, Sulman and Zhang have source-input gaps; Mahato-Attar remains blocked by incomplete method specification. No candidate may use 2025 for feature, horizon, threshold, architecture or hyperparameter selection. For Yadav and Sulman, the source papers themselves used 2025, so a Gold Control 2025 replay is external-literature-informed transport evidence rather than independent confirmatory OOS evidence. No implementation is authorized until the user explicitly selects the next candidate and missing inputs are reviewed.

All future work must preserve point-in-time integrity, native engine clocks, role semantics, engine-independent event definitions, time-ordered validation, explicit missingness and strict separation of retrospective diagnostics from genuine prospective evidence.
