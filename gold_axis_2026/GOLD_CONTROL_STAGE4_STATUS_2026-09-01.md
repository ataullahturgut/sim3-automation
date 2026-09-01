# GOLD CONTROL — STAGE 4 DETERMINISTIC R4.1 STATUS

**Status date:** 2026-09-01  
**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.6  
**Stage:** 4 — Deterministic R4.1 Decision Engine / Issuer  
**Current status:** `IN_PROGRESS_BLOCKED_INPUT_CONTRACTS`

## 1. Verified engine/store state

- Frozen R4.1 engine is deterministic under the audited contract.
- Decision Store schema/read path is present and guarded.
- `action_state` remains null under `NOT_PROVEN_POSITION_MAPPING`.
- `LIVE_PRODUCTION` remains disabled.
- No prospective decision row has been fabricated/backfilled.

## 2. Canonical XAU EOD contract — manifest v1.6

Active canonical series:

`XAU_EOD_TWELVE_NY17`

Contract:

- session-definition authority: CME Group / EBS Market;
- trade-date boundary: 17:00 ET, `America/New_York`;
- actual price provider: Twelve Data;
- provider symbol: `XAU/USD`;
- interval: `1min`;
- exact selected bar: `16:59:00` ET;
- decision reference: that bar's `close`;
- provider lineage remains Twelve Data;
- no fallback/forward-fill/provider relabelling.

This is an internal EOD decision reference, not an official market settlement or fixing.

## 3. Access/mapping proof

GitHub Actions run `33510985399`, job `99866288149`: `SUCCESS`.

The protected probe proved:

- Twelve XAU/USD 1-minute access;
- `America/New_York` timezone request;
- exact 16:59 bar availability on the audited date;
- valid OHLC fields;
- no raw market values logged;
- no database writes.

Status:

`TWELVE_XAU_NY17_EXECUTABLE_MAPPING_PROVEN`

## 4. Superseded CME/EBS feed path

`XAU_EOD_CME_EBS` is no longer the active operational source. CME/EBS remains the authority for the 17:00 ET session convention and an audit/history candidate. Direct EBS Ticker entitlement is therefore **not required** for the manifest v1.6 active path.

## 5. Active readiness blockers

1. `FORECAST_CONTRACT_NOT_ISSUED`
2. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`
3. `TWELVE_XAU_NY17_PIPELINE_NOT_SUCCESS`

The source-definition/access/mapping blocker is now closed. The remaining XAU task is implementation and a successful canonical Neon ingestion run.

## 6. Required next work

1. implement the canonical `XAU_EOD_TWELVE_NY17` writer with exact 16:59 ET mapping and quality gates;
2. create the explicit Twelve NY17 series/provider lineage in Neon and obtain a successful daily run;
3. issue the first genuine immutable H=1 forecast input snapshot and monthly forecast contract before outcome realization;
4. build/schedule the canonical R4.1 EOD issuer only after those inputs pass;
5. first forward Decision Store state = `PROSPECTIVE_SHADOW`, never retroactive and not `LIVE_PRODUCTION`.

`NOT_PROVEN_POSITION_MAPPING` remains unchanged.
