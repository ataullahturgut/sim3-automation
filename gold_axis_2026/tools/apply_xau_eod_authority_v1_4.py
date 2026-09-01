from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
manifest_path = root / 'GOLD_CONTROL_PROJECT_MANIFEST.md'
stage4_path = root / 'GOLD_CONTROL_STAGE4_STATUS_2026-09-01.md'
cc_path = root / 'GOLD_CONTROL_XAU_EOD_SOURCE_CHANGE_CONTROL_2026-09-01.md'
contracts_path = root / 'data_pipeline' / 'source_contracts.json'

manifest = manifest_path.read_text(encoding='utf-8')
if '**Manifest version:** 1.3' not in manifest:
    raise SystemExit('EXPECTED_MANIFEST_V1_3_NOT_FOUND')
manifest = manifest.replace('**Manifest version:** 1.3', '**Manifest version:** 1.4', 1)

old_xau_block = '''### XAU daily operational history

Series: `XAU_DAILY_XAUS`  
Contract source: XAUS history  
Role: operational cross-check  
Status: `CANDIDATE_NOT_BENCHMARK`

The persisted operational lineage currently exposes an upstream/source label associated with Yahoo/GC=F. This remains an operational cross-check lineage and is not promoted to settlement/EOD authority.
'''
new_xau_block = old_xau_block + '''
### Canonical XAU EOD decision-session authority

Series identity reserved for implementation: `XAU_EOD_CME_EBS`  
Economic semantic: spot XAU/USD daily decision-session close  
Authority/source: **CME Group / EBS Market on CME Globex**  
Instrument: **XAU/USD SM**, EBS Market product code **GCUS**  
Session timezone: `America/New_York`  
Trade-date boundary: **17:00 ET**  
Role: canonical R4.1 EOD decision-price authority  
Status: `APPROVED_AUTHORITY_AND_SESSION; BLOCKED_EXECUTABLE_FIELD_MAPPING_AND_ENTITLEMENT`

Authority decision rationale is frozen in `gold_axis_2026/GOLD_CONTROL_XAU_EOD_SOURCE_CHANGE_CONTROL_2026-09-01.md`.

The authority review found no single reviewed benchmark that is simultaneously a regulated/global gold benchmark and an end-of-trade-date spot close. Therefore the contract separates **benchmark** from **EOD decision-session close**:

- LBMA Gold Price PM remains the global Loco London benchmark and is **not** relabelled as EOD close;
- CME Group Spot Gold Reference Rate remains a 13:29–13:30 ET spot marker and is **not** relabelled as EOD close;
- COMEX Gold futures settlement / Yahoo `GC=F` remains futures semantics and is **not** relabelled as spot XAU/USD;
- Twelve Data provider-default `1day` XAU/USD remains a vendor Commodity Aggregate daily bar in `Australia/Sydney` exchange-local time and is **not** the canonical EBS 17:00 ET close.

The approved source/session contract does **not** authorize an invented price-extraction rule. Before first Neon write, the authorized CME/EBS data entitlement and the exact executable EOD field/aggregation mapping must be audited and frozen. If an explicit EBS EOD close field is unavailable, the project remains `BLOCKED_FIELD_MAPPING_NOT_PROVEN`; no ad-hoc last-trade, midpoint, Twelve, XAUS, LBMA, or futures fallback is permitted under the canonical series id.
'''
if old_xau_block not in manifest:
    raise SystemExit('XAU_OPERATIONAL_BLOCK_ANCHOR_NOT_FOUND')
manifest = manifest.replace(old_xau_block, new_xau_block, 1)

old_blocker_item = '- Current XAUS source availability incident: `DEGRADED_UPSTREAM_HTTP_503`; unrelated provider ingestion must continue independently\n'
new_blocker_item = old_blocker_item + '- Canonical CME/EBS XAU EOD executable ingestion: `BLOCKED_ENTITLEMENT_AND_EOD_FIELD_MAPPING_NOT_PROVEN`; source/session authority is approved, but no price value may be written until exact authorized data mapping is frozen\n'
if old_blocker_item not in manifest:
    raise SystemExit('BLOCKER_ANCHOR_NOT_FOUND')
manifest = manifest.replace(old_blocker_item, new_blocker_item, 1)

