# SKEW-H3 V1 — AUTHORITY, PREREGISTRATION & DATA GATE

**Date:** 2026-10-03  
**Identity:** `SKEW_H3_V1_RESEARCH`  
**Branch:** `gold-h3-skew-v1-20261003`  
**Status:** **PREREGISTERED / BLOCKED_EXTERNAL_CVOL_ENTITLEMENT**

## 1. Purpose

SKEW-H3 is the second high-recall reversal-candidate specialist.

It is not a generic UP/DOWN forecaster, does not replace HELIOS V5-DCE, and does not reinterpret GVZ as directional skew.

Target:
`reversal_target = 1[y_up != momentum_up]`

Eligible context:
`aurora_follows_momentum == True`.

## 2. Official directional-options authority

CME Gold CVOL is the preferred authority because it already publishes the exact directional simple-variance indicators required by the research design.

Gold CVOL identifiers:
- CVOL: `GCVL`
- UpVar: `GCUP`
- DownVar: `GCDN`
- Skew: `GCSK`
- ATM: `GCAM`
- Convexity: `GCCV`

Definitions:
- UpVar is derived from OTM calls.
- DownVar is derived from OTM puts.
- Skew captures the difference/relative asymmetry between upside and downside implied variance.

This is materially different from GVZ, which measures aggregate implied volatility rather than directional tail asymmetry.

## 3. Origin-safe clock

Canonical H3 origin: 17:00 America/New_York.

CME CVOL EOD publication occurs after the H3 origin:
- DST schedule approximately 01:05 UTC next calendar date;
- non-DST approximately 02:05 UTC next calendar date.

Therefore same-trade-date EOD CVOL is not available at the 17:00 ET origin.

Frozen V1 rule:
`eligible CVOL row = latest published EOD business-date row strictly prior to feature_cutoff_date`

Same-date CVOL EOD is forbidden.

## 4. Frozen feature family

Core:
1. `gc_cvol`
2. `gc_upvar`
3. `gc_dnvar`
4. `gc_skew`
5. `gc_skew_change_1`
6. `gc_skew_z60`
7. `gc_up_dn_ratio`
8. `gc_asymmetry = (upvar-dnvar)/(upvar+dnvar)`
9. `momentum_x_skew`
10. `momentum_x_skew_change`
11. `gvz_minus_cvol` if same-origin GVZ is available under its existing governed lag
12. `skew_x_gvz_z` if GVZ state is available without adding a new lag search.

No feature may be selected from 2026 outcomes.

## 5. Model and evaluation freeze

Model:
- StandardScaler
- LogisticRegression
- C=1.0
- solver=lbfgs
- class_weight=balanced
- seed=20261003
- monthly expanding-origin refit
- min matured rows=80

Period roles:
- DEV / threshold selection: 2023-2024
- confirmation: 2025
- holdout: 2026

Candidate threshold grid:
`[0.35, 0.40, 0.45, 0.50, 0.55]`

Selection objective:
- maximize reversal F2;
- precision >= 0.45;
- candidate rate <= 0.35.

Tie-breaks:
1. higher reversal recall
2. higher precision
3. lower candidate rate
4. higher threshold

No eligible threshold => `NO_ELIGIBLE_SKEW_THRESHOLD`.

2025 confirmation requires:
- SKEW reversal recall > OPAL candidate recall on same eligible universe;
- >=1 true OPAL-missed reversal nominated;
- precision >=0.40.

2026 is opened only after confirmation PASS.

## 6. Data-access audit

Production Neon:
- GVZ exists.
- no Gold CVOL UpVar/DownVar/Skew series exists.

Repository:
- no `GCVL`, `GCUP`, `GCDN`, `GCSK`, CVOL EOD API, or CME OAuth integration exists.

Official access:
- CME CVOL EOD REST history endpoint supports date ranges and product filtering.
- production endpoint requires OAuth API ID/access token and product entitlement.
- historical DataMine CVOL also requires licensed/entitled access.

Current environment:
- exact directional skew source identity: PASS
- origin-safe lag authority: PASS
- feature/model/evaluation preregistration: PASS
- historical payload: ABSENT
- OAuth entitlement: ABSENT
- fitting allowed: NO

## 7. Stage result

**SKEW-H3 V1 is BLOCKED_EXTERNAL_CVOL_ENTITLEMENT.**

No GVZ-derived pseudo-skew, realized-return skew, GLD put/call volume proxy, or unrelated Cboe SKEW index may be substituted under the SKEW-H3 identity.

This stage is therefore completed as a governed data-access block, not as a failed model.

The next independent stage, HAZARD-H3, may proceed because it uses the existing origin-safe XAU intraday path and does not depend on unavailable licensed option-surface history.

If CVOL entitlement later becomes available, SKEW-H3 resumes from this frozen contract without retuning from later-stage results.
