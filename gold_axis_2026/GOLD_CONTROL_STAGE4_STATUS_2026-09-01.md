# GOLD CONTROL — STAGE 4 DETERMINISTIC R4.1 STATUS

**Status date:** 2026-09-01  
**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.9  
**Stage:** 4 — Deterministic R4.1 Decision Engine / Issuer  
**Current status:** `IN_PROGRESS_BLOCKED_FORECAST_AND_MONTHLY_CONTEXT`

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

## 5. Active readiness blockers — manifest v1.9

1. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`
2. `FORECAST_CONTRACT_NOT_ISSUED`
3. `PATCH_R1_CURRENT_ISSUER_NOT_PROVEN`
4. `VW_CURRENT_MONTHLY_REFERENCE_NOT_ISSUED` / `VW_EXECUTABLE_REPRODUCTION_BLOCKED_NOT_PROVEN`
5. `MONTHLY_DIRECTION_CONTEXT_NOT_ISSUED`
6. `CANONICAL_XAU_HISTORY_BACKFILL_NOT_YET_SUCCESS`

The latest single-day canonical production ingestion remains `SUCCESS` by run `33511805110`, job `99869043161`; the new history blocker is distinct from that daily-pipeline success and exists because R4.1 Fast/Slow/3M context require longer same-lineage history.

## 6. Required next work

1. complete PIT-safe NY17 history backfill and verify sufficient Fast/Slow/monthly-context coverage;
2. keep exact VW identity `BLOCKED_NOT_PROVEN` unless identity is actually recovered; do not promote rebuild scripts by name similarity;
3. resolve/freeze the current monthly VW reference and 3M direction issuance contracts;
4. resolve the current H=1 executable issuer without extending Patch constants beyond their proven horizon by assumption;
5. only then persist the first immutable forecast input snapshot + monthly forecast contract and verify in Neon;
6. build/schedule canonical R4.1 issuer only after all mandatory `EngineSnapshot` inputs exist; first forward Decision Store state = `PROSPECTIVE_SHADOW`.

`NOT_PROVEN_POSITION_MAPPING` remains unchanged.


## 7. Forecast/monthly-context audit evidence

- forecast schema/horizon audit: run `33512445624`, job `99871192709`, `SUCCESS`; DB read-only; forecast-state row counts all zero; `core5` ends July 2026 and retained Patch runner is August-horizon specific.
- VW canonical-history forensic: run `33513175499`, job `99873596626`, `SUCCESS`; exact original VW runner/source chain `NOT_FOUND` in reachable canonical history; existing rebuild scripts do not close identity provenance.
- NY17 May-Aug depth probe: run `33513634775`, job `99875100590`, `SUCCESS`; sampled exact bars available.
- first atomic Jul-Aug history backfill: run `33512957983`, job `99872871327`, `FAILURE` before persistence because provider/request errors remained; no partial write was authorized by the backfill code.

## 8. Prospective-origin cutoff

The canonical H=1 origin is the end of the previous completed calendar month. The forecast ledger remained empty after the 31-August-2026 origin had passed. Therefore:

`SEPTEMBER_2026_H1_PROSPECTIVE_ORIGIN_MISSED`

This is a temporal evidence boundary, not a data value to reconstruct. A September forecast created now may not be backdated or labelled as a 31-August prospective issuance. The first fully contract-compliant prospective H=1 target remains **October 2026**, origin end-September, subject to the current issuer/VW/input blockers being closed by then.

A September 3M direction or R4.1 initialization may be created only as an explicitly labelled late bootstrap/shadow context with its true calculation and data-availability timestamps. It does not close the H=1 forecast issuance blocker.

