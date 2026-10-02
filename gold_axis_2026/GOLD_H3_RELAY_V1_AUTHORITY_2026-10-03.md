# RELAY-H3 V1 — REGIME-ADAPTIVE OPTIONS-RESCUE TRUST ROUTER

**Date:** 2026-10-03
**Identity:** `RELAY_H3_V1_RESEARCH`
**Parents:** `AURORA_H3_V1_RESEARCH`, `OPAL_H3_V1_RESEARCH`
**Status:** PREREGISTERED / POST-HOC MECHANISM RESEARCH

## 1. Motivation

OPAL adds a genuinely new directional derivatives-market channel by reconstructing delta-adjusted options-only trader positioning from official CFTC futures-only and futures+options-combined Disaggregated COT reports.

Its usefulness is time-varying:
- it damages AURORA materially in 2023;
- is near-neutral in 2024/2025;
- improves 2026 strongly.

This suggests a forecast-combination / expert-reliability regime problem rather than a permanently valid or invalid OPAL signal.

RELAY therefore does **not** change OPAL's features, model, CFTC lag, or p(reversal) threshold. It learns only whether OPAL's **actual direction-changing interventions** are currently trustworthy.

## 2. Information-bearing event stream

An OPAL information event exists only when:
- OPAL direction differs from AURORA direction.

At such an event exactly one of the two directions is correct.

Define:
- X=1 if OPAL is correct and AURORA is wrong;
- X=0 if AURORA is correct and OPAL is wrong.

Rows where OPAL and AURORA issue the same direction carry no relative-skill information and do not update the detector.

## 3. Bayesian trust detector

RELAY reuses the already-frozen DART-H3 V1 Bayesian Online Change-Point Detection parameters **without modification**:

- piecewise Bernoulli event stream;
- new-regime prior Beta(1,1);
- constant hazard = **1/20** per matured OPAL override event;
- maximum run length = **120** events.

At every origin:
- only OPAL override events with `target_end_date_h3 <= current feature_cutoff_date` may update the detector.

Summaries:
- `q_opal = E[theta | matured override events]`
- `Pr(theta>0.5)`
- expected run length.

## 4. Frozen state rule

Initial state:
- `AURORA_ONLY`.

If matured OPAL override events < **8**:
- remain `AURORA_ONLY`.

Enter `OPAL_TRUSTED` when:
- matured events >= 8;
- `Pr(theta>0.5) >= 0.90`;
- `q_opal >= 0.60`.

Return to `AURORA_ONLY` when:
- `Pr(theta>0.5) <= 0.10`;
- `q_opal <= 0.40`.

Otherwise retain the current trust state.

These are exactly the frozen DART thresholds; no RELAY-specific threshold search is allowed.

## 5. Forecast rule

At an origin:

- if state = AURORA_ONLY -> output AURORA.
- if state = OPAL_TRUSTED:
  - if OPAL changes AURORA direction -> output OPAL;
  - otherwise OPAL and AURORA coincide and output is naturally the same.

No probability blending.

## 6. Scientific basis

Forecast-combination research has long documented time-varying optimal weights and regime-dependent forecast skill. Regime-switching combination models can outperform fixed combinations when relative model performance changes across latent regimes.

RELAY applies that principle to a sparse, information-bearing rescue stream rather than every H3 origin.

## 7. Evaluation

The architecture is motivated after observing historical OPAL behavior; therefore all 2022-2026 evidence is **RETROSPECTIVE_MECHANISM_VALIDATION**.

Report:
- 2022 H2
- 2023
- 2024
- 2025
- 2026
- 2023-2024
- 2025-2026.

Mechanism pass requires:
- 2023 accuracy >= AURORA -1 pp
- 2024 accuracy >= AURORA -1 pp
- 2023 Brier <= AURORA +0.003
- 2024 Brier <= AURORA +0.003
- 2023-2024 balanced accuracy >= AURORA -1 pp
- at least one trust-state transition.

2025/2026 are descriptive retrospective stress evidence only.

## 8. Dependence-aware audit

If mechanism passes:
- paired circular moving-block bootstrap;
- 10,000 replicates;
- block lengths 5 and 10;
- RELAY vs AURORA;
- periods 2023-2024, 2025-2026, 2026.

## 9. Governance

No 2022-2026 result may change:
- OPAL model or p(reversal) threshold;
- CFTC 7-day lag;
- BOCPD hazard;
- Beta prior;
- minimum events;
- state thresholds.

Frozen AURORA prospective validation remains untouched.

If RELAY passes retrospectively, it may become a separately frozen prospective challenger only; it cannot rewrite existing AURORA prospective forecasts.
