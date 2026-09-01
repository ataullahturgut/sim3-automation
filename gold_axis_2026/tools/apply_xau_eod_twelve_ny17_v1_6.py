from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
manifest_path = root / 'GOLD_CONTROL_PROJECT_MANIFEST.md'
stage4_path = root / 'GOLD_CONTROL_STAGE4_STATUS_2026-09-01.md'
cc_path = root / 'GOLD_CONTROL_XAU_EOD_SOURCE_CHANGE_CONTROL_2026-09-01.md'
contracts_path = root / 'data_pipeline' / 'source_contracts.json'

# ---------- Manifest ----------
manifest = manifest_path.read_text(encoding='utf-8')
if '**Manifest version:** 1.5' not in manifest:
    raise SystemExit('EXPECTED_MANIFEST_V1_5_NOT_FOUND')
manifest = manifest.replace('**Manifest version:** 1.5', '**Manifest version:** 1.6', 1)

new_xau_section = '''### Canonical XAU EOD decision-reference contract

Canonical series: `XAU_EOD_TWELVE_NY17`  
Economic semantic: **spot XAU/USD 17:00 ET internal EOD decision reference price**  
Session-definition authority: **CME Group / EBS Market**  
Operational market-data provider: **Twelve Data**  
Provider symbol: `XAU/USD`  
Provider interval: `1min`  
Requested timezone: `America/New_York`  
Session boundary: **17:00 ET**  
Role: canonical R4.1 EOD decision reference  
Status: `APPROVED_EXECUTABLE_CANONICAL_SOURCE_CONTRACT; PIPELINE_NOT_YET_PRODUCTION_SUCCESS`

The contract deliberately separates **session authority** from **price-data provider**:

- CME/EBS is the authority for the 17:00 ET spot FX / precious-metals trade-date roll;
- Twelve Data supplies the actual `XAU/USD` intraday OHLC observation used operationally;
- the stored series lineage is Twelve Data and must never be labelled as CME/EBS price data;
- `XAU_EOD_CME_EBS` is retained only as a superseded authority/feed candidate and is not the active production-ingestion series.

Official Twelve Data documentation states that for intraday intervals the requested IANA timezone may be applied, `datetime` identifies when the bar was opened, and `close` is the price at the end of that bar. Therefore the frozen R4.1 decision-reference rule is:

1. Request Twelve Data `/time_series` for `XAU/USD`, `interval=1min`, `timezone=America/New_York`.
2. Select the bar whose `datetime` is exactly `16:59:00` ET for the completed EBS trade date.
3. Require positive finite OHLC values and a unique `16:59:00` bar.
4. Use that bar's `close` as the 17:00 ET internal decision reference price.
5. If the exact 16:59 bar is absent, duplicated, invalid, or not retrievable after the session boundary, emit `BLOCKED_NO_VALID_TWELVE_NY1659_BAR`; no forward-fill or provider substitution is allowed.
6. Persist provider symbol, interval, requested timezone, source bar timestamp, retrieval timestamp, source vintage/payload hash and derived decision-price hash.
7. Raw vendor data remains subject to Twelve Data display/redistribution rights.
8. Historical reconstruction must use the same provider, interval, timezone and mapping rule; it may not relabel legacy XAUS/LBMA/futures history as Twelve data.

Access/mapping evidence: GitHub Actions run `33510985399`, job `99866288149`, `SUCCESS`, proved the protected Twelve credential can retrieve a valid `XAU/USD` `1min` bar at `16:59:00` with `America/New_York` timezone without logging raw prices or writing to the database.

This value is named **decision reference price**, not official settlement or official market close. LBMA Gold Price PM remains a benchmark comparator; CME Group Spot Gold Reference Rate remains a 13:29–13:30 ET spot marker; COMEX settlement remains futures semantics; Twelve provider-default `1day` Australia/Sydney bar remains a different daily semantic and is not used here.

### GVZ'''
manifest, n = re.subn(r'### Canonical XAU EOD decision-reference contract\n.*?\n### GVZ', new_xau_section, manifest, count=1, flags=re.S)
if n != 1:
    raise SystemExit('CANONICAL_XAU_SECTION_REPLACE_FAILED')

old_block = '- Canonical CME/EBS XAU EOD executable ingestion: field mapping/aggregation is frozen in v1.5; remaining external gate is `CME_EBS_TICKER_DATA_ENTITLEMENT_NOT_PROVEN`, and no value may be written until licensed access is proven'
new_block = '- Canonical Twelve NY17 XAU ingestion: protected `XAU/USD` 1-minute access and exact 16:59 ET bar mapping are proven by run `33510985399`; production Neon ingestion is still `TWELVE_XAU_NY17_PIPELINE_NOT_SUCCESS` until the canonical writer completes successfully'
if old_block not in manifest:
    raise SystemExit('BLOCKED_ITEM_ANCHOR_NOT_FOUND')
