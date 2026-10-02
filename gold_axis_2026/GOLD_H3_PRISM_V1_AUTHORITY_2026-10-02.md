# PRISM-H3 V1 — PHASE-RESOLVED INTRADAY SPECTRAL RESIDUAL MODEL

**Date:** 2026-10-02
**Identity:** `PRISM_H3_V1_RESEARCH`
**Parent:** `AURORA_H3_V1_RESEARCH`
**Status:** PREREGISTERED / RESEARCH-ONLY

## 1. Objective

Test whether AURORA's remaining H3 direction errors contain **multi-scale intraday phase / reversal information** that is not represented by the frozen IRIS aggregate return features.

PRISM does not replace AURORA. It models only a residual correction:

`logit(p_PRISM) = logit(p_AURORA) + beta' z_wavelet`.

The coefficient on the AURORA logit is fixed at 1.0. PRISM can only add a regularized latent spectral correction.

## 2. Timing

- same validated XAU/USD 1-hour source as IRIS;
- 16:00 America/New_York anchor on feature_cutoff_date;
- no forecast_issue_date or later hourly bar;
- all supervised training targets must satisfy
  `target_end_date_h3 <= current test feature cutoff`.

## 3. Fixed latent representation

For each origin:
- take the last 48 hourly XAU log returns;
- divide by 48h realized L2 norm + epsilon;
- apply stationary wavelet transform:
  - wavelet: `db2`
  - level: 3;
- for approximation and each detail scale, compute 4 chronological PAA blocks;
- latent spectral vector = 16 phase-resolved coefficients;
- append two amplitude descriptors:
  - log 48h realized norm;
  - 48h jump concentration = max(abs(r))/sqrt(sum(r^2)).

Total latent dimension = 18.

No feature or wavelet-family search is allowed.

## 4. Residual logistic model

For training row i:

`eta_i = logit(p_AURORA_i) + beta' z_i`

and

`Pr(Y_i=1)=sigmoid(eta_i)`.

Fit beta by penalized Bernoulli negative log likelihood:

`NLL + 0.5 * lambda * ||beta||^2`.

Latent features are standardized from the current matured training set only.

## 5. Frozen regularization grid

Only lambda is selected:
- 1
- 10
- 50.

Selection authority:
- Jul-Dec 2022 only.

No other architecture search.

## 6. Selection gate

Matched AURORA is comparator.

Candidate eligible if on 2022-H2:
- balanced accuracy >= AURORA;
- accuracy >= AURORA - 0.5 pp;
- Brier <= AURORA + 0.0025;
- prediction standard deviation >= 0.02.

Rank:
1. balanced accuracy;
2. accuracy;
3. Brier;
4. log loss.

Fail closed if no lambda eligible.

## 7. Frozen confirmation

Selected lambda is frozen after 2022-H2.

PRISM is a mechanism pass only if:
- 2023 accuracy >= AURORA -1 pp;
- 2024 accuracy >= AURORA -1 pp;
- 2023 Brier <= AURORA +0.003;
- 2024 Brier <= AURORA +0.003;
- 2023-2024 aggregate balanced accuracy >= AURORA.

2025/2026 are transport/stress only and cannot alter V1.

## 8. Diagnostics

Report:
- annual / aggregate accuracy, balanced accuracy, Brier, log loss;
- AURORA errors rescued by PRISM;
- AURORA correct calls broken by PRISM;
- 2026 call-by-call changed decisions;
- standardized correction coefficients from the frozen selected fit through 2022.

## 9. Scientific rationale

Wavelet decomposition provides localized time-frequency information and separates short- and longer-run fluctuations without requiring additional exogenous data. Recent self-supervised time-series work similarly emphasizes learning transferable representations that jointly encode local and global temporal structure. PRISM uses a deliberately low-capacity, fixed-transform version of that principle to reduce overfitting risk.

## 10. Governance

- No lambda, wavelet, level, latent dimension or threshold may be changed using 2023-2026 results.
- PRISM does not alter the already-frozen AURORA prospective ledger.
- A pass makes PRISM a research challenger only; prospective deployment requires a new frozen identity.
