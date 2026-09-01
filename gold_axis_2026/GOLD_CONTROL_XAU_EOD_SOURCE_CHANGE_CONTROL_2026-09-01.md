# GOLD CONTROL — XAU EOD DECISION SOURCE CHANGE CONTROL

**Status date:** 2026-09-01  
**Manifest target:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.4  
**Stage:** 4 — Deterministic R4.1 Decision Engine / Issuer  
**Decision:** `CME_EBS_XAUUSD_1700_ET_AUTHORITY_AND_SESSION_APPROVED; EXECUTABLE_INGESTION_BLOCKED`

## 1. Decision summary

The canonical R4.1 daily decision-price **source/session authority** is frozen as:

- venue/operator: **CME Group / EBS Market on CME Globex**;
- spot instrument: **XAU/USD SM**;
- EBS Market product code: **GCUS**;
- economic semantic: spot XAU/USD;
- trade-date/session timezone: `America/New_York`;
- daily trade-date boundary: **17:00 ET**;
- reserved canonical series id: `XAU_EOD_CME_EBS`.

This decision approves the authority, instrument and session boundary. It does **not** invent an executable market-data field. First ingestion remains blocked until authorized CME/EBS entitlement and exact EOD field/aggregation mapping are proven.

## 2. Authority research

### 2.1 LBMA Gold Price

Official LBMA/ICE documentation identifies the LBMA Gold Price as the global benchmark for unallocated Loco London gold. The auction begins twice daily at 10:30 and 15:00 London time and benchmark use can require IBA licensing.

Conclusion:

`LBMA_GOLD_PRICE_PM = AUTHORITY_BENCHMARK_NOT_EOD_SESSION_CLOSE`

It remains a benchmark/comparator. It is not relabelled as an end-of-trade-date spot close.

Official sources:

- https://www.lbma.org.uk/prices-and-data/lbma-precious-metal-prices
- https://www.lbma.org.uk/prices-and-data/lbma-gold-price
- https://www.ice.com/iba/lbma-precious-metals

### 2.2 CME Group Spot Gold Reference Rate

CME states that EBS Market data is used for the Spot Gold Reference Rate. The first calculation tier uses trades during 13:29:00–13:30:00 ET.

Conclusion:

`CME_SPOT_GOLD_REFERENCE_RATE = AUTHORITY_SPOT_MARKER_NOT_EOD_SESSION_CLOSE`

It is an important independent marker/comparator but is not the daily session boundary.

Official source:

- https://www.cmegroup.com/markets/metals-marker-prices.html

### 2.3 EBS Market spot precious metals session

CME's official trading-hours schedule states that EBS Market spot FX & precious metals use a **17:00 ET trade-date roll Monday–Thursday** and **17:00 ET Friday close**. CME's EBS product guide lists spot Gold `XAU/USD SM` on EBS Market with product code `GCUS`. CME describes EBS Market as a primary market/reference-price venue and offers real-time/historical spot precious-metals market data.

Conclusion:

`CME_EBS_XAUUSD_SM_1700_ET = BEST_AUTHORITY_MATCH_FOR_R4_1_EOD_DECISION_SESSION`

Official sources:

- https://www.cmegroup.com/trading-hours.html
- https://www.cmegroup.com/markets/fx/fx-product-guide.html
- https://www.cmegroup.com/markets/ebs/ebs-market.html
- https://www.cmegroup.com/market-data/browse-data/catalog/ebs-spot-fx.html

### 2.4 Twelve Data XAU/USD

Twelve identifies `XAU/USD` as `Gold Spot / US Dollar`, Commodity Aggregate. Its commodity reference uses `Australia/Sydney` exchange-local timezone and 24/7 schedule. Twelve documentation states timezone selection is ignored for 1day/1week/1month intervals and those bars are returned in exchange-local time.

Conclusion:

