# OLC-H3 V1 — OPTIONS / LEAD-LAG CONCURRENCE PREREGISTRATION

**Freeze date:** 2026-10-04
**Identity:** `OLC_H3_V1`
**Branch:** `gold-h3-olc-v1-20261004`
**Status:** FROZEN BEFORE OLC OUTCOMES

## 1. Mechanism

OLC tests a second rare exception channel independent from OCS's internal hourly flow.

An OLC exception requires simultaneous:
- options pressure against momentum and rising (OAR mechanism), and
- external cross-asset lead-lag opposition (LLRS mechanism).

## 2. Eligible universe

Only when `v5_pred == momentum_up`.

## 3. Frozen OAR condition

Reuse the previously frozen OAR q=0.60 rule:
- `p_rte >= 0.60`
- `p_inst >= 0.50`
- `signed_opt_pressure > 0`
- `signed_d_opt_pressure > 0`

No OAR threshold search.

## 4. Frozen LLRS condition

Reuse the existing OCS/LLRS exception condition:
- `llrs_external_opposes == True`
- `llrs_incremental > 0`
- `llrs_pressure >= 0.10`

## 5. OLC exception

`OLC = OAR_condition AND LLRS_condition`

If OLC true:
- FLIP V5.

Otherwise:
- KEEP V5.

## 6. Development replay

Use only dates where RTE/OAR and LLRS are both available under origin-time source semantics.

Report:
- candidates
- rescue / broken / net
- precision
- half-year stability
- overlap with frozen OCS
- OLC-only rescues not already captured by OCS
- OCS OR OLC union.

## 7. Development gate

OLC is promising only if all:
- candidates >= 6
- precision >= 0.60
- net rescue >= +3
- candidate rate <= 0.15
- every available half-year block net >= -1
- at least 2 blocks net > 0
- at least 2 true OLC-only rescues outside OCS
- source identity / chronology failures = 0

No outcome-dependent retuning is allowed.
