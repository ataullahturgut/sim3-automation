# VAST-H3 V1 — VOLUME ABSORPTION & SESSION TRANSITION PREREGISTRATION

**Date:** 2026-10-04  
**Identity:** `VAST_H3_V1`  
**Branch:** `gold-h3-vast-v1-20261004`  
**Evidence class:** retrospective mechanism/development; no clean historical holdout claim.

## 1. Hypothesis

Daily aggregate futures Volume/OI failed to produce selective reversal candidates.

VAST tests a different microstructure hypothesis:

> Before an H3 reversal, the prevailing 12h Gold trend may still be positive/negative in price, while intraday effort/result deteriorates: opposite-direction hours absorb more volume, late-session price progress stalls or rejects, and Silver flow ceases to confirm Gold.

This information is not present in prior daily FLOW or DIVERGE models and is not explicitly encoded in the frozen RIFT path feature family.

## 2. Data

Research-only hourly proxies:
- Gold futures: `GC=F`
- Silver futures: `SI=F`

Verified 2025-01 through 2026-10 hourly coverage:
- GC positive volume rate ≈96.4%
- SI positive volume rate ≈96.4%

No production authority claim is made from Yahoo transport.

## 3. Origin clock

Canonical H3 reference remains 17:00 America/New_York.

At every H3 origin:
- only hourly rows timestamped <= **16:00 ET** on feature-cutoff date are usable;
- same/future bars beyond 16:00 ET are forbidden;
- origin requires at least 12 synchronized usable GC/SI hourly bars in the preceding 18 wall-clock hours.

## 4. Diurnal volume normalization

For every hourly GC/SI row:
- `log_volume = log1p(volume)`;
- identify ET hour-of-day;
- normalize only against prior observations at the **same ET hour**;
- trailing same-hour window = **40 observations**;
- minimum prior observations = **15**;
- current observation is excluded.

This removes the strong futures intraday volume seasonality without using future information.

## 5. Frozen origin features

Let `s=+1` when H3 12h momentum is UP and `s=-1` when DOWN.

Hourly return sign is based on log close-to-close return.

### Gold effort / confirmation
For h ∈ {3,6,12}:
- `gc_flow_h = s * sum(ret1 * volume) / sum(volume)`
- `gc_opp_vol_share_h = volume share on hours where s*ret1 < 0`

For h ∈ {6,12}:
- `gc_efficiency_h = abs(net log return) / sum(abs(hourly log returns))`
- `gc_absorption_h = mean(max(volume_z,0)) * (1 - gc_efficiency_h)`

Additional:
- `gc_late_rejection_3 = -s * GC_return_3h`
- `gc_late_rejection_6 = -s * GC_return_6h`
- `gc_opp_climax_z6 = max(volume_z among opposite-direction hours in last 6h)`
- `gc_with_climax_z6 = max(volume_z among momentum-direction hours in last 6h)`
- `gc_climax_gap6 = gc_opp_climax_z6 - gc_with_climax_z6`

### Silver confirmation
For h ∈ {6,12}:
- `si_flow_h = s * sum(SI_ret1 * SI_volume) / sum(SI_volume)`
- `si_opp_vol_share_h`

Additional:
- `si_late_rejection_3 = -s * SI_return_3h`
- `gc_si_flow_gap12 = gc_flow_12 - si_flow_12`
- `joint_opposition_share12 = mean(gc_opp_vol_share_12, si_opp_vol_share_12)`

No post-result feature search is allowed in V1.

## 6. Target / universe

Universe:
- HELIOS V5 follows 12h momentum.

Target:
- `rescue_target = 1[V5 is wrong]`

A VAST candidate means flip V5.

## 7. Model

- StandardScaler
- LogisticRegression
- C = 0.5
- class_weight = balanced
- solver = lbfgs
- seed = 20261004
- monthly expanding-origin refit
- minimum matured H3 training rows = 60

A training row is usable only when its H3 target end is <= current monthly feature cutoff.

## 8. Candidate thresholds

Frozen grid:
`[0.55, 0.60, 0.65, 0.70]`

## 9. Historical development robustness

Historical 2026 is development only.

Scored blocks:
- 2025 H2
- 2026 H1
- 2026 H2 through available September history

2025 H1 is primarily warm-up/training.

A threshold is development-eligible if:
- total candidates >=10
- aggregate net rescue >0
- rescue precision >=0.55
- at least 2 of 3 scored blocks have net rescue >0
- no block net < -2

Selection:
1. maximum aggregate net rescue
2. higher precision
3. more rescued
4. fewer candidates
5. higher threshold

No eligible threshold => `NO_ELIGIBLE_VAST_V1_MECHANISM`.

## 10. Prospective interpretation

A historical PASS is mechanism/development evidence only.

If VAST passes:
- freeze V1 before post-freeze use;
- run as shadow challenger from the first technically eligible prospective origin;
- production adoption requires authoritative hourly futures data and separate promotion evidence.

## 11. Governance

- No retrospective 2026 result is a clean holdout claim.
- No post-result feature additions or threshold changes under V1.
- HELIOS V5-DCE remains binding champion.