`TWELVE_PROVIDER_DEFAULT_1DAY = DOCUMENTED_VENDOR_DAILY_BAR_NOT_EBS_1700_ET_EOD`

Twelve remains useful for private/internal research and bridge testing. It is not authorized as a silent replacement for the canonical EBS authority.

Official sources:

- https://twelvedata.com/markets/300755/commodity/xau-usd
- https://twelvedata.com/exchanges/commodity
- https://twelvedata.com/docs

## 3. Frozen validation evidence

GitHub Actions run `33506001316`, job `99850068530`, completed `SUCCESS` using only the frozen Tactical validation period `2021–2023`; `2024+` was explicitly excluded from source selection.

Pinned StakTrakr Gold provider labels in that validation window were `LBMA:754/754`.

Bridge results versus the legacy pinned series:

| Candidate | Fast-state agreement | Slow-state agreement | Return correlation | Return-sign agreement |
|---|---:|---:|---:|---:|
| Twelve provider-default Sydney daily | 84.332% | 82.692% | 0.295370 | 58.167% |
| Twelve 17:00 New York intraday-derived sample | 87.690% | 78.205% | 0.400753 | 60.118% |

Interpretation:

- neither Twelve construction is identity-equivalent to the legacy LBMA-labelled series;
- these validation scores are **not used to optimize the final authority/session choice**;
- they prove that a new canonical spot-EOD series must receive a new lineage and a controlled source migration rather than being relabelled as legacy/XAUS/LBMA data.

## 4. Why 17:00 ET is approved

R4.1 requires a completed daily market state, not merely an intraday benchmark observation. Among the reviewed official authorities:

- LBMA PM is an auction benchmark at 15:00 London;
- CME Spot Gold Reference Rate is a 13:29–13:30 ET marker;
- EBS Market explicitly defines the spot precious-metals **trade-date roll at 17:00 ET**.

Therefore 17:00 ET is the strongest documented session boundary for a spot-XAU/USD daily decision close without mislabelling a benchmark or futures settlement as EOD.

This is a semantic/market-structure decision, not a hindsight optimization.

## 5. Exact executable price mapping remains blocked

Authority approval does not by itself prove the exact field available under the future CME/EBS entitlement.

Before first `XAU_EOD_CME_EBS` write, the implementation must prove and freeze:

1. authorized CME/EBS market-data entitlement or explicitly authorized redistributor whose lineage is EBS XAU/USD SM;
2. exact API/file/product identifier and schema;
3. exact EOD close field supplied by that product, if one exists;
4. otherwise a separately audited deterministic aggregation rule — no ad-hoc assumption;
5. `observation_ts`, trade-date and DST handling using `America/New_York`;
6. holiday/early-close handling from the CME/EBS calendar;
7. retrieved-at timestamp, payload hash, source vintage and revision policy;
8. raw-data/private-display restrictions under the applicable licence.

Until these pass:

`CME_EBS_XAU_EOD_PIPELINE_NOT_SUCCESS`

Sub-blockers:

- `CME_EBS_DATA_ENTITLEMENT_NOT_PROVEN`
- `CME_EBS_EOD_FIELD_MAPPING_NOT_PROVEN`

## 6. Fallback policy

Canonical fallback policy:

`NONE_SILENT`

If the approved EBS source is unavailable or incomplete, R4.1 EOD issuance is `BLOCKED` for that session. The system must not substitute:

- `XAU_DAILY_XAUS`;
- `XAU_SPOT_XAUS`;
- Twelve provider-default daily bars;
- a Twelve-derived 17:00 ET price;
- LBMA Gold Price PM;
- CME Spot Gold Reference Rate;
- COMEX GC settlement / Yahoo `GC=F`;
- any other provider under the `XAU_EOD_CME_EBS` series identity.

A future contingency source requires its own explicit change-control approval and separate lineage.

## 7. Stage-4 blocker transition

Closed:

`NO_APPROVED_CANONICAL_XAU_EOD_DECISION_SOURCE` → `CLOSED_BY_MANIFEST_V1_4`

