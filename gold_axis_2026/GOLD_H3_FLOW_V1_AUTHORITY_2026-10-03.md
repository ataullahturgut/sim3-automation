# FLOW-H3 V1 — AUTHORITY, DATA-READINESS & PREREGISTRATION

**Date:** 2026-10-03  
**Identity:** `FLOW_H3_V1_RESEARCH`  
**Branch:** `gold-h3-flow-v1-20261003`  
**Parent:** `gold-midas-headswap-v1-20260925`  
**Status:** **PREREGISTERED / DATA ACCESS GATE OPEN**

## 1. Scientific purpose

FLOW-H3 is a new **reversal-candidate specialist** for the clean H3 XAU/USD project.

It is **not** a generic UP/DOWN forecaster and it does **not** replace HELIOS V5-DCE.

Primary question:

> Can origin-safe COMEX Gold futures daily Volume + Open Interest identify momentum reversals that OPAL does not nominate?

The target is the existing project reversal target:

`reversal_target = 1[y_up != momentum_up]`

where `momentum_up = 1[h_ret_12 >= 0]`.

The specialist is operationally relevant only when:

`aurora_follows_momentum = (aurora_pred == momentum_up)`.

## 2. Frozen baseline and holdout policy

Frozen comparator:
- `HELIOS V5-DCE` remains untouched.
- Clean 2026 V5 result remains the retrospective binding baseline.
- FLOW-H3 is challenger-only.

Period roles:
- formation/background: data before 2023 may be used in expanding training and rolling normalization;
- **DEV / threshold selection:** 2023-01-01 through 2024-12-31 only;
- **confirmation:** 2025 only;
- **final retrospective holdout:** 2026 only.

Binding prohibition:
- no 2026 outcome, rescue/broken status, or missed-reversal identity may be used to select feature definitions, model hyperparameters, threshold, window, or data clock.
- the known 55 V5-missed / OPAL-no-candidate 2026 reversals are evaluation targets only after the DEV rule is frozen.

## 3. Official source identity

Primary source:
- CME Group / COMEX Gold Futures
- exchange code: `XCEC`
- product code: `GC`
- DataMine EOD dataset code: `EOD_XCEC_GC_FUT_0`
- instrument class: FUT

Required information:
- daily Gold futures volume
- daily Gold futures open interest
- trade date / contract identity
- final/preliminary file identity
- source publication / availability timestamp when obtainable

No silent provider substitution is allowed.

Yahoo, Stooq, Barchart, Nasdaq mirrors, broker feeds, or synthetic GC proxies may not be inserted under this source identity.

## 4. Origin-safe publication clock

Canonical H3 live origin is the project 17:00 America/New_York reference.

CME states:
- daily VOI released at end of trading day is preliminary and may differ from final;
- official data are released in the Daily Bulletin the following morning;
- current Daily Bulletin timing is approximately 12:00 a.m. CT preliminary and 10:00 a.m. CT final on the next business day.

Therefore FLOW-H3 V1 uses **FINAL ONLY**.

For every H3 origin at time `origin_ts`:

`eligible GC row = latest FINAL trade-date record with available_as_of <= origin_ts`

Consequences:
- same-trade-date GC VOI is never used at the 17:00 ET origin;
- the normal information set is at least the prior eligible COMEX trade date;
- weekends/holidays are resolved by the CME exchange calendar, not by naïve calendar-day subtraction;
- preliminary/early files are excluded from V1.

This clock is a data-governance choice, not a forecast hyperparameter.

## 5. Normalized FLOW input contract

The CME adapter must emit one normalized daily product-state row per COMEX trade date:

- `trade_date`
- `available_as_of`
- `source_dataset_code`
- `source_file_id`
- `source_file_class` = FINAL
- `gc_volume_total`
- `gc_open_interest_total`
- `contract_count`
- optional `front_contract`
- optional `front_volume`
- optional `front_open_interest`

Required audit fields:
- retrieval timestamp
- payload/file hash
- parser version
- duplicate/revision status
- quality status

If aggregate product totals are not directly supplied, aggregation must be deterministic from the official GC futures contract rows and documented before model fitting.

## 6. Frozen V1 feature family

No feature is selected using 2026 results.

Core FLOW features:
1. `dlog_volume_1`
2. `dlog_oi_1`
3. `volume_z20`
4. `oi_z20`
5. `volume_oi_ratio`
6. `d_volume_oi_ratio_1`
7. `oi_accel_5`
8. `volume_accel_5`
9. `momentum_x_dlog_oi`
10. `momentum_x_volume_z20`

