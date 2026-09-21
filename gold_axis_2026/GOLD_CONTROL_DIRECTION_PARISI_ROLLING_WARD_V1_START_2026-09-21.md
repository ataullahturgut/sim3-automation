# GOLD CONTROL — DIRECTION_PARISI_ROLLING_WARD_V1_RESEARCH START / METHOD-RECOVERY CHECKPOINT

**Date:** 2026-09-21  
**Identity:** `DIRECTION_PARISI_ROLLING_WARD_V1_RESEARCH`  
**Status:** `METHOD_RECOVERY_AND_DATA_AUDIT_STARTED / NO_2025_SCORING_YET`  
**Authority:** Parisi, A., Parisi, F., Díaz, D. (2008), *Forecasting gold price changes: Rolling and recursive neural network models*, Journal of Multinational Financial Management 18(5), 477–487. DOI 10.1016/j.mulfin.2007.12.002.

## Why this is the first literature-backed motor to start

Among the registered 2026-09-21 literature queue, Parisi has the smallest current input gap.

The source model needs only:
- gold-price first differences;
- four lags of gold-price first differences;
- Dow Jones Industrial Average first differences;
- four lags of DJIA first differences;
- one-step-ahead gold sign evaluation.

Current Gold Control already holds both long XAU research history and DJIA daily closes. No VIX/OVX/EPU/volume/futures panel is required for the source core.

## Source facts recovered before implementation

Source-supported facts:
- native target frequency is weekly gold-price change;
- one-step-ahead sign variation is the evaluation target;
- inputs are `ΔG[t-1]..ΔG[t-4]` and `ΔDJI[t-1]..ΔDJI[t-4]`;
- rolling and recursive feed-forward/Ward neural networks are compared;
- rolling operation re-estimates network weights period by period using recent information;
- rolling Ward is the strongest reported family;
- block bootstrap is used for validation;
- reported average rolling-Ward sign prediction is 60.68% with standard deviation 2.82%;
- a Ward network with two hidden layers and 21 neurons is reported among the best architecture combinations.

## Current data-readiness audit

Read-only Neon audit on 2026-09-21:

Gold candidate research series:
- `XAU_STAKTRAKR_RESEARCH_DAILY_R1`
- coverage: 2010-01-04 through 2026-07-31
- status: `APPROVED_RESEARCH_ONLY_NOT_PIT`

DJIA:
- `DJIA_FRED`
- coverage: 2016-08-29 through 2026-09-18
- status: `APPROVED_PRIVATE_MODEL_USE_NO_PUBLIC_RAW_REDISTRIBUTION`

Using Monday-start weekly buckets and the last observed daily value in each week:
- common weeks through 2025: 488;
- pre-2025 common weeks: 436;
- 2025 common weeks: 52;
- weeks with identical XAU/DJIA last-observation date: 482/488;
- weeks where both series have at least four observations: 476/488.

After construction of weekly first differences and four lags:
- eligible total origins: 483;
- eligible pre-2025 origins: 431;
- eligible 2025 origins: 52;
- 2025 realized Gold sign balance on this provisional bridge: 35 UP / 17 DOWN.

This proves data sufficiency for a Gold/DJIA adaptation. It does **not** yet freeze the weekly-close bridge.

## Remaining method details that MUST be recovered/frozen before model fitting

The following are not yet sufficiently proven from the accessible primary-source text and must not be guessed:

1. exact rolling training-window sizes evaluated in the paper;
2. exact Ward-network layer allocation behind the reported two-hidden-layer / 21-neuron configuration;
3. exact activation-function combination selected for the best rolling Ward model;
4. exact scaling/normalization rule;
5. exact optimizer/training stopping rule and random initialization/repetition policy;
6. exact source weekly price observation/close convention;
7. exact block-bootstrap implementation used for validation.

Until these are recovered or a separately labelled Gold adaptation is preregistered, status remains:
`METHOD_SPEC_PARTIAL / NO_MODEL_FIT / NO_2025_SCORE`.

## Governance for the eventual Gold-Control adaptation

If exact source details remain unavailable, the project may later create a separately named adaptation, but only after explicit freeze of:
- weekly close rule;
- rolling-window length;
- network architecture;
- activation functions;
- scaler;
- optimizer/stopping;
- deterministic seed/repetition aggregation;
- 2023/2024 development-validation role;
- 2025 locked retrospective challenge.

No 2025 outcome may choose any of those items.

## Immediate next step

Continue source-method recovery first. If the missing details can be proven, preregister the source-faithful replay. If they cannot, present the unresolved items to the user before opening any Gold-adaptation implementation.
