# FLOW-H3 V1 — DATA READINESS RESULT

**Date:** 2026-10-03  
**Branch:** `gold-h3-flow-v1-20261003`  
**Status:** **AUTHORITY PASS / HISTORICAL PAYLOAD BLOCKED**

## Executive result

The first FLOW-H3 stage was executed without touching HELIOS V5-DCE.

The source and clock question is resolved:

- official product: COMEX Gold Futures (`GC`)
- official EOD DataMine dataset: `EOD_XCEC_GC_FUT_0`
- FLOW V1 uses **FINAL** volume/open-interest only
- H3 origin is 17:00 America/New_York
- same-trade-date VOI is not origin-safe for this project
- use the latest FINAL GC row whose `available_as_of <= origin_ts`
- normally this means the previous eligible COMEX trade date

Reason: CME explicitly distinguishes preliminary daily VOI from official final data, and the current Daily Bulletin is finalized the next business day.

## Live production inventory audit

Production Neon:
- project: `winter-art-94880101`
- branch: `br-gentle-mouse-b22dzkr1`
- database: `neondb`

The source registry was searched for GC / COMEX / CME / volume / open-interest identities.

Result:
- no daily GC futures volume/open-interest research series is currently registered.

Interpretation:
- FLOW-H3 will add a genuinely new information channel if loaded correctly.

## Repository access audit

Repository:
- `ataullahturgut/sim3-automation`

Searches:
- DATAMINE
- EOD_XCEC_GC_FUT_0
- CME_API
- CMEGROUP
- api.datamine.cmegroup.com

Result:
- no existing CME DataMine download integration / credential reference was found.

## Historical access finding

CME's DataMine List API documentation states that:
- the API lists **entitled** files;
- authentication is required;
- Gold Futures example identity is exactly `XCEC / GC / EOD_XCEC_GC_FUT_0`.

CME's public VOI page provides current daily/preliminary reports and states that official figures arrive in the following-morning Daily Bulletin. CME directs historical daily data to DataMine.

Therefore the research pipeline must not silently replace official historical GC VOI with an unrelated public mirror merely to complete a backtest.

## Stage decision

### PASS
- source identity
- product identity
- final/preliminary distinction
- conservative PIT clock
- normalized schema authority
- target definition
- DEV / confirmation / holdout split
- model family
- threshold-selection protocol
- production duplicate-source audit

### BLOCKED
- official historical GC FINAL VOI payload has not yet been obtained
- DataMine entitlement for this account/environment has not been verified

### NOT EXECUTED BY DESIGN
- FLOW model fit
- threshold selection
- 2025 confirmation
- 2026 holdout
- 55-missed-reversal analysis

Those steps would be invalid without the official historical payload.

## Frozen next gate

Do **not** move to SKEW-H3.

The next admissible operation is:

1. obtain official CME GC FINAL daily volume/open-interest history;
2. normalize it under `FLOW_H3_V1`;
3. audit trade-date continuity, duplicates/revisions and publication clock;
4. freeze the normalized panel/hash;
5. execute the already-preregistered 2023-2024 threshold selection;
6. run 2025 confirmation;
7. only then open the 2026 holdout and measure coverage of the 55 OPAL-no-candidate reversals.

No rules may be changed using 2026 outcomes.
