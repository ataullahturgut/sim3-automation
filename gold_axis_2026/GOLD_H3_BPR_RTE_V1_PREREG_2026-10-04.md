# BPR-RTE-H3 V1 — BAYES PRIOR-SHIFT REVERSAL ENGINE PREREGISTRATION

**Date:** 2026-10-04  
**Identity:** `BPR_RTE_H3_V1`  
**Branch:** `gold-h3-bpr-rte-v1-20261004`  
**Status:** **PREREGISTERED BEFORE 2026 OPENING**

## 1. Structural diagnosis

RTE V1 uses a LogisticRegression fitted with `class_weight=balanced`.

That is useful for learning reversal-vs-continuation feature evidence, but it intentionally suppresses the observed class prior.

The development blocks show that the real V5-continuation error prior is not stable:
- 2025 H1 V5 accuracy on the eligible universe ≈ 60.8%;
- 2025 H2 V5 accuracy ≈ 74.3%.

Therefore a reversal score learned under approximately balanced class odds can remain too aggressive when the live base rate of V5 missed reversals falls.

BPR-RTE treats this as **prior-probability shift**, not a new feature-model problem.

## 2. Evidence score

Use the existing origin-safe RTE V1 instantaneous score:
- `p_inst`

No RTE feature or model is refit in this experiment.

Interpret `p_inst` as a balanced-prior reversal evidence score.

## 3. Origin-safe live reversal prior

At each origin t:

1. collect eligible V5-continuation origins whose `target_end_date_h3 <= feature_cutoff_date_t`;
2. take the **most recent 60 matured origins**;
3. let:
   - n = matured rows in the window
   - k = number with `rescue_target=1`

Apply fixed Beta(5,5) shrinkage:

`pi_t = (k + 5) / (n + 10)`

If fewer than 20 matured origins exist, no BPR candidate is permitted.

No window-length search and no prior-hyperparameter search are allowed.

## 4. Prior-shift correction

Because the evidence model was trained with balanced class weighting, use equal-odds reference prior 0.5.

Define:

`logit(p_bpr) = logit(p_inst) + logit(pi_t)`

and

`p_bpr = logistic(logit(p_bpr))`.

This is treated as a prior-shift score, not claimed as perfectly calibrated probability.

## 5. Candidate rule

Frozen threshold grid:

`q ∈ [0.40, 0.45, 0.50, 0.55, 0.60]`

Candidate:
`p_bpr >= q`

Action:
flip V5 direction.

No additional options, regime, or path gate is used in V1. The experiment isolates the contribution of base-rate correction.

## 6. Development robustness

Development blocks:
- 2024 H1
- 2024 H2
- 2025 H1
- 2025 H2

For each q report:
- candidate count/rate
- rescued
- broken
- net rescue
- rescue precision

Robust-eligible if:
- aggregate candidate count >=15
- aggregate net rescue >= +5
- aggregate rescue precision >=0.58
- candidate rate <=0.25
- at least 3 of 4 half-year blocks have net rescue >0
- no half-year block has net rescue < -1

Selection:
1. maximum aggregate net rescue
2. higher precision
3. more rescued
4. lower candidate rate
5. higher threshold

No eligible threshold => `NO_ROBUST_BPR_RTE_RULE`; 2026 remains unopened.

## 7. 2026 final holdout

Only if the pre-2026 robustness gate passes.

The selected q is frozen.

For each 2026 origin:
- recompute `pi_t` only from matured eligible origins available at that origin;
- compute `p_bpr`;
- apply the frozen q exactly once.

Report:
- live prior range/median
- candidates/rate
- rescued/broken/net
- rescue precision
- eligible V5 -> assisted accuracy
- whole-clean-2026 accuracy
- OPAL-no-candidate missed-reversal coverage

No 2026 outcome may alter q, prior window, Beta shrinkage, or formula.

## 8. Governance

2026 remains unopened unless the 2024-2025 half-year robustness gate passes.  
HELIOS V5-DCE remains binding until a separate promotion decision.