manifest = manifest.replace(old_block, new_block, 1)

old_stage4 = '| 4 | `IN_PROGRESS_BLOCKED_INPUT_CONTRACTS` | Deterministic engine/bridge tests PASS. Canonical XAU EOD decision-reference contract is approved as CME/EBS XAU/USD SM (GCUS), EBS Ticker, 17:00 ET trade-date boundary with final-minute two-sided midquote rule; active blockers are forecast contract, immutable forecast input snapshot, CME/EBS Ticker entitlement, and successful ingestion |'
new_stage4 = '| 4 | `IN_PROGRESS_BLOCKED_INPUT_CONTRACTS` | Deterministic engine/bridge tests PASS. Canonical XAU EOD decision reference is `XAU_EOD_TWELVE_NY17`: CME/EBS defines the 17:00 ET session boundary and Twelve Data supplies `XAU/USD` 1-minute data; access/mapping probe PASS. Active blockers are forecast contract, immutable forecast input snapshot, and successful canonical Twelve NY17 Neon ingestion |'
if old_stage4 not in manifest:
    raise SystemExit('ROADMAP_STAGE4_ANCHOR_NOT_FOUND')
manifest = manifest.replace(old_stage4, new_stage4, 1)

old_active = '''Confirmed active blockers after XAU authority change control:

1. `FORECAST_CONTRACT_NOT_ISSUED`
2. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`
3. `CME_EBS_XAU_EOD_PIPELINE_NOT_SUCCESS`
   - `CME_EBS_TICKER_DATA_ENTITLEMENT_NOT_PROVEN`
'''
new_active = '''Confirmed active blockers after manifest v1.6 source revision:

1. `FORECAST_CONTRACT_NOT_ISSUED`
2. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`
3. `TWELVE_XAU_NY17_PIPELINE_NOT_SUCCESS`

Closed source-side sub-blockers:

- `CME_EBS_TICKER_DATA_ENTITLEMENT_NOT_PROVEN` → superseded; direct CME/EBS feed is no longer required for the active operational contract.
- Twelve `XAU/USD` 1-minute credential/access → `PROVEN` by run `33510985399`, job `99866288149`.
- Twelve exact `16:59 ET` bar mapping → `PROVEN` by the same run.
'''
if old_active not in manifest:
    raise SystemExit('ACTIVE_BLOCKERS_ANCHOR_NOT_FOUND')
manifest = manifest.replace(old_active, new_active, 1)

source_interp = '''Important source interpretation:

- canonical R4.1 EOD series is **`XAU_EOD_TWELVE_NY17`**;
- **CME/EBS supplies the market-session convention only**: spot FX & precious-metals trade date rolls at **17:00 ET**;
- **Twelve Data is the actual operational price provider**: `XAU/USD`, `1min`, `timezone=America/New_York`; the exact `16:59:00` bar close is the 17:00 ET internal decision reference;
- this is a Gold Control decision-reference construction, not an official CME close, LBMA fixing, or Twelve provider-default daily close;
- `XAU_EOD_CME_EBS` is superseded as the active operational series because licensed EBS Ticker access is unnecessary for this contract;
- `XAU_DAILY_XAUS` remains operational cross-check only / `CANDIDATE_NOT_BENCHMARK`;
- `XAU_SPOT_XAUS` remains indicative monitoring;
- no silent fallback, relabelling, or forward-fill is allowed if the exact Twelve NY17 input is unavailable;
- Cboe GVZ and the Fed/FRED/GPR/Twelve auxiliary pipelines remain independent.

Required next gates, in order:'''
manifest, n = re.subn(r'Important source interpretation:\n\n.*?\n\nRequired next gates, in order:', source_interp, manifest, count=1, flags=re.S)
if n != 1:
    raise SystemExit('SOURCE_INTERPRETATION_REPLACE_FAILED')

new_gates = '''Required next gates, in order:

1. implement the canonical `XAU_EOD_TWELVE_NY17` writer using Twelve `XAU/USD` `1min`, `America/New_York`, exact `16:59:00` bar close and the frozen no-fallback quality gates;
2. write the new lineage to Neon without overwriting or relabelling XAUS/LBMA/CME/futures history and obtain a successful scheduled daily run;
3. create the first genuine immutable H=1 forecast input snapshot and monthly forecast contract from the executable frozen forecasting path before outcome realization;
4. only then build/schedule the canonical R4.1 EOD issuer using the frozen engine and complete provenance;
5. the first real forward state must begin as `PROSPECTIVE_SHADOW`; `LIVE_PRODUCTION` remains disabled until Stage 12 graduation;
6. do not backfill historical rows and relabel them as prospective.

No `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` decision row may be written while any active Stage-4 readiness blocker remains open.'''
manifest, n = re.subn(r'Required next gates, in order:\n\n.*?No `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` decision row may be written while any active Stage-4 readiness blocker remains open\.', new_gates, manifest, count=1, flags=re.S)
if n != 1:
    raise SystemExit('NEXT_GATES_REPLACE_FAILED')

