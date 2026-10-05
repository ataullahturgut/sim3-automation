# GOLD D1 — AUGUST 2026 TIMING DIAGNOSTIC CONTINUATION

**Date:** 2026-10-05  
**Status:** RETROSPECTIVE DIAGNOSTIC / NO MODEL PROMOTION  
**Parent:** CIG-D1 August 2026 coverage-collapse diagnostic + HAG-D1 V1

## 1. Binding August baseline

August 2026:
- 21 D1 days
- 10 full 4/4 consensus actions
- 8 correct = 80.00%
- coverage = 47.62%
- 11 UNCERTAIN

The 11 UNCERTAIN rows are caused by the OPAL/V5 reversal lineage conflicting with the AURORA-side lineage. The low coverage remains protective abstention.

## 2. Timing anatomy of the 11 August UNCERTAIN rows

Using cumulative XAU direction from the feature cutoff to D+1/D+2/D+3, relative to OPAL direction:

- EARLY_STABLE: 5
- DELAYED_H3: 2
- PREMATURE_REVERSED: 1
- FALSE_H3: 3

Rows:

| D1 issue | OPAL | D+1 cumulative | D+2 cumulative | D+3 cumulative | Class |
|---|---|---:|---:|---:|---|
| 2026-08-03 | UP | -0.194% | +0.230% | +3.139% | DELAYED_H3 |
| 2026-08-04 | UP | +0.424% | +3.340% | +5.110% | EARLY_STABLE |
| 2026-08-07 | UP | +1.203% | +2.168% | +2.963% | EARLY_STABLE |
| 2026-08-12 | UP | +0.486% | -0.118% | -0.629% | PREMATURE_REVERSED |
| 2026-08-13 | DOWN | -0.601% | -1.110% | -0.060% | EARLY_STABLE |
| 2026-08-14 | UP | -0.512% | +0.544% | +0.029% | DELAYED_H3 |
| 2026-08-21 | DOWN | +1.732% | +3.239% | +3.232% | FALSE_H3 |
| 2026-08-24 | DOWN | +1.482% | +1.475% | +0.926% | FALSE_H3 |
| 2026-08-25 | DOWN | -0.007% | -0.547% | -0.902% | EARLY_STABLE |
| 2026-08-26 | DOWN | -0.541% | -0.895% | -2.096% | EARLY_STABLE |
| 2026-08-28 | UP | -1.212% | -3.604% | -4.826% | FALSE_H3 |

Among these 11 rows:
- OPAL D1 direction correct: 6/11
- OPAL terminal H3 direction correct: 7/11
- AURORA D1 direction correct: 5/11

Therefore August UNCERTAIN is not one homogeneous failure class.

## 3. State-age / CFTC-vintage timing challenger

Added origin-safe state variables:
- p(reversal) level and change
- reversal-state age
- override-run age
- CFTC vintage age / position
- optional COT and fast-path features

Pre-2025 family selection again preferred a FAST_STATE-type specification.

Transport:
- 2025 override selective action accuracy: 61.11%
- 2026 override selective action accuracy: 63.64%
- August original 11 UNCERTAIN: 10 resolved, only 5 correct = 50.00%

Decision: **FAIL / no promotion.**

State duration and CFTC-vintage age are not sufficient to resolve August D1 timing.

## 4. Four-state competing-risk / timing classifier

A four-class target was tested:
1. EARLY_STABLE
2. DELAYED_H3
3. PREMATURE_REVERSED
4. FALSE_H3

Family selection used <=2023 development and 2024 confirmation; selected family was FAST_STATE.

Results after <=2024 refit:
- 2025 D1 timing: 16 actions / 23, 62.50% selective accuracy
- 2026 D1 timing: 22 actions / 25, 63.64% selective accuracy
- 2026 four-state class accuracy: 24%
- August 11 UNCERTAIN: 10 actions, 5 correct = 50.00%

Decision: **FAIL / no promotion.**

