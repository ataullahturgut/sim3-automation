# GOLD H3 — Latent-Regime Handoff V1 Preregistration

**Date:** 2026-10-04  
**Status:** unsupervised regime discovery on 2023-2024, 2025 reliability calibration, frozen 2026 stress.  
**Purpose:** determine whether the Handoff warning is reliable only in specific latent market regimes.

## Scientific idea

The Handoff warning is treated as a **conditional hazard**, not as a universal reversal rule.

A latent market regime is learned without reversal labels using pre-2025 data.  
Then 2025 Handoff alarm outcomes are used only to estimate **regime-specific reliability**.  
Only regimes with sufficiently high posterior probability of precision above 50% are allowed to act in 2026.

This is a selective/reject-option overlay:
- reliable regime -> permit Handoff FLIP;
- unreliable/uncertain regime -> reject Handoff action and keep the existing combined baseline.

## Existing combined baseline

HELIOS V5-DCE + frozen SAGE/OCS exception-only + frozen RuleFlow V3-TG.

## Canonical Handoff alarm

Before any regime filter:

- external_premax >= 0.60
- internal_now >= 0.60
- internal_d1 >= 0.00
- combined baseline still follows prevailing H3 momentum

No topology veto is applied at this stage.

## Latent-regime training universe

**2023-01-01 through 2024-12-31 only.**

No 2025/2026 reversal label or Handoff outcome is used to fit regimes.

### Regime features

All are known at the feature cutoff or are computed from strictly prior observations:

1. abs_h_ret_12
2. trend_strength
3. adverse_excursion
4. path_consistency
5. gc_volume_z20
6. opt_total_z20
7. signed_opt_pressure
8. core_confirmation
9. cross_dispersion
10. trailing-60 corr(Gold daily return, Nasdaq return), excluding current origin
11. trailing-60 corr(Gold daily return, VIX return), excluding current origin

Features are robust-scaled using **2023-2024 median and IQR only**.

Missing values are imputed with the **2023-2024 training median only**.

## Unsupervised regime model

Gaussian Mixture Model with full covariance.

Candidate K:
- 2
- 3
- 4

K is chosen by minimum BIC on 2023-2024 only.

Random state = 20261004.  
n_init = 50.  
reg_covar = 1e-5.

After fitting, the exact 2023-2024 scaler, imputation values, K, GMM parameters, and regime identities are frozen.

## Regime assignment uncertainty

For each origin:
- hard regime = maximum posterior component probability
- regime confidence = maximum component posterior
- regime entropy = normalized entropy of component posterior probabilities

A Handoff action can be considered only when regime confidence >= 0.60.  
Otherwise reject/KEEP baseline.

## 2025 reliability calibration

Use 2025 Handoff alarms only.

For each frozen regime:
- rescue count R
- broken count B
- Jeffreys posterior: theta ~ Beta(R + 0.5, B + 0.5)
- compute P(theta > 0.50)

A regime is **action-eligible** iff:
- Handoff alarms in 2025 >= 3
- P(theta > 0.50 | 2025) >= 0.80
- posterior mean theta > 0.50

No threshold grid is searched.

If no regime passes, V1 closes and 2026 is not used to create a rule.

## Frozen 2026 stress

Apply unchanged:
1. canonical Handoff alarm
2. frozen GMM regime mapping
3. regime confidence >= 0.60
4. regime must be in the 2025 action-eligible set

If all conditions pass -> FLIP existing combined baseline.
Else -> KEEP baseline.

Report:
- 2025 regime table and posterior reliability
- 2026 actions/rescue/broken/net/precision
- remaining missed reversals rescued
- baseline and assisted accuracy / balanced accuracy
- monthly stability
- action dates
- regime posterior confidence
- comparison of acted vs rejected Handoff alarms

## Governance

- 2026 is not used for GMM training.
- 2026 is not used for regime selection.
- 2026 is not used to select Bayesian reliability thresholds.
- No 2026-driven feature deletion/addition after this preregistration.
- Because the Handoff concept itself was motivated by 2026 diagnostics, the 2026 result remains a strict retrospective stress, not pristine prospective validation.
