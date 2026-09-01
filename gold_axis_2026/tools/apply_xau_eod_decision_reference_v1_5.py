from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
manifest_path = root / 'GOLD_CONTROL_PROJECT_MANIFEST.md'
stage4_path = root / 'GOLD_CONTROL_STAGE4_STATUS_2026-09-01.md'
cc_path = root / 'GOLD_CONTROL_XAU_EOD_SOURCE_CHANGE_CONTROL_2026-09-01.md'
contracts_path = root / 'data_pipeline' / 'source_contracts.json'

manifest = manifest_path.read_text(encoding='utf-8')
if '**Manifest version:** 1.4' not in manifest:
    raise SystemExit('EXPECTED_MANIFEST_V1_4_NOT_FOUND')
manifest = manifest.replace('**Manifest version:** 1.4', '**Manifest version:** 1.5', 1)

old = '''### Canonical XAU EOD decision-session authority

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
new = '''### Canonical XAU EOD decision-reference contract

Series identity reserved for implementation: `XAU_EOD_CME_EBS`  
Economic semantic: **spot XAU/USD 17:00 ET internal EOD decision reference price**  
Authority/source: **CME Group / EBS Market on CME Globex**  
Instrument: **XAU/USD SM**, EBS Market product code **GCUS**  
Market-data product: **EBS Ticker**  
Session timezone: `America/New_York`  
Trade-date boundary: **17:00 ET**  
Role: canonical R4.1 EOD decision reference  
Status: `APPROVED_EXECUTABLE_DECISION_REFERENCE_CONTRACT; BLOCKED_DATA_ENTITLEMENT`

Authority and executable decision-reference rationale is frozen in `gold_axis_2026/GOLD_CONTROL_XAU_EOD_SOURCE_CHANGE_CONTROL_2026-09-01.md`.

Important semantic correction: spot XAU/USD does not have a single exchange-style official daily settlement/close. CME/EBS officially defines the EBS Spot FX & Precious Metals **trade-date roll at 17:00 ET**, while EBS Ticker provides one-second time slices containing `Best Bid`, `Best Offer`, dealt-rate data and timestamp. Therefore Gold Control does **not** claim that CME publishes an official XAU/USD 17:00 close field.

The frozen internal R4.1 decision-reference rule is:

1. Define the trade-date cutoff as `17:00:00 America/New_York`.
2. From EBS Ticker for `XAU/USD SM (GCUS)`, select the latest one-second time slice strictly before the cutoff with both `Best Bid` and `Best Offer` present and positive.
3. Require that selected quote timestamp lies in `[16:59:00, 17:00:00)` ET. Otherwise status is `BLOCKED_NO_FRESH_TWO_SIDED_EBS_QUOTE` and no substitute price is permitted.
4. Require `Best Bid <= Best Offer`; otherwise status is `BLOCKED_INVALID_EBS_BOOK_STATE`.
5. Compute the internal decision reference as `(Best Bid + Best Offer) / 2`.
6. Store source timestamp, bid/offer lineage, retrieval/vintage identifiers and derived-price hash; raw licensed fields remain subject to CME display/redistribution rights.
7. Historical reconstruction, when licensed, must use the corresponding EBS Ticker historical product through CME DataMine under the identical rule.
8. No Twelve, XAUS, LBMA, COMEX futures, last-trade, prior-day or forward-fill fallback is allowed under `XAU_EOD_CME_EBS`.

