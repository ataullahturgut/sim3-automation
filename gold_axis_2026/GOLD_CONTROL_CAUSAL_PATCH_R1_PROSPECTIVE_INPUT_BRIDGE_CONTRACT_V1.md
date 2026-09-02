# GOLD CONTROL — CAUSAL PATCH R1 PROSPECTIVE INPUT BRIDGE CONTRACT V1

**Date frozen:** 2026-09-02  
**Status:** `FROZEN_BEFORE_BRIDGE_AUDIT`  
**Applies to:** `CAUSAL_PATCH_R1_REPRO_V1`  
**Evidence class:** source/input compatibility audit only; no prospective forecast claim

## 1. Purpose

The 43-month historical replay proved the new Patch executable is deterministic and historically eligible. It did not yet prove that every input can be constructed at a real month-end origin with an operational source that preserves the historical feature semantics.

This contract freezes that continuation test before any bridge result is inspected.

No forecast-ledger row, Decision Store row, September backfill, threshold tuning, model-family substitution, auto-selector or ensemble is authorized by this contract.

## 2. Historical Patch feature semantics that must be preserved

The locked Patch implementation uses:

- daily Gold, Silver, Platinum and Palladium log returns; 252-observation lookback; causal 21-observation decomposition;
- `fedfunds[p]`;
- `log(nasdaq[p] / nasdaq[p-1])`;
- `log(usdcny[p] / usdcny[p-1])`;
- GPR period `p-1` (equivalent to target `t-2`) plus its expanding-origin normalization;
- target-month forecast issued from the end of month `p`.

Historical daily metals remain pinned to:

`lbruton/StakTrakr@ed2e549f82ba0d1cd3ca32842b82d3888d301e01`

That historical artifact is not extended or relabelled.

## 3. Macro prospective construction — frozen candidate

At each month-end origin, construct the current-month macro feature from values that ALFRED says were available by that month-end date:

- `FEDFUNDS_ORIGIN_MEAN_V1`: arithmetic mean of valid `DFF` observations in month `p` visible in the ALFRED realtime snapshot dated the calendar month-end;
- `NASDAQCOM_ORIGIN_MEAN_V1`: arithmetic mean of valid `NASDAQCOM` observations in month `p` visible in that ALFRED realtime snapshot;
- `DEXCHUS_ORIGIN_MEAN_V1`: arithmetic mean of valid `DEXCHUS` observations in month `p` visible in that ALFRED realtime snapshot;
- `GPR_LAG2_V1`: unchanged conservative GPR rule; use period `p-1`, never current-month GPR.

The ALFRED snapshot date is authoritative for the replayed information set. Retrieval time is never backdated.

### Macro bridge gates — frozen before audit

Audit origins: target `2023-01` through `2026-07` (`N=43`).

Hard gates for each of the three reconstructed monthly series:

- usable reconstruction count = `43/43`;
- no future observation date beyond the origin month-end;
- no API/retrieval failure silently filled;
- no forward fill.

Materiality gates versus the locked CORE5 monthly feature value:

- DFF→FEDFUNDS: median absolute relative gap `<= 0.50%`, p95 `<= 1.50%`;
- NASDAQCOM→NASDAQ_AVG: median absolute relative gap `<= 0.30%`, p95 `<= 1.00%`;
- DEXCHUS→USDCNY_AVG: median absolute relative gap `<= 0.20%`, p95 `<= 0.75%`.

These are governance materiality thresholds, not claims that the series are mathematically identical.

## 4. Daily precious-metals prospective construction — frozen candidate

Direct continued use of licensed LBMA benchmark history is not assumed. The first operational candidate is a separately named Twelve Data spot proxy sampled around the London benchmark-time convention:

| Historical feature | Operational candidate | Twelve symbol | Interval | Timezone | Selected hourly bar |
|---|---|---|---|---|---|
| Gold daily return | `XAU_TWELVE_LONDON15_PROXY_V1` | `XAU/USD` | `1h` | `Europe/London` | timestamp hour `15:00` close |
| Silver daily return | `XAG_TWELVE_LONDON12_PROXY_V1` | `XAG/USD` | `1h` | `Europe/London` | timestamp hour `12:00` close |
| Platinum daily return | `XPT_TWELVE_LONDON14_PROXY_V1` | `XPT/USD` | `1h` | `Europe/London` | timestamp hour `14:00` close |
| Palladium daily return | `XPD_TWELVE_LONDON14_PROXY_V1` | `XPD/USD` | `1h` | `Europe/London` | timestamp hour `14:00` close |

These are **spot proxies**, not LBMA benchmark prices. No Twelve value may be relabelled as an LBMA fix/benchmark.

Authority rationale frozen before result: LBMA publishes benchmark auction start conventions of 15:00 London for Gold PM, 12:00 for Silver, and 14:00 for Platinum/Palladium PM. Twelve Data supports precious-metal commodity pairs and `1h` historical intervals. The audit tests compatibility; it does not presume equivalence.

### Metal bridge gates — frozen before audit

Overlap audit window: `2026-01-01` through pinned-history end `2026-08-19`.

Per metal:

- common aligned daily observations `>= 120`;
- consecutive common return pairs `>= 100`;
- Pearson correlation of aligned log returns `>= 0.90`;
- return-direction sign agreement `>= 0.75`;
- median absolute log-return gap:
  - Gold/Silver `<= 75 bps`;
  - Platinum/Palladium `<= 100 bps`;
- p95 absolute log-return gap `<= 300 bps`.

All four metals must pass every gate. No averaging of pass/fail across metals is allowed.

## 5. Stitch rule if and only if the metal bridge passes

The frozen historical source remains authoritative through its last pinned date. The operational source starts only after that date.

Because the Patch input is a return series, the provider transition must not create a cross-provider level return:

- returns through the final historical date are computed only within the historical source;
- the first operational return is computed only after two consecutive operational-source observations exist;
- no return is calculated from an LBMA/StakTrakr level directly to a Twelve level;
- missing operational days remain missing; no forward fill.

## 6. Decision logic

`PATCH_PROSPECTIVE_INPUT_BRIDGE_V1_PASS` requires **both**:

1. all macro hard/materiality gates PASS; and
2. all four metal hard/materiality gates PASS.

If either block fails:

`BLOCKED_PATCH_PROSPECTIVE_INPUT_SEMANTICS_NOT_PROVEN`

A failure may be followed only by a versioned bridge contract addressing the failed semantic/source issue. It may not trigger a broad model search or post-score threshold relaxation.

## 7. After a bridge PASS

A PASS still does not authorize a live forecast. Required next gates remain:

1. run the frozen Patch model-impact replay with the approved operational input construction;
2. freeze the resulting executable/input identity if model-impact gates pass;
3. validate the generic monthly-reference → Emergency geometry bridge without silently inserting Patch into the historical R4.1 `monthly_vw_forecast` identity;
4. persist immutable forecast input snapshot + forecast contract before the first eligible real month-end origin;
5. first forward evidence class is `PROSPECTIVE_SHADOW`.

The September 2026 H=1 origin remains missed and may never be reconstructed as prospective evidence.
