# RC-RTE-H3 V1 — REGIME-CONDITIONAL REVERSAL TRANSITION ENGINE PREREGISTRATION

**Date:** 2026-10-04  
**Identity:** `RC_RTE_H3_V1`  
**Branch:** `gold-h3-rc-rte-v1-20261004`  
**Status:** **PREREGISTERED BEFORE 2026 OPENING**

## 1. Research question

The RTE V1–V4 batch established that reversal specialists are not globally stable.

The most important development instability is:
- 2025 H1: several reversal specialists have positive net rescue;
- 2025 H2: the same specialists become harmful.

Origin-state analysis shows that 2025 H2 is more continuation-dominant:
- trend strength shifts upward materially;
- the custom persistence axis rises;
- momenta-opposing Gold options pressure weakens.

RC-RTE therefore asks:

> Can we detect, from origin-available state only, which latent regime allows reversal specialists to act and which regime should force KEEP/V5 continuation?

## 2. State representation

Use only origin-available state from the frozen RTE V1 feature panel.

Raw state variables:
- v5_confidence
- trend_strength
- opposite_semivar_share
- deceleration_6h
- path_consistency
- adverse_excursion
- gc_dlog_volume_1
- gc_volume_z20
- gc_volume_accel_5
- signed_opt_pressure
- signed_d_opt_pressure
- opt_total_z20

At each sequential development block, standardize each raw variable using the matured training set only.

Define four custom mechanism axes with equal weights:

`persistence = (trend_strength_z + path_consistency_z + v5_confidence_z - adverse_excursion_z - opposite_semivar_share_z) / 5`

`fragility = (deceleration_6h_z + opposite_semivar_share_z + adverse_excursion_z - path_consistency_z) / 4`

`option_opposition = (signed_opt_pressure_z + signed_d_opt_pressure_z + opt_total_z20_z) / 3`

`participation_shock = (gc_volume_z20_z + gc_volume_accel_5_z + gc_dlog_volume_1_z) / 3`

No target information enters these axes.

## 3. Unsupervised regime map

Within each sequential training block:
- fit KMeans on the four custom mechanism axes;
- number of regimes: **K=3**
- n_init=50
- random_state=20261004

KMeans is used only as an unsupervised state compressor. It is not the direction forecast model.

Cluster IDs have no fixed semantic label. Each fitted cluster is evaluated for reversal-specialist utility using only matured training outcomes.

## 4. Frozen specialist proposal union

Three previously developed, already frozen reversal mechanisms may propose a V5 flip:

### SB — slow-burn
`p_rte >= 0.75 AND prev_p_rte >= 0.60 AND dp_rte <= 0.05`

### OPT — option-confirmed transition
`p_rte >= 0.65 AND p_inst >= 0.50 AND signed_opt_pressure > 0`

### MAT — material-reversal specialist
`p_material >= 0.70`

Union proposal:
`proposal = SB OR OPT OR MAT`

No specialist threshold is changed in RC-RTE.

## 5. Regime enablement rule

For each fitted regime in the matured training set, inspect only rows where `proposal=True`.

A regime is **REVERSAL_ENABLED** if all hold:
- proposal support >= 8
- rescue precision >= 0.55
- net rescue > 0

Otherwise the regime is **CONTINUATION_PROTECTED**.

At a test origin:
- if no proposal: KEEP V5
- if proposal and assigned regime is REVERSAL_ENABLED: flip V5
- otherwise: KEEP V5

Thus the regime router never invents a new directional signal; it only decides whether an already-frozen reversal proposal is permitted to override V5.

## 6. Sequential internal prospective development

No random split.

### Block A
Training / regime fit:
- all eligible rows before 2024-07-01

Test:
- 2024 H2

### Block B
Training / regime fit:
- all eligible rows before 2025-01-01

Test:
- 2025 H1

### Block C
Training / regime fit:
- all eligible rows before 2025-07-01

Test:
- 2025 H2

For each block:
- state standardization uses training only;
- KMeans uses training only;
- regime enablement uses training outcomes only;
- test block is scored once without alteration.

## 7. Pre-2026 robustness gate

Aggregate across Block A/B/C.

RC-RTE passes only if:
- total gated candidates >= 10
- aggregate net rescue >= +4
- aggregate rescue precision >= 0.58
- at least 2 of 3 sequential blocks have net rescue > 0
- no block has net rescue < -1
- RC-RTE assisted accuracy > V5 accuracy on the pooled three test blocks

Failure => `NO_ROBUST_RC_RTE_RULE`; 2026 remains unopened.

## 8. 2026 final holdout

Only if the robustness gate passes.

Final pre-2026 fit:
- training = all eligible rows through 2025-12-31
- fit state scaler and K=3 regime map
- compute regime enablement from training outcomes
- freeze enabled regimes

Apply exactly once to 2026.

Report:
- candidate count/rate
- rescued / broken / net rescue
- rescue precision
- eligible V5 accuracy -> RC-RTE assisted accuracy
- whole-clean-2026 correct count and accuracy
- V5 missed reversal + OPAL-no-candidate coverage
- regime counts and enabled-regime behavior

No 2026 outcome may change axes, K, specialist union, enablement criteria, or robustness gate.

## 9. Governance

- 2026 remains unopened until the sequential pre-2026 robustness gate passes.
- No future target enters regime construction.
- No cluster label is hand-named before utility audit.
- HELIOS V5-DCE remains binding unless RC-RTE passes all gates and a later promotion decision is made.
