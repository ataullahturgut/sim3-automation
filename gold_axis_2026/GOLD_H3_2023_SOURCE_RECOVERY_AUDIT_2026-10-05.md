# GOLD H3 — 2023 IFBC/LLRS Source Recovery Audit

**Date:** 2026-10-05  
**Status:** **EXACT 2023 DPTC SOURCE RECOVERY BLOCKED**  
**Purpose:** Recover the missing 2023 hourly state required to replay IFBC, LLRS, canonical Handoff and DPTC under the same historical model identity.

## Required hourly identities

The exact DPTC/Handoff reconstruction requires hourly futures histories for:

- GC = COMEX Gold futures
- SI = COMEX Silver futures
- NQ = CME E-mini Nasdaq-100 futures
- ZN = CBOT 10-Year Treasury Note futures
- CL = NYMEX WTI Crude Oil futures

The frozen LLRS equation requires all five channels. IFBC additionally requires GC/SI hourly volume under the original VAST construction.

## Sources checked

### 1. Yahoo Finance hourly continuous futures

Original model source identities:
`GC=F`, `SI=F`, `NQ=F`, `ZN=F`, `CL=F`.

Result:
- same-source 2025 backfill succeeded;
- 2023/most-2024 requests fail because the current 1h endpoint enforces a **730-day historical depth limit**.

Decision:
**BLOCKED FOR 2023**, not replaced with daily or spot data.

Authority:
`GOLD_H3_HOURLY_HISTORY_DEPTH_PROBE_2026-10-05.md`.

### 2. Existing project Git history / old H3 hourly branches

Checked the historical hourly/backfill branches and current repository tree.

Result:
- historical XAU/TwelveData artifacts exist;
- no archived 2023 five-channel GC/SI/NQ/ZN/CL hourly futures panel was found;
- the archived original LLRS hourly panel begins in 2025 and was sufficient to validate the 2025 backfill, but not 2023.

Decision:
**NO EXACT 2023 ARCHIVE FOUND**.

### 3. Connected Twelve Data source

A symbol/entitlement/depth probe was run using the connected Twelve Data key.

Result:
- no usable set of the required five CME/COMEX/CBOT/NYMEX futures identities was exposed under the current entitlement;
- returned futures-like search candidates were unrelated instruments or plan-gated;
- therefore no 2023 bridge could be validated against the frozen 2025 Yahoo panel.

Authority:
`GOLD_H3_2023_TWELVE_FUTURES_BRIDGE_PROBE_2026-10-05.md`.

### 4. Public GitHub CME futures OHLCV archive

Repository inspected:
`axb0306/cme-futures-ohlc`.

It contains the relevant symbols, but the available 1h files begin too late:

- GC: 2025-03-21
- SI: 2025-03-21
- NQ: 2025-03-21
- ZN: 2026-02-22
- CL: 2025-06-01

Git history was inspected back to repository creation and earlier data-extension commits. No deleted or superseded 2023 1h versions of the required files were found.

Decision:
**NOT A 2023 SOURCE**.

## Viable licensed acquisition routes

Two technically appropriate routes remain:

1. **Databento CME Globex historical data** — supports CME Globex historical futures, continuous-contract symbology and hourly OHLCV aggregation for historical dates including 2023.
2. **CME DataMine** — official CME historical futures/options delivery under licensed access.

Neither source is currently authenticated/connected to this project, so no data from them is used in the evidence chain.

## Scientific rule

A 2023 DPTC replay may be opened only if a source can supply all mandatory hourly channels and passes a bridge test against the frozen 2025 source:

- return-direction agreement;
- timestamp/session alignment;
- rolling-return agreement;
- GC/SI volume-feature agreement where applicable;
- downstream LLRS/IFBC score stability under frozen equations.

Spot metals, ETFs, daily futures, synthetic intraday interpolation or unrelated proxies **must not** be relabeled as exact DPTC history.

## Current conclusion

2025 missing IFBC/LLRS history has been validly reconstructed and replayed.

2023 exact DPTC/Handoff history remains **data-access blocked**, not model-failed.

No 2023 DPTC performance number is reported until the mandatory futures source is recovered under an accepted bridge contract.
