# GOLD SHORT-HORIZON — TARGET RESEARCH AUTHORITY

**Date:** 2026-10-02  
**Status:** FROZEN PRE-RUN  
**Identity:** `GLOBAL_XAU_PUBLIC_STAKTRAKR_R2`

## Research question

Before adding another model family, determine **which short-horizon target is intrinsically more predictable** under the same fixed information set and same fixed classifier.

This experiment compares target definitions, not algorithms.

## Data / features

Use the frozen R2 daily panel and the existing `CORE3` feature block:

- gold_r1, gold_r3, gold_r5, gold_r10, gold_r21, sigma20
- silver_r1, silver_r5, silver_r21, silver_age_days
- platinum_r1, platinum_r5, platinum_r21, platinum_age_days

No 2025 or 2026 outcomes may enter fit or target choice.

## Fixed model

For every target:

- StandardScaler
- LogisticRegression
- L2
- C=1.0
- lbfgs
- max_iter=3000
- random_state=20261001

For 3-class barrier targets use multinomial-capable LogisticRegression with the same fixed regularization.

No model or hyperparameter search.

## Evaluation

DEV only: forecast_issue_date in 2022-2024.

- chronological expanding training;
- 5-origin test blocks;
- a training label is usable only after its target end date has matured by the test block's feature-cutoff date;
- annual 2022, 2023 and 2024 metrics retained.

## Target set

### Ordinary direction targets

1. `DIR_H1`
   - UP if target_r1 > 0 else DOWN.

2. `DIR_H3`
   - UP if target_r3 > 0 else DOWN.

3. `DIR_H5`
   - UP if target_r5 > 0 else DOWN.

### Volatility-normalized first-close-hit targets

Barrier size is based only on the issue row's lag-safe `sigma20`.

For each horizon, compute the cumulative future Gold log-return after each retained weekday close from the target-start date. Label:

- `UP` if +k*sigma20 is reached before -k*sigma20;
- `DOWN` if -k*sigma20 is reached before +k*sigma20;
- `NO_MOVE` if neither barrier is reached by the horizon.

Because the R2 panel is daily, these are **first retained-daily-close hits**, not intraday high/low barrier hits.

Frozen barrier targets:

4. `BARRIER_H3_K050`
5. `BARRIER_H3_K075`
6. `BARRIER_H3_K100`
7. `BARRIER_H5_K075`

No threshold is changed after results are observed.

## Metrics

Binary direction:
- accuracy
- balanced accuracy
- Brier
- log loss
- UP recall
- DOWN recall
- prediction SD
- class balance.

3-class barrier:
- accuracy
- balanced accuracy
- macro F1
- multiclass log loss
- multiclass Brier
- UP / DOWN / NO_MOVE recall
- actual NO_MOVE share
- predicted directional coverage = fraction of predictions that are UP or DOWN
- selective directional accuracy = accuracy among rows where the model predicts UP or DOWN.

Also report a simple majority-class baseline for each target and year.

## Interpretation

The purpose is to identify whether:
- H1, H3 or H5 carries the cleanest direction signal;
- volatility-normalized targets reduce label noise;
- a NO_MOVE class creates a more useful selective forecasting problem.

This is target research only; it does not authorize trading or promotion.
