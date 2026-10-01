# GOLD SHORT-HORIZON GLOBAL XAU — Frozen 2025 / 2026 Transport Authority

**Date:** 2026-10-01  
**Status:** FROZEN PRE-RUN  
**Parent:** GOLD_SHORT_HORIZON_GLOBAL_XAU_PROJECT_MANIFEST.md

## Mission

Open the previously frozen 2025 transport period and the already reporting-only 2026 period **only after** the pre-2025 model contract has been frozen.

No 2025 or 2026 result may change:
- horizon;
- feature block;
- model family or hyperparameters;
- probability threshold;
- calibration method;
- conviction-band boundaries.

## Frozen model

- target: XAU_STAKTRAKR_RESEARCH_DAILY_R1
- horizon: H3
- head: direction
- representation: CORE3
- model: Logistic L2
- StandardScaler
- C=1.0
- solver=lbfgs
- max_iter=1000
- random_state=20261001
- calibration: RAW
- direction threshold: p>=0.50 => UP
- frozen conviction bands: p>=0.55 HIGH_UP, p<=0.45 LOW_UP, otherwise NEUTRAL.

## Primary transport mode

**STRICT_FROZEN_FIT**

Fit once using only rows whose H3 label is fully mature by 2024-12-31.
The fitted scaler, medians and Logistic coefficients are then left unchanged across all 2025 and 2026 predictions.

This is the binding transport score.

## Secondary production-style diagnostic

**FROZEN_WALK_FORWARD_PROTOCOL**

The model specification remains unchanged, but it is refit every 5 origins using only labels fully mature before the current block origin.

This diagnostic is reported separately and cannot replace the primary strict frozen-fit score.

## Evaluation periods

- 2025: all eligible signal dates in calendar year 2025 with known H3 outcome.
- 2026: all eligible signal dates in calendar year 2026 with known H3 outcome in the historical StakTrakr series (currently through July 2026).

## Metrics

Report separately by period and mode:
- N
- Brier
- log loss
- accuracy
- balanced accuracy
- UP precision / recall
- DOWN recall
- prediction SD
- p>=0.55 support and realized UP rate
- p<=0.45 support and realized UP rate.

Also write an origin-level ledger containing:
- signal date
- origin price date
- actual H3 return
- actual direction
- predicted UP probability
- predicted direction
- correct/incorrect
- frozen conviction band.

## Governance

This is transport/reporting only.
No retuning after seeing 2025/2026.
No P&L optimization.
No target/source stitching.
