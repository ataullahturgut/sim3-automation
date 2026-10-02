# AURORA-H3 V1 — ASYMMETRIC UNIFIED REGIME ONLINE ROUTING AUTHORITY

**Date:** 2026-10-02
**Identity:** `AURORA_H3_V1_RESEARCH`
**Parents:** `SENTRY_H3_V1_RESEARCH`, `DART_H3_V1_RESEARCH`
**Status:** PREREGISTERED / RESEARCH-ONLY

## 1. Motivation

SENTRY and DART expose complementary strengths:

- SENTRY detects emerging PATH superiority earlier using a local paired-rescue window.
- DART is more persistent and avoids premature return to STRUCTURAL_IRIS once a probabilistically supported PATH regime is established.

AURORA combines these two **already-frozen evidence mechanisms** through asymmetric hysteresis.

No new threshold is estimated.

## 2. Experts

Unchanged:
- STRUCTURAL_IRIS
- PATH_GLOBAL

Frozen expert probabilities come from the SENTRY / DART ledgers.

## 3. Fast-entry evidence

Use the frozen SENTRY paired-rescue statistic:

- window: latest 63 matured H3 origins
- minimum matured history: 42
- +1 if PATH correct and Structural wrong
- -1 if Structural correct and PATH wrong
- enter PATH when `net_rescue_63 >= +3`.

These are exactly the SENTRY V1 entry rules.

## 4. Slow-exit evidence

Once PATH is active, ignore the SENTRY exit trigger.

Return to STRUCTURAL only when the frozen DART Bayesian disagreement posterior gives strong reversal evidence:

- matured disagreement events >= 8
- `Pr(PATH superior) <= 0.10`
- `q_path <= 0.40`.

These are exactly the DART V1 return thresholds.

## 5. State machine

Initial:
- STRUCTURAL_IRIS.

STRUCTURAL -> PATH:
- SENTRY fast-entry condition.

PATH -> STRUCTURAL:
- DART slow-exit condition.

Otherwise retain current state.

This produces deliberate asymmetric hysteresis:
- rapid response to a locally demonstrated expert failure;
- conservative reversal after a regime transfer.

## 6. Anti-leakage

All evidence fields are read from frozen causal ledgers:
- SENTRY paired-rescue values were computed only from matured prior H3 outcomes.
- DART posterior values were computed only from matured prior expert-disagreement outcomes.

AURORA never uses current or future target outcomes to set its state.

## 7. Evaluation

Warm-up:
- 2022.

Frozen confirmation:
- 2023
- 2024.

Transport/stress:
- 2025
- 2026.

Pass only if:
- 2023 and 2024 accuracy are each no worse than Structural IRIS by >1 pp;
- 2023 and 2024 Brier each no worse by >0.003;
- 2023-2024 aggregate balanced accuracy no worse by >1 pp;
- at least one post-warm-up transition occurs.

No 2025/2026 result may change the state rule.

## 8. Comparators

- STRUCTURAL_IRIS
- PATH_GLOBAL
- SENTRY
- DART
- AURORA.

## 9. Dependence-aware inference

If AURORA passes:
- paired circular moving-block bootstrap
- 10,000 replicates
- block lengths 5 and 10
- compare AURORA to DART, SENTRY and Structural IRIS
- periods 2026 and 2025-2026.

## 10. Interpretation

AURORA tests a **stability-plasticity asymmetry**:
- adapt quickly when recent realized evidence indicates expert failure,
- revert slowly unless Bayesian disagreement evidence strongly supports reversal.

This remains retrospective research and requires frozen prospective validation.