manifest_path.write_text(manifest, encoding='utf-8')

# ---------- Source contracts ----------
contracts = json.loads(contracts_path.read_text(encoding='utf-8'))
contracts['version'] = 'GOLD_DATA_R2_2026-09-01_XAU_EOD_TWELVE_NY17_V1'
series = contracts['series']
if 'XAU_EOD_CME_EBS' not in series:
    raise SystemExit('EXPECTED_XAU_EOD_CME_EBS_NOT_FOUND')
series['XAU_EOD_CME_EBS']['role'] = 'superseded authority/feed candidate; 17:00 ET session research reference only'
series['XAU_EOD_CME_EBS']['status'] = 'SUPERSEDED_AS_OPERATIONAL_SOURCE_BY_MANIFEST_V1_6; KEEP_FOR_AUDIT_HISTORY'
series['XAU_EOD_CME_EBS']['entitlement_status'] = 'NOT_REQUIRED_FOR_ACTIVE_V1_6_PATH'

new_series = {
    'semantic': 'XAU_USD_SPOT_EOD_DECISION_REFERENCE',
    'tier': 'B',
    'source': 'Twelve Data',
    'symbol': 'XAU/USD',
    'frequency': 'trade-date daily derived from 1-minute intraday bar',
    'unit': 'USD/troy_oz',
    'session_definition_authority': 'CME Group / EBS Market spot FX & precious-metals trade-date roll',
    'session_timezone': 'America/New_York',
    'trade_date_boundary': '17:00 ET',
    'provider_endpoint': '/time_series',
    'provider_interval': '1min',
    'provider_timezone': 'America/New_York',
    'bar_datetime_semantic': 'bar open timestamp per Twelve Data documentation',
    'selection_rule': 'unique bar with datetime exactly 16:59:00 ET for completed trade date',
    'price_field': 'close',
    'price_semantic': 'end-of-16:59-minute bar = 17:00 ET internal decision reference',
    'role': 'canonical R4.1 EOD internal decision reference',
    'status': 'APPROVED_EXECUTABLE_CANONICAL_SOURCE_CONTRACT; PIPELINE_NOT_YET_PRODUCTION_SUCCESS',
    'access_evidence': {'run_id': 33510985399, 'job_id': 99866288149, 'result': 'SUCCESS'},
    'quality_gates': [
        'exactly_one_16_59_bar',
        'open_positive_finite',
        'high_positive_finite',
        'low_positive_finite',
        'close_positive_finite'
    ],
    'block_if_missing_or_invalid': True,
    'fallback_policy': 'NONE_SILENT; BLOCK_IF_PRIMARY_UNAVAILABLE_OR_EXACT_BAR_MISSING',
    'official_close_claim': False,
    'display_policy': 'RAW_VENDOR_NON_DISPLAY_UNLESS_RIGHTS_SEPARATELY_APPROVED',
    'not_equivalent_to': [
        'Twelve Data provider-default 1day Australia/Sydney bar',
        'LBMA Gold Price AM/PM',
        'CME Spot Gold Reference Rate',
        'CME/EBS Ticker midquote',
        'COMEX GC futures settlement or Yahoo GC=F',
        'XAU_DAILY_XAUS',
        'XAU_SPOT_XAUS'
    ]
}

# Insert new active series immediately after the retained CME/EBS audit object.
rebuilt = {}
for key, value in series.items():
    rebuilt[key] = value
    if key == 'XAU_EOD_CME_EBS':
        rebuilt['XAU_EOD_TWELVE_NY17'] = new_series
contracts['series'] = rebuilt
contracts_path.write_text(json.dumps(contracts, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

# ---------- Change-control ----------
cc = '''# GOLD CONTROL — XAU EOD DECISION SOURCE CHANGE CONTROL

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
'''
cc_path.write_text(cc, encoding='utf-8')

# ---------- Stage 4 status ----------
stage4 = '''# GOLD CONTROL — STAGE 4 DETERMINISTIC R4.1 STATUS

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
'''
stage4_path.write_text(stage4, encoding='utf-8')

print('GOLD_CONTROL_XAU_EOD_TWELVE_NY17_V1_6_APPLY_PASS')
