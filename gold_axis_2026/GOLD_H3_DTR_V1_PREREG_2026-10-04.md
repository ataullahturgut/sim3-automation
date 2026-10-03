# DTR-H3 V1 — DUAL-TRANSITION REVERSAL PREREGISTRATION

**Date:** 2026-10-04  
**Identity:** `DTR_H3_V1`  
**Branch:** `gold-h3-dtr-v1-20261004`  
**Evidence class:** **POST-HOLDOUT DEVELOPMENT FOR FUTURE PROSPECTIVE USE**  
**Status:** **PREREGISTERED BEFORE DTR RESULTS**

## 1. Motivation

The OAR/RTE concept-drift audit shows that the reversal relationship itself changed between 2024-2025 and 2026:
- OAR rescue rate fell from 64.71% to 15.79%;
- rescue-vs-broken feature-effect correlation was -0.155;
- opposite-semivariance-share effect changed from +0.151 SMD in 2024-2025 to -1.355 SMD in 2026;
- V5 confidence and trend strength were both shifted upward in 2026 OAR states.

This suggests two reversal morphologies:

1. **Exhaustion transition:** opposite-side realized variance has already built relative to similar continuations.
2. **Pre-emptive transition:** in a high-persistence / high-confidence trend, a true reversal may occur before opposite-side realized variance becomes visible.

DTR encodes these as two state-conditional branches rather than forcing one global reversal morphology.

## 2. Base proposal

Use the frozen OAR proposal:
- pRTE >= 0.60
- pInst >= 0.50
- signed option pressure > 0
- signed change in option pressure > 0

No OAR threshold is searched.

## 3. Origin-local persistence state

For every eligible origin, using only prior origins with feature_cutoff_date < current feature_cutoff_date:
- take the most recent 60 eligible feature rows;
- compute the median V5 confidence;
- compute the median trend strength.

If fewer than 20 prior rows exist, DTR does not act.

Define:
`HIGH_PERSISTENCE = v5_confidence > rolling_median(v5_confidence) AND trend_strength > rolling_median(trend_strength)`.

This uses no target outcome.

## 4. Dual transition branches

Use the already-origin-safe counterfactual gap:
`cf_opposite_semivar_share_gap = current opposite-semivariance share - median matched-continuation-twin share`.

### PREEMPTIVE branch
If HIGH_PERSISTENCE:
- permit OAR only when `cf_opposite_semivar_share_gap < 0`.

Interpretation: options pressure is turning against a strong trend before adverse realized variance has expanded beyond continuation twins.

### EXHAUSTION branch
If not HIGH_PERSISTENCE:
- permit OAR only when `cf_opposite_semivar_share_gap > 0`.

Interpretation: reversal pressure is already confirmed by excess adverse realized variance versus matched continuations.

All thresholds are structural zero/median thresholds. No numeric cut-point search is allowed.

## 5. Development audit

Because 2026 has already been consumed as an APT holdout, DTR is developed on 2024-2026 and cannot claim any independent retrospective holdout.

Report separately for:
- 2024
- 2025
- 2026

Development viability requires:
- total candidates >= 10
- pooled net rescue > 0
- pooled rescue precision >= 0.60
- at least 2 of 3 years have net rescue >= 0
- worst year net rescue >= -1.

No alternative branch definition is searched if this fails.

## 6. Prospective freeze

If development viability passes:
- freeze exact DTR rule on 2026-10-04;
- first prospective eligible feature cutoff: 2026-10-05;
- DTR runs SHADOW ONLY initially;
- live override authority requires at least 5 matured prospective DTR candidates and recent-5 net utility >= +1;
- otherwise HELIOS V5-DCE remains the live decision.

If development viability fails:
- no DTR prospective freeze is allowed.

## 7. Governance

No 2024-2026 DTR result is independent validation.  
The next valid independent evidence is future prospective data after the freeze date.
