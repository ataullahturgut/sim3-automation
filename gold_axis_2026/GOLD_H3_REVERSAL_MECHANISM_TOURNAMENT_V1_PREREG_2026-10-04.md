# GOLD H3 — Reversal Mechanism Tournament V1 Preregistration

**Date:** 2026-10-04
**Status:** multi-mechanism research tournament.
**Objective:** solve the remaining H3 reversal problem with several scientifically distinct mechanisms rather than a single ad-hoc rule.

## Governance

- 2023-2024: mechanism construction / fitting.
- 2025: threshold selection and eligibility only.
- 2026: frozen retrospective stress only.
- No 2026 outcome may choose a feature, threshold, model, or tie-break.
- Target is actual H3 reversal relative to prevailing 12h momentum, not generic V5 error.
- Any FLIP is allowed only when the current combined baseline still follows prevailing momentum.
- Combined baseline = HELIOS V5-DCE + frozen SAGE/OCS exception-only + frozen RuleFlow V3-TG.

## Shared origin-safe feature set

Available before the target:
- |12h Gold return|
- trend_strength
- adverse_excursion
- path_consistency
- opposite_semivar_share
- session_against_trend
- trend_close_location
- signed_opt_pressure
- signed_d_opt_pressure
- opt_total_z20
- gc_volume_z20
- gc_volume_accel_5
- core_confirmation
- cross_dispersion
- Gold-Nasdaq trailing correlation
- Gold-VIX trailing correlation

Derived only from current/past origins:
- trend age = consecutive origins with same momentum direction
- 1-origin and 3-origin deltas for structural features
- topology rotation
- recent-window multivariate mean shift

No future H3 event labels, no target-derived TRES path fields, no same-target information.

## Mechanism A — Multivariate Change-Point (MCP)

For every origin:
- reference window = prior 60 origins excluding the most recent 5
- recent window = prior/current 5 origins
- robustly standardized with reference median/MAD
- change score = Euclidean norm of recent-vs-reference standardized mean shift
- add topology-rotation magnitude as a separately reported component, not fitted weight

Threshold candidates are fixed quantiles of the 2023-2024 MCP score:
0.80, 0.85, 0.90, 0.95.

## Mechanism B — Sequential Evidence Log-Likelihood Ratio (SELLR)

On 2023-2024 only:
- define actual reversal vs continuation from target direction and current momentum;
- bin each signed mechanism feature into quintiles using 2023-2024 feature cut points;
- estimate Laplace-smoothed log P(bin | reversal) / P(bin | continuation);
- sum across features.

Features:
- adverse_excursion
- negative trend_strength
- negative trend_close_location
- session_against_trend
- opposite_semivar_share
- signed option pressure
- signed option-pressure change
- negative core_confirmation
- cross_dispersion
- topology rotation
- trend age

Threshold candidates = 2023-2024 SELLR score quantiles:
0.80, 0.85, 0.90, 0.95.

## Mechanism C — Duration/Hazard (HAZ)

Fit an interpretable logistic discrete-time hazard model on 2023-2024:
reversal ~
- log(1 + trend_age)
- |12h Gold return|
- trend_strength
- adverse_excursion
- path_consistency
- signed_opt_pressure
- opt_total_z20
- core_confirmation
- cross_dispersion
- MCP change score

Use L2 logistic regression with fixed C=1.0, class_weight=balanced.
No feature selection.

Threshold candidates = 2023-2024 fitted hazard-score quantiles:
0.80, 0.85, 0.90, 0.95.

## Mechanism D — Historical Analog Reversal Probability (ANALOG)

Using standardized shared features and 2023-2024 only:
- k = 25 nearest historical origins by Euclidean distance;
- score = mean reversal label among the 25 analogs.
- for 2023-2024 in-sample diagnostics use leave-one-out neighbors.

Threshold candidates = 2023-2024 analog-score quantiles:
0.80, 0.85, 0.90, 0.95.

## Handoff confirmation variants

For every mechanism, evaluate both:
1. RAW mechanism.
2. mechanism AND canonical Handoff:
   - external_premax >= 0.60
   - internal_now >= 0.60
   - internal_d1 >= 0

This tests whether Handoff is useful as confirmation rather than a standalone FLIP engine.

## 2025 eligibility gate

For each fixed mechanism/threshold/confirmation variant:
- actions >= 6
- precision >= 60%
- net rescue > 0
- action rate <= 15%
- >=70% of action months non-negative
- worst action-month net >= -1

Per mechanism family, select the eligible variant by:
1. highest net
2. highest precision
3. fewer actions
4. higher quantile
5. Handoff-confirmed preferred only as final tie-break

## Consensus challenger

If at least two mechanism families have an eligible 2025 variant:
- CONSENSUS2 acts when at least two selected mechanisms fire on the same origin.
- It must independently pass the same 2025 eligibility gate.
- No consensus threshold is tuned.

## Tournament winner

Eligible 2025 finalists (A/B/C/D and CONSENSUS2) are ranked:
1. highest 2025 net rescue
2. highest precision
3. fewer actions
4. higher balanced-accuracy gain over combined baseline

The single winner is frozen for 2026.

## 2026 report

For every 2025-eligible finalist and the frozen winner:
- actions / rescue / broken / net / precision
- remaining-53 rescues
- combined baseline accuracy and balanced accuracy
- assisted accuracy and balanced accuracy
- action dates
- overlap with SAGE and RuleFlow
- episode-first rescue count

## Scientific interpretation

This is not a black-box accuracy hunt. The four mechanisms test distinct hypotheses:
- MCP: a reversal follows a multivariate state change.
- SELLR: multiple weak origin-safe signals accumulate sequentially.
- HAZ: reversal risk depends on state age and fragility.
- ANALOG: reversal occurs when current geometry resembles historical reversal states.

Because the research question was motivated by retrospective 2026 errors, positive 2026 results remain retrospective stress evidence, not pristine prospective OOS validation.
