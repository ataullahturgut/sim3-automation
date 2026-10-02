# HERA-H3 V1 — HIERARCHICAL EXHAUSTION-REVERSAL ADAPTER AUTHORITY

**Date:** 2026-10-03
**Identity:** `HERA_H3_V1_RESEARCH`
**Parents:** `AURORA_H3_V1_RESEARCH`, `OPAL_H3_V1_RESEARCH`
**Status:** PREREGISTERED / POST-HOC MECHANISM RESEARCH

## 1. Motivation

AURORA's dominant structural weakness is momentum reversal.

OPAL introduces an orthogonal directional derivatives-market signal using official CFTC options-only positioning reconstructed from futures+options-combined minus futures-only reports.

Raw OPAL is unstable:
- weak/damaging in 2023-2024;
- strongly useful in 2026.

AURORA already carries a causal regime state:
- `STRUCTURAL_IRIS`
- `PATH_GLOBAL`.

The central HERA hypothesis is:

> options-positioning reversal information should only be trusted when AURORA has itself determined that the market is in the PATH_GLOBAL regime, i.e. when recent intraday path information has displaced the structural expert.

This creates a two-level hierarchy:
1. AURORA determines the market-information regime.
2. OPAL is allowed to correct reversals only inside PATH_GLOBAL.

## 2. Inputs

Frozen parent outputs only:
- AURORA V1 active expert and probability;
- OPAL V1 probability / reversal intervention.

No new raw feature is fit inside HERA.

## 3. Frozen routing rule

At every origin:

### If AURORA active expert = STRUCTURAL_IRIS
- output AURORA exactly.
- OPAL is suppressed.

### If AURORA active expert = PATH_GLOBAL
- output OPAL V1 probability.

Because OPAL differs from AURORA only when its fixed reversal rule fires, this is equivalent to allowing OPAL reversal corrections only in the PATH_GLOBAL regime.

No new numerical threshold is introduced.

## 4. Timing / anti-leakage

AURORA's active state is causal:
- SENTRY fast entry uses only matured prior H3 paired outcomes;
- DART slow exit uses only matured prior expert-disagreement outcomes.

OPAL is causal under its own authority:
- CFTC reports use a conservative 7-calendar-day availability lag;
- reversal head uses monthly expanding target-matured training only.

HERA uses only these already-causal parent outputs at the current origin.

## 5. Scientific basis

Regime-switching forecast-combination research shows that relative model value may change across latent states and that time-varying expert weights can outperform fixed combinations when forecast relationships are unstable.

HERA uses an economically interpretable nested state rather than estimating a new regime:
- Structural regime -> structural/intraday champion only.
- Path-dominant regime -> permit directional derivatives positioning to correct exhaustion/reversal.

## 6. Evaluation

The architecture was motivated after observing historical OPAL regime dependence, including 2026. Therefore all 2022-2026 results are **RETROSPECTIVE_MECHANISM_VALIDATION**.

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
- HERA must differ from AURORA on at least one post-2024 origin.

2025/2026 are descriptive retrospective stress evidence and cannot be called clean transport proof.

## 7. Dependence-aware audit

If mechanism passes:
- paired circular moving-block bootstrap;
- 10,000 replicates;
- block lengths 5 and 10;
- HERA vs AURORA;
- HERA vs OPAL;
- periods 2025, 2026, 2025-2026.

## 8. Governance

No 2022-2026 result may change:
- AURORA state rules;
- OPAL model/features/threshold;
- CFTC lag;
- HERA routing rule.

HERA does not replace or edit the existing frozen AURORA prospective ledger.

If retrospective evidence remains favorable, HERA may be frozen as a **separate prospective challenger** for future origins only.
