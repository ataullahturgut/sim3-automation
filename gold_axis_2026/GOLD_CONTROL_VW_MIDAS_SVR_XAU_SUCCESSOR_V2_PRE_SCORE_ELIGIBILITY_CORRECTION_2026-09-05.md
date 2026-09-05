# Gold Control — VW-MIDAS-SVR XAU Successor V2 Pre-Score Eligibility Correction

**Freeze date:** 2026-09-05  
**Identity:** `VW_MIDAS_SVR_XAU_SUCCESSOR_V2`  
**Contract amendment:** `V2_PRE_SCORE_ELIGIBILITY_CORRECTION_2026-09-05`  
**Evidence timing:** frozen before any V2 model prediction, validation metric, diagnostic metric, or September 2026 V2 reconstruction is produced.

## 1. Reason for correction

The V2 change-control correctly freezes:

- first feature-complete origin = `2022-09`;
- minimum model fit sample = 24 completed target months;
- inner selection from past expanding one-step origins only;
- the same minimum-fit constraint for every actual SVR fit.

The original V2 date arithmetic called `2024-09` the first outer origin eligible for an SVR fit. That is sufficient for an **outer training set of 24 completed target months**, but it is not sufficient to choose a hyperparameter tuple using the frozen inner rolling-origin rule: at that point every candidate inner origin has fewer than 24 prior fit rows.

No default hyperparameter tuple was pre-registered, and inventing one would silently change the model contract. Therefore the first **fully executable tuned outer origin** is the next month, `2024-10`, when the newest eligible inner one-step origin has 24 prior fit rows.

This is a deterministic contract-consistency correction, not a performance-driven change. No V2 model score existed when this amendment was frozen.

## 2. Corrected untouched windows

Feature/source rules remain unchanged.

First feature-complete origin:

`2022-09`

First fully executable tuned outer origin:

`2024-10`

Untouched validation origins:

`2024-10` through `2025-09` = 12 origins.

Corresponding H=1 target months:

`2024-11` through `2025-10`.

Source-determined validation calendar buckets for the frozen 1.50x RW MAE cap:

- origin bucket A: `2024-10..2024-12`;
- origin bucket B: `2025-01..2025-09`.

Locked diagnostic origins:

`2025-10` through `2026-07`.

Current origin remains:

`2026-08` -> target `2026-09`.

## 3. What does not change

No change is made to:

- source identity or PIT rules;
- GPR window `2022-03..2026-08`;
- XAU research lineage;
- feature vector;
- GPR weighting formula;
- RBF SVR model family;
- `C`, `gamma`, or `epsilon` grids;
- minimum fit = 24;
- inner expanding-origin tuning rule;
- Random Walk benchmark;
- validation thresholds;
- bridge thresholds;
- governance locks;
- `AUTO_SELECTOR=OFF`;
- `AUTO_ENSEMBLE=OFF`;
- production/decision write prohibition.

## 4. Binding interpretation

For V2 execution, this amendment supersedes only the inconsistent V2 statements that treated origin `2024-09` as fully tunable and used `2024-09..2025-08` as the 12-origin validation window.

If the source preflight or later execution reveals a different window is required, V2 must stop rather than move the window after seeing model performance.
