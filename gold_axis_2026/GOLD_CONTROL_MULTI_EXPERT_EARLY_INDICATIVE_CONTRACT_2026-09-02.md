# GOLD CONTROL — MULTI-EXPERT EARLY INDICATIVE CONTRACT

**Issue date:** 2026-09-02  
**Authority:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.22  
**Status:** `FROZEN_FAIL_CLOSED_EARLY_INDICATIVE_CONTRACT_V1`

## 1. Purpose

`EARLY_INDICATIVE` is a separate revision track for the Multi-Expert Monthly Forecast Engine. It may recompute an expert's next-month view when new point-in-time-safe information becomes available during the current month.

It is **not** the canonical end-of-month H=1 forecast, does not populate the official prospective scorecard, and cannot select or combine experts while `NOT_PROVEN_EXPERT_SELECTION_RULE` remains unresolved.

## 2. Binding separation

The two tracks are distinct objects:

- `MONTH_END_EXPERT` — expert output at the canonical end-of-previous-completed-month origin.
- `EARLY_INDICATIVE` — intramonth revision at an explicit `as_of` timestamp.

Rows from the two tracks must never be silently merged, relabelled, or used interchangeably.

Every Early Indicative row must contain its own:

- target month,
- forecast origin / as-of timestamp,
- expert identity,
- exact model/version,
- immutable input snapshot IDs,
- input fingerprint,
- evidence class,
- Git commit,
- source lineage and availability metadata.

## 3. Selector / ensemble lock

The following remain binding:

- `selector_status = NOT_PROVEN_EXPERT_SELECTION_RULE`
- `auto_selector = OFF`
- `auto_ensemble = OFF`
- `canonical_authority = false`

An Early Indicative row may never self-promote into `monthly_forecast_contracts` or the official canonical scorecard.

## 4. Expert readiness as of 2026-09-02

### Causal Patch

Status:

`BLOCKED_EARLY_INDICATIVE_PATCH_PIT_CONTRACT_NOT_FROZEN`

Reason: the currently proven Patch V7 forward issuer is frozen for the end-September origin and uses month-end-specific input semantics. Reusing those hard-coded September-complete / month-end features at an earlier intramonth `as_of` would not prove causal availability and is forbidden.

A separate Patch Early Indicative input contract must be frozen **before** any result is inspected. It must define, at minimum, completed-session daily feature cutoff, partial/current-month anchor semantics, macro vintage cutoffs, minimum history, missing-data behavior, target/origin semantics, and immutable snapshot binding.

### VW-MIDAS-MSVR

Status:

`BLOCKED_NOT_PROVEN_EXECUTABLE`

Reason: the exact archived executable runner remains unproven. Historical analytical evidence does not authorize a forward or Early Indicative issuer.

### 3M Momentum

Status:

`BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND`

Reason: the formula is reproducible, but no manifest-authorized point-in-time-safe forward monthly-level source has yet been bound to the expert. No source substitution is allowed by convenience.

### Random Walk

Status:

`BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND`

Reason: the benchmark formula is reproducible, but the forward monthly-level source contract has not yet been frozen and bound.

## 5. Current operational decision

As of this contract issue:

`EARLY_INDICATIVE_OVERALL_STATUS = BLOCKED_NO_EXECUTABLE_PIT_SAFE_EXPERT_TRACK`

The correct behavior is to evaluate readiness and write **no forecast row** until at least one expert has a track-specific, frozen, PIT-safe forward contract.

No placeholder forecast, partial-month proxy, backfilled current-month value, winner expert, selector weight, or ensemble value may be produced to make the track appear populated.

## 6. Unblocking rule

An expert may enter `EARLY_INDICATIVE` only after all of the following are true:

1. its executable identity is reproducible;
2. its `as_of` information set is defined before result inspection;
3. all inputs have point-in-time availability rules and source lineage;
4. input snapshots and fingerprinting are immutable;
5. missing-data behavior is fail-closed and does not silently substitute providers;
6. deterministic tests pass;
7. a versioned change-control record is committed;
8. the expert output remains separate from canonical month-end and selector/ensemble authority.

## 7. Prohibited inference

The existence of a valid Patch V7 month-end issuer does **not** prove that Patch V7 is valid at arbitrary intramonth `as_of` timestamps. Month-end eligibility cannot be generalized backwards by assumption.
