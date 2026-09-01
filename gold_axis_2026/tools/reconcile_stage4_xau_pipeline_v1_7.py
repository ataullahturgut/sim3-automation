from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
manifest_path = ROOT / 'GOLD_CONTROL_PROJECT_MANIFEST.md'
stage4_path = ROOT / 'GOLD_CONTROL_STAGE4_STATUS_2026-09-01.md'
cc_path = ROOT / 'GOLD_CONTROL_XAU_EOD_SOURCE_CHANGE_CONTROL_2026-09-01.md'
contracts_path = ROOT / 'data_pipeline' / 'source_contracts.json'

RUN_ID = '33511805110'
JOB_ID = '99869043161'
OBS_RUN_ID = '12099dfa-a370-4710-aed5-d02388f652ac'
OBS_TS = '2026-08-31T21:00:00+00:00'

manifest = manifest_path.read_text(encoding='utf-8')
if '**Manifest version:** 1.6' not in manifest:
    raise SystemExit('EXPECTED_MANIFEST_V1_6_NOT_FOUND')
manifest = manifest.replace('**Manifest version:** 1.6', '**Manifest version:** 1.7', 1)

old = 'Status: `APPROVED_EXECUTABLE_CANONICAL_SOURCE_CONTRACT; PIPELINE_NOT_YET_PRODUCTION_SUCCESS`'
new = 'Status: `APPROVED_CANONICAL_PIPELINE_SUCCESS`'
if old not in manifest:
    raise SystemExit('XAU_STATUS_ANCHOR_NOT_FOUND')
manifest = manifest.replace(old, new, 1)

anchor = 'Access/mapping evidence: GitHub Actions run `33510985399`, job `99866288149`, `SUCCESS`, proved the protected Twelve credential can retrieve a valid `XAU/USD` `1min` bar at `16:59:00` with `America/New_York` timezone without logging raw prices or writing to the database.\n'
addition = anchor + f'''\nProduction-ingestion evidence: GitHub Actions run `{RUN_ID}`, job `{JOB_ID}`, `SUCCESS`, executed the frozen canonical writer against Neon. It selected completed trade date `2026-08-31`, stored observation timestamp `{OBS_TS}` (17:00 ET), source `Twelve Data`, quality status `APPROVED_CANONICAL_TWELVE_NY17`, retrieval run `{OBS_RUN_ID}`=`SUCCESS`, wrote one canonical observation, reported zero quality errors, and logged no raw market price.\n'''
if anchor not in manifest:
    raise SystemExit('ACCESS_EVIDENCE_ANCHOR_NOT_FOUND')
manifest = manifest.replace(anchor, addition, 1)

old_row = '| 4 | `IN_PROGRESS_BLOCKED_INPUT_CONTRACTS` | Deterministic engine/bridge tests PASS. Canonical XAU EOD decision reference is `XAU_EOD_TWELVE_NY17`: CME/EBS defines the 17:00 ET session boundary and Twelve Data supplies `XAU/USD` 1-minute data; access/mapping probe PASS. Active blockers are forecast contract, immutable forecast input snapshot, and successful canonical Twelve NY17 Neon ingestion |'
new_row = '| 4 | `IN_PROGRESS_BLOCKED_FORECAST_ISSUANCE` | Deterministic engine/bridge tests PASS. Canonical `XAU_EOD_TWELVE_NY17` access, mapping and Neon ingestion are PASS. Remaining blockers are the first genuine immutable H=1 forecast input snapshot and monthly forecast contract |'
if old_row not in manifest:
    raise SystemExit('ROADMAP_STAGE4_ANCHOR_NOT_FOUND')
manifest = manifest.replace(old_row, new_row, 1)