old_stage4_row = '| 4 | `IN_PROGRESS_BLOCKED_INPUT_CONTRACTS` | Deterministic engine/bridge tests PASS, but readiness audit is BLOCKED: forecast contract missing, immutable forecast input snapshot missing, latest daily XAU run not SUCCESS, and no approved canonical XAU EOD decision source |'
new_stage4_row = '| 4 | `IN_PROGRESS_BLOCKED_INPUT_CONTRACTS` | Deterministic engine/bridge tests PASS. Canonical XAU EOD source/session authority is now approved as CME/EBS XAU/USD SM (GCUS), 17:00 ET trade-date boundary; active blockers are forecast contract, immutable forecast input snapshot, and successful authorized CME/EBS EOD ingestion with exact field mapping |'
if old_stage4_row not in manifest:
    raise SystemExit('STAGE4_ROW_ANCHOR_NOT_FOUND')
manifest = manifest.replace(old_stage4_row, new_stage4_row, 1)

old_confirmed = '''Confirmed blockers:

1. `FORECAST_CONTRACT_NOT_ISSUED`
2. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`
3. `LATEST_DAILY_XAU_PIPELINE_NOT_SUCCESS`
4. `NO_APPROVED_CANONICAL_XAU_EOD_DECISION_SOURCE`
'''
new_confirmed = '''Confirmed active blockers after XAU authority change control:

1. `FORECAST_CONTRACT_NOT_ISSUED`
2. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`
3. `CME_EBS_XAU_EOD_PIPELINE_NOT_SUCCESS`
   - `CME_EBS_DATA_ENTITLEMENT_NOT_PROVEN`
   - `CME_EBS_EOD_FIELD_MAPPING_NOT_PROVEN`

Closed Stage-4 source-authority blocker:

`NO_APPROVED_CANONICAL_XAU_EOD_DECISION_SOURCE` → `CLOSED_BY_MANIFEST_V1_4`
'''
if old_confirmed not in manifest:
    raise SystemExit('CONFIRMED_BLOCKERS_ANCHOR_NOT_FOUND')
manifest = manifest.replace(old_confirmed, new_confirmed, 1)

old_interpretation = '''Important source interpretation:

- `XAU_DAILY_XAUS` is transported through the frozen XAUS history endpoint and the registry already documents the upstream Yahoo lineage; upstream disclosure alone is not treated as silent substitution;
- nevertheless this series is explicitly `operational cross-check only` / `CANDIDATE_NOT_BENCHMARK`, so it is not authorized as the R4.1 canonical EOD decision source;
- `XAU_SPOT_XAUS` is indicative/non-settlement monitoring and likewise is not the frozen EOD decision close;
- Cboe GVZ is available and the latest audited daily Cboe run is successful.
'''
new_interpretation = '''Important source interpretation:

- canonical R4.1 EOD source/session authority is **CME Group / EBS Market XAU/USD SM (GCUS)** with `America/New_York` trade-date boundary at **17:00 ET**;
- this approval freezes the economic/source/session identity, not an unverified market-data field; exact CME/EBS EOD value extraction remains blocked until entitlement and schema/field mapping are proven;
- `XAU_DAILY_XAUS` remains `operational cross-check only` / `CANDIDATE_NOT_BENCHMARK`; its Yahoo/GC=F-like lineage is not spot EOD authority;
- `XAU_SPOT_XAUS` remains indicative/non-settlement monitoring;
- LBMA Gold Price PM remains a benchmark, not EOD; CME Spot Gold Reference Rate remains a 13:29–13:30 ET marker, not EOD;
- Twelve Data `XAU/USD` remains a licensed/internal research bridge and may not be silently substituted for EBS authority because its provider-default daily bar uses `Australia/Sydney` exchange-local semantics;
- Cboe GVZ is available and the latest audited daily Cboe run is successful.
'''
if old_interpretation not in manifest:
    raise SystemExit('SOURCE_INTERPRETATION_ANCHOR_NOT_FOUND')
manifest = manifest.replace(old_interpretation, new_interpretation, 1)

