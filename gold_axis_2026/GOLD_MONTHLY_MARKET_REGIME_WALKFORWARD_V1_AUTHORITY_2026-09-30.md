# GOLD MONTHLY — Market Regime Walk-Forward Detection V1 Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / REAL-TIME DETECTION AUDIT  
**Parent study:** GOLD_MONTHLY_MARKET_REGIME_DISCOVERY_V1  
**Purpose:** test whether the already-discovered 3-state market-regime architecture can identify the *current* regime at each month-end using only information available through that month, without forecast errors or alarm inputs.

## 1. Question

This is **not** a forecast of next month's regime.

At completed month t, ask only:

> Using market-state observations available through t, can the detector identify whether the current state is R0, R1, R2, or BELIRSIZ?

The detector must be evaluated against the frozen full-development reference labels from Market Regime Discovery V1.

## 2. Frozen source authority

Use the exact Market Regime Discovery V1 artifact:

- run: 36716979693
- artifact: 11097041821
- file: GOLD_MONTHLY_MARKET_REGIME_DISCOVERY_V1_2026-09-30.json
- artifact digest: sha256:6bf8455e93ece5dc42f06dc58930a79be2a94ea70f5f3f9da82bff8da752338e

The walk-forward detector may read only these market-state columns from the artifact:

- Gold_r1
- Gold_r3
- Gold_level_gap
- Gold_rv_ratio
- cross_metal_dispersion
- gvz_ratio12
- cftc_mm_net_oi
- cftc_oi_ratio12
- broad_usd_logchg
- nom10_change
- real10_change
- etf_combined_flow
- etf_outflow_breadth

Reference state/probability/OOD fields in the artifact are **evaluation-only** and must not enter scaler, PCA, HMM fitting, state naming, confidence, or OOD calculations for the walk-forward detector.

## 3. Forbidden inputs

The detector must not use:

- ChHHO forecast errors;
- model forecasts;
- HIGH/MEDIUM/NORMAL error labels;
- A/B/C/D/E/G/H/I1/I2/T1 alarm flags;
- router/fallback outputs;
- future market-state observations after the evaluated month.

## 4. Walk-forward clock

Effective panel begins 2010-07.

Primary replay begins 2015-07 so each first origin has at least 60 completed prior months.

For every evaluated month t:

1. fit only on months strictly before t;
2. fit StandardScaler on that expanding training history;
3. fit PCA on that history only;
4. retain the minimum PCs explaining >=85% variance, capped at 6 and floored at 2;
5. fit a diagonal-covariance Gaussian HMM with **K=3**, using 10 deterministic seeds and retaining the highest training log-likelihood;
6. filter the training history and then the current month t;
7. assign the current state from the filtered posterior;
8. map HMM state IDs to R0/R1/R2 using only the training-history state profiles, with the same canonical rule as Discovery V1: ascending state mean Gold_r1 (volatility only as deterministic tie-break context);
9. if maximum filtered posterior <60%, output **BELIRSIZ**;
10. compute current OOD status from the current month's maximum state-emission log density against the 5th percentile of training-history emission log density. OOD is an additional AŞIRI/OOD flag; it does not silently force a different R-state.

The current month is never included in scaler/PCA/HMM parameter fitting.

## 5. Fixed architecture vs historical model selection

K=3 is frozen because Market Regime Discovery V1 already established the primary persistence-aware architecture before this operational-detection audit.

Therefore:

- 2025-01..2026-08 is the cleanest transport portion for the frozen K=3 architecture.
- 2015-07..2024-12 is a retrospective replay/backcast of that architecture, useful for detection-timing diagnostics but not an untouched model-selection test.
- In particular, the 2024-04 R2 onset test is a replay diagnostic, not a claim that K=3 had already been selected prospectively by 2024-04.

## 6. Frozen reference

Reference labels are the Discovery V1 monthly HMM assignments.

For comparison:

- reference posterior >=60% -> reference R0/R1/R2;
- reference posterior <60% -> reference BELIRSIZ;
- reference OOD remains a separate flag.

The walk-forward detector never sees the reference label before producing its own label for that month.

## 7. Required metrics

Report separately for:

- full replay: 2015-07..2026-08;
- core recent period: 2022-01..2026-08;
- frozen-architecture transport: 2025-01..2026-08.

For each period report:

- number of months;
- walk-forward BELIRSIZ rate;
- walk-forward OOD rate;
- exact agreement with reference labels;
- strict R0/R1/R2 accuracy on reference-confident months, counting walk-forward BELIRSIZ as a miss;
- decided-only accuracy on months where both sides are confident R-states;
- per-regime recall for R0/R1/R2;
- balanced accuracy = mean of available R0/R1/R2 recalls;
- confusion matrix with reference rows R0/R1/R2 and walk-forward columns R0/R1/R2/BELIRSIZ.

## 8. Transition detection

Using the sequence of confident reference states, identify every transition from one confident regime to another, allowing BELIRSIZ reference months to form a bridge.

For each reference transition, report:

- transition month;
- previous and new reference regime;
- first month at or after the transition where walk-forward detector confidently outputs the new regime;
- detection delay in months, censored after 6 months if not detected.

Mandatory checkpoints:

- 2024-04 R2 onset;
- 2026-05 and 2026-06 ambiguity/transition zone;
- 2026-07 and 2026-08 R1 stabilization.

## 9. Governance

This audit may conclude only whether real-time regime detection is sufficiently stable/descriptive to justify a later regime-conditioned alarm study.

This audit does **not**:

- select alarms;
- suppress alarms;
- weight alarms;
- tune alarm thresholds;
- correct forecasts;
- route between forecasting models.

No alarm x regime reliability calculation is authorized until this walk-forward audit is inspected.
