# SAGE-H3 V2 — EXCEPTION-ONLY PROSPECTIVE FREEZE

**Freeze date:** 2026-10-04  
**Identity:** `SAGE_H3_V2_EXCEPTION_ONLY`  
**Branch:** `gold-h3-sage-v1-20261004`  
**First eligible clean origin:** **2026-10-05**  
**Status:** **FROZEN SHADOW CHALLENGER**

## 1. Binding baseline

Direction baseline:
**HELIOS V5-DCE**

SAGE V2 does not retrain, recalibrate or replace V5.

## 2. Frozen exception rule

An exception is eligible only if V5 follows the prevailing momentum direction.

### IFBC
- `ifbc_count60 >= 4`
- `ifbc_score >= 0.70`

### LLRS
- `llrs_external_opposes == True`
- `llrs_incremental > 0`
- `llrs_pressure >= 0.10`

### Action

If all conditions are true:
- **FLIP V5**

Otherwise:
- **KEEP V5**

No ABSTAIN rule is active in V2.

TRES is not permitted to alter direction in V2.

## 3. Source policy

The exception may run only when both IFBC and LLRS source states are available at the origin under their frozen source semantics.

If either source is absent, stale beyond its source contract, or fails its integrity gate:
- exception = FALSE
- action = KEEP V5
- record the source failure / missing status.

No later backfill may create a retrospective prospective exception.

## 4. Historical development evidence

This is **not clean validation**.

Mature development universe:
- 252 common rows
- 2025 H2 through 2026 Sep.

Exception events:
- 7
- rescue / broken / net = **6 / 1 / +5**
- precision = **85.71%**

Whole-year development diagnostics:

2025:
- V5 165/248 = **66.53%**
- exception-only 166/248 = **66.94%**

2026:
- V5 121/191 = **63.35%**
- exception-only 125/191 = **65.45%**

The 2026 result is retrospective development evidence because the exception thresholds were identified before this freeze using historical data including 2026.

## 5. Prospective ledger

For every post-freeze origin record:

- feature_cutoff_date
- forecast_issue_date
- V5 probability / direction
- momentum direction
- IFBC score
- IFBC count60
- LLRS pressure
- LLRS incremental
- LLRS external-opposes
- source freshness / integrity states
- exception TRUE/FALSE
- SAGE V2 direction
- TRES F_reversal / F_continuation / S3 as telemetry only
- target maturity date
- matured outcome
- rescue / broken classification

No matured outcome may alter V2.

## 6. Promotion gate

Production promotion is prohibited until both hold:

1. at least **20 prospective exception actions**;
2. at least **6 calendar months** of prospective operation.

At that point all must hold:

- cumulative net rescue > 0
- exception precision >= 0.60
- no unresolved data-integrity violation
- V5+exception full-direction accuracy >= V5 on the same prospective origins
- no single completed calendar quarter has net rescue < -2.

Until then:
**HELIOS V5-DCE remains binding.**

## 7. Fail-safe

If prospective cumulative exception net rescue reaches **-3** before the promotion gate:
- SAGE V2 exception enters shadow-suppressed state;
- continue recording proposed exceptions;
- do not alter V5 direction;
- any redesign requires a new version.

## 8. Governance

Frozen and prohibited from post-outcome adjustment:

- IFBC 0.70 threshold
- IFBC count60 minimum 4
- LLRS 0.10 pressure threshold
- LLRS incremental sign rule
- LLRS external-opposition rule
- exception precedence
- no-ABSTAIN design
- missing-source fail-closed behavior

Any change creates V3 and restarts prospective evidence.