old_blockers = '''Confirmed active blockers after manifest v1.6 source revision:\n\n1. `FORECAST_CONTRACT_NOT_ISSUED`\n2. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`\n3. `TWELVE_XAU_NY17_PIPELINE_NOT_SUCCESS`\n'''
new_blockers = f'''Confirmed active blockers after manifest v1.7 XAU pipeline closure:\n\n1. `FORECAST_CONTRACT_NOT_ISSUED`\n2. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`\n\nClosed XAU pipeline blocker:\n\n`TWELVE_XAU_NY17_PIPELINE_NOT_SUCCESS` → `CLOSED_BY_RUN_{RUN_ID}`\n'''
if old_blockers not in manifest:
    raise SystemExit('ACTIVE_BLOCKERS_ANCHOR_NOT_FOUND')
manifest = manifest.replace(old_blockers, new_blockers, 1)

old_gates = '''Required next gates, in order:\n\n1. implement the canonical `XAU_EOD_TWELVE_NY17` writer using Twelve `XAU/USD` `1min`, `America/New_York`, exact `16:59:00` bar close and the frozen no-fallback quality gates;\n2. write the new lineage to Neon without overwriting or relabelling XAUS/LBMA/CME/futures history and obtain a successful scheduled daily run;\n3. create the first genuine immutable H=1 forecast input snapshot and monthly forecast contract from the executable frozen forecasting path before outcome realization;\n4. only then build/schedule the canonical R4.1 EOD issuer using the frozen engine and complete provenance;\n5. the first real forward state must begin as `PROSPECTIVE_SHADOW`; `LIVE_PRODUCTION` remains disabled until Stage 12 graduation;\n6. do not backfill historical rows and relabel them as prospective.\n'''
new_gates = '''Required next gates, in order:\n\n1. create the first genuine immutable H=1 forecast input snapshot from the executable frozen forecasting path using only data point-in-time available at the issuance origin;\n2. issue the matching monthly forecast contract binding target definition, executable Patch R1 point forecast, audited VW reference, RW benchmark, 3M direction context, model/code version, input snapshot id and issued-at timestamp;\n3. verify the new snapshot/contract rows in Neon before outcome realization;\n4. only then build/schedule the canonical R4.1 EOD issuer using the frozen engine and complete provenance;\n5. the first real forward decision state must begin as `PROSPECTIVE_SHADOW`; `LIVE_PRODUCTION` remains disabled until Stage 12 graduation;\n6. do not backfill historical rows and relabel them as prospective.\n'''
if old_gates not in manifest:
    raise SystemExit('NEXT_GATES_ANCHOR_NOT_FOUND')
manifest = manifest.replace(old_gates, new_gates, 1)
manifest_path.write_text(manifest, encoding='utf-8')

stage4 = stage4_path.read_text(encoding='utf-8')
stage4 = stage4.replace('**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.6', '**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.7', 1)
stage4 = stage4.replace('**Current status:** `IN_PROGRESS_BLOCKED_INPUT_CONTRACTS`', '**Current status:** `IN_PROGRESS_BLOCKED_FORECAST_ISSUANCE`', 1)
old_stage_block = '''## 5. Active readiness blockers\n\n1. `FORECAST_CONTRACT_NOT_ISSUED`\n2. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`\n3. `TWELVE_XAU_NY17_PIPELINE_NOT_SUCCESS`\n\nThe source-definition/access/mapping blocker is now closed. The remaining XAU task is implementation and a successful canonical Neon ingestion run.\n'''
new_stage_block = f'''## 5. Active readiness blockers\n\n1. `FORECAST_CONTRACT_NOT_ISSUED`\n2. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`\n\nClosed by canonical production-ingestion run `{RUN_ID}`, job `{JOB_ID}`:\n\n`TWELVE_XAU_NY17_PIPELINE_NOT_SUCCESS` → `CLOSED`\n\nThe run wrote one `XAU_EOD_TWELVE_NY17` observation for completed trade date `2026-08-31` at `{OBS_TS}`, with source `Twelve Data`, quality `APPROVED_CANONICAL_TWELVE_NY17`, retrieval status `SUCCESS`, zero quality errors and no raw market-price logging.\n'''
if old_stage_block not in stage4:
    raise SystemExit('STAGE4_BLOCKERS_ANCHOR_NOT_FOUND')
