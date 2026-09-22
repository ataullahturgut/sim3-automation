# GOLD CONTROL — SINGLE-POLICY LTT V2 WITH EXTERNAL PRE-2022 EXTENSION PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `SINGLE_POLICY_LTT_V2_EXTERNAL_EXTENSION_RESEARCH`  
**Frozen suppression policy:** hard frozen Router-V2 UP countersign: suppress SQRT forced-DOWN iff Router V2 emits UP.  
**Risk target:** alarm-conditional BAD_SUPPRESSION.  
**Runtime authority:** NONE.

## 1. Why this is a single-policy test

No policy family is selected here.

The tested policy was frozen before the external historical extension:

> On an SQRT alarm, if frozen Router V2 emits UP, suppress the forced-DOWN interpretation; otherwise retain it.

No F30/D30 threshold, WATCH rule, model coefficient or post-hoc candidate is eligible.

Therefore no multiplicity correction is required for this single fixed policy.

## 2. Calibration population

If the external-source harmonization gate passes, pool only pre-2025 calibration alarm cases from:

- 2020 external-source extension
- 2021 external-source extension
- 2022 governed source
- 2023 governed source
- 2024 governed source

Each year must use its own origin-safe annual SQRT formation and Router Y-1 competence formation.

External 2020/2021 cases remain tagged `EXTERNAL_SOURCE_EXTENSION`.

## 3. Exact safety hypothesis

Among calibration cases satisfying:

- SQRT alarm = 1
- actual next-day direction = DOWN

let:
- n = total actual-DOWN SQRT alarms;
- x = cases also suppressed by frozen Router-V2 UP.

Target:
- alpha = 0.20
- delta = 0.10

Exact one-sided test:

`H0: BAD_SUPPRESSION_RATE >= 0.20`

Use the exact lower-tail binomial p-value:

`p = P[Binomial(n, 0.20) <= x]`.

The frozen hard policy is risk-certified only if `p <= 0.10`.

## 4. Secondary effectiveness metrics

Report descriptively:
- total SQRT alarms;
- actual DOWN / actual UP;
- total suppressions;
- good suppressions;
- bad suppressions;
- suppression precision;
- false-alarm reduction;
- true-DOWN retention;
- remaining forced-DOWN precision.

Certification is determined only by the exact safety test, not by these secondary metrics.

## 5. Integrity requirements

External 2020/2021 may enter only if:
- the harmonization gate passes;
- reconstruction is chronological/origin-safe;
- no 2025 data are used;
- source tags remain explicit.

## 6. Forbidden actions

Do not:
- change the hard Router policy;
- remove weak historical years;
- tune alpha or delta;
- select among multiple policies after seeing external outcomes;
- pool external years if harmonization fails;
- use 2025 to certify pre-2025 risk.

## 7. Governance

- no random split;
- no production writes;
- no runtime promotion.
