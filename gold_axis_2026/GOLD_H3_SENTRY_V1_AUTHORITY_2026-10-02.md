# SENTRY-H3 V1 — CAUSAL EXPERT FAILOVER AUTHORITY

**Date:** 2026-10-02
**Identity:** `SENTRY_H3_V1_RESEARCH`
**Parent:** `IRIS_H3_V1_RESEARCH`
**Status:** PREREGISTERED / RESEARCH-ONLY

## 1. Motivation

AIM-H3 showed that continuous probability mixing dilutes the strong Structural-IRIS expert in 2023-2024 and does not adapt sharply enough in 2026.

However, the frozen expert ledger shows a different pattern:
- Structural IRIS dominates PATH_GLOBAL in 2023-2024.
- PATH_GLOBAL is modestly stronger in 2025 and materially stronger in 2026.

SENTRY therefore uses **hard causal failover with hysteresis**, not continuous blending.

## 2. Frozen experts

### STRUCTURAL_IRIS
- expanding Logistic L2
- A1 structural logit + frozen IRIS PATH.

### PATH_GLOBAL
- expanding Logistic L2
- frozen IRIS PATH only.

Expert probabilities are generated with the same leakage-free monthly walk-forward contract as AIM.

## 3. Causal paired-advantage signal

For each matured historical H3 forecast:
- +1 = PATH_GLOBAL correct and STRUCTURAL_IRIS wrong
- -1 = STRUCTURAL_IRIS correct and PATH_GLOBAL wrong
- 0 = both same correctness.

At each new origin use only the latest **63 matured paired forecasts**.

`net_rescue_63 = sum(paired_advantage)`.

## 4. Frozen state machine

Initial state:
- STRUCTURAL_IRIS.

Switch STRUCTURAL -> PATH when:
- at least 42 matured paired forecasts exist; and
- `net_rescue_63 >= +3`.

Switch PATH -> STRUCTURAL when:
- `net_rescue_63 <= 0`.

Otherwise retain the current expert.

The rule has no fitted threshold search and no later-period optimization.

## 5. Output

At each origin:
- active expert
- net_rescue_63
- p_up_sentry
- UP/DOWN at 0.50.

## 6. Evaluation chronology

- 2022 H2: warm-up / diagnostic.
- 2023: confirmation 1.
- 2024: confirmation 2.
- 2025: transport.
- 2026: stress transport.

Because the failover mechanism was hypothesized after inspection of broader project history, none of these periods is claimed as a pristine prospective lockbox. The causal chronology is nevertheless enforced exactly.

## 7. Acceptance rule

SENTRY is a mechanism pass only if:
- in 2023 and 2024 separately, accuracy is not worse than STRUCTURAL_IRIS by more than 1 percentage point and Brier not worse by more than 0.003;
- 2023-2024 aggregate balanced accuracy is not worse than STRUCTURAL_IRIS by more than 1 percentage point;
- the state machine actually switches at least once somewhere after warm-up.

2025/2026 results are report-only and cannot change V1.

## 8. Diagnostics

Report:
- annual accuracy / balanced accuracy / Brier;
- fraction of origins assigned to PATH;
- state-switch dates;
- 2026 rescued/broken calls;
- 2026 month-by-month comparison.

## 9. Interpretation

SENTRY tests whether **observed recent paired directional competence** provides a cleaner adaptation signal than state novelty, meta error-risk prediction, or continuous expert averaging.
