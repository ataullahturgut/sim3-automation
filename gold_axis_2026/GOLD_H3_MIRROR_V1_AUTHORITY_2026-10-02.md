# MIRROR-H3 V1 — BAYESIAN ANTI-EXPERT SKILL REGIME AUTHORITY

**Date:** 2026-10-02
**Identity:** `MIRROR_H3_V1_RESEARCH`
**Parent:** `AURORA_H3_V1_RESEARCH`
**Status:** PREREGISTERED / RESEARCH-ONLY

## 1. Objective

AURORA's remaining errors may not always be random. In some local regimes, a previously strong classifier can become systematically anti-informative.

MIRROR tests a strict hypothesis:

> if the matured recent correctness process of AURORA enters a regime whose latent skill is credibly below 50%, route temporarily to the exact inverse expert.

Experts:
- NORMAL: `p_normal = p_AURORA`
- INVERSE: `p_inverse = 1 - p_AURORA`.

No new directional feature or fitted classifier is introduced.

## 2. Causal skill observations

For each historical AURORA forecast after its H3 target matures:

- `X=1` if AURORA direction was correct;
- `X=0` if AURORA direction was wrong.

At forecast origin t, only rows with:
`target_end_date_h3 <= feature_cutoff_date_t`
may update the skill detector.

Current/future outcomes are never used.

## 3. Bayesian online change-point detector

Piecewise Bernoulli model:

`X_t ~ Bernoulli(theta)`

where theta is current AURORA directional skill.

New-regime prior:
- Beta(1,1).

BOCPD:
- constant hazard = **1/20 matured skill events**
- maximum run length = **120**
- no hyperparameter search.

At each origin report:
- `q_skill = E[theta|data]`
- `Pr(theta < 0.5)`
- `Pr(theta > 0.5)`
- expected run length.

## 4. Frozen state rule

Initial state:
- NORMAL.

NORMAL -> INVERSE only when:
- at least **12** matured skill events exist;
- `Pr(theta < 0.5) >= 0.90`;
- `q_skill <= 0.40`.

INVERSE -> NORMAL only when:
- `Pr(theta > 0.5) >= 0.90`;
- `q_skill >= 0.60`.

Thresholds are symmetric and fixed ex ante.

## 5. Evaluation

Warm-up / diagnostics:
- 2022.

Frozen stability confirmation:
- 2023
- 2024.

Transport:
- 2025
- 2026.

MIRROR is acceptable only if:
- 2023 accuracy >= AURORA -1 pp and Brier <= AURORA +0.003;
- 2024 accuracy >= AURORA -1 pp and Brier <= AURORA +0.003;
- 2023-2024 aggregate balanced accuracy >= AURORA -1 pp.

No 2025/2026 outcome may tune hazard or thresholds.

## 6. Diagnostics

Report:
- state switch dates;
- annual inverse-active share;
- accuracy / balanced accuracy / Brier / log loss;
- 2026 rescued AURORA errors;
- 2026 broken AURORA calls;
- net rescue;
- monthly 2026 performance;
- posterior skill path around switches.

## 7. Dependence-aware inference

If MIRROR improves 2025/2026:
- paired circular moving-block bootstrap;
- 10,000 replicates;
- block lengths 5 and 10 origins;
- accuracy, Brier, log loss.

## 8. Interpretation

MIRROR is a concept-drift skill router, not a post-hoc error classifier.

It can only invert when already-matured performance provides strong Bayesian evidence that the primary model is locally anti-informative.

The frozen AURORA prospective champion is not modified retroactively.
