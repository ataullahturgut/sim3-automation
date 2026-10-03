# PGR-H3 V1 — PROSPECTIVE GUARDED REVERSAL SPECIALIST

**Date:** 2026-10-04  
**Identity:** `PGR_H3_V1`  
**Branch:** `gold-h3-pgr-v1-20261004`  
**Evidence class:** **POST-HOLDOUT DEVELOPMENT FOR FUTURE PROSPECTIVE USE**

## 1. Governance reset

APT-RTE passed its pre-2026 development gate but failed the independent 2026 holdout:
- 2 rescue / 10 broken / net -8
- whole-clean-2026 hypothetical accuracy 59.16% vs V5 63.35%.

Therefore 2026 Jan-Sep is now development data for any successor designed after 2026-10-04.

No PGR result on 2024-2026 may be described as an independent holdout.

The first independent PGR evidence begins with the governed prospective stream from 2026-10-05 onward.

## 2. Base proposal

PGR uses the strongest broad reversal mechanism found before the APT holdout:

OAR q=0.60:
- `p_rte >= 0.60`
- `p_inst >= 0.50`
- `signed_opt_pressure > 0`
- `signed_d_opt_pressure > 0`

PGR does not use APT's futures-volume sign gate as a hard rule, because that rule failed in 2026.

## 3. Candidate-state representation

For each OAR candidate use six origin-available validity coordinates:

1. `opposite_extreme_recency`
2. `gc_volume_accel_5`
3. `gc_dlog_volume_1`
4. `path_consistency`
5. `v5_confidence`
6. `trend_strength`

These were chosen as mechanism variables describing:
- single-shock/whipsaw character,
- futures participation change,
- path persistence,
- V5 certainty,
- trend maturity.

No target magnitude or future information is used.

## 4. Rescue-vs-broken prototypes

For a training set of matured OAR candidates:

- standardize the six coordinates using training-candidate mean and standard deviation only;
- construct a **RESCUE prototype** as the coordinate-wise median of rescued candidates;
- construct a **BROKEN prototype** as the coordinate-wise median of broken candidates;
- compute L1 / Manhattan distance from a test candidate to each prototype.

Prototype margin:
`margin = distance_to_broken - distance_to_rescue`.

A candidate is `prototype_trusted` iff:
`margin > 0`.

No distance threshold is searched.

## 5. Cross-year development audit

Use leave-one-year-out development across:
- 2024
- 2025
- 2026

For each held-out year:
- prototype scaler and medians use the other two years only;
- the held-out year does not influence its own prototypes.

Report OAR baseline and prototype-guarded:
- candidate count
- rescue / broken / net
- precision.

Development viability requires:
- guarded acted candidates >=10 pooled
- pooled net rescue >0
- pooled precision >=0.60
- at least 2 of 3 held-out years have net rescue >=0
- worst held-out year net >=-1.

This is **development evidence only**, not an independent validation gate.

## 6. Frozen prospective model

If the cross-year audit is viable, freeze one production candidate-validity model using all matured 2024-2026 development OAR candidates available by 2026-10-04:
- scaler
- rescue median prototype
- broken median prototype
- six feature identities
- OAR base rule.

No future recalibration of prototypes is allowed until a separately governed version change.

## 7. Prospective shadow-first trust

From 2026-10-05 onward:

1. PGR generates a candidate when:
   - OAR proposal is true;
   - prototype margin >0.

2. Initially every PGR candidate is **SHADOW ONLY**.

3. Maintain outcomes of prospective PGR candidates after their H3 target matures.

4. Live override may activate only after **5 matured prospective PGR candidates** exist and the most recent 5 have net utility >= +1, equivalent to at least 3 successful rescues out of 5.

5. If recent-5 net falls below +1, live override automatically returns to SHADOW ONLY.

6. Vetoed/shadow candidates continue to be scored after maturity.

This creates a self-validating specialist whose live authority can be earned, lost, and regained using only prospective evidence.

## 8. Binding fallback

Until prospective trust activates:
- HELIOS V5-DCE remains the live direction decision;
- PGR may emit diagnostics/shadow reversal candidates but may not override V5.

## 9. Prospective evaluation

Primary prospective metrics:
- candidate count
- shadow rescue / broken / net
- last-5 trust status
- live override count
- live rescue / broken / net
- whole-system direction accuracy vs frozen V5 baseline.

No retrospective threshold tuning is permitted after 2026-10-04.
