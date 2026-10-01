# GOLD INTRAMONTH OPPORTUNITY — Stage 4 Monthly Context Incremental Test Authority

**Date:** 2026-10-01  
**Status:** FROZEN PRE-RUN AUTHORITY  
**Parent:** `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md`

## 1. Question

Does causally available monthly context improve the frozen Stage-3 K100 strong-rally detector?

Frozen target:
- **K100** = MFE5 >= SIGMA20 × sqrt(5)

Frozen core:
- **G_ONLY**
- **HGB_CLASS**
- Stage-3 hyperparameters unchanged
- 5-origin prequential refit
- 5-observation label-maturity purge.

Supporting comparator:
- G_ONLY / LOGIT_L2 with Stage-3 settings unchanged.

## 2. Evaluation population

Stage-4 DEV is restricted to daily origins whose signal month has a frozen canonical ChHHO monthly forecast:
- target months **2022-04..2024-12**
- expected daily origins: 685.

The frozen CORE_ONLY model is rerun on this exact same evaluation population so every context comparison is apples-to-apples.

Training history may include all matured pre-2025 daily rows, exactly as Stage 3.

2025/2026 are not evaluated and cannot select a context block.

## 3. Causal monthly forecast context

For a daily signal inside target month M:

Known from prior completed month M-1:
- frozen ChHHO target-month predicted log return;
- frozen ChHHO UP/DOWN direction;
- frozen ChHHO target price forecast;
- prior-month actual / origin level.

Allowed forecast features:
- `monthly_down` (1 DOWN, 0 UP)
- `monthly_pred_log_return`
- `monthly_abs_pred_log_return`.

No realized target-month monthly average is allowed.

## 4. T0-safe reliability context

The frozen Specialist Hedge artifact contains some T1 information that may arrive after the target month begins.

Therefore Stage 4 **does not use router p_HIGH / p_ELEVATED** as static features across the whole target month.

Allowed reliability feature:
- `raw_T0_STANDARD` from the frozen router row for target month M, computed from origin M-1 information.

The following are forbidden as all-month static inputs:
- target-month T1_WGC information;
- full router p_HIGH if it incorporates target-month T1 evidence;
- target-month realized severity.

This preserves daily-origin timing.

## 5. Causal regime/state context

For signal month M, only state information for the **previous completed month M-1** is allowed.

From frozen expanding-refit monthly state artifacts:
- semantic state R0/R1/R2/BELIRSIZ one-hot
- semantic/live posterior probability
- OOD flag
- Transition V2 status for M-1
- Extreme V1 status for M-1.

The state of target month M itself is forbidden because it is not complete at early daily origins inside M.

## 6. Context blocks

All use the exact frozen Stage-3 core model settings.

1. **CORE_ONLY**
   - Stage-3 G_ONLY only.

2. **CORE_DIR**
   - G_ONLY + monthly_down.

3. **CORE_MAG**
   - G_ONLY + monthly_pred_log_return + abs magnitude.

4. **CORE_DIR_MAG**
   - G_ONLY + direction + magnitude.

5. **CORE_DIR_MAG_T0REL**
   - CORE_DIR_MAG + raw_T0_STANDARD.

6. **CORE_DIR_MAG_STATE**
   - CORE_DIR_MAG + previous-month state/posterior/OOD/transition/extreme.

7. **CORE_ALL_SAFE**
   - CORE_DIR_MAG + T0 reliability + previous-month state block.

No context-feature search beyond these seven preregistered blocks.

## 7. Models

Primary:
- frozen HGB_CLASS:
  - learning_rate=0.05
  - max_iter=100
  - max_leaf_nodes=7
  - max_depth=3
  - min_samples_leaf=40
  - l2_regularization=1.0
  - fixed seed.

Supporting:
- frozen LOGIT_L2:
  - StandardScaler
  - L2, C=1.0
  - no class weighting.

No hyperparameter tuning.

## 8. Metrics

Primary:
- Brier score.

Co-primary:
- log loss.

Supporting:
- PR-AUC
- ROC-AUC
- prediction dispersion.

Mandatory slices:
- monthly-DOWN origins
- monthly-UP origins
- by DEV year.

## 9. Promotion gate

A monthly-context block is **GLOBAL PASS** only if versus CORE_ONLY on the exact same DEV rows:

- overall Brier improves by >= **1.0% relative**;
- overall log loss is not worse;
- monthly-DOWN Brier is not worse by more than **1.0% relative**.

Mission-specific diagnostic:
- report relative Brier improvement inside monthly-DOWN origins separately;
- do not promote a block solely because of a favorable subset if the global gate fails.

If multiple blocks pass:
- select the simplest passing block within 0.25 percentage points of the best Brier relative improvement;
- otherwise select best Brier-improvement PASS block.

## 10. Governance

Forbidden:
- 2025/2026 context-based selection;
- target-month realized state;
- target-month realized severity;
- target-month T1 values applied before their publication;
- retuning the Stage-3 HGB core;
- changing K100 definition.

## 11. Required outputs

- monthly-context audit table
- prediction-level results by context block
- overall metrics
- DOWN/UP slice metrics
- year metrics
- selected/rejected decision
- immutable hashes.

If no context block passes:
- retain Stage-3 K100 G_ONLY/HGB core;
- monthly direction remains descriptive context only.
