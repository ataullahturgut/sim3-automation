# OCS-H3 V1 — ORTHOGONAL CONCURRENCE STACK

**Date:** 2026-10-04  
**Identity:** `OCS_H3_V1`  
**Branch:** `gold-h3-ocs-v1-20261004`  
**Evidence class:** retrospective development; first clean evidence must be prospective.

## 1. Rationale

Two distinct new information channels have been tested:

1. **IFBC** — internal Gold/Silver hourly volume-flow breakdown.
2. **LLRS** — external Treasury/Nasdaq/Silver/Oil hourly lead-lag repricing stress.

Each channel alone had insufficient precision, but their error mechanisms are physically different.

OCS tests a strict conjunction:

> V5 may be flipped only when internal futures microstructure and external cross-asset lead-lag both independently indicate reversal.

This is not score averaging and does not add a fitted router.

## 2. Frozen IFBC condition

IFBC candidate requires:
- `ifbc_count60 >= 4`
- `ifbc_score >= q_ifbc`

Frozen IFBC grid:
`q_ifbc ∈ [0.70, 0.75, 0.80]`

## 3. Frozen LLRS condition

LLRS concurrence requires:
- `llrs_external_opposes = True`
- `llrs_incremental > 0`
- `llrs_pressure >= q_llrs`

Frozen LLRS grid:
`q_llrs ∈ [0.00, 0.10, 0.25]`

## 4. OCS action

Candidate:
`IFBC_condition AND LLRS_condition`

Action:
- flip V5.

No other feature or model is used.

## 5. Development universe

Historical 2026 has already been spent and is development only.

Blocks:
- 2025 H2
- 2026 H1
- 2026 H2 through available September history.

## 6. Development gate

There are exactly 9 configurations.

A configuration is eligible if:
- total candidates >= 8
- aggregate net rescue > 0
- precision >= 0.60
- at least 2 of 3 blocks have net rescue > 0
- no block net < -1.

Selection:
1. maximum net rescue
2. higher precision
3. more rescued
4. fewer candidates
5. higher IFBC threshold
6. higher LLRS threshold.

No eligible configuration => `NO_ELIGIBLE_OCS_V1_MECHANISM`.

## 7. Prospective status

Historical results are development only.

If OCS passes:
- freeze selected thresholds before post-freeze use;
- run as shadow challenger;
- production use requires authoritative hourly sources.

Promotion evidence requires:
- 20 prospective accepted candidates;
- 6 months;
- cumulative net rescue >0;
- precision >=0.60.

## 8. Governance

- No new features may be introduced after this preregistration.
- No historical 2026 result is a clean holdout claim.
- HELIOS V5-DCE remains binding.
