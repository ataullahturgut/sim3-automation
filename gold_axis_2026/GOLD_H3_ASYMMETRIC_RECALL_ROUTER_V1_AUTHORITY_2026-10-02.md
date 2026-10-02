# GOLD H3 — ASYMMETRIC RECALL-CONSTRAINED ROUTER V1

**Date:** 2026-10-02  
**Status:** FROZEN PRE-RUN  
**Target:** Global XAU H3 UP/DOWN direction  
**Model:** `ARCR-H3-v1`

## Motivation from the completed error anatomy

The H3 cross-family audit showed:

- the best DEV model (CORE3 Logistic L2) has materially stronger UP recall than DOWN recall;
- alternative model families do not reliably rescue Logistic errors;
- consensus is not robust under the 2026 distribution shift;
- 2026 is dominated by a large volatility-state displacement, especially `sigma20`.

Therefore V1 does **not** add another large model family. It tests whether a low-capacity recent/global hybrid plus an asymmetric decision boundary can improve the weak DOWN side while preserving the strong UP side.

## Data split

- historical model-selection window: **2019-2021**
- confirmation: **2022-2024**
- 2025/2026: report-only transport diagnostics
- all predictions are chronological and use only matured H3 targets.

The wider project has already opened later years, so this is a structured retrospective research test, not a pristine blind trial.

## Experts

### GLOBAL_L2
CORE3 Logistic L2:
- all matured history
- StandardScaler
- C=1.0.

### RECENT252_BAL_L2
CORE3 Logistic L2:
- last 252 matured rows
- StandardScaler
- C=1.0
- class_weight=balanced.

## Fixed blend grid

Candidate global/recent probability blends:

- 1.00 / 0.00
- 0.75 / 0.25
- 0.50 / 0.50
- 0.25 / 0.75
- 0.00 / 1.00.

No other blend is allowed after results are observed.

## Fixed asymmetric UP-threshold grid

Predict UP only if blended `p_up >= t`.

Grid:
- 0.50
- 0.52
- 0.54
- 0.56
- 0.58
- 0.60
- 0.62.

Raising the UP threshold is the explicit weak-DOWN repair mechanism.

## Selection on 2019-2021 only

Baseline is GLOBAL_L2 at threshold 0.50.

Candidate is eligible only if:
- UP recall is no more than **5 percentage points below** the baseline UP recall;
- Brier is no more than **0.005 absolute worse** than baseline;
- coverage remains 100% (no abstention in V1).

Among eligible candidates:
1. maximize DOWN recall;
2. tie-break by balanced accuracy;
3. tie-break by accuracy;
4. tie-break by lower Brier;
5. tie-break by higher global-model weight;
6. tie-break by threshold closer to 0.50.

Freeze the selected blend and threshold before 2022-2024 confirmation.

## Required report

For 2019-2021 selection and 2022-2024 confirmation:
- accuracy
- balanced accuracy
- UP recall
- DOWN recall
- minimum-side recall
- Brier
- log loss
- false-call rate.

Also report annual 2022, 2023, 2024.

For 2025/2026 report-only:
- same metrics
- 2026 monthly direction diagnostics.

## Decision logic

If ARCR improves DOWN recall on 2022-2024 while keeping UP recall within the pre-registered tolerance and without materially worsening Brier, then asymmetric routing is supported.

If it fails, the next model must add **new information or a novelty/regime representation** rather than further classifier hybridization.
