# ADAH-D1 V1 — ADAPTIVE DIRECTION-AGE HAZARD PREREGISTRATION

**Date:** 2026-10-05  
**Identity:** `ADAH_D1_V1`  
**Status:** FROZEN BEFORE ADAH RESULT RUN

## Purpose

Resolve only the specific CIG-D1 uncertainty class created when an OPAL H3 reversal survives into a final V5-vs-AURORA direction flip.

The scientific hypothesis is that the mapping

`OPAL H3 reversal -> immediate next-day D1 reversal`

is non-stationary. Therefore ADAH does not fit one static 2022-2025 coefficient vector and transport it unchanged. It uses only **matured prior OPAL events** and updates online.

## Event universe and target

Universe: every frozen OPAL override event for which the next D1 price is available.

Target:
- `immediate=1` if next-day D1 direction equals OPAL reversal direction;
- `immediate=0` if next-day D1 direction equals the pre-OPAL AURORA direction.

ADAH may be used operationally only when OPAL survives to a final V5-vs-AURORA flip and the parent CIG state is UNCERTAIN.

## Origin-safe context

1. OPAL reversal probability.
2. OPAL direction.
3. trend strength.
4. CFTC options money-manager z52.
5. CFTC options swap z52.
6. spec-vs-swap gap.
7. CFTC report age = calendar days from frozen `cot_available_date` to feature cutoff.
8. fresh-state flag = report age <= 2 calendar days.

No future path, D1 realization, or later CFTC report is used.

## Predeclared adaptive candidates

All predictions are strictly prequential: an event can update a candidate only after its D1 target is mature.

### DBH93
Hierarchical dynamic Beta-Bernoulli hazard.
- state cell = OPAL direction x fresh/aged CFTC state.
- monthly forgetting retention = 0.93.
- Jeffreys prior Beta(0.5,0.5).
- cell probability shrunk toward global dynamic probability using fixed `w=n_eff/(n_eff+4)`.

### DBH97
Same as DBH93, retention = 0.97.

### ANALOG9
Recency-weighted local analog hazard.
- features: p_reversal, trend_strength, MM z52, swap z52, spec-swap gap, CFTC report age, OPAL direction.
- standardization uses only prior events.
- k = 9 nearest prior events.
- distance weight = exp(-distance).
- recency weight = exp(-age_days/365).
- Jeffreys smoothing Beta(0.5,0.5).

### ENSEMBLE
Arithmetic mean of DBH97 and ANALOG9 probabilities.

## Period roles

- initialization/development history: 2022-2023.
- candidate selection: 2024 only.
- confirmation: 2025 only.
- 2026 is opened only after the 2025 confirmation rule is evaluated.

Candidate selection criterion:
1. lowest 2024 Brier score on all OPAL override events;
2. tie: lower log loss;
3. tie: simpler candidate order DBH93, DBH97, ANALOG9, ENSEMBLE.

No 2025/2026 result may change the selected candidate.

## Fixed selective action rule

For the selected candidate:
- p(immediate) >= 0.65 -> choose OPAL/V5 reversal direction.
- p(immediate) <= 0.35 -> choose AURORA/base direction.
- otherwise -> ABSTAIN / preserve CIG UNCERTAIN.

No threshold search is allowed.

## 2025 confirmation gate

PASS requires all:
1. selected model Brier <= prequential static-global baseline Brier on all 2025 OPAL override events;
2. on 2025 final V5 flip events, at least 4 selective actions;
3. selective accuracy >= 70%;
4. no more than 2 incorrect selective actions.

If FAIL, 2026 is reported only as a diagnostic stress test and ADAH is not promotable.

If PASS, 2026 is a frozen retrospective holdout for this challenger.

## 2026 decision test

Report:
- all OPAL override Brier/log loss;
- final V5 flip selective actions, accuracy, coverage;
- CIG-D1 integration overall;
- August 2026 11 original UNCERTAIN dates individually;
- comparison against original CIG and HAG-D1 V1.

Promotion requirement:
- 2026 CIG selective accuracy must not fall below original CIG;
- August coverage may rise only if August selective accuracy remains >=75%;
- at least 3 August UNCERTAIN dates must be resolved to count as a meaningful coverage gain.

Failure => reject ADAH-D1 V1; do not retune on 2026.
