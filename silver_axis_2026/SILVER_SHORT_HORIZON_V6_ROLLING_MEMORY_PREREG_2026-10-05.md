# SILVER SHORT-HORIZON V6 — ROLLING-MEMORY REGIME ADAPTATION PREREGISTRATION

**Date:** 2026-10-05  
**Identity:** `GLOBAL_XAG_H5_ROLLING_MEMORY_V6`  
**Status:** PREREGISTERED BEFORE V6 2025/2026 TRANSPORT IS OPENED.

## Motivation

V1-V5 show:
- weak but nonzero H5 DEV signal;
- severe 2025/2026 transport instability;
- no robust repair from precious-metal relative value, macro/risk, Copper, consensus, or confidence abstention.

This pattern is consistent with non-stationary parameter mapping rather than a missing static feature alone.

V6 tests whether **recent-history memory** improves the frozen H5 Silver-path Logistic.

## Target / features / model

Unchanged:
- Silver H5 direction;
- SILVER_PATH feature block;
- standardized Logistic L2, C=1;
- threshold 0.5.

## Candidate training memories

At each DEV origin/block, use only matured prior labels and either:
- EXPANDING: all matured history;
- ROLL126: most recent 126 matured origins;
- ROLL252: most recent 252 matured origins;
- ROLL504: most recent 504 matured origins.

No exponential weighting and no additional tuning.

## DEV selection

2022-2024 only, five-origin chronological blocks.

Eligible if aggregate BA > 50%.

Primary lowest Brier; within 0.002 choose higher BA, then accuracy.

Annual stability is reported. Two DEV years below 50% BA disqualify promotion.

Only the frozen DEV winner may be opened on 2025/2026.

## Transport

The selected memory rule is applied origin-safely with the same fixed feature/model identity.

No 2025/2026 retuning.