old_gates = '''Required next gates, in order:

1. define and approve a canonical XAU EOD decision-price source/lineage under change control; do not silently promote the current cross-check or indicative spot series;
2. restore a successful daily XAU ingestion path for the approved source;
3. create the first genuine immutable H=1 forecast input snapshot and monthly forecast contract from the executable frozen forecasting path before outcome realization;
4. only then build/schedule the canonical R4.1 EOD issuer using the frozen engine and complete provenance;
5. the first real forward state must begin as `PROSPECTIVE_SHADOW`; `LIVE_PRODUCTION` remains disabled until Stage 12 graduation;
6. do not backfill historical rows and relabel them as prospective.

No `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` decision row may be written while any of the four readiness blockers remains open.
'''
new_gates = '''Required next gates, in order:

1. prove/activate authorized CME/EBS XAU/USD SM market-data entitlement and freeze the exact EOD value field/aggregation that corresponds to the approved 17:00 ET trade-date boundary;
2. create the new explicit `XAU_EOD_CME_EBS` lineage and obtain a successful daily ingestion run without overwriting or relabelling XAUS/Twelve/LBMA/futures history;
3. create the first genuine immutable H=1 forecast input snapshot and monthly forecast contract from the executable frozen forecasting path before outcome realization;
4. only then build/schedule the canonical R4.1 EOD issuer using the frozen engine and complete provenance;
5. the first real forward state must begin as `PROSPECTIVE_SHADOW`; `LIVE_PRODUCTION` remains disabled until Stage 12 graduation;
6. do not backfill historical rows and relabel them as prospective.

No `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` decision row may be written while any active Stage-4 readiness blocker remains open.
'''
if old_gates not in manifest:
    raise SystemExit('NEXT_GATES_ANCHOR_NOT_FOUND')
manifest = manifest.replace(old_gates, new_gates, 1)
manifest_path.write_text(manifest, encoding='utf-8')

contracts = json.loads(contracts_path.read_text(encoding='utf-8'))
contracts['version'] = 'GOLD_DATA_R2_2026-09-01_XAU_EOD_AUTHORITY_V1'
series = contracts['series']
if 'XAU_EOD_CME_EBS' in series:
    raise SystemExit('XAU_EOD_CME_EBS_ALREADY_EXISTS')
rebuilt = {}
for key, value in series.items():
    rebuilt[key] = value
    if key == 'XAU_DAILY_XAUS':
        rebuilt['XAU_EOD_CME_EBS'] = {
            'semantic': 'XAU_USD_SPOT_EOD_SESSION_CLOSE',
            'tier': 'A',
            'source': 'CME Group / EBS Market on CME Globex',
            'symbol': 'XAU/USD SM (GCUS)',
            'frequency': 'trade-date daily',
            'unit': 'USD/troy_oz',
            'session_timezone': 'America/New_York',
            'trade_date_boundary': '17:00 ET',
            'role': 'canonical R4.1 EOD decision-price authority',
            'status': 'APPROVED_AUTHORITY_AND_SESSION; BLOCKED_EXECUTABLE_FIELD_MAPPING_AND_ENTITLEMENT',
            'fallback_policy': 'NONE_SILENT; BLOCK_IF_PRIMARY_UNAVAILABLE',
            'not_equivalent_to': [
                'LBMA Gold Price AM/PM',
                'CME Group Spot Gold Reference Rate 13:29-13:30 ET marker',
                'COMEX GC futures settlement or Yahoo GC=F',
                'Twelve Data Commodity Aggregate provider-default 1day Australia/Sydney',
                'XAU_DAILY_XAUS',
                'XAU_SPOT_XAUS'
            ]
        }