Still active:

1. `FORECAST_CONTRACT_NOT_ISSUED`
2. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`
3. `CME_EBS_XAU_EOD_PIPELINE_NOT_SUCCESS`

No Neon market observation and no Decision Store row is authorized by this document alone.

## 8. Evidence-class safeguards

- no historical row may be relabelled as prospective;
- no `LIVE_PRODUCTION` state is authorized;
- first forward decision state remains `PROSPECTIVE_SHADOW` only after all Stage-4 input blockers pass;
- `NOT_PROVEN_POSITION_MAPPING` remains unchanged;
- no 2024+ locked outcome was used to tune the authority/session choice.


---

# Manifest v1.5 executable decision-reference amendment

## A. Authority finding

Further CME authority research confirms that EBS Market Spot FX & Precious Metals uses a 17:00 ET trade-date roll, but CME does not expose a single exchange-style official XAU/USD daily close/settlement field for this spot market. EBS Ticker is the official CME market-data product that includes XAU/USD SM and provides one-second time slices with Best Bid, Best Offer, Paid/Given trade data, daily highs/lows and Timestamp. Historical EBS Ticker data is available through CME DataMine; real-time delivery includes direct CME delivery options.

Official CME evidence:

- EBS trading hours / 17:00 ET trade-date roll: https://www.cmegroup.com/trading-hours.html
- EBS Value Date Calendar / standard-pair EOD definition: https://www.cmegroup.com/content/dam/cmegroup/documents/ebs_value-date-calendar.pdf
- EBS XAU/USD SM product code GCUS: https://www.cmegroup.com/markets/fx/fx-product-guide.html
- EBS Ticker fields/frequency/access: https://www.cmegroup.com/market-data/browse/files/ebs-ticker-fact-sheet.pdf
- CME cash-market historical access/DataMine: https://www.cmegroup.com/datamine.html

## B. Final decision-price contract

Decision:

`CME_EBS_XAUUSD_1700_ET_DECISION_REFERENCE_RULE_APPROVED`

Gold Control will not claim an official spot closing price that CME does not publish. Instead, R4.1 receives a frozen internal EOD **decision reference price** based entirely on official EBS Ticker fields:

1. cutoff = 17:00:00 `America/New_York`;
2. candidate observations = EBS Ticker `XAU/USD SM (GCUS)` one-second slices in `[16:59:00,17:00:00)` ET;
3. select latest slice with valid positive `Best Bid` and `Best Offer` and `Best Bid <= Best Offer`;
4. decision reference = `(Best Bid + Best Offer) / 2`;
5. if no valid two-sided quote exists in that final 60-second window, emit `BLOCKED_NO_FRESH_TWO_SIDED_EBS_QUOTE`; do not forward-fill or substitute another provider;
6. persist quote timestamp, source/product identity, retrieval/vintage identifiers and derived hash;
7. raw licensed EBS fields remain private/non-display unless redistribution rights are separately proven.

This rule is a governance/data-contract definition, not a threshold tuned on 2024+ outcomes.

## C. Why midpoint instead of last trade

EBS Ticker provides two-sided best rates continuously in one-second slices, whereas a last dealt rate can be irregular in time and side-dependent (`Paid`/`Given`). A cutoff midquote gives a deterministic, side-neutral state of the authoritative EBS central market at the frozen trade-date boundary. It is explicitly labelled an internal decision reference, not a benchmark, fixing, settlement or official close.

## D. Blocker reduction

Closed by v1.5:

`CME_EBS_EOD_FIELD_MAPPING_NOT_PROVEN` → `CLOSED_BY_EXECUTABLE_EBS_TICKER_RULE`

Remaining external source blocker:

`CME_EBS_TICKER_DATA_ENTITLEMENT_NOT_PROVEN`

No Neon observation is authorized until the entitlement is actually proven and the ingestion run passes.
