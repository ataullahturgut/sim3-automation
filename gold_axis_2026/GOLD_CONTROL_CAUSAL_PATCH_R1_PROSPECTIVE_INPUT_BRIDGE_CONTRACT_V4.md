# GOLD CONTROL — CAUSAL PATCH R1 PROSPECTIVE INPUT BRIDGE CONTRACT V4

**Date frozen:** 2026-09-02  
**Status:** `FROZEN_BEFORE_V4_SOURCE_RESULT`  
**Change control:** `GOLD_CONTROL_CAUSAL_PATCH_R1_INPUT_SOURCE_CHANGE_CONTROL_V4_2026-09-02.md`  
**Parent manifest:** v1.17  
**Architecture:** Patch Transformer family unchanged  
**Geometry:** `L=252`, `P=21`, `D=32` unchanged  
**Daily channel set:** `[XAU]` only; Silver/Platinum/Palladium `OMITTED_NOT_IMPUTED`

## 1. Source semantics

Daily XAU:

- provider Twelve Data;
- symbol `XAU/USD`;
- interval `1day`;
- lineage `PATCH_XAU_TWELVE_DAILY_FULL_HISTORY_V4`;
- no claim that this is LBMA fixing, NY17, London-time close, or official exchange settlement.

NASDAQ:

- inherit V3 source PASS;
- feature `NASDAQCOM_COMPLETED_MONTH_RETURN_MARKET_CLOSE_V3`;
- availability policy `MARKET_CLOSE_AVAILABILITY_RECONSTRUCTION_NEXT_DAY_V1`.

DFF/FEDFUNDS and DEXCHUS/USDCNY:

- inherit V1 immutable source PASS.

GPR:

- existing conservative lag rule unchanged.

## 2. XAU source-readiness gate

Fetch Twelve `XAU/USD`, `1day`, `2010-01-01→2026-08-31`, ascending, max 5,000 rows.

PASS requires:

- metadata symbol is `XAU/USD` and interval `1day`;
- no duplicate dates;
- all closes finite and positive;
- at least `253` daily closes through `2011-02-28`;
- at least `3500` total daily closes;
- last close date `>=2026-08-28`;
- no forward-fill/interpolation;
- no raw market values in logs.

## 3. Inherited-source gate

PASS also requires:

- immutable V3 evidence file exists and `nasdaq_source_identity_availability.pass=true`;
- immutable V1 evidence file exists and both `fedfunds.pass=true`, `usdcny.pass=true`.

## 4. Decision

All source gates PASS:

`PATCH_PROSPECTIVE_INPUT_BRIDGE_V4_SOURCE_PASS`

Otherwise:

`BLOCKED_PATCH_PROSPECTIVE_INPUT_V4_SOURCE_NOT_PROVEN`

No source audit writes Neon, forecast ledger, or Decision Store.

## 5. Model-impact contract after source PASS

Reserved identity:

`CAUSAL_PATCH_R1_REPRO_V1_3_XAU_ONLY_ORIGIN_SAFE`

Locked score window:

`2023-01→2026-07`, `N=43`.

Frozen gates:

- target reconciliation 43/43;
- RW reconciliation 43/43;
- deterministic replay equality;
- no future information;
- no geometry selection/retune;
- MAPE `< RW MAPE`;
- MAE `< RW MAE`;
- worst APE `<=1.25 × RW worst APE`.

No result-dependent threshold, channel, source, or geometry change is allowed.
