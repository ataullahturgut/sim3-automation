# SILVER SHORT-HORIZON V2 — RELATIVE-VALUE / METAL-STATE PREREGISTRATION

**Date:** 2026-10-05  
**Identity:** `GLOBAL_XAG_RELATIVE_VALUE_V2`  
**Status:** PREREGISTERED BEFORE V2 2025/2026 TRANSPORT IS OPENED.

## Motivation

V1 showed that a direct Silver-path Logistic model is weak:
- DEV champion: H5 SILVER_ONLY, 53.91% accuracy / 53.91% BA;
- 2025 and 2026 transport failed materially.

Therefore V2 does not retune the V1 Silver-only model. It tests a different mechanism:

> Silver direction may be more predictable from its relative state versus Gold and the precious/industrial-metal complex than from its own momentum alone.

## Candidate features

All features are computed at the feature cutoff only.

### SILVER_PATH
- Silver log returns r1/r3/r5/r10/r21
- Silver realized sigma20

### RELATIVE_VALUE
SILVER_PATH plus:
- Gold r1/r3/r5/r10/r21
- Silver minus Gold return spread r1/r3/r5/r10/r21
- log(Gold/Silver) z-score 20 and 60
- ratio change r1/r5/r21

### METAL_STATE
RELATIVE_VALUE plus:
- Platinum r1/r5/r21
- Palladium r1/r5/r21
- cross-metal breadth at 1d/5d/21d
- cross-metal return dispersion at 1d/5d/21d
- Silver-vs-industrial-average spread r1/r5/r21

## Candidate horizons

H1, H3, H5.

## Fixed model families

- LOGIT_L2: standardized Logistic Regression, C=1.
- HGB: HistGradientBoostingClassifier with shallow depth and fixed regularization.

No model-specific threshold tuning. Direction threshold remains 0.5.

## DEV protocol

- 2022-2024 only.
- Expanding origin-safe training.
- Five-origin chronological test blocks.
- Only labels matured by the first feature cutoff of a block may enter training.

## Selection

A candidate is eligible only if aggregate DEV balanced accuracy > 50%.

Primary: lowest Brier.  
Within 0.002 Brier: higher balanced accuracy.  
Then higher accuracy.

Annual stability is reported; a candidate that is below 50% balanced accuracy in two of three DEV years will be marked unstable even if aggregate is best.

## Transport

After DEV winner is frozen:
- 2025 transport;
- 2026 available transport;
- STATIC_PRE2025 and ADAPTIVE_ORIGIN_SAFE reported separately.

No 2025/2026 result may change the V2 configuration.
