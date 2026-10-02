# IRIS-H3 V1 — ROBUSTNESS / TIMING AUDIT AUTHORITY

**Date:** 2026-10-02  
**Identity:** `IRIS_H3_V1_ROBUSTNESS_AUDIT`  
**Parent:** `IRIS_H3_V1_RESEARCH`  
**Status:** DIAGNOSTIC ONLY — NO RETUNING

## Purpose

The parent IRIS-H3 V1 produced an unusually large improvement. This audit checks whether the result is plausibly transportable or is an artifact of one exact anchor/time representation.

No audit result may change the frozen V1 representation selected on 2023.

## Frozen parent model

- selected representation: `A1_PLUS_PATH`
- baseline: A1/ARCR probability
- official anchor: 16:00 America/New_York on `feature_cutoff_date`
- 2023 selected, 2024 confirmed, 2025/2026 frozen transport.

## Diagnostic variants

1. `A1_PATH_16`
   - exact parent specification, independently recomputed.

2. `A1_PATH_15`
   - same features/model, but anchor at 15:00 NY on feature_cutoff_date.
   - purpose: check one-hour timing sensitivity.

3. `A1_PATH_PREV16`
   - same 16:00 features shifted to the previous available 16:00 anchor.
   - purpose: placebo / information-age control.

4. `PATH_ONLY_16`
   - intraday PATH block without the A1 structural probability.
   - purpose: quantify how much signal is genuinely intraday.

5. `A1_RET12_16`
   - A1 plus only 12h intraday return.
   - purpose: determine whether the effect is essentially one-factor or distributed across path structure.

All models remain Logistic L2 and use the same monthly expanding chronology as IRIS V1.

## Metrics

- yearly accuracy / balanced accuracy / Brier / log loss / UP recall / DOWN recall;
- 2023-2024 and 2025-2026 aggregates;
- monthly stability for the frozen parent representation:
  - number/share of months above 50% accuracy,
  - median monthly accuracy,
  - worst monthly accuracy,
  - number/share of months with balanced accuracy above 50%.

## Interpretation

Evidence supporting robustness:
- independent 16:00 recomputation reproduces parent metrics;
- 15:00 anchor retains material signal;
- previous-anchor placebo degrades meaningfully;
- PATH-only retains substantial signal;
- result is not solely dependent on h_ret_12.

This audit is descriptive. It cannot replace A1_PLUS_PATH with another representation based on later results.
