# GOLD MONTHLY — CROSS-MODEL ERROR OVERLAP / ROUTER VIABILITY V1

**Date:** 2026-09-29  
**Status:** COMPLETE / ROUTER HYPOTHESIS REMAINS VIABLE  
**Scope:** DEV 2022-04..2024-12 only; no 2025/2026 selection or tuning.

## Purpose

Test the prerequisite question before building any error-risk gate:

> When ChHHO makes a large error, do the other models generally fail in the same month, or do structurally different models sometimes rescue the month?

If essentially every competitive model fails in the same months, a side-model/router has little value. If some ChHHO high-error months are materially better forecast by other already-frozen models, cross-model complementarity exists and an origin-safe gate may be worth testing.

## Evidence pool

Exact per-origin DEV rows were assembled from authoritative retained artifacts.

- broad exact-row pool: **24 models**
- competitive pool: **16 models**
- competitive rule frozen before month-level conclusions: **DEV ΣAE <= 1.15 × ChHHO ΣAE**
- ChHHO DEV ΣAE: **1413.029779**
- high-error month definition for overlap analysis: each model's own **worst 8 of 33 months**
- robust IQR outlier diagnostic also computed; ChHHO has no month above Q3 + 1.5×IQR, so the rank-based top-8 definition is the useful cross-model comparison.

Competitive models include ChHHO-ANFIS, DE-ABC-RBFNN, PLS1, LMC2-RBF GPR, FULL7/REDUCED4 ANN, AOA-ELM, CatBoost, Random Forest, leading SVR representations, and CNN/LSTM variants with exact 33-month rows.

## ChHHO worst 8 months

The ChHHO worst 8 months contribute **747.086 USD**, or about **52.9%** of total DEV ΣAE, despite representing only 8/33 months.

| Month | ChHHO AE | Competitive models also top-8 | Best alternative | Best alt AE | Hindsight rescue |
|---|---:|---:|---|---:|---:|
| 2024-03 | 131.58 | **16/16** | LSTM LB3 | 126.11 | +5.47 |
| 2024-11 | 119.13 | **15/16** | CNN-LSTM LB6 | 62.99 | +56.14 |
| 2022-11 | 102.20 | 10/16 | REDUCED4 ANN | 43.74 | +58.46 |
| 2023-01 | 100.74 | 12/16 | CNN-LSTM LB6 | 29.59 | +71.15 |
| 2022-05 | 79.94 | 11/16 | Random Forest | 62.18 | +17.77 |
| 2023-08 | 77.53 | **3/16** | Random Forest | 22.36 | +55.17 |
| 2024-07 | 71.01 | 10/16 | LSTM LB3 | 44.75 | +26.26 |
| 2022-07 | 64.95 | **14/16** | Random Forest | 63.19 | +1.76 |

### Two distinct failure types

**Shared hard months**
- 2024-03: 16/16 competitive models rank it in their own worst eight; virtually no rescue is available.
- 2022-07: 14/16; best alternative improves ChHHO by only 1.76 USD.
- 2024-11 is broadly hard at 15/16, but CNN-LSTM LB6 nevertheless produces a large rescue, so shared difficulty does not always imply no alternative value.

**ChHHO-specific / partially model-specific failures**
- 2023-08: only 3/16 competitive models rank it as top-eight; 14/15 alternatives beat ChHHO; best alternative reduces AE from 77.53 to 22.36.
- 2022-11: all 15 alternatives beat ChHHO; best AE 43.74 vs 102.20.
- 2023-01: 14/15 alternatives beat ChHHO; best AE 29.59 vs 100.74.
- 2024-07: 9/15 alternatives beat ChHHO.

Therefore the project does **not** support the claim that all strong models fail on essentially the same months.

## Fixed fallback diagnostic on ChHHO worst 8

This is retrospective diagnosis only; the worst-eight set is known using actuals and cannot be used as a deployment rule.

| Alternative | ΣAE on ChHHO worst 8 | Improvement vs ChHHO | Wins |
|---|---:|---:|---:|
| **CNN-LSTM LB6** | **588.89** | **158.19** | 6/8 |
| LMC2-RBF M32 | 626.30 | 120.79 | **7/8** |
| REDUCED4 ANN | 639.09 | 108.00 | 6/8 |
| AOA-ELM | 641.59 | 105.49 | 4/8 |
| PLS1 | 654.80 | 92.28 | **7/8** |
| FULL7 ANN | 660.74 | 86.35 | 5/8 |
| DE-ABC-RBFNN | 699.06 | 48.02 | 5/8 |

The strongest price model is therefore **not** automatically the strongest fallback on its own failure months.

Notably, CNN-LSTM LB6 has the lowest absolute-error correlation with ChHHO among the competitive pool:
- signed-error correlation ≈ **0.767**
- absolute-error correlation ≈ **0.588**

This diversity is diagnostically useful even though CNN-LSTM is worse than ChHHO on aggregate DEV.

## Oracle ceiling — diagnostic only

Perfect hindsight is not deployable and is reported only to measure whether complementarity exists.

- ChHHO total DEV ΣAE: **1413.030**
- perfect hindsight best competitive model every month: **704.522**
- theoretical improvement: **708.507**
- if switching were allowed only on ChHHO's known worst 8 months:
  - ChHHO worst-8 error: **747.086**
  - best-model oracle error on those months: **454.895**
  - resulting total DEV ΣAE: **1120.839**
  - theoretical improvement: **292.191**

This proves substantial **ex-post complementarity**, not that a valid ex-ante router can achieve it.

## Decision

1. The router hypothesis is **not rejected**.
2. The failure structure is mixed:
   - some months are genuinely hard for nearly all models;
   - several important ChHHO failures are materially rescued by other frozen models.
3. Therefore the next scientific question is no longer “is there a side model?” but:
   > **Can we identify, using only origin-known information, when ChHHO is entering one of the model-specific failure regimes rather than a shared-hard regime?**
4. Do **not** directly switch to CNN-LSTM, GPR, PLS1, or another model based on this retrospective table.
5. Next valid stage should first build an **error-risk / rescueability gate** with no price switching. Only if that gate works prequentially may a fallback router be opened.

## Authoritative execution

- workflow: **Gold Monthly Cross Model Error Overlap V1**
- run: **36600141673**
- head: **ee82eb25cb4017e9f59d38affeee27304f32ea7a**
- job: **109515089218**
- artifact: **11049132605**
- digest: `sha256:baa25ab1ee06130bdf188cde96be00ee9a8344b5e7a6c609ada996dfd8bec414`
