# GOLD CONTROL — STAGE 4 DETERMINISTIC R4.1 STATUS

**Status date:** 2026-09-01
**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.4
**Stage:** 4 — Deterministic R4.1 Decision Engine / Issuer
**Current status:** `IN_PROGRESS_BLOCKED_INPUT_CONTRACTS`

## 1. What is verified

- Frozen R4.1 engine tests are deterministic under the audited test contract.
- R4.1 descriptive emitted state can be mapped to Decision Store without recomputing signals.
- Persistence bridge refuses action/exposure fields and unreviewed emitted-state shape drift.
- Store-reader roundtrip, idempotency and rollback are verified.
- `LIVE_PRODUCTION` has an additional disabled-by-default write gate.
- A current app reader exists but there are no display-eligible decision rows.

## 2. Canonical live emitter audit

Status:

`NOT_FOUND_CANONICAL_LIVE_R4_1_EMITTER`

`replay_daily.py` is a sequential replay CLI, not a prospective scheduled issuer.

The older R4 workflow that emits LONG/CASH and AL/SAT cannot be promoted into R4.1 because the current contract is `NOT_PROVEN_POSITION_MAPPING`.

## 3. Source-authority change-control result

Authority research and frozen validation are recorded in:

`GOLD_CONTROL_XAU_EOD_SOURCE_CHANGE_CONTROL_2026-09-01.md`

Approved source/session authority:

- CME Group / EBS Market on CME Globex;
- XAU/USD SM (`GCUS`);
- spot XAU/USD semantic;
- `America/New_York` session timezone;
- 17:00 ET trade-date boundary;
- reserved series id `XAU_EOD_CME_EBS`.

Decision:

`CME_EBS_XAUUSD_1700_ET_AUTHORITY_AND_SESSION_APPROVED`

Closed blocker:

`NO_APPROVED_CANONICAL_XAU_EOD_DECISION_SOURCE` → `CLOSED_BY_MANIFEST_V1_4`

The authority approval does not authorize a guessed close field or vendor substitution.

## 4. Why alternatives were not promoted

- LBMA Gold Price PM is the global Loco London benchmark but is an auction benchmark at 15:00 London, not EOD.
- CME Group Spot Gold Reference Rate is an EBS-based 13:29–13:30 ET spot marker, not EOD.
- `XAU_DAILY_XAUS` remains operational cross-check / Yahoo-GC=F-like lineage, not spot-EOD authority.
- `XAU_SPOT_XAUS` remains indicative monitoring.
- Twelve provider-default daily XAU/USD uses Commodity Aggregate / `Australia/Sydney` exchange-local daily semantics and is not EBS 17:00 ET EOD.

No silent fallback is approved.

## 5. Frozen validation evidence

Run `33506001316`, job `99850068530`: `SUCCESS`.

Validation period only:

`2021–2023`

`2024+` used for selection:

`NO`

The pinned legacy validation series was LBMA-labelled for 754/754 Gold rows. Neither Twelve daily construction was identity-equivalent to it. Therefore the canonical EBS EOD source receives a new lineage rather than mutating legacy/XAUS/Twelve history.

## 6. Active readiness blockers

The original read-only readiness audit run `33499509482`, job `99829327414` executed successfully. After source-authority change control, active blockers are:

1. `FORECAST_CONTRACT_NOT_ISSUED`
2. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`
3. `CME_EBS_XAU_EOD_PIPELINE_NOT_SUCCESS`
   - `CME_EBS_DATA_ENTITLEMENT_NOT_PROVEN`
   - `CME_EBS_EOD_FIELD_MAPPING_NOT_PROVEN`

Decision Store and forecast-state tables remain unpopulated by this change-control action.

## 7. Required next work

1. prove/activate authorized CME/EBS XAU/USD SM data access;
2. inspect the entitled schema/product and freeze the exact 17:00 ET EOD value field/aggregation; if not provable, remain `BLOCKED`;
3. add explicit `XAU_EOD_CME_EBS` ingestion lineage and obtain a successful daily run;
4. issue the first genuine immutable H=1 forecast input snapshot and monthly forecast contract before outcome realization;
5. build/schedule the canonical R4.1 EOD issuer only after those prerequisites pass;
6. first forward Decision Store state must be `PROSPECTIVE_SHADOW`, never retroactive and not `LIVE_PRODUCTION`.

`NOT_PROVEN_POSITION_MAPPING` remains unchanged.
