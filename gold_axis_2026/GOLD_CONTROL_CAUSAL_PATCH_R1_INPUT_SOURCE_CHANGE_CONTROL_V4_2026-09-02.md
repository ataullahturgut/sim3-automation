# GOLD CONTROL — CAUSAL PATCH R1 INPUT SOURCE CHANGE CONTROL V4

**Date:** 2026-09-02  
**Status:** `FROZEN_BEFORE_V4_SOURCE_RESULT`  
**Parent manifest:** v1.17  
**Model family:** unchanged Patch Transformer  
**Frozen temporal geometry:** `L=252`, `P=21`, `D=32`  
**Locked model-impact window:** `2023-01→2026-07`, `N=43`

## 1. Why V4 exists

V1, V2 and V3 established that the historical four-metal Patch input cannot currently be continued prospectively under the available source entitlements without relabelling or inventing data.

Proven facts before this V4 freeze:

- V1/V2 DFF/FEDFUNDS and DEXCHUS/USDCNY source semantics passed;
- V3 `NASDAQCOM_COMPLETED_MONTH_RETURN_MARKET_CLOSE_V3` passed: 199 monthly comparisons, 0 missing, all 86 locked completed-month inputs availability-safe, median/p95 level gaps far inside the frozen 0.30%/1.00% materiality gates;
- Twelve Data current entitlement returns valid `XAU/USD` `1day` data;
- the same current entitlement explicitly returns provider code 404 for `XAG/USD`, `XPT/USD`, and `XPD/USD` with the message that those symbols require Grow or Venture plan access;
- anonymous Nasdaq Data Link `CHRIS/CME_GC1`, `CME_SI1`, `CME_PL1`, `CME_PA1` probes all return HTTP 403;
- direct operational LBMA benchmark use remains `BLOCKED_LICENSE_NOT_PROVEN`;
- StakTrakr daily metal history does not establish forward continuation after 2026-08-19.

Therefore V4 does not fill inaccessible channels with proxies and does not change to a broad model-search lane.

## 2. V4 input correction

V4 retains the Patch Transformer family and its frozen temporal geometry, but changes the daily metal channel set from four channels to one:

`[Gold, Silver, Platinum, Palladium] → [Gold]`

Gold lineage:

`PATCH_XAU_TWELVE_DAILY_FULL_HISTORY_V4`

Source:

- Twelve Data `XAU/USD`;
- interval `1day`;
- no timezone/fixing/NY17/LBMA claim;
- daily closes are treated only as the model's daily XAU return feature.

The removed Silver/Platinum/Palladium channels are explicitly `OMITTED_NOT_IMPUTED`.

No zero-fill, stale carry-forward, synthetic proxy, futures substitution, or provider mixing is permitted.

This changes the input channel count but does **not** change:

- target;
- horizon;
- Patch Transformer architecture class;
- `L=252`, `P=21`, `D=32`;
- loss/optimizer/training procedure;
- locked replay window;
- RW benchmark;
- acceptance gates.

Reserved executable identity after source and model-impact PASS:

`CAUSAL_PATCH_R1_REPRO_V1_3_XAU_ONLY_ORIGIN_SAFE`

## 3. Macro/input semantics inherited

V4 uses:

- DFF/FEDFUNDS: V1-proven source semantic, unchanged;
- DEXCHUS/USDCNY: V1-proven source semantic, unchanged;
- NASDAQ: V3 completed-month return semantic `NASDAQCOM_COMPLETED_MONTH_RETURN_MARKET_CLOSE_V3`;
- GPR: existing conservative lag rule unchanged.

## 4. V4 source gate before score

Before any V4 model score:

1. Twelve `XAU/USD` `1day` full-history retrieval must succeed;
2. no duplicate/non-positive/non-finite daily closes;
3. at least 253 closes must exist through 2011-02-28, sufficient for the frozen `L=252` return lookback before the original first sample boundary;
4. at least 3,500 XAU daily closes must exist in the governed 2010-01-01→2026-08-31 history;
5. latest available XAU close must be at least 2026-08-28;
6. V3 NASDAQ source PASS must be inherited immutably;
7. V1 FEDFUNDS and USDCNY PASS must be inherited immutably;
8. no raw market values logged;
9. no Neon, forecast-ledger, or Decision Store write.

Source PASS:

`PATCH_PROSPECTIVE_INPUT_BRIDGE_V4_SOURCE_PASS`

Failure:

`BLOCKED_PATCH_PROSPECTIVE_INPUT_V4_SOURCE_NOT_PROVEN`

## 5. Model-impact gate after source PASS

Only after source PASS, run the locked 43-month replay twice with:

- single XAU daily-return channel from Twelve full history;
- V3 completed-month NASDAQ return;
- existing DFF/DEXCHUS/GPR treatment;
- same `L=252`, `P=21`, `D=32`;
- no geometry selection or retuning.

Frozen gates, unchanged from V2/V3:

- target reconciliation `43/43`;
- RW reconciliation `43/43`;
- deterministic rerun equality;
- no future information;
- no geometry retune;
- MAPE `< RW MAPE`;
- MAE `< RW MAE`;
- worst APE `<= 1.25 × RW worst APE`.

The 43 locked outcomes may not be used to tune channel selection, geometry, source rule, or threshold after the result.

## 6. Downstream dependency

Even a V4 model-impact PASS is `HISTORICAL_REPLAY`, not a live forecast.

Then, without reopening broad model search:

1. freeze executable/input identity;
2. validate generic monthly-reference → Emergency geometry;
3. persist immutable forecast input snapshot + forecast contract before an eligible future origin;
4. first forward evidence is `PROSPECTIVE_SHADOW`;
5. September 2026 remains non-backfillable.
