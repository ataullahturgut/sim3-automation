# R48 — May 2026 H3 dual-source completed-price truth versus historical unrepaired vintage: full 21-row independent test

**Executed 2026-10-12.** Status: `COMPLETE_VENDOR_TRUTH_CROSSCHECK_PASS`; `PREREPAIR_SOURCE_SENSITIVITY_RECOMPUTED`; `BASE_EXPERT_TRUE_ASOF_REFIT_UNAVAILABLE`; `LIVE_ISSUED_H3=NO`. Never relabel the original H3 horizon or overwrite R40–R47.

## Purpose: keep two questions separate
1. Does fixed historic May **H3 gold-average-to-gold-average target direction** and its frozen model prediction comparison reproduce after full-day-data correction, including *independent intraday gold vendors*? YES.
2. Can it be reproduced with real source price vintages from around the historical issue dates, including different observation and release clocks, and can the entire nested H3 model be refit? The old-vintage prices **materially disagree** with the independent full-day target; FULL contemporaneous model training/issuance cannot be certified from available audit records. Quantitative sensitivity recalculated below, with no bogus 'live' accuracy.

## 1. Exactly frozen 21 May issues, original target and independent full-day gold truth
Model freeze: DPTC-Q95/SAGE-V2+RuleFlow-V3-TG/V5, native `feature_cutoff_date D0 -> third retained source gold observation day D3`; issue day D1 is one retained source date after D0. The target is `sign(log(Au_mean[D3]/Au_mean[D0]))`; each source day full UTC date (Turkey 03TR→next 03TR). No 09/15TR execution target or +72h substitution.

`GOLD_R42_20261012_ORIGINAL_H3_SOURCE_TIME_MAY_UTC_AVERAGE_RECONSTRUCTION.csv` provides the full UTC-day averaged historical frozen StakTrakr `sqld` gold target, and independent 15-minute **Dukascopy and HistData** UTC-day midmean reconstructions. Both independent vendor **direction labels agree 21/21** with fully completed original 21/21 target signs. Numerical retrospective score (unchanged frozen model): Q95 17/21=80.95%, Q99 16/21=76.19%, SAGE+RuleFlow 13/21=61.90%, HELIOS V5 12/21=57.14%, always-DOWN 13/21=61.90%. Q95 frozen balanced accuracy 0.8221 (7/8 UP, 10/13 DOWN). Paired McNemar two-sided exact p=0.34375 against constant DOWN (7 Q95-only successes, 3 always-DOWN-only successes): no statistical proof of outperformance over simple baseline from this n=21 sample. DPTC selection was after knowing 2026 historical outcomes, so NO genuine independent OOS.

## 2. Same vendor, single historic June 3 'pre-repair' source vintage
Fetched exact historical upstream `lbruton/StakTrakr` Git commit **`67f83f4ab6ae5baaf4a35c7ce9175fbdd1dbb295`**, committed **2026-06-03T03:00:01Z = June03 06:00TR**. It contains all 21 May origin and target gold dates, Gold/Silver/Platinum/Palladium. Contrasted with original later post-repair pinned `54fdf1c8d39b7b6c7b874d0f30f784296e886044` Sep29. **These are two coherent full-month archived price vintages**, but June source may freeze incompletely sampled intraday averages, and June3 is AFTER all May forecast issue dates; DO NOT call it May 'at-issue' values or correct real target.

Fixed vote vs **both** vintage-derived gold target-label evaluations, *not model refit*:

| Retrospective fixed forecast | Fully complete daily target + independent intraday source signs | Unrepaired 2026-06-03 repo vintage target sign |
|---|---:|---:|
| DPTC Q95 | 17/21=80.95% | **13/21=61.90%** |
| DPTC Q99 | 16/21=76.19% | **12/21=57.14%** |
| SAGE + RuleFlow | 13/21=61.90% | **13/21=61.90%** |
| HELIOS V5 | 12/21=57.14% | **14/21=66.67%** |
| constant DOWN | 13/21=61.90% | **11/21=52.38%** |

Four H3 labels differ **May08 DOWN→UP, May19 DOWN→UP, May22 DOWN→UP, May27 UP→DOWN** when using unrepaired full-vintage source data. Each change turns a correct fixed Q95 vote into an incorrect one. Thus 17→13 exactly. This does NOT prove a decline in genuine prediction quality; it proves source-vintage/target construction affects retrospective scores.

