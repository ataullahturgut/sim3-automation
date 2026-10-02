# VISTA-H3 V1 — VOLATILITY-INFORMED STATE-TRANSITION ADAPTATION AUTHORITY

**Date:** 2026-10-02
**Identity:** `VISTA_H3_V1_RESEARCH`
**Parent:** `DART_H3_V1_RESEARCH`
**Status:** PREREGISTERED / RESEARCH-ONLY

## 1. Hypothesis

DART-H3 uses a fixed Bayesian change-point hazard of 1/20 matured expert-disagreement events.

VISTA tests a narrower mechanism:

**regime transitions in relative expert competence should be assigned a higher prior hazard when the forecast origin is in an unusually volatile / jump-concentrated intraday state, and a lower prior hazard in calm states.**

The volatility/jump state is NOT a direction predictor and does NOT alter expert probabilities.

## 2. Frozen experts

Unchanged from DART:
- STRUCTURAL_IRIS = A1 structural logit + frozen hourly PATH
- PATH_GLOBAL = frozen hourly PATH only

Frozen expert probabilities are read from:
- `GOLD_H3_SENTRY_V1_PREDICTIONS_2026-10-02.csv`

No expert refit is performed in VISTA.

## 3. Origin-safe shock state

From the validated XAU/USD 1-hour IRIS source at 16:00 America/New_York on feature_cutoff_date:

- `rv24` = sqrt(sum of squared hourly log returns over last 24 hourly bars)
- `jump24` = max(abs(hourly return),24h) / (rv24 + epsilon)

For each origin, compute empirical percentiles relative only to the prior **504 available 16:00 anchors**:
- `rv_pct`
- `jump_pct`

Minimum history before percentile activation:
- 60 anchors;
- before that, percentile defaults to 0.50.

Shock score:
`shock = 0.70 * rv_pct + 0.30 * jump_pct`

This weighting is fixed ex ante.

## 4. Dynamic hazard

Base DART hazard:
`h0 = 0.05`.

Dynamic hazard:
`h_t = clip(h0 * exp(k * (shock_t - 0.5)), 0.02, 0.125)`

where:
`k = ln(4) / 0.8`.

Therefore approximately:
- shock percentile 0.10 -> hazard 0.025
- shock percentile 0.50 -> hazard 0.050
- shock percentile 0.90 -> hazard 0.100.

No hazard coefficient is fitted.

For each matured disagreement event, BOCPD uses the hazard that was known at that event's original forecast origin.

## 5. Bayesian disagreement model

Same as DART:
- matured expert disagreements only;
- X=1 if PATH_GLOBAL wins;
- X=0 if STRUCTURAL_IRIS wins;
- new-regime prior Beta(1,1);
- max run length 120 disagreement events.

State thresholds remain exactly DART V1:
- enter PATH when matured disagreements >= 8,
  Pr(theta>0.5) >= 0.90,
  q_path >= 0.60;
- return STRUCTURAL when
  Pr(theta>0.5) <= 0.10,
  q_path <= 0.40.

## 6. Evaluation

- 2022: warm-up / diagnostics.
- 2023 and 2024: frozen mechanism confirmation.
- 2025: transport.
- 2026: stress transport.

Mechanism pass only if:
- 2023 and 2024 accuracy each no worse than Structural IRIS by >1 pp;
- 2023 and 2024 Brier each no worse by >0.003;
- 2023-2024 aggregate balanced accuracy no worse by >1 pp;
- at least one post-warm-up state transition occurs.

2025/2026 may not alter any rule.

## 7. Comparators

Report:
- STRUCTURAL_IRIS
- PATH_GLOBAL
- DART fixed-hazard
- SENTRY
- VISTA dynamic-hazard.

Primary scientific question:
- does state-dependent hazard preserve 2023-2024 while improving detection timing / probability quality in later transport?

## 8. Dependence-aware inference

If VISTA passes, run the same paired circular moving-block bootstrap:
- 10,000 replicates
- block lengths 5 and 10
- VISTA vs DART
- VISTA vs SENTRY
- VISTA vs Structural IRIS
for 2026 and 2025-2026.

## 9. Interpretation

VISTA tests a mechanism-level extension of DART:
**intraday shock affects the prior probability of a competence regime transition, not the forecast direction itself.**

This remains retrospective research and requires prospective frozen validation.