Explicit multi-state timing does not solve the problem with the current T-1 information set.

## 5. Upcoming Tier-1 event-clock hypothesis

Exploratory August observation:
- among the 11 UNCERTAIN rows, issue dates with CPI/PPI/NFP/JOLTS were 4/4 OPAL-correct on D1.

2026 transport across all OPAL overrides:
- upcoming CPI/PPI/NFP/JOLTS/FOMC-statement issue days: 8/9 OPAL D1 correct = 88.89%
- non-event override days: 6/16 = 37.50%

This looked strong but was discovered after inspecting August.

Exact same event definition transported to 2025:
- 2025-04-04 NFP: OPAL wrong
- 2025-07-15 CPI: OPAL wrong
- 2025-07-29 JOLTS: OPAL wrong
- event subset: 0/3
- non-event subset: 9/20

Decision: **REJECT AS GENERAL RULE.**

Scheduled event proximity is a catalyst/timing context, not a stable standalone D1 realization gate.

## 6. RTE path-geometry reuse as D1 timing sensor

RTE was not reused as an override model. Origin-safe path geometry was tested as timing information:
- opposite semivariance share
- 6h deceleration
- session-against-trend
- path consistency
- trend close location
- opposite-extreme recency
- jump concentration
- trend-to-range
- adverse excursion
- optional CME/option-flow variables

Pre-2025 family selection:
- GEOM_ONLY 2024 confirmation accuracy 70.00%
- balanced accuracy 76.92%

But transport failed:
- 2025 selective action accuracy: 58.82%
- 2026 selective action accuracy: 52.38%
- August 11 UNCERTAIN: 9 actions, only 3 correct = 33.33%

Decision: **FAIL / no promotion.**

## 7. Binding diagnosis after continuation tests

The evidence now rejects the following as sufficient August fixes:
- remove OPAL
- HAG binary timing classifier
- threshold retuning
- state age / CFTC vintage age
- four-state competing-risk classifier on existing T-1 features
- upcoming Tier-1 event flag
- RTE path geometry / flow reuse

The remaining mechanistic hypothesis is an **information-clock deficiency**.

The current CIG/HAG decision state is effectively based on information available through the prior daily cutoff. The operational use case is a morning daily forecast. Between the prior cutoff and the morning issuance, new XAU path information exists but is absent from the current D1 timing gate.

## 8. Next preregistered challenger

Proposed identity: **MORNING_CONCORDANCE_D1_V1**

Purpose:
- NOT a new general direction model.
- Act only when CIG is UNCERTAIN specifically because OPAL/V5 conflicts with AURORA-side lineage.
- Estimate whether the OPAL reversal has begun to realize by the morning issuance clock.
- Otherwise preserve UNCERTAIN.

Required raw source:
- read-only `public.xau_intraday_research_cache_5m`
- XAU/USD 5-minute research cache
- coverage through 2026-08-31

Primary information family:
- return from prior D1 cutoff to morning cutoff
- overnight / Asia path efficiency
- realized 5m volatility
- up/down 5m fraction
- maximum adverse/favorable excursion versus OPAL direction
- distance from overnight high/low
- last 30m / 60m / 120m momentum
- first-passage / recross count around prior cutoff price
- path acceleration/deceleration
- interaction with OPAL p(reversal) and AURORA disagreement

Governance:
- primary morning clock must be frozen before reading August outcomes for this model;
- development <=2023;
- 2024 family/threshold confirmation;
- 2025 transport;
- 2026/August only retrospective stress because 2026 has already been inspected;
- action layer remains selective; abstention is allowed and preferred to forced low-quality coverage;
- no change to binding CIG until transport evidence passes.

## 9. Current binding decision

**CIG UNCERTAIN remains binding.**

August coverage collapse is not yet safely repairable from the existing T-1 feature set.

The next scientifically justified experiment is a true morning-nowcast timing gate using the 5-minute XAU cache.
