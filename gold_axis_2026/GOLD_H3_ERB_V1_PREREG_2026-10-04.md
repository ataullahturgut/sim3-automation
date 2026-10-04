# ERB-H3 V1 — EXPECTATION REGIME BREAK PREREGISTRATION

**Date:** 2026-10-04  
**Identity:** `ERB_H3_V1`  
**Branch:** `gold-h3-erb-v1-20261004`  
**Baseline:** SAGE-H3 V2 exception-only on top of HELIOS V5-DCE

## Hypothesis

A missed reversal is most likely when two conditions coincide:

1. the existing Gold momentum is internally fragile; and
2. the short-run Gold/cross-asset reaction function has shifted relative to its longer-run relationship in the direction opposite the current momentum.

ERB does not use event labels as direction signals.

## Origin-safe inputs

Reuse the frozen DIVERGE-PROXY V1 origin panel:
- prior-day Gold daily return;
- USD return;
- 10Y yield change;
- Nasdaq return;
- VIX return;
- Silver return.

All source observations are already aligned strictly before the H3 feature cutoff under the DIVERGE source contract.

Stable internal susceptibility variables:
- lower trend_strength;
- higher session_against_trend;
- lower trend_close_location;
- higher adverse_excursion.

No 2025/2026 outcome is used to define these signs; they were retained from the multi-year root-cause audit.

## Relationship-break construction

At each origin:

Long relationship:
- previous 120 eligible observations;
- minimum 80;
- StandardScaler + Ridge(alpha=10).

Short relationship:
- previous 30 eligible observations;
- minimum 20;
- same model.

Cross-asset regressors:
- usd_ret1
- tnx_chg1
- ndx_ret1
- vix_ret1
- silver_ret1

Target:
- gold_daily_ret1.

Outputs, normalized by long-model residual sigma:
- `response_break = -momentum_sign * (gold_daily_ret1 - pred_long) / sigma`
- `relation_shift = -momentum_sign * (pred_short - pred_long) / sigma`
- `external_opp = -momentum_sign * pred_short / sigma`

Positive values point against the current Gold momentum.

## Internal susceptibility

For each origin, compute outcome-free empirical ranks from the previous 120 eligible origins, minimum 60:

- weak trend rank = percentile of `-trend_strength`
- session opposition rank = percentile of `session_against_trend`
- failed close rank = percentile of `-trend_close_location`
- adverse excursion rank = percentile of `adverse_excursion`

`susceptibility = median(four ranks)`.

## Frozen candidate family

DEV = 2023-2024 only.

Quantile grid from DEV origin scores:
- susceptibility quantile: [0.60, 0.70, 0.80]
- break quantile: [0.60, 0.70, 0.80]

Rules:

A. RESPONSE:
- susceptibility >= q_s
- response_break >= q_b

B. SHIFT:
- susceptibility >= q_s
- relation_shift >= q_b
- external_opp > 0

C. CONCURRENCE:
- susceptibility >= q_s
- max(response_break, relation_shift) >= q_b
- external_opp > 0

No other rule or threshold may be searched in V1.

DEV eligibility:
- actions >= 8
- action rate <= 20%
- precision >= 55%
- net rescue >= +2

Selection:
1. highest net rescue
2. highest precision
3. highest rescue count
4. lower action rate
5. higher q_s
6. higher q_b
7. C > B > A

No eligible rule => `ERB_DEV_FAIL`.

## 2025 confirmation

Apply the frozen DEV rule to 2025.

ERB acts only when SAGE V2 has not already flipped V5.

Confirmation PASS requires:
- at least 4 incremental actions;
- at least 3 rescues;
- net rescue > 0;
- precision >= 55%;
- SAGE+ERB accuracy >= SAGE accuracy on identical covered origins;
- neither 2025 H1 nor H2 has net rescue < -1.

Only after PASS may 2026 be opened.

## 2026 stress test

If 2025 passes:
- no parameter or threshold changes;
- report incremental actions, rescue/broken/net, precision;
- compare SAGE vs SAGE+ERB accuracy;
- report H1/H2 stability.

Historical 2026 is stress/development evidence, not a pristine holdout.

## Governance

No post-result threshold changes under V1.