This value is deliberately named **decision reference price**, not official settlement or official market close. LBMA Gold Price PM remains the benchmark comparator; CME Group Spot Gold Reference Rate remains a 13:29–13:30 ET spot marker; COMEX settlement remains futures semantics; Twelve provider-default daily remains a different vendor/session semantic.
'''
if old not in manifest:
    raise SystemExit('MANIFEST_XAU_V14_BLOCK_NOT_FOUND')
manifest = manifest.replace(old, new, 1)

manifest = manifest.replace(
    '- Canonical CME/EBS XAU EOD executable ingestion: `BLOCKED_ENTITLEMENT_AND_EOD_FIELD_MAPPING_NOT_PROVEN`; source/session authority is approved, but no price value may be written until exact authorized data mapping is frozen',
    '- Canonical CME/EBS XAU EOD executable ingestion: field mapping/aggregation is frozen in v1.5; remaining external gate is `CME_EBS_TICKER_DATA_ENTITLEMENT_NOT_PROVEN`, and no value may be written until licensed access is proven',
    1,
)
manifest = manifest.replace(
    'Canonical XAU EOD source/session authority is now approved as CME/EBS XAU/USD SM (GCUS), 17:00 ET trade-date boundary; active blockers are forecast contract, immutable forecast input snapshot, and successful authorized CME/EBS EOD ingestion with exact field mapping',
    'Canonical XAU EOD decision-reference contract is approved as CME/EBS XAU/USD SM (GCUS), EBS Ticker, 17:00 ET trade-date boundary with final-minute two-sided midquote rule; active blockers are forecast contract, immutable forecast input snapshot, CME/EBS Ticker entitlement, and successful ingestion',
    1,
)
manifest = manifest.replace(
    '3. `CME_EBS_XAU_EOD_PIPELINE_NOT_SUCCESS`\n   - `CME_EBS_DATA_ENTITLEMENT_NOT_PROVEN`\n   - `CME_EBS_EOD_FIELD_MAPPING_NOT_PROVEN`',
    '3. `CME_EBS_XAU_EOD_PIPELINE_NOT_SUCCESS`\n   - `CME_EBS_TICKER_DATA_ENTITLEMENT_NOT_PROVEN`',
    1,
)
manifest = manifest.replace(
    '- canonical R4.1 EOD source/session authority is **CME Group / EBS Market XAU/USD SM (GCUS)** with `America/New_York` trade-date boundary at **17:00 ET**;\n- this approval freezes the economic/source/session identity, not an unverified market-data field; exact CME/EBS EOD value extraction remains blocked until entitlement and schema/field mapping are proven;',
    '- canonical R4.1 EOD decision-reference authority is **CME Group / EBS Market XAU/USD SM (GCUS)** with `America/New_York` trade-date boundary at **17:00 ET**;\n- executable value construction is frozen from **EBS Ticker Best Bid + Best Offer + Timestamp** using the final valid two-sided one-second slice in `[16:59:00,17:00:00)` ET and midpoint `(bid+offer)/2`; this is an internal decision reference, not an official settlement/close;',
    1,
)
manifest = manifest.replace(
    '1. prove/activate authorized CME/EBS XAU/USD SM market-data entitlement and freeze the exact EOD value field/aggregation that corresponds to the approved 17:00 ET trade-date boundary;\n2. create the new explicit `XAU_EOD_CME_EBS` lineage and obtain a successful daily ingestion run without overwriting or relabelling XAUS/Twelve/LBMA/futures history;',
    '1. prove/activate authorized **EBS Ticker** entitlement for XAU/USD SM (GCUS), using real-time EBS Ticker delivery and CME DataMine for licensed historical reconstruction as applicable;\n2. implement the frozen v1.5 final-minute two-sided midquote rule, create the explicit `XAU_EOD_CME_EBS` lineage and obtain a successful daily ingestion run without overwriting or relabelling XAUS/Twelve/LBMA/futures history;',
    1,
)
manifest_path.write_text(manifest, encoding='utf-8')

contracts = json.loads(contracts_path.read_text(encoding='utf-8'))
contracts['version'] = 'GOLD_DATA_R2_2026-09-01_XAU_EOD_DECISION_REFERENCE_V2'
x = contracts['series']['XAU_EOD_CME_EBS']
x.update({
    'semantic': 'XAU_USD_SPOT_EOD_DECISION_REFERENCE',
    'source': 'CME Group / EBS Market on CME Globex; EBS Ticker',
    'frequency': 'trade-date daily derived from 1-second EBS Ticker',
    'role': 'canonical R4.1 EOD internal decision reference',
    'status': 'APPROVED_EXECUTABLE_DECISION_REFERENCE_CONTRACT; BLOCKED_DATA_ENTITLEMENT',
    'official_close_claim': False,
    'data_product': 'EBS Ticker',
    'required_fields': ['Best Bid', 'Best Offer', 'Timestamp'],
    'cutoff_timezone': 'America/New_York',
    'cutoff_time': '17:00:00',
    'selection_window': '[16:59:00,17:00:00) ET',
    'selection_rule': 'latest one-second slice strictly before cutoff with positive two-sided Best Bid and Best Offer',
    'price_formula': '(Best Bid + Best Offer) / 2',
    'quality_gates': ['timestamp_in_final_60_seconds', 'best_bid_positive', 'best_offer_positive', 'best_bid_lte_best_offer'],
    'block_if_no_valid_quote': True,
    'historical_product': 'EBS Ticker historical via CME DataMine',
    'realtime_access_path': 'EBS Ticker Direct Delivery via GCP WebSocket or other authorized CME delivery',
    'entitlement_status': 'NOT_PROVEN',
    'fallback_policy': 'NONE; BLOCK_IF_PRIMARY_UNAVAILABLE_OR_STALE',
})
contracts_path.write_text(json.dumps(contracts, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

cc = cc_path.read_text(encoding='utf-8')
cc += '''

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
'''
cc_path.write_text(cc, encoding='utf-8')

stage4 = stage4_path.read_text(encoding='utf-8')
stage4 = stage4.replace('**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.4', '**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.5', 1)
stage4 = stage4.replace(
    'Approved source/session authority:\n\n- CME Group / EBS Market on CME Globex;\n- XAU/USD SM (`GCUS`);\n- spot XAU/USD semantic;\n- `America/New_York` session timezone;\n- 17:00 ET trade-date boundary;\n- reserved series id `XAU_EOD_CME_EBS`.\n\nDecision:\n\n`CME_EBS_XAUUSD_1700_ET_AUTHORITY_AND_SESSION_APPROVED`',
    'Approved executable decision-reference contract:\n\n- CME Group / EBS Market on CME Globex;\n- XAU/USD SM (`GCUS`);\n- EBS Ticker one-second market data;\n- `America/New_York` 17:00 ET trade-date boundary;\n- final valid two-sided quote in `[16:59:00,17:00:00)` ET;\n- derived price = `(Best Bid + Best Offer) / 2`;\n- reserved series id `XAU_EOD_CME_EBS`;\n- this is an internal decision reference, not an official spot settlement/close.\n\nDecision:\n\n`CME_EBS_XAUUSD_1700_ET_DECISION_REFERENCE_RULE_APPROVED`',
    1,
)
stage4 = stage4.replace(
    '1. `FORECAST_CONTRACT_NOT_ISSUED`\n2. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`\n3. `CME_EBS_XAU_EOD_PIPELINE_NOT_SUCCESS`\n   - `CME_EBS_DATA_ENTITLEMENT_NOT_PROVEN`\n   - `CME_EBS_EOD_FIELD_MAPPING_NOT_PROVEN`',
    '1. `FORECAST_CONTRACT_NOT_ISSUED`\n2. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`\n3. `CME_EBS_XAU_EOD_PIPELINE_NOT_SUCCESS`\n   - `CME_EBS_TICKER_DATA_ENTITLEMENT_NOT_PROVEN`',
    1,
)
stage4 = stage4.replace(
    '1. prove/activate authorized CME/EBS XAU/USD SM data access;\n2. inspect the entitled schema/product and freeze the exact 17:00 ET EOD value field/aggregation; if not provable, remain `BLOCKED`;\n3. add explicit `XAU_EOD_CME_EBS` ingestion lineage and obtain a successful daily run;',
    '1. prove/activate authorized EBS Ticker access for XAU/USD SM (GCUS);\n2. implement the frozen v1.5 final-minute two-sided midquote rule and its quality gates;\n3. add explicit `XAU_EOD_CME_EBS` ingestion lineage and obtain a successful daily run;',
    1,
)
stage4 += '''

## 8. Manifest v1.5 field-mapping closure

Official CME documentation confirms EBS Ticker contains the required `Best Bid`, `Best Offer` and `Timestamp` fields in one-second time slices and includes XAU/USD SM. Manifest v1.5 therefore closes the executable field/aggregation design blocker by defining the 17:00 ET decision reference as the final valid two-sided EBS Ticker midquote in the last minute before trade-date roll.

Closed:

`CME_EBS_EOD_FIELD_MAPPING_NOT_PROVEN`

Remaining source-side blocker:

`CME_EBS_TICKER_DATA_ENTITLEMENT_NOT_PROVEN`

No production write is authorized until entitlement and the actual ingestion run are proven.
'''
stage4_path.write_text(stage4, encoding='utf-8')

print('GOLD_CONTROL_XAU_EOD_DECISION_REFERENCE_V1_5_APPLY_PASS')