Optional front-contract features may be activated only if the actual official file supports a stable, auditable front-contract mapping **before any outcome-based model comparison**. If not, they stay disabled for V1.

Rolling statistics use only observations available by that origin.

## 7. Frozen model family

Model:
- StandardScaler
- LogisticRegression
- `C=1.0`
- `solver=lbfgs`
- `class_weight=balanced`
- deterministic seed `20261003`

Training:
- monthly expanding-origin refit;
- training rows must have `target_end_date_h3 <= current feature cutoff`;
- minimum matured training rows = 80;
- random split forbidden.

Output:
- `p_flow_reversal`
- `flow_candidate`

FLOW-H3 does not directly overwrite V5 in this stage.

## 8. Candidate-threshold selection — preregistered

Candidate threshold grid is frozen before GC history is inspected against outcomes:

`[0.35, 0.40, 0.45, 0.50, 0.55]`.

Threshold selection uses **2023-2024 only** and only eligible `aurora_follows_momentum` origins.

Objective:
- maximize reversal `F2` (recall-weighted);
- subject to candidate precision >= 0.45;
- subject to candidate rate <= 0.35 of eligible origins.

Tie-breaks, in order:
1. higher reversal recall;
2. higher precision;
3. lower candidate rate;
4. higher threshold.

If no threshold is eligible, status = `NO_ELIGIBLE_FLOW_THRESHOLD`; 2025/2026 may not rescue the selection.

## 9. Confirmation and final evaluation

### 2025 confirmation
Report:
- reversal recall;
- candidate precision;
- candidate rate;
- FLOW-only recall among true reversals for which OPAL candidate is false;
- overlap with OPAL;
- diagnostic direct-flip rescue/broken/net-rescue;
- Brier/logloss for reversal probability.

Confirmation is considered mechanistically useful only if:
- FLOW reversal recall > OPAL candidate recall on the same eligible 2025 universe;
- FLOW finds at least one true OPAL-missed reversal;
- FLOW precision >= 0.40.

This is a candidate-generation gate, not a production-routing promotion gate.

### 2026 final holdout
After threshold freeze and 2025 confirmation:
- score once, no retuning;
- explicitly report how many of the known 55 OPAL-no-candidate missed reversals receive a FLOW candidate;
- report new true candidates, false candidates, overlap, complement recall, and candidate-union recall;
- separately calculate the theoretical and realized V5 rescue opportunity, but do not promote a router from this stage.

## 10. Data-readiness gate — 2026-10-03 live audit

Production Neon inventory was checked:
- no existing GC daily volume/open-interest research series is registered;
- therefore FLOW is genuinely a new information channel rather than an algorithmic re-use of existing H3 inputs.

Repository search was checked:
- no existing DataMine credential/workflow integration was found.

CME official DataMine List API:
- requires authentication;
- lists only entitled files;
- identifies Gold futures EOD as `EOD_XCEC_GC_FUT_0`.

Current readiness:
- source identity: **PASS**
- PIT/publication clock authority: **PASS**
- normalized schema authority: **PASS**
- production Neon duplicate-source check: **PASS / ABSENT**
- historical file entitlement: **NOT YET VERIFIED**
- historical GC VOI payload loaded: **NO**
- model fitting allowed: **NO — fail closed until official history is available**

Required historical acquisition window for first run:
- preferred: 2021-01-01 through 2026-09-30;
- minimum for governed DEV/confirm/holdout: enough pre-2023 history to initialize rolling features plus complete 2023-2026 coverage.

## 11. Stage gate

FLOW-H3 may proceed to model fitting only after:
1. official CME GC FINAL EOD/VOI history is accessible;
2. file identity and final/prelim semantics are verified on actual payloads;
3. trade-date coverage and duplicate/revision audit pass;
4. `available_as_of` mapping passes origin-safe replay;
5. normalized FLOW panel is frozen and hashed.

Until then, do not move to SKEW-H3. This preserves the user-approved stage order.

## 12. Relationship to clean prospective H3

`CLEAN_H3_PROSPECTIVE_V1` remains unchanged.

FLOW-H3 V1 is a separate research challenger and does not alter:
- clean daily price history;
- Data Integrity Gate V1;
- AURORA;
- OPAL;
- HELIOS V1-V5;
- any existing prospective ledger.

Any eventual FLOW prospective use requires a new separately frozen challenger identity.
