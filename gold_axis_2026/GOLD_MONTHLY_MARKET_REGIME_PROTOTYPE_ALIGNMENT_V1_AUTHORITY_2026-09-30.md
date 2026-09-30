# GOLD MONTHLY — Prototype-Anchored State Alignment V1 Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / REGIME-ONLY SEMANTIC ALIGNMENT  
**Parents:** Market Regime Discovery V1; Market Regime Walk-Forward V1; Anchored vs Expanding Comparison V1

## 1. Purpose

Determine whether the weak/unstable R0/R1/R2 behavior seen across independently re-fitted HMMs is caused partly by latent-state label switching / semantic drift rather than by the underlying state inference itself.

This stage changes **only the mapping of latent HMM state IDs to semantic labels R0/R1/R2**.

It does **not** change:
- scaler;
- PCA;
- HMM parameters;
- posterior probabilities;
- predictive log score;
- OOD calculation;
- confidence threshold;
- training schedule.

## 2. Frozen semantic prototypes

Build three frozen semantic prototypes from the Market Regime Discovery V1 development period only:

- period: 2010-07..2024-12;
- reference states: R0, R1, R2 from Discovery V1;
- features: all 13 frozen market-state variables.

For each feature:
- compute development-period mean and population standard deviation across all months;
- standardize the 13 feature dimensions with those frozen development statistics.

For each reference regime R0/R1/R2:
- compute its 13-dimensional mean vector in this frozen standardized feature space.

These three vectors are the semantic prototypes.

## 3. New state-alignment rule

For every independently fitted HMM already used in the expanding-refit and annual-anchored detectors:

1. use that fit's own training history only to compute each latent state's 13-feature mean profile as a **filtered-posterior-weighted mean** over its training months (weights = that latent state's filtered posterior probability);
2. transform those latent-state profiles with the **frozen 2010-2024 prototype standardization**;
3. compute Euclidean distance from each latent state to each frozen R0/R1/R2 prototype across all 13 dimensions;
4. solve the one-to-one minimum-cost assignment with the Hungarian algorithm;
5. use that assignment to label latent states R0/R1/R2.

No Gold_r1-only ordering is allowed in the primary prototype-aligned result.

## 4. Governance boundary

Frozen prototype labels from 2010-2024 are allowed only for semantic naming.

They must not enter:
- HMM fitting;
- posterior filtering;
- predictive density;
- OOD;
- confidence;
- alarm logic.

For 2015-07..2024-12 replay, prototype alignment uses semantic prototypes that include later 2010-2024 information and is therefore **retrospective diagnostic only**.

For 2025-01..2026-08, the prototypes are fully frozen before the period and are operationally valid for this semantic-alignment test.

## 5. Systems to re-evaluate

Re-run with identical underlying fits:

### A. EXPANDING_REFIT + PROTOTYPE ALIGNMENT
- monthly refit through t-1;
- semantic mapping by frozen 13D prototypes.

### B. ANNUAL_ANCHORED + PROTOTYPE ALIGNMENT
- prior-December annual parameter freeze;
- 2015 warm-up exception unchanged;
- semantic mapping by frozen 13D prototypes.

The previous Gold_r1-order mappings must also be reproduced as a comparator.

## 6. Required outputs

For each detector:
- month-by-month old label vs prototype-aligned label;
- latent-state-to-prototype distance matrix;
- one-to-one assignment;
- count/share of months whose semantic label changes;
- R0/R1/R2 recall and balanced accuracy against Discovery reference labels (secondary descriptive metric);
- BELIRSIZ rate unchanged except where the semantic label attached to the same posterior changes;
- transition-delay diagnostics.

Mandatory checkpoint table:
- 2024-03..2024-06;
- 2026-04..2026-08.

## 7. Primary decision question

Does prototype alignment remove the suspicious R0 behavior without changing the underlying density model?

Key evidence for a useful alignment:
- 2026-05/06/07 semantic path becomes more coherent relative to frozen prototypes;
- R0 recall does not collapse under annual anchoring;
- cross-refit label changes are explainable by prototype distances;
- predictive log score is exactly unchanged from the prior comparison (mapping-only invariant).

## 8. Binding interpretation rule

If prototype alignment materially improves state semantic stability, use the prototype-aligned labels for the next detector comparison.

If it does not, label switching is not the main issue; the next regime-only stage must address model dynamics / transition detection rather than naming.

No alarm selection, weighting, suppression, forecast correction, or routing is authorized by this stage.
