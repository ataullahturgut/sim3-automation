# GOLD CONTROL — CAUSAL PATCH R1 INPUT SOURCE CHANGE CONTROL V3

**Date:** 2026-09-02  
**Status:** `FROZEN_BEFORE_V3_SOURCE_RESULT`  
**Parent manifest:** v1.17  
**Model family:** unchanged `CAUSAL_PATCH_R1_REPRO_V1`  
**Geometry:** unchanged `L=252`, `P=21`, `D=32`

## 1. Problem statement

Patch historical replay passed, but prospective input continuation did not.

V1 decision: `BLOCKED_PATCH_PROSPECTIVE_INPUT_SEMANTICS_NOT_PROVEN`.

V2 decision: `BLOCKED_PATCH_PROSPECTIVE_INPUT_V2_SOURCE_NOT_PROVEN`.

V2 evidence is immutable and is not reinterpreted as a pass:

- DFF and DEXCHUS remain proven for the frozen 43-month source audit;
- NASDAQCOM lagged construction still had 2 ALFRED month-end vintage gaps;
- Twelve `1day` Gold had adequate overlap coverage but failed the frozen return-correlation and sign-agreement gates versus the pinned LBMA-labelled historical artifact;
- Silver/Platinum/Palladium V2 requests were `NOT_PROVEN` after provider retries.

No V1/V2 threshold is relaxed after seeing these results.

## 2. Authority findings that constrain V3

### LBMA benchmark data

Official LBMA/ICE materials state that the LBMA Gold, Silver, Platinum and Palladium benchmark prices are administered by ICE Benchmark Administration and that obtaining/using the benchmark data requires the applicable IBA licence. The public website may show delayed pricing, but this does not prove a licence for Gold Control to ingest and use the benchmark as a model input.

Therefore:

`DIRECT_LBMA_OPERATIONAL_MODEL_INPUT = BLOCKED_LICENSE_NOT_PROVEN`

Gold Control will not scrape, relabel, or silently operationalize LBMA benchmark data without separate licence proof.

### StakTrakr historical artifact

The pinned historical artifact remains:

`lbruton/StakTrakr@ed2e549f82ba0d1cd3ca32842b82d3888d301e01`

Repository history shows the latest commit touching `data/spot-history-2026.json` was dated 2026-08-19 and described coverage through 2026-08-19. The repository may have later unrelated pushes, but the frozen daily metal data file itself does not establish a post-2026-08-19 operational continuation.

Therefore:

`STAKTRAKR_FORWARD_DAILY_METALS_CONTINUATION = NOT_PROVEN`

### Twelve Data daily history

Official Twelve Data documentation states that daily intervals generally contain substantially deeper history than intraday data and often extend to the first trading date; `/time_series` supports bounded `start_date`/`end_date` retrieval and up to 5,000 points per response. Official documentation also states that the timezone parameter is ignored for `1day`, `1week`, and `1month` intervals and daily data is returned in provider/exchange local semantics.

Therefore V3 does **not** call Twelve `1day` data a London fixing, LBMA price, NY17 price, or London-time bar.

## 3. V3 design decision

V3 stops trying to stitch a new provider onto the LBMA-labelled historical daily-metal artifact.

Instead, it tests a single-provider daily-metal history for the entire Patch daily-return feature:

- `XAU/USD`, Twelve Data, `1day`;
- `XAG/USD`, Twelve Data, `1day`;
- `XPT/USD`, Twelve Data, `1day`;
- `XPD/USD`, Twelve Data, `1day`.

Provisional lineage name:

`PATCH_METALS_TWELVE_DAILY_FULL_HISTORY_V3`

This is a **new input semantic**, not a continuation or relabelling of LBMA.

The old pinned StakTrakr artifact remains immutable historical evidence and remains the data source used by `CAUSAL_PATCH_R1_REPRO_V1`. It is not overwritten.

## 4. NASDAQ V3 design decision

FRED identifies `NASDAQCOM` as the NASDAQ Composite daily market-close index and notes that the market normally closes at 16:00 ET.

The V3 feature uses only completed months, never the current origin month:

For target month `t`, origin month `p=t-1`:

`log(NASDAQCOM_mean[p-1] / NASDAQCOM_mean[p-2])`

Historical availability is reconstructed conservatively from the market-close semantic, not from missing ALFRED month-end snapshots:

- each daily close is treated as available **no earlier than the next calendar day** after its observation date;
- because V3 uses only months `p-1` and `p-2`, every input observation is at least one completed month old at the origin month-end;
- this is labelled `MARKET_CLOSE_AVAILABILITY_RECONSTRUCTION`, not an original historical retrieval record;
- current-vintage FRED values may be used only after source-identity/materiality audit against frozen CORE5 monthly values passes.

Provisional feature identity:

`NASDAQCOM_COMPLETED_MONTH_RETURN_MARKET_CLOSE_V3`

## 5. V3 source-readiness gate

Before any V3 Patch score is run:

1. prove Twelve Data `1day` access for all four metal symbols in one governed source audit;
2. prove common daily history is deep enough to build the frozen `L=252` input at the first model sample used by the reproduction path;
3. prove recent coverage reaches the latest completed business-day region required for prospective operation;
4. do not log raw vendor values;
5. prove FRED `NASDAQCOM` current historical daily series reconstructs the frozen CORE5 monthly means within the already-used V1/V2 materiality gates;
6. prove every V3 NASDAQ input month is completed before the forecast origin under the conservative next-day availability rule;
7. do not write Neon, forecast ledger, or Decision Store.

Source-readiness PASS name:

`PATCH_PROSPECTIVE_INPUT_BRIDGE_V3_SOURCE_PASS`

Failure name:

`BLOCKED_PATCH_PROSPECTIVE_INPUT_V3_SOURCE_NOT_PROVEN`

## 6. Model-impact gate after source PASS

Only if V3 source readiness passes, run the same locked `2023-01→2026-07`, `N=43` replay with:

- frozen `L=252`, `P=21`, `D=32`;
- no geometry re-selection;
- Twelve `1day` four-metal full-history input instead of StakTrakr metals;
- completed-month NASDAQ return V3 instead of the original current-month NASDAQ return;
- DFF, DEXCHUS, GPR rules otherwise unchanged;
- same target and RW benchmark.

Reserved identity:

`CAUSAL_PATCH_R1_REPRO_V1_2_TWELVE_DAILY_ORIGIN_SAFE`

The locked model-impact gates remain those frozen in V2:

- target reconciliation `43/43`;
- RW reconciliation `43/43`;
- deterministic rerun equality;
- no future information;
- no geometry retune;
- MAPE `< RW MAPE`;
- MAE `< RW MAE`;
- worst APE `<= 1.25 × RW worst APE`.

If any gate fails, V3 is rejected. No post-result threshold or geometry tuning is allowed.

## 7. Downstream dependency remains unchanged

A V3 model-impact PASS still does not authorize a live decision.

Next gates remain:

1. freeze the accepted executable/input identity;
2. validate generic monthly-reference → Emergency geometry;
3. persist immutable forecast input snapshot + forecast contract before an eligible real origin;
4. first forward evidence is `PROSPECTIVE_SHADOW`;
5. September 2026 is never backdated.
