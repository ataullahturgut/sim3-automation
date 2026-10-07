# SESSION MODEL-05B — STRUCTURAL_IRIS A1+1H PATH FEATURE SELECTION — PREREGISTRATION

**Date:** 2026-10-07  
**Status:** BINDING BEFORE 2025 REVIEW

## Baseline identity

Canonical SESSION Model-05:

`S14_A1_PLUS_1H_FULL`

- mandatory structural input: fresh `a1_logit`
- path block: original 1h XAU PATH/VOL/SHAPE features
- StandardScaler
- LogisticRegression(L2, C=1.0)
- threshold = 0.50
- block = 5
- minimum matured structural training rows = 80

## Objective

Test whether the canonical A1+1h Structural-IRIS improves when the **1h PATH block** is reduced separately by session.

The A1 structural input is mandatory and may not be dropped by feature selection.

## Candidate universe

Mandatory:
- `a1_logit`

Selectable:
- only the original 1h PATH/VOL/SHAPE features from the canonical S1.4 helper.

No 15m, Silver intraday, Platinum intraday, macro, GVZ, COT, or downstream model state may be added.

## Clock rule

The same canonical S1.4 clock-safe helper is binding.

- A1 is generated causally from matured same-window history.
- 1h XAU is deterministically derived from governed 15m XAU.
- all 1h predictor state must be available before the target window;
- no target-window bar may enter the model.

## Chronology

- 2022: training/warm-up only
- 2023–2024: development + path-variable selection
- 2025: one-time frozen transport
- 2026: unopened

## Nested selection

For each session and every 5-row outer development block:

1. Use only matured same-window rows before the block.
2. Keep `a1_logit` in every candidate model.
3. Use class-balanced L1 logistic only to propose sparse subsets of 1h PATH variables.
4. Selector C grid: 0.03, 0.10, 0.30, 1.00, 3.00.
5. Evaluate proposed subsets using the unchanged final canonical estimator:
   - StandardScaler
   - LogisticRegression(L2, C=1.0)
   - class_weight=None
   - threshold 0.50
6. Select by inner Balanced Accuracy; within 1pp prefer lower Brier, then fewer path variables, then smaller selector C.
7. Outer outcomes never select their own variables.

## Frozen session subset

After 2023–2024:
- rank path variables by outer-block selection frequency;
- prefer variables selected in both years;
- freeze 3–8 path variables per session;
- `a1_logit` remains mandatory;
- no 2025 outcome may modify the frozen representation.

## Exact comparator

On identical rows compare:
- `S14_A1_PLUS_1H_FULL`
- `S14_A1_PLUS_1H_SELECTED`

Required:
- N
- Accuracy
- Balanced Accuracy
- UP recall
- DOWN recall
- Brier
- log loss

30% minimum-class-recall floor remains binding.

## 2025

Baseline and selected challenger must be replayed on identical 2025 rows with the same causal block chronology.

No 2025 retuning of:
- features
- C
- threshold
- A1 construction
- path horizons
- session clocks.
