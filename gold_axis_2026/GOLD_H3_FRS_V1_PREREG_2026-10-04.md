# FRS-H3 V1 — FUZZY / UNCERTAINTY REPRESENTATION TOURNAMENT PREREGISTRATION

**Freeze date:** 2026-10-04  
**Branch:** `gold-h3-fuzzy-reversal-tournament-v1-20261004`  
**Identity:** `FRS_H3_V1`  
**Status:** **FROZEN BEFORE TOURNAMENT RESULTS**

## 1. Purpose

The objective is not to fit another generic UP/DOWN classifier.

The experiment asks:

> Given the same origin-safe reversal and continuation evidence, which uncertainty representation best separates genuine V5 reversals from correct V5 continuations while preserving abstention / damping when evidence is conflicting?

Historical 2026 is development/stress-test only because the prior clean holdout has already been spent.

The first possible new clean evidence begins prospectively after the freeze.

## 2. Eligible universe

Use only origins where:
`v5_pred == momentum_up`

Target for retrospective mechanism evaluation:
`rescue_target = 1[v5_pred != y_up]`

The fuzzy systems do not replace V5 globally. They act only as reversal separators around V5 continuation calls.

## 3. Common evidence layer

All representations receive the **same** evidence. Only the uncertainty geometry changes.

### Reversal evidence set H_R

1. `rte = p_rte`
2. `material = p_material`
3. `options = prior-history empirical percentile(signed_opt_pressure)`
4. `fragility = prior-history empirical percentile(fragility_axis)`

### Continuation evidence set H_C

1. `v5 = v5_confidence`
2. `persistence = prior-history empirical percentile(persistence_axis)`
3. `options_support = 1 - options`
4. `path_support = 1 - fragility`

All empirical percentiles are computed from prior-origin history only. No current/future target enters evidence construction.

Mechanism axes:

`persistence_axis = mean(z(trend_strength), z(path_consistency), z(v5_confidence), -z(adverse_excursion), -z(opposite_semivar_share))`

`fragility_axis = mean(z(deceleration_6h), z(opposite_semivar_share), z(adverse_excursion), -z(path_consistency))`

The z-standardization uses prior-origin history only and is refreshed monthly.

## 4. Common summary statistics

For every origin:

`R = mean(H_R)`

`C = mean(H_C)`

`delta = R - C`

Expert dispersion:

`D = clip((std(H_R)+std(H_C))/2, 0, 1)`

Raw conflict:

`K = min(R,C)`

No representation may change H_R or H_C.

## 5. Tournament representations

### A. Type-1 fuzzy baseline (T1)

`mu_R = R`
`mu_C = C`

certainty:
`Q = abs(mu_R-mu_C)`

### B. Intuitionistic fuzzy set (IFS)

Raw `R,C` are projected to satisfy:
`mu + nu <= 1`

Let:
`s=max(1,R+C)`
`mu=R/s`
`nu=C/s`
`pi=1-mu-nu`

score:
`S=mu-nu`

certainty:
`Q=1-pi`

### C. Pythagorean fuzzy set (PFS)

Let:
`s=max(1,sqrt(R^2+C^2))`
`mu=R/s`
`nu=C/s`
`pi=sqrt(max(0,1-mu^2-nu^2))`

score:
`S=mu^2-nu^2`

certainty:
`Q=1-pi`

### D. q-rung orthopair fuzzy set (QROFS)

Frozen q:
`q=3`

Let:
`s=max(1,(R^q+C^q)^(1/q))`
`mu=R/s`
`nu=C/s`
`pi=(max(0,1-mu^q-nu^q))^(1/q)`

score:
`S=mu^q-nu^q`

certainty:
`Q=1-pi`

### E. Hesitant fuzzy set (HFS)

Retain the full evidence sets H_R and H_C.

score:
`S=mean(H_R)-mean(H_C)`

hesitation/disagreement:
`H=clip((std(H_R)+std(H_C))/2,0,1)`

certainty:
`Q=1-H`

### F. Picture fuzzy set (PFS-Picture)