contracts['series'] = rebuilt
contracts_path.write_text(json.dumps(contracts, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

cc = '''# GOLD CONTROL — XAU EOD DECISION SOURCE CHANGE CONTROL

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
'''
cc_path.write_text(cc, encoding='utf-8')

stage4 = '''# GOLD CONTROL — STAGE 4 DETERMINISTIC R4.1 STATUS

**Status date:** 2026-09-01
**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.4
**Stage:** 4 — Deterministic R4.1 Decision Engine / Issuer
**Current status:** `IN_PROGRESS_BLOCKED_INPUT_CONTRACTS`

## 1. What is verified

- Frozen R4.1 engine tests are deterministic under the audited test contract.
- R4.1 descriptive emitted state can be mapped to Decision Store without recomputing signals.
- Persistence bridge refuses action/exposure fields and unreviewed emitted-state shape drift.
- Store-reader roundtrip, idempotency and rollback are verified.
- `LIVE_PRODUCTION` has an additional disabled-by-default write gate.
- A current app reader exists but there are no display-eligible decision rows.

## 2. Canonical live emitter audit

Status:

`NOT_FOUND_CANONICAL_LIVE_R4_1_EMITTER`

`replay_daily.py` is a sequential replay CLI, not a prospective scheduled issuer.

The older R4 workflow that emits LONG/CASH and AL/SAT cannot be promoted into R4.1 because the current contract is `NOT_PROVEN_POSITION_MAPPING`.

## 3. Source-authority change-control result

Authority research and frozen validation are recorded in:

`GOLD_CONTROL_XAU_EOD_SOURCE_CHANGE_CONTROL_2026-09-01.md`

Approved source/session authority:

- CME Group / EBS Market on CME Globex;
- XAU/USD SM (`GCUS`);
- spot XAU/USD semantic;
- `America/New_York` session timezone;
- 17:00 ET trade-date boundary;
- reserved series id `XAU_EOD_CME_EBS`.

Decision:

`CME_EBS_XAUUSD_1700_ET_AUTHORITY_AND_SESSION_APPROVED`

Closed blocker:

`NO_APPROVED_CANONICAL_XAU_EOD_DECISION_SOURCE` → `CLOSED_BY_MANIFEST_V1_4`

The authority approval does not authorize a guessed close field or vendor substitution.

## 4. Why alternatives were not promoted

- LBMA Gold Price PM is the global Loco London benchmark but is an auction benchmark at 15:00 London, not EOD.
- CME Group Spot Gold Reference Rate is an EBS-based 13:29–13:30 ET spot marker, not EOD.
- `XAU_DAILY_XAUS` remains operational cross-check / Yahoo-GC=F-like lineage, not spot-EOD authority.
- `XAU_SPOT_XAUS` remains indicative monitoring.
- Twelve provider-default daily XAU/USD uses Commodity Aggregate / `Australia/Sydney` exchange-local daily semantics and is not EBS 17:00 ET EOD.

No silent fallback is approved.

## 5. Frozen validation evidence

Run `33506001316`, job `99850068530`: `SUCCESS`.

Validation period only:

`2021–2023`

`2024+` used for selection:

`NO`

The pinned legacy validation series was LBMA-labelled for 754/754 Gold rows. Neither Twelve daily construction was identity-equivalent to it. Therefore the canonical EBS EOD source receives a new lineage rather than mutating legacy/XAUS/Twelve history.

## 6. Active readiness blockers

The original read-only readiness audit run `33499509482`, job `99829327414` executed successfully. After source-authority change control, active blockers are:

1. `FORECAST_CONTRACT_NOT_ISSUED`
2. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`
3. `CME_EBS_XAU_EOD_PIPELINE_NOT_SUCCESS`
   - `CME_EBS_DATA_ENTITLEMENT_NOT_PROVEN`
   - `CME_EBS_EOD_FIELD_MAPPING_NOT_PROVEN`

Decision Store and forecast-state tables remain unpopulated by this change-control action.

## 7. Required next work

1. prove/activate authorized CME/EBS XAU/USD SM data access;
2. inspect the entitled schema/product and freeze the exact 17:00 ET EOD value field/aggregation; if not provable, remain `BLOCKED`;
3. add explicit `XAU_EOD_CME_EBS` ingestion lineage and obtain a successful daily run;
4. issue the first genuine immutable H=1 forecast input snapshot and monthly forecast contract before outcome realization;
5. build/schedule the canonical R4.1 EOD issuer only after those prerequisites pass;
6. first forward Decision Store state must be `PROSPECTIVE_SHADOW`, never retroactive and not `LIVE_PRODUCTION`.

`NOT_PROVEN_POSITION_MAPPING` remains unchanged.
'''
stage4_path.write_text(stage4, encoding='utf-8')

# Verify deterministic outcome before caller commits.
check_manifest = manifest_path.read_text(encoding='utf-8')
if '**Manifest version:** 1.4' not in check_manifest:
    raise SystemExit('MANIFEST_V1_4_VERIFY_FAIL')
if 'XAU_EOD_CME_EBS' not in check_manifest:
    raise SystemExit('MANIFEST_EBS_CONTRACT_VERIFY_FAIL')
parsed = json.loads(contracts_path.read_text(encoding='utf-8'))
ebs = parsed['series'].get('XAU_EOD_CME_EBS')
if not ebs or ebs.get('trade_date_boundary') != '17:00 ET':
    raise SystemExit('SOURCE_CONTRACT_EBS_VERIFY_FAIL')
if 'CLOSED_BY_MANIFEST_V1_4' not in stage4_path.read_text(encoding='utf-8'):
    raise SystemExit('STAGE4_BLOCKER_TRANSITION_VERIFY_FAIL')
print('GOLD_CONTROL_XAU_EOD_AUTHORITY_APPLY_PASS')
