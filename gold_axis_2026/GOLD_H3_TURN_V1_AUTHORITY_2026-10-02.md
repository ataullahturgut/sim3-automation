# TURN-H3 V1 — TAIL-UNBALANCED REVERSAL NAVIGATOR AUTHORITY

**Date:** 2026-10-02
**Identity:** `TURN_H3_V1_RESEARCH`
**Parent:** `AURORA_H3_V1_RESEARCH`
**Related diagnostic:** `RIFT_H3_V1_RESEARCH`
**Status:** PREREGISTERED / POST-HOC MECHANISM RESEARCH

## 1. Motivation

AURORA exhibits a persistent momentum-life-cycle asymmetry: it is highly accurate when recent 12h momentum continues and weak when H3 reverses that momentum.

RIFT-H3 V1 showed that a learned reversal classifier can improve 2026 but did not pass 2023-2024 confirmation.

TURN therefore removes the fitted reversal classifier and adapts the published Tuned Time Series Momentum (TTSM) semivariance-tail logic to the AURORA H3 setting.

This architecture was motivated after historical error inspection including 2026. All 2022-2026 results are retrospective mechanism evidence, not pristine lockbox evidence.

## 2. Literature-derived reversal state

At each 16:00 America/New_York anchor:

- compute hourly returns over the latest **120 active hourly bars**;
- `RS_PLUS_120 = sum(r_h^2 * 1[r_h>0])`;
- `RS_MINUS_120 = sum(r_h^2 * 1[r_h<0])`.

For each anchor compute historical reference thresholds from the **previous 250 valid anchors only**:
- `Q80_PLUS` = 80th percentile of prior RS_PLUS_120;
- `Q80_MINUS` = 80th percentile of prior RS_MINUS_120.

The 250-anchor / 80th-percentile design follows the published TTSM construction.

Minimum history before a rule can fire:
- 120 prior anchors.

## 3. Momentum state

Momentum sign is the frozen IRIS:
- `sign(h_ret_12)`.

AURORA remains the primary prediction.

TURN may act only when AURORA direction agrees with 12h momentum.

## 4. Fixed rule

### Upward momentum
If:
- AURORA predicts UP;
- h_ret_12 > 0;
- RS_MINUS_120 > Q80_MINUS;
- RS_PLUS_120 <= Q80_PLUS;

then TURN flips to DOWN.

### Downward momentum
If:
- AURORA predicts DOWN;
- h_ret_12 < 0;
- RS_PLUS_120 > Q80_PLUS;
- RS_MINUS_120 <= Q80_MINUS;

then TURN flips to UP.

### Both-tail region
If both RS_PLUS and RS_MINUS exceed their 80th percentiles:
- published TTSM interprets this as a high-risk / sideways region;
- TURN **does not force a direction change** because the project target requires a directional H3 call;
- it records `BOTH_TAIL_RISK=1` as an uncertainty diagnostic.

### Low-tail / same-side-tail
Retain AURORA.

No threshold search, regression, machine learning, or fitted parameter is allowed.

## 5. Probability handling

For a flipped call:
- preserve AURORA confidence magnitude symmetrically:
  `p_TURN = 1 - p_AURORA`.

Otherwise:
- `p_TURN = p_AURORA`.

This isolates the directional rule from probability-model fitting.

## 6. Evaluation

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
- 2023-2024 balanced accuracy >= AURORA
- 2023-2024 net rescue > 0.

If passed, 2025/2026 remain descriptive retrospective stress evidence only.

## 7. Dependence-aware audit

If mechanism passes:
- paired circular moving-block bootstrap
- 10,000 replicates
- block lengths 5 and 10
- TURN vs AURORA
- 2023-2024, 2025-2026, and 2026.

## 8. Governance

No 2022-2026 result may change:
- 120-hour semivariance horizon
- 250-anchor reference window
- 80th percentile
- both-tail handling
- reversal conditions.

A successful TURN must receive a separate future prospective freeze before it can challenge frozen AURORA operationally.
