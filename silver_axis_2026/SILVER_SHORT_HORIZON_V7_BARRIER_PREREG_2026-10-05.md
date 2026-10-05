# SILVER SHORT-HORIZON V7 — BARRIER / HIGH-MOVE TARGET PREREGISTRATION

**Date:** 2026-10-05  
**Identity:** `GLOBAL_XAG_BARRIER_TARGET_V7`  
**Status:** PREREGISTERED BEFORE V7 2025/2026 TRANSPORT IS OPENED.

## Motivation

Forced binary H5 direction does not transport robustly. V1-V6 reject static feature expansion, macro/risk, monthly Copper, consensus, confidence abstention and rolling-memory repair.

V7 changes the **target**, not the feature stack:

> distinguish meaningful directional moves from small/noisy paths.

## Candidate targets

Using origin-time Silver sigma20 and the future retained daily Silver path.

For horizon H in {3,5} and k in {0.50,0.75,1.00}:
- cumulative future Silver log returns are examined one retained day at a time;
- UP if +k*sigma20 is hit before -k*sigma20;
- DOWN if -k*sigma20 is hit first;
- otherwise NO_MOVE.

No target-period feature enters the model.

## Features

Frozen SILVER_PATH only:
- r1, r3, r5, r10, r21;
- sigma20.

## Model

Multinomial Logistic Regression with standardized features, fixed regularization.

No probability threshold tuning.

## DEV protocol

- expanding maturity-safe training;
- 5-origin chronological blocks;
- 2022-2024 only for target selection.

Metrics:
- multiclass accuracy;
- balanced accuracy;
- macro F1;
- multiclass Brier;
- log loss;
- predicted directional coverage;
- selective directional accuracy when predicted class is UP or DOWN.

## Selection

Eligible candidate must have:
- predicted directional coverage >= 30%;
- selective directional accuracy > 50%;
- multiclass balanced accuracy above the 1/3 chance reference.

Primary:
1. highest selective directional accuracy;
2. within 1 pp, higher directional coverage;
3. then higher macro F1;
4. then lower multiclass Brier.

Annual stability is reported.

Only the frozen DEV winner may be opened on 2025/2026.

No 2025/2026 retuning.
