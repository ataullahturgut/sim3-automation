# Gold Control — BOCPD Return Successor V1 Engineering & Risk Evidence

**Date:** 2026-09-04  
**Status:** `FROZEN_RESEARCH_EVIDENCE_V1`  
**Successor identity:** `BOCPD_RETURN_SUCCESSOR_V1`  
**Archived identity:** `BOCPD` remains blocked  
**Evidence scope:** engineering reproducibility + historical risk diagnostic only  
**Prospective claim:** `NO`  
**Production promotion authorized:** `NO`

## 1. Authority chain

This evidence is governed by:

1. `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.30;
2. `GOLD_CONTROL_V130_UNRESOLVED_ENGINE_RECOVERY_AUDIT_2026-09-04.md`;
3. `GOLD_CONTROL_UNRESOLVED_ENGINE_SUCCESSOR_ROADMAP_2026-09-04.md`;
4. `GOLD_CONTROL_BOCPD_RETURN_SUCCESSOR_V1_CHANGE_CONTROL_2026-09-04.md`;
5. `GOLD_CONTROL_BOCPD_RETURN_SUCCESSOR_V1_RISK_VALIDATION_CONTRACT_2026-09-04.md`;
6. Adams & MacKay (2007), *Bayesian Online Changepoint Detection*, arXiv:0710.3742, as methodological authority for the successor BOCPD recursion.

The archived Gold Control BOCPD likelihood/prior/reset-score implementation is still not recovered. This evidence does not claim otherwise.

## 2. CI evidence

### Run 1 — engineering gate

- workflow: `Gold Control BOCPD Return Successor V1`
- run: `33872811566`
- exact head SHA: `ca89435f212b2a0016568481c99bc9e09cfee36e`
- conclusion: `SUCCESS`
- tests: `9 passed`
- artifact: `9936606484`
- artifact digest: `sha256:d824d674fb10e4ec05b44f137907b07cc60372728660929199dd83b86e4521dc`

### Run 2 — engineering + frozen risk diagnostic

- workflow: `Gold Control BOCPD Return Successor V1`
- run: `33873106128`
- exact head SHA: `993ad49abae525a58362dd7d51f551d965cf2156`
- conclusion: `SUCCESS`
- tests: `14 passed`
- engineering replay: `SUCCESS`
- frozen risk diagnostic: `SUCCESS`
- generated evidence audit: `PASS`
- artifact: `9936723648`
- artifact digest: `sha256:567246a228b3126acd37223b670ef82a875a53e7b3c36aef0950b582f42b2b8f`

No CI step had database-write permission; workflow `contents` permission was read-only.

## 3. Frozen engineering result

- replay span: `2010-01` through `2026-07`
- rows: `199`
- period counts:
  - DEV = `132`
  - VAL = `36`
  - LOCK = `31`
- expected run length: `36 months`
- hazard: `1/36 = 0.027777777777777776`
- numeric alarm threshold: `NONE`
- archived threshold reused: `NO`

Frozen development-only NIG prior:

- `mu0 = 0.0037338484049869755`
- `kappa0 = 1.0`
- `alpha0 = 2.0`
- `beta0 = 0.0011254083384199375`

Determinism SHA256:

`59195f0375b43a30f77829b10d33101cc737624a9626b5281f9c637ab046358a`

Engineering hard gates all passed:

- contract identity;
- no archived-threshold reuse;
- development-only prior;
- posterior normalization;
- deterministic replay;
- prefix invariance / future-data independence;
- completed-month-only rule;
- no validation tuning;
- no locked tuning;
- direction vote false;
- DB writes none;
- no position mapping.

Maximum engineering status:

`RESEARCH_SHADOW_CANDIDATE_ENGINEERING_PASS`

This is not runtime ACTIVE status.

## 4. Successor candidate events

Validation candidate months:

- 2021-07
- 2022-04
- 2022-06
- 2022-07
- 2022-09

Locked candidate months:

- 2024-12
- 2026-04

These differ from the archived BOCPD alarm path. That difference is expected because V1 is a new successor definition and is additional evidence that it must not inherit the archived BOCPD identity.

## 5. Frozen historical risk diagnostic

The diagnostic reused prior Gold Control risk-evaluation semantics rather than creating a new post-result performance threshold:

- primary risk horizon: `2–3 months`;
- tail definition: cumulative forward GOLD return `<= -3%`;
- 1M remains secondary only;
- no statistical threshold tuning;
- no exposure/action mapping;
- LOCK is diagnostic only.

### Validation 2021–2023

Candidate N = `5`; non-candidate N = `31`.

Candidate group:

- mean FWD 1M = `-2.1257%`
- mean FWD 2M = `-2.2579%`
- mean FWD 3M = `-3.5516%`
- median FWD 2M = `-3.0133%`
- median FWD 3M = `-3.9815%`
- 2M tail rate = `60.0%`
- 3M tail rate = `60.0%`

Non-candidate group:

- mean FWD 1M = `+0.6703%`
- mean FWD 2M = `+1.1198%`
- mean FWD 3M = `+2.1201%`
- median FWD 2M = `+0.7316%`
- median FWD 3M = `+2.0728%`
- 2M tail rate = `12.9032%`
- 3M tail rate = `19.3548%`

Candidate minus non-candidate:

- mean FWD 2M difference = `-3.3778 percentage points`
- mean FWD 3M difference = `-5.6716 percentage points`
- 2M tail-rate difference = `+47.0968 percentage points`
- 3M tail-rate difference = `+40.6452 percentage points`

Interpretation:

`DESCRIPTIVE_ONLY`

The result is directionally consistent with a downside-risk/severity context, but N=5 remains small and no new inferential/production threshold was pre-registered. Therefore this historical result cannot authorize an automatic action or production promotion.

### Locked 2024–2026-07

Candidate N = `2`.

Candidate group:

- mean FWD 2M = `-0.5575%`
- mean FWD 3M = `-0.5374%`
- 2M tail rate = `50.0%`
- 3M tail rate = `50.0%`

Non-candidate group with available outcomes:

- mean FWD 2M = `+5.7798%`
- mean FWD 3M = `+9.2567%`
- 2M tail rate = `11.1111%`
- 3M tail rate = `7.6923%`

Interpretation:

`DIAGNOSTIC_ONLY`

The locked sample is too small for approval and was prohibited from tuning or approving V1 by the pre-frozen contract.

## 6. Current project decision

### Proven now

`BOCPD_RETURN_SUCCESSOR_V1` has:

- a pre-frozen explicit identity and contract;
- a deterministic executable implementation;
- completed-month causal semantics;
- prefix/PIT invariance tests;
- no hidden threshold fitting;
- reproducible frozen historical replay;
- a separately frozen historical risk diagnostic;
- descriptive validation evidence in the intended risk/severity direction.

### Not proven now

The following remain `NOT_PROVEN`:

- genuine prospective performance;
- production runtime suitability;
- live-production graduation;
- automatic action value;
- position mapping;
- direction-vote value.

### Archived BOCPD remains

`BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED`

No successor artifact changes that historical fact.

## 7. Maximum current successor status

`RESEARCH_SHADOW_CANDIDATE_RISK_DIAGNOSTIC_COMPLETE_PROSPECTIVE_VALIDATION_REQUIRED`

The next legitimate evidence upgrade is a separately governed future month-close prospective shadow observation. No historical run may be relabelled as prospective.
