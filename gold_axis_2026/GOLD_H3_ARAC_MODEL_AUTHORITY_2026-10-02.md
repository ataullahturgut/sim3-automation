# GOLD H3 — ADAPTIVE REGIME-ANALOG CONSENSUS (ARAC) AUTHORITY

**Date:** 2026-10-02  
**Status:** FROZEN PRE-RUN  
**Model name:** `ARAC-H3-v1`  
**Target:** Global XAU H3 UP/DOWN direction

## Research hypothesis

Static global classifiers dilute short-lived structure. A more useful H3 model may require four distinct memories:

1. long-run structural relation;
2. recent-regime relation;
3. historically similar market states;
4. explicit low/mid/high-volatility + trend/breadth regime memory.

ARAC is a new composite model built for this problem rather than another single off-the-shelf classifier.

## Data

Identity: `GLOBAL_XAU_PUBLIC_STAKTRAKR_R2`.

Base information set: frozen `CORE3` only:

- gold_r1, gold_r3, gold_r5, gold_r10, gold_r21, sigma20
- silver_r1, silver_r5, silver_r21, silver_age_days
- platinum_r1, platinum_r5, platinum_r21, platinum_age_days

No 2025/2026 outcomes.

## Development / confirmation

- model architecture and reliability rule development: **2019-2021**
- confirmation report: **2022-2024**
- 2022-2024 is already-opened research history in the wider project, so this is not called a pristine blind lockbox.

All forecasting is chronological with 5-origin blocks. A label may be used only after its H3 target-end date has matured.

## Four experts

### Expert A — GLOBAL_EN

Global Elastic-Net Logistic:
- all matured history
- StandardScaler
- C=0.30
- l1_ratio=0.50
- saga.

### Expert B — RECENT504_BAL_LOGIT

Recent-memory balanced Logistic:
- last 504 matured observations only
- StandardScaler
- C=1.0
- L2
- class_weight=balanced.

### Expert C — LOCAL_ANALOG

Non-parametric state analog:
- standardize CORE3 by training median/std;
- use 75 nearest matured historical states by Euclidean distance;
- inverse-distance exponential weights;
- local UP probability shrunk toward the training UP prior with 20 pseudo-observations.

No target information enters distance calculation.

### Expert D — REGIME_PRIOR

Discrete regime-conditioned historical probability.

Regime is defined only from issue-time variables:
- sigma20 tertile determined from training history: LOW / MID / HIGH;
- gold_r21 sign: UP_TREND / DOWN_TREND;
- cross-metal 21-day breadth:
  - POS if silver_r21 + platinum_r21 > 0,
  - NEG otherwise.

For the current regime, estimate past H3 UP probability with Beta-style shrinkage toward the global training prior using 25 pseudo-observations.

## Adaptive expert weighting

For each forecast block, expert weights use only previously issued ARAC expert predictions whose H3 targets have matured by the current feature cutoff.

- memory: most recent 126 matured forecast rows;
- exponential recency half-life: 63 rows;
- expert loss: Brier score;
- weight = exp(-30 * EWMA_Brier);
- normalize weights to sum to 1;
- if fewer than 40 matured meta-history rows exist, use equal weights.

Full-coverage probability is the weighted mean of the four expert probabilities.

## Reliability / selective call layer

Reliability score:
- `agreement_fraction * abs(p_final - 0.5)`,
- where agreement_fraction is the fraction of the four experts whose direction matches the final ARAC direction.

On 2019-2021 only, evaluate reliability thresholds corresponding to nominal retained coverage:
- 70%, 60%, 50%, 40%, 30%.

Freeze the threshold with highest balanced accuracy subject to:
- realized development coverage >= 30%;
- at least 120 calls across 2019-2021.

Tie-break:
1. higher accuracy;
2. lower false-call rate;
3. higher coverage.

The frozen rule is then applied unchanged to 2022-2024.

## Comparators

Report against:
- expanding prior;
- fixed CORE3 + Logistic L2;
- fixed CORE3 + Elastic-Net Logistic.

## Required metrics

Full coverage:
- accuracy
- balanced accuracy
- false-call rate
- Brier
- log loss
- UP recall
- DOWN recall
- annual metrics.

Selective:
- coverage
- accuracy
- balanced accuracy
- false-call rate
- UP/DOWN call counts
- annual metrics.

## Integrity

No architecture, feature, expert, memory length, K, pseudo-count, loss coefficient, or threshold candidate is changed after the 2019-2021 development run is observed.

Any later modification is `ARAC-H3-v2`.
