# MORNING-D1 V1 — 09:00 TR MICROSTATE NOWCAST PREREGISTRATION

**Date:** 2026-10-05  
**Identity:** `MORNING_D1_V1`  
**Status:** FROZEN BEFORE RESULT RUN

## Research question

Can the August CIG-D1 uncertainty be reduced by changing the information set from **previous-close only** to a genuine same-day morning nowcast?

This is not a replacement for the prior-close CIG forecast. It is a later operational layer with an explicit information advantage.

## Issuance clock

Primary issuance checkpoint: **06:00 UTC = 09:00 Europe/Istanbul**.

For each D1 issue date:
- previous H3/CIG state is known;
- hourly futures observations with timestamp <= 06:00 UTC on the issue date may be used;
- no observation after 06:00 UTC may enter a feature;
- target remains the existing D1 close-to-close sign used by CIG:
  `Gold(issue date) > Gold(feature cutoff date)`.

Because part of the target day has elapsed by issuance, this is explicitly a **nowcast**, not a prior-close forecast.

## Historical hourly source

Retrospective Yahoo 1h futures:
- GC=F gold
- SI=F silver
- NQ=F Nasdaq-100
- ZN=F 10Y Treasury note
- CL=F WTI

Source data are used only to compute derived features. Raw hourly vendor values are not written to repository artifacts.

## Frozen feature families

### M1 GOLD_MICRO
At 06:00 UTC:
- GC return from previous 16:00 America/New_York anchor to checkpoint;
- last 1h, 3h, 6h returns;
- 6h/12h realized volatility;
- 6h/12h positive-hour fraction;
- 6h/12h log range;
- 6h/12h log-price slope.

### M2 GOLD_PLUS_CROSS
M1 plus same-clock:
- SI checkpoint return from previous anchor;
- NQ checkpoint return;
- ZN checkpoint return;
- CL checkpoint return.

### M3 MICRO_PLUS_H3
M2 plus previous-cutoff H3 sensors:
- p_aurora
- p_v5
- p_rift
- p_vega
- p_opal_reversal
- OPAL override
- candidate_reversal
- expert probability dispersion and V5-RIFT / V5-VEGA gaps.

## Candidate models

For M1/M2/M3:
1. LogisticRegression L2, C=0.5, standardized, median imputation.
2. HistGradientBoosting small: depth=2, learning_rate=.05, max_iter=150, min_samples_leaf=20, L2=1.

No hyperparameter search.

## Temporal protocol

- initial training: 2025-H1.
- family/model selection: 2025-Q3 by lowest Brier; tie by higher balanced accuracy, then simpler family/model.
- selective threshold selection: 2025-Q4 from t={0.55,0.60,0.65,0.70,0.75}; require >=50% coverage, choose highest selective accuracy, tie by coverage then higher t.
- refit selected specification on all 2025.
- **2026 is untouched test evidence** for this morning-nowcast identity.

## CIG integration

Two fixed policies on 2026:
- RESOLVE_ONLY: use MORNING-D1 only when prior-close CIG is UNCERTAIN.
- VETO_RESOLVE: resolve UNCERTAIN; if prior-close CIG has a direction and MORNING-D1 confidently opposes it, set final state to UNCERTAIN rather than reverse it.

## Promotion gates

A morning layer may be promoted only if:
1. standalone 2026 selective accuracy >=72%;
2. standalone coverage >=50%;
3. integrated 2026 accuracy >= original CIG accuracy;
4. August integrated accuracy >=75%;
5. August integrated coverage >47.62%.

This is retrospective source reconstruction, not prospective OOS. No 2026 outcome may alter the checkpoint, source symbols, feature families, candidate models, or thresholds.
