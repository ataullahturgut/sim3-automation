# GOLD CONTROL — XAU EOD DECISION SOURCE CHANGE CONTROL

**Status date:** 2026-09-01  
**Manifest target:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.6  
**Stage:** 4 — Deterministic R4.1 Decision Engine / Issuer  
**Decision:** `TWELVE_XAUUSD_NY17_CANONICAL_OPERATIONAL_SOURCE_APPROVED`

## 1. Final architecture

The active canonical R4.1 EOD decision reference is:

- canonical series: `XAU_EOD_TWELVE_NY17`;
- economic semantic: spot XAU/USD internal daily decision reference;
- session-definition authority: CME Group / EBS Market;
- session boundary: 17:00 ET, `America/New_York`;
- operational price provider: Twelve Data;
- provider symbol: `XAU/USD`;
- provider interval: `1min`;
- selected bar: exact `16:59:00` ET bar;
- decision price: selected bar `close`;
- no silent fallback.

This supersedes `XAU_EOD_CME_EBS` as the active operational ingestion series. The CME/EBS object remains in the registry for audit history and session-methodology provenance only.

## 2. Why this split is methodologically correct

Spot XAU/USD is an OTC market and does not have one universal exchange-style official daily close. CME/EBS is nevertheless an authoritative primary-market source for the **trade-date convention**: EBS spot FX and precious-metals trade date rolls at 17:00 ET. That convention is used to define when Gold Control's daily R4.1 state becomes complete.

The actual price observation must preserve its real provider lineage. Twelve Data therefore remains visibly the price provider; it is not relabelled as CME/EBS data.

Official authority evidence:

- CME Group trading hours: EBS Market Spot FX & Precious Metals trade-date roll = 17:00 ET.
- CME EBS dealing/value-date rules: 17:00 New York is the standard trade-date transition.
- Twelve Data documentation: intraday timezone may be specified with an IANA timezone; `datetime` identifies the bar open; `close` is the price at the end of the bar.
- Twelve XAU/USD reference: Gold Spot / US Dollar is an available commodity instrument.

## 3. Executable mapping

Frozen mapping:

1. request `/time_series?symbol=XAU/USD&interval=1min&timezone=America/New_York`;
2. after the 17:00 ET boundary, select the unique bar with `datetime=16:59:00` ET for that trade date;
3. validate positive finite OHLC values;
4. set `decision_reference_price = close`;
5. preserve the original Twelve timestamp and retrieval/payload lineage;
6. if the exact bar is absent/invalid, block the daily issuer; never use provider-default 1day, previous bar, forward-fill, XAUS, LBMA, futures, or a CME-labelled substitute.

Twelve documentation defines the datetime as the bar-open time and close as the end-of-bar price, so the 16:59 one-minute bar ends at the 17:00 ET decision boundary.

## 4. Live access proof

GitHub Actions run `33510985399`, job `99866288149`, completed `SUCCESS`.

The protected credential probe verified, without logging raw prices or writing to Neon:

- Twelve `XAU/USD` intraday access;
- `interval=1min`;
- requested `America/New_York` timezone;
- exact `16:59:00` bar exists for the audited date;
- OHLC values were present and positive;
- executable mapping gate passed.

Result:

`TWELVE_XAU_NY17_EXECUTABLE_MAPPING_PROVEN`

## 5. Historical/frozen validation evidence

Run `33506001316`, job `99850068530`, used only Tactical VAL `2021–2023`; `2024+` was explicitly excluded from source selection. Its NY17 intraday-derived candidate showed that changing daily source/session is not identity-preserving. The validation score is not used to tune the provider choice; it supports explicit new lineage/change control.

The active v1.6 mapping is a one-minute exact-cutoff implementation of the already pre-defined 17:00 ET session concept, not a rule fitted to 2024+ outcomes.

## 6. Why provider-default Twelve daily is still rejected

Twelve provider-default `1day` XAU/USD is returned in the provider's exchange-local commodity timezone (`Australia/Sydney`), and Twelve documents that timezone overrides are ignored for daily intervals. It is therefore a different daily semantic and is not the v1.6 EOD decision series.

## 7. Source identities after v1.6

- `XAU_EOD_TWELVE_NY17` — active canonical R4.1 daily decision reference.
- `XAU_EOD_CME_EBS` — retained audit/history authority candidate; not active ingestion.
- `XAU_DAILY_XAUS` — operational cross-check only.
- `XAU_SPOT_XAUS` — indicative monitoring only.
- `LBMA_GOLD` — authority benchmark candidate, not EOD decision close.

## 8. Stage-4 blocker transition

Closed/superseded:

- `CME_EBS_TICKER_DATA_ENTITLEMENT_NOT_PROVEN` — no longer required by active v1.6 path.
- Twelve XAU/USD 1-minute access — `PROVEN`.
- Twelve 16:59 ET mapping — `PROVEN`.

Still active:

1. `FORECAST_CONTRACT_NOT_ISSUED`
2. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`
3. `TWELVE_XAU_NY17_PIPELINE_NOT_SUCCESS`

No Neon observation or Decision Store row is created by this change-control commit itself.

## 9. Evidence safeguards

- provider identity is never relabelled;
- no historical row is called prospective;
- no `LIVE_PRODUCTION` state is authorized;
- first forward state remains `PROSPECTIVE_SHADOW` after all Stage-4 input blockers pass;
- `NOT_PROVEN_POSITION_MAPPING` remains unchanged.


---

# Manifest v1.7 canonical ingestion closure

GitHub Actions run `33511805110`, job `99869043161`, completed `SUCCESS` on the active v1.6 source contract. The run persisted and verified one canonical `XAU_EOD_TWELVE_NY17` observation for trade date `2026-08-31` with observation timestamp `2026-08-31T21:00:00+00:00` (17:00 ET), Twelve Data lineage, quality `APPROVED_CANONICAL_TWELVE_NY17`, retrieval run `12099dfa-a370-4710-aed5-d02388f652ac`=`SUCCESS`, zero quality errors and no raw-price logging.

Decision:

`TWELVE_XAU_NY17_PIPELINE_NOT_SUCCESS` → `CLOSED_BY_MANIFEST_V1_7`

The XAU EOD input source is no longer a Stage-4 readiness blocker. Remaining Stage-4 blockers are forecast issuance only: `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED` and `FORECAST_CONTRACT_NOT_ISSUED`.
