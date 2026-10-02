# DART-H3 V1 — DEPENDENCE-AWARE INFERENCE AUDIT

**Date:** 2026-10-02
**Identity:** `DART_H3_V1_INFERENCE_AUDIT`
**Parent:** `DART_H3_V1_RESEARCH`
**Status:** DIAGNOSTIC / NO RETUNING

## Purpose

H3 forecasts overlap in calendar time, so row-level correctness observations are serially dependent and must not be treated as independent Bernoulli trials.

This audit quantifies uncertainty around paired performance differences using a circular moving-block bootstrap. It does not change DART, SENTRY, expert definitions, thresholds, or states.

## Inputs

Frozen prediction ledgers:
- `GOLD_H3_DART_V1_PREDICTIONS_2026-10-02.csv`
- `GOLD_H3_SENTRY_V1_PREDICTIONS_2026-10-02.csv`

## Comparisons

1. DART vs STRUCTURAL_IRIS
2. DART vs SENTRY
3. PATH_GLOBAL vs STRUCTURAL_IRIS

Periods:
- 2025
- 2026
- 2025-2026.

## Metrics

Paired differences:
- accuracy, percentage points;
- Brier, candidate minus comparator;
- log loss, candidate minus comparator.

## Dependence robustness

Circular moving-block bootstrap:
- block length 5 origins;
- block length 10 origins;
- 10,000 replicates each;
- fixed seed 20261002.

Report:
- observed paired difference;
- 95% percentile interval;
- bootstrap share where candidate improves:
  - accuracy > 0;
  - Brier < 0;
  - log loss < 0.

The two block lengths are sensitivity analyses, not model-selection alternatives.

## Interpretation

A point-estimate improvement with an interval crossing zero is suggestive rather than statistically decisive.

This audit cannot promote a model that failed its preregistered mechanism gate and cannot retune DART.
