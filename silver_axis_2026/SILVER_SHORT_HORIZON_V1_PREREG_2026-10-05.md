# SILVER SHORT-HORIZON V1 — TARGET / BASELINE PREREGISTRATION

**Date:** 2026-10-05  
**Identity:** `GLOBAL_XAG_PUBLIC_STAKTRAKR_V1`  
**Target asset:** Silver / XAG research proxy from pinned StakTrakr public metal history.  
**Status:** PREREGISTERED BEFORE OPENING 2025/2026 TRANSPORT RESULTS.

## Objective

Replicate the successful scientific structure of the Gold short-horizon project for Silver without assuming that Gold's winning horizon, feature block, or controller architecture transports automatically.

The first question is deliberately narrow:

> Which ordinary direction horizon (H1, H3, H5) and which same-day metal-information block carries the strongest leakage-safe Silver signal on 2022-2024 DEV?

Only after this selection is frozen may 2025 and 2026 transport be inspected.

## Source and clock

- Pinned public source: StakTrakr commit `54fdf1c8d39b7b6c7b874d0f30f784296e886044`.
- Metals: Silver, Gold, Platinum, Palladium.
- Common weekday intersection only.
- Feature cutoff = retained metal date at row t.
- Forecast issue = next retained common weekday.
- H1/H3/H5 target = log Silver return from feature cutoff to exact retained date t+h.
- No target-period feature is allowed.

## DEV / transport split

- TRAIN HISTORY: 2010-2021.
- DEV / selection: 2022-2024 only.
- TRANSPORT 1: 2025, opened only after DEV winner is frozen.
- TRANSPORT 2: 2026 available period, opened only after DEV winner is frozen.

2025/2026 outcomes may not change horizon, feature block, model family, threshold, or selection metric.

## Feature blocks

### SILVER_ONLY
- silver_r1
- silver_r3
- silver_r5
- silver_r10
- silver_r21
- silver_sigma20

### CORE3
SILVER_ONLY plus:
- gold_r1 / r5 / r21
- platinum_r1 / r5 / r21

### CORE4
CORE3 plus:
- palladium_r1 / r5 / r21

No macro, volatility, futures, options, or hourly block is admitted in V1.

## Model

Fixed `LogisticRegression(L2, C=1.0)` with standardization.

Evaluation:
- chronological expanding-window;
- test blocks of 5 consecutive DEV origins;
- training labels must have matured by the first feature cutoff in each block.

## DEV selection rule

For every horizon/block pair compute:
- Brier score;
- log loss;
- direction accuracy;
- balanced accuracy;
- UP recall;
- DOWN recall.

Champion selection:
1. lowest Brier on aggregate 2022-2024 DEV;
2. if Brier difference <= 0.002, higher balanced accuracy wins;
3. if still tied, higher raw accuracy wins.

A candidate with balanced accuracy <= 50% cannot be promoted as a meaningful direction engine regardless of raw accuracy.

## Transport reporting

After the DEV champion is frozen, report both:
1. **STATIC_PRE2025** — one model fit using all matured pre-2025 training information;
2. **ADAPTIVE_ORIGIN_SAFE** — same frozen recipe refit using only labels matured before each transport origin.

These are separate evidence classes and must not be conflated.

## Next-stage gate

Do not port AURORA / HELIOS / RIFT / VEGA / SAGE / CIG-D1 mechanics automatically.

Proceed to specialist architecture only if:
- the Silver DEV direction engine materially exceeds chance / majority behavior,
- performance is not carried by only one DEV year,
- and 2025/2026 transport does not reveal complete structural collapse.

If the base target/horizon does not survive, the Silver project must redesign the target before importing Gold-specific controllers.