stage4 = stage4.replace(old_stage_block, new_stage_block, 1)
old_stage_next = '''## 6. Required next work\n\n1. implement the canonical `XAU_EOD_TWELVE_NY17` writer with exact 16:59 ET mapping and quality gates;\n2. create the explicit Twelve NY17 series/provider lineage in Neon and obtain a successful daily run;\n3. issue the first genuine immutable H=1 forecast input snapshot and monthly forecast contract before outcome realization;\n4. build/schedule the canonical R4.1 EOD issuer only after those inputs pass;\n5. first forward Decision Store state = `PROSPECTIVE_SHADOW`, never retroactive and not `LIVE_PRODUCTION`.\n'''
new_stage_next = '''## 6. Required next work\n\n1. inspect the live Neon forecast-state table contract and executable Patch R1 issuance path;\n2. create the first genuine immutable H=1 forecast input snapshot using point-in-time available inputs only;\n3. issue the matching monthly forecast contract before target outcome realization and verify both rows in Neon;\n4. build/schedule the canonical R4.1 EOD issuer only after those inputs pass;\n5. first forward Decision Store state = `PROSPECTIVE_SHADOW`, never retroactive and not `LIVE_PRODUCTION`.\n'''
if old_stage_next not in stage4:
    raise SystemExit('STAGE4_NEXT_ANCHOR_NOT_FOUND')
stage4 = stage4.replace(old_stage_next, new_stage_next, 1)
stage4_path.write_text(stage4, encoding='utf-8')

contracts = json.loads(contracts_path.read_text(encoding='utf-8'))
contracts['version'] = 'GOLD_DATA_R2_2026-09-01_XAU_NY17_PIPELINE_V3'
spec = contracts['series']['XAU_EOD_TWELVE_NY17']
if 'PIPELINE_NOT_YET_PRODUCTION_SUCCESS' not in spec.get('status', ''):
    raise SystemExit('CONTRACT_PIPELINE_STATUS_ANCHOR_NOT_FOUND')
spec['status'] = 'APPROVED_CANONICAL_PIPELINE_SUCCESS'
spec['production_ingestion_evidence'] = {
    'workflow_run_id': int(RUN_ID),
    'job_id': int(JOB_ID),
    'retrieval_run_id': OBS_RUN_ID,
    'trade_date': '2026-08-31',
    'observation_ts': OBS_TS,
    'observations_written': 1,
    'quality_errors': 0,
    'result': 'SUCCESS',
    'raw_market_values_logged': False,
}
contracts_path.write_text(json.dumps(contracts, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

cc = cc_path.read_text(encoding='utf-8')
appendix = f'''\n\n---\n\n# Manifest v1.7 canonical ingestion closure\n\nGitHub Actions run `{RUN_ID}`, job `{JOB_ID}`, completed `SUCCESS` on the active v1.6 source contract. The run persisted and verified one canonical `XAU_EOD_TWELVE_NY17` observation for trade date `2026-08-31` with observation timestamp `{OBS_TS}` (17:00 ET), Twelve Data lineage, quality `APPROVED_CANONICAL_TWELVE_NY17`, retrieval run `{OBS_RUN_ID}`=`SUCCESS`, zero quality errors and no raw-price logging.\n\nDecision:\n\n`TWELVE_XAU_NY17_PIPELINE_NOT_SUCCESS` → `CLOSED_BY_MANIFEST_V1_7`\n\nThe XAU EOD input source is no longer a Stage-4 readiness blocker. Remaining Stage-4 blockers are forecast issuance only: `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED` and `FORECAST_CONTRACT_NOT_ISSUED`.\n'''
if '# Manifest v1.7 canonical ingestion closure' not in cc:
    cc += appendix
cc_path.write_text(cc, encoding='utf-8')

print('GOLD_CONTROL_STAGE4_XAU_PIPELINE_RECONCILE_V1_7_PASS')