Specific same-vintage price pairs USD/oz:
- **Issue May08** D0 May07: origin (unrepaired 4717.64, completed 4717.64), D3 May12: terminal (unrepaired 4763.05, completed 4706.50), label UP vs DOWN.
- **Issue May19** D0 May18: origin (unrepaired 4522.86, completed 4547.06), D3 May21: terminal (unrepaired 4528.85, completed 4530.49), UP vs DOWN.
- **Issue May22** D0 May21: origin (unrepaired 4528.85, completed 4530.49), D3 May26: terminal (unrepaired 4542.23, completed 4520.98), UP vs DOWN.
- **Issue May27** D0 May26: origin (unrepaired 4542.23, completed 4520.98), D3 May29: terminal (unrepaired 4530.32, completed 4530.32), DOWN vs UP.

## 3. Recalculated original core family predictor transformations, 21 May issues
In addition to label rescore, actually recalculated previous-day-cutoff four-metal log-return input features at lags **1,5,21 retained source weekdays** from each historic (June3) vs later complete (Sep29) Stak date/metal price set (all issue origins). The R48 second row-level CSV contains for each four metals and lag old and complete log-return, delta in basis points, and feature sign-change indicator. These differences persist beyond target labels:

| Metal | 1d lag sign changed among 21 | Median abs 1d return revision | Largest abs 1d revision |
|---|---:|---:|---:|
| Gold | 3/21 | 36.57 basis points | 235.90 bp |
| Silver | 2/21 | 57.30 bp | 816.20 bp |
| Platinum | 5/21 | 84.98 bp | 349.03 bp |
| Palladium | 7/21 | 73.04 bp | 269.75 bp |

The computed log-difference uses `log(spot_day/spot_lagged_workday)`, with the two vendor vintages, source-synchronous four metals. No price or model fitted beyond the data. It confirms changing provider vintage can alter the H3 model's predictors (not merely labels). Note that original NOVA uses additional lag 3/10 and rolling sigma20, while the per-source daily data uses all retained common dates; these R48 tests cover major metal-origin 1/5/21 predictors and not the full rederived design matrix.

## 4. Historical firstprint/source eligibility is still NOT certified
R46 confirms 21 historical May issue snapshots (sampled prior Git `v3` commit by issue 15TR): **7 missing all 4 origin metals, 12 present but vintage-revised, 2 fully equal**. Precisely verified upstream 2026 May **spot-history file-changing Git commits** in May show gap Apr30→May09; source May06 metal price cannot have been obtained from this public historical JSON at May07, although underlying sqld/API data could have been available by another route. The historical June3 frozen price set is **not** an at-May-issued time slice. There are no historic May DPTC-Q95 model artifacts: Q95 architecture frozen only October 2026. Replacing the target labels *without retraining fitted experts with at-issue vintages* cannot establish a May live forecast skill or replace original COT/macro firstprints.

## 5. Scientific verdict and next gate
- `EVAL_COMPLETE_FULLDAY=PASS`: H3 source Gold target labels independently vendor corroborated 21/21 and fixed historic Q95 accuracy 17/21; the advantage over DOWN baseline is four May events, not statistically established.
- `EVAL_PRE_REPAIR_ARCHIVE_VINTAGE=PASS`: 2026-06-03 early version reconstructs old H3 labels and four sign reversals; Q95 fixed votes align 13/21 against old inaccurate/incomplete source averages. Do not conflate with 'May PIT score'.
- `MODEL_INPUT_SOURCE_DRIFT=CONFIRMED`: independent reconstruction of 4-metal 1/5/21 feature vectors confirms substantial shifts.
- `FULL_MAY_ASOF_Q95_REFIT=NOT_POSSIBLE_FROM_CURRENT_VERIFIED_MATERIAL`: no source-complete all-history timestamped provider-vintage feature panels, no archived May model as developed after May. Distinct 'what if' simulation would require new prespecified preprocessing/source, all experts rolling fitted, and explicitly be a **simulated PIT backtest**; future post-Oct05 actual issuance needed to test live forecast claim.

Source CSVs: `GOLD_R48_20261012_MAY_H3_COMPLETED_VS_PREREPAIR_21ROW_SOURCE_VINTAGE_RESCORE.csv` and `GOLD_R48_20261012_MAY_H3_FOUR_METAL_PREDICTOR_VINTAGE_LOGRETURN_RECOMPUTATION.csv`.

Prior audit: R45, R46, R47. Original project manifest authority should link this report; no previous H3 files overwritten.
