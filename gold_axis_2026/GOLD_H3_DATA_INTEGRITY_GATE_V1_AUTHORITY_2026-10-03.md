# GOLD H3 DATA INTEGRITY GATE V1 — AUTHORITY

**Date:** 2026-10-03  
**Identity:** `GOLD_H3_DATA_INTEGRITY_GATE_V1`  
**Status:** FROZEN DATA-QUALITY POLICY

## Purpose

Prevent an upstream bad daily price row from silently entering H3 feature generation, target settlement or prospective forecast issuance.

This is a data-quality control, not a forecasting model and not a trading rule.

## Inputs

Candidate retained daily row:
- Gold
- Silver
- Platinum
- Palladium

Context:
- previous **accepted** retained daily row
- independent XAU reference for the candidate date.

## Trigger

A row requires independent confirmation when any of the following is true:
- at least 2 of 4 metals move by >=25% in absolute log-return from the previous accepted retained row;
- any one metal moves by >=35%;
- optional robust historical discontinuity score reaches |z|>=12.

A trigger is not itself a declaration of bad data.

## Cross-source decision

For a triggered row:
- independent XAU unavailable -> **QUARANTINE**
- XAU level divergence >=5% -> **QUARANTINE**
- XAU divergence <=3% -> **PASS_SEVERE_XAU_CONFIRMED**
- 3% < divergence < 5% -> **QUARANTINE_AMBIGUOUS**

Rows without a severe trigger -> **PASS_NORMAL**.

## Fail-closed behavior

A quarantined row:
- is not appended to the admitted prospective daily-price ledger;
- cannot create CORE3 features;
- cannot issue a forecast;
- cannot settle an outstanding H3 target;
- remains visible in a separate integrity audit ledger with source ref, values and reason.

No quarantined row may be backfilled after its forecast deadline merely because its true outcome has become known.

## Governance

Thresholds are frozen before forward use.
Changing them requires a new integrity-gate version.
The gate must never mutate historical frozen evidence in place.
The pre-existing AURORA prospective ledger remains immutable; this gate protects new prospective data ingestion only.

Historical replay is validation of the gate, not model tuning.