Frozen decomposition:
- reversal-positive `P=max(R-C,0)`
- continuation-negative `N=max(C-R,0)`
- neutral `U=min(R,C)`
- refusal `F=1-max(R,C)`

These components sum to 1.

score:
`S=P-N`

certainty:
`Q=1-(U+F)`

### G. Single-valued neutrosophic set (SVNS)

`T=R`
`F=C`

Indeterminacy combines conflict and expert disagreement:
`I=clip(0.5*(1-abs(R-C)) + 0.5*D, 0, 1)`

score:
`S=T-F`

certainty:
`Q=1-I`

T, I and F remain independent; no sum-to-one projection is applied.

### H. Interval Type-2 fuzzy set (IT2FS)

Reversal footprint of uncertainty:
- `R_low = Q25(H_R)`
- `R_high = Q75(H_R)`

Continuation footprint:
- `C_low = Q25(H_C)`
- `C_high = Q75(H_C)`

Dominance interval:
- lower `L = R_low - C_high`
- upper `U = R_high - C_low`

score:
`S=(L+U)/2`

uncertainty width:
`W=clip(U-L,0,1)`

certainty:
`Q=1-W`

## 6. Frozen four-way action rule

Actions:
- KEEP V5
- DAMP V5
- FLIP V5
- ABSTAIN

For T1 / IFS / Pythagorean / q-rung / HFS / SVNS:

- FLIP if `S >= 0.15 AND Q >= 0.55`
- DAMP if `S > 0 AND Q >= 0.35` but FLIP condition fails
- ABSTAIN if `Q < 0.35`
- KEEP otherwise

Picture fuzzy:
- FLIP if `P >= 0.15 AND P > U AND P > F`
- DAMP if `P > N` and FLIP fails
- ABSTAIN if `F >= max(P,N,U)`
- KEEP otherwise

Interval Type-2:
- FLIP if `L >= 0.10`
- DAMP if `U > 0 AND L < 0.10`
- ABSTAIN if `L <= 0 <= U AND W >= 0.50`
- KEEP if `U <= 0`

If both DAMP and ABSTAIN conditions could apply, ABSTAIN has priority.

## 7. Probability action mapping

Direction:
- KEEP: V5 direction unchanged
- DAMP: V5 direction unchanged
- FLIP: V5 direction reversed
- ABSTAIN: no action prediction

Probability for calibration diagnostics:
- KEEP: `p_adj=p_v5`
- DAMP: `p_adj=0.5 + 0.5*(p_v5-0.5)`
- FLIP: `p_adj=1-p_v5`
- ABSTAIN: `p_adj=0.5`

## 8. Historical forward replay

Retrospective development blocks:
- 2024 H2
- 2025 H1
- 2025 H2
- 2026 H1
- 2026 H2 through available September data

Metrics per representation:
- FLIP count
- rescue
- broken
- net rescue
- flip precision
- DAMP count
- ABSTAIN count
- action coverage
- assisted directional accuracy where ABSTAIN is treated as KEEP only for whole-benchmark comparability
- Brier and log loss from p_adj
- block stability
- worst block net
- OPAL-no-candidate missed-reversal hits

## 9. Tournament interpretation

Historical replay is explicitly **development evidence**, not clean validation.

A representation is development-promising only if:
- aggregate net rescue > 0
- flip precision >= 0.55
- at least 3 of 5 blocks have net rescue >= 0
- worst block net >= -2
- assisted full directional accuracy is not below V5
- no more than 35% of eligible origins are FLIP decisions

If several pass, rank by:
1. aggregate net rescue
2. flip precision
3. lower worst-block loss
4. lower FLIP rate
5. Brier score

No historical winner is promoted directly.

## 10. Prospective governance

After the historical tournament:
- choose at most one representation as the shadow challenger;
- freeze its mathematical rules unchanged;
- first clean origin is post-freeze only;
- promotion requires at least 20 prospective FLIP actions or 6 calendar months, whichever is later;
- HELIOS V5-DCE remains binding production champion until prospective evidence supports promotion.
