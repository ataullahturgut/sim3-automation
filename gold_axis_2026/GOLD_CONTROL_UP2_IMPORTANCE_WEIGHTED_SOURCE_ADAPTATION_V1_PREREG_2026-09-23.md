# GOLD CONTROL — IMPORTANCE-WEIGHTED HISTORICAL SOURCE ADAPTATION FOR UP-2 FAILURE DETECTOR V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `UP2_IMPORTANCE_WEIGHTED_SOURCE_ADAPTATION_V1_RESEARCH`  
**Role:** use older route-consistent labeled residual rows without pretending they were historical UP-2 calls  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Scientific basis

This study uses **covariate-shift / sample-selection correction by importance weighting**.

Core idea:
- the older 2020–2021 route-consistent residual pool has valid realized UP/DOWN labels;
- only a tiny subset can be reconstructed as strict historical UP-2 calls because the frozen UP-2 threshold requires substantial prequential calibration support;
- therefore, instead of fabricating historical UP-2 calls, reweight the full older labeled residual pool so that its **origin-state covariate distribution resembles the 2022 UP-2-call population**.

This is a standard transfer-learning idea under covariate shift:
`w(x)=p_target(x)/p_source(x)`.

References motivating the method:
- Sugiyama, Krauledat & Müller (2007), importance weighting under covariate shift;
- Vogel et al. (2020), weighted empirical risk minimization under sample-selection bias;
- robust importance-weighting literature motivating weight truncation when estimated ratios are unstable.

The key assumption is not guaranteed:
`P(Y|X)` must be sufficiently stable between source and target after conditioning on the chosen features.
Therefore this experiment is a falsification study, not an authority upgrade.

## 2. Source population

Corrected external 2020–2021 route-consistent residual rows only:

`SQRT HIGH RISK + Frozen Primary UP Verifier V2 ABSTAIN`.

Expected exact source:
- 2020: 72 =35 UP +37 DOWN;
- 2021: 26 =11 UP +15 DOWN;
- pooled source: **98 =46 UP +52 DOWN**.

Labels:
- failure target = 1 when realized target close is DOWN;
- failure target = 0 when realized target close is UP.

Important:
these 98 rows are **not relabeled as historical UP-2 calls**.

## 3. Target covariate population

Use only the **covariates** of frozen 2022 One-Sided UP-2 calls.

Expected:
- n=7;
- outcomes are not used to estimate source-to-target weights.

The 2022 call population defines the target covariate domain because it is the first governed year in which actual UP-2 calls exist.

## 4. Frozen adaptation/failure features

Use only the three Stage-4 mechanism variables:

1. `last_hour_trend_r2`
2. `sqrt_score`
3. `late_downside_intensity`

The same three variables are used for:
- source-to-target density-ratio estimation;
- the failure detector.

No feature search.

## 5. Density-ratio estimation

Combine:
- source rows: domain label 0;
- 2022 target-call covariate rows: domain label 1.

Standardize the three variables on the combined domain-estimation sample.

Fit:
- LogisticRegression;
- L2;
- C=1.0;
- lbfgs;
- no class weighting.

For a source row:
`eta(x)=P(domain=target|x)`.

Estimate:
`density_ratio = eta/(1-eta) * N_source/N_target`.

For numerical stability:
- clip eta to [1e-6, 1-1e-6];
- cap the raw density ratio at **10.0**;
- normalize capped source weights to mean 1.0.

No cap sweep.

Report:
- raw/capped weight distribution;
- effective sample size `ESS=(sum w)^2/sum(w^2)`;
- domain-classifier AUC as a descriptive shift diagnostic.

Minimum support gate:
- ESS >=20.
If ESS <20, block weighted-model interpretation.

## 6. Failure detector

Fit two fixed comparators on the same 98 older source labels:

### A. UNWEIGHTED_SOURCE
- L2 logistic;
- C=1.0;
- three frozen features;
- source-only standardization;
- no sample weights.

### B. IMPORTANCE_WEIGHTED_SOURCE
- identical model and standardization;
- sample weights from section 5.

Decision for both:
- veto if `p_fail >=0.50`;
- veto means **ABSTAIN**, never DOWN.

No threshold search.

## 7. Chronological evaluation

### 2022 target-domain diagnostic
Evaluate both models on the 7 frozen 2022 UP-2 calls.

Caveat:
- their covariates were used to estimate domain weights;
- their outcome labels were not used for either detector.
Therefore this is diagnostic, not independent validation.

### 2023–2024 forward guard
Expected:
- n=4;
- all four are CAPTURED_UP;
- no false-UP exists.

Forward retention gate:
- retain >=3/4 true UPs.

### Locked 2025 transport
Expected:
- n=25 =13 CAPTURED_UP +12 FALSE_UP_ACTUAL_DOWN.

Transport-supportive gate:
- remove >=3/12 false-UPs;
- retain >=10/13 captured-UPs.

2025 cannot change weights, features, cap, model, or threshold.

## 8. Comparative interpretation

The weighted method is considered **adaptation-useful** only if:
- ESS gate passes;
- 2023–2024 forward retention gate passes;
- 2025 transport-supportive gate passes;
- and its 2025 trade-off is not worse than the unweighted source comparator on both false-UP removal and true-UP retention.

Because the only pre-2025 forward guard has no false-UP cases, even a successful result remains:
`SAMPLE_LIMITED / NOT_CERTIFIED`.

Allowed final statuses:
- `BLOCKED_IMPORTANCE_WEIGHT_ESS`
- `IMPORTANCE_WEIGHTED_ADAPTATION_NOT_SUPPORTED`
- `IMPORTANCE_WEIGHTED_SIGNAL_SAMPLE_LIMITED_NOT_CERTIFIED`

## 9. Integrity

Mandatory:
- reproduce exact 2020–2021 residual counts;
- source-feature external/governed transfer for promoted mechanism variables must remain consistent with already frozen audits;
- exact 2022/2023/2024/2025 UP-2 call counts must reproduce.

## 10. Governance

- no random split;
- no fabricated historical UP-2 calls;
- no source-label relabeling;
- no feature/hyperparameter/threshold/cap sweep;
- no 2025 tuning;
- no 2026 use;
- no DOWN conversion;
- DB read-only;
- no runtime/production promotion.
