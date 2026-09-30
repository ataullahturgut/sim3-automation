# GOLD MONTHLY — E/G Historical Validation V2 Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / SUPERSEDES V1 SCOPE  
**Purpose:** extend independent pre-discovery validation through 2024 and separate canonical ChHHO evidence from counterfactual historical stress replay.

## 1. Independent pre-discovery market window

Use canonical monthly Gold from **2010-01..2024-12** because E/G were discovered only after inspecting 2025/2026 misses.

Frozen signals:
- E-level precursor: Gold >20% above prior trailing-12-month mean.
- G: Gold 3-month log return <= -10%.

Report next-month absolute Gold movement versus the unconditional 2010-2024 baseline:
- mean;
- median;
- Q3;
- event mean/median;
- uplift ratio;
- event count above unconditional Q3.

No threshold fitting to event outcomes.

## 2. Model-specific evidence hierarchy

### Canonical evidence
For signal origins whose target is inside the frozen canonical ChHHO period, use the frozen ChHHO artifact directly. Do not rerun the model.

Artifact authority:
- ChHHO artifact 10989389723.

### Counterfactual historical stress
For signal origins before the canonical ChHHO period, use the unchanged ChHHO implementation with the earliest current-method GPR snapshot (2021-10-18), truncated to each historical required month.

This is not PIT validation because that GPR methodology/snapshot was not available at the old origin date.

Origins that fail the frozen ChHHO internal minimum-history gate remain unbuildable.

## 3. Full E and G interpretation

Full E requires:
- E-level precursor; and
- |ChHHO predicted return - current canonical Gold 1m return| > 5pp.

G itself does not require a model prediction. ChHHO is evaluated conditionally to determine whether G also predicts ChHHO failure.

Frozen model-error labels:
- AE > 63.06 USD
- APE > 2.96117%
- absolute log-return error > 3.00590pp

## 4. Decision rule

A signal may be called a historical market-risk signal if its pre-discovery market-state outcomes show materially elevated next-month movement.

A signal may be called a ChHHO high-error alarm only if pre-discovery model-specific evidence supports elevated ChHHO error. Discovery-period 2025/2026 hits are not sufficient by themselves.
