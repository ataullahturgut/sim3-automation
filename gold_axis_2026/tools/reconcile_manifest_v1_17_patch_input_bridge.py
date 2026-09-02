from pathlib import Path
import re

P = Path(__file__).resolve().parents[1] / "GOLD_CONTROL_PROJECT_MANIFEST.md"
s = P.read_text(encoding="utf-8")

if "**Manifest version:** 1.16" not in s:
    raise SystemExit("EXPECTED_MANIFEST_V1_16_NOT_FOUND")
if "IN_PROGRESS_PATCH_R1_REPRODUCIBILITY" not in s:
    raise SystemExit("EXPECTED_V116_STAGE4B_STATUS_NOT_FOUND")

s = s.replace("**Manifest version:** 1.16", "**Manifest version:** 1.17", 1)

s = s.replace(
    "| 4B | `IN_PROGRESS_PATCH_R1_REPRODUCIBILITY` | Broad R2 model-search lane retired; Causal Patch reproducibility contract frozen before locked score; VW remains audited reference; forecast snapshot/contract not issued |",
    "| 4B | `BLOCKED_PATCH_PROSPECTIVE_INPUT_SEMANTICS_NOT_PROVEN` | `CAUSAL_PATCH_R1_REPRO_V1` locked historical replay PASS and deterministic; prospective input bridge V1 FAIL/NOT_PROVEN; VW remains audited reference; forecast snapshot/contract not issued |",
    1,
)

new24 = r'''# 24. IMMEDIATE NEXT WORK

The immediate canonical task is now:

## `STAGE 4B — RESOLVE CAUSAL_PATCH_R1 PROSPECTIVE INPUT SEMANTICS ONLY; DO NOT REOPEN MODEL SEARCH`

Completed and frozen:

1. `CAUSAL_PATCH_R1_REPRO_V1` geometry was selected only on pre-2023 development data: `L=252`, `P=21`, `D=32`;
2. locked `2023-01→2026-07`, `N=43` replay was run twice with deterministic max absolute difference `0`;
3. Patch historical replay MAPE `3.108253722%` and MAE `101.660660440`, versus RW MAPE `3.302322023%` and MAE `107.465116279`;
4. historical-replay decision: `PATCH_R1_REPRO_V1_HISTORICAL_REPLAY_ELIGIBLE`;
5. new executable identity is frozen separately from the archived Patch artifact; archived exact executable identity remains not proven.

Prospective input bridge V1 evidence:

- contract: `GOLD_CONTROL_CAUSAL_PATCH_R1_PROSPECTIVE_INPUT_BRIDGE_CONTRACT_V1.md`;
- workflow run `33602829565`, successful fail-closed attempt job `100161187043`;
- evidence commit `1a27dca699b6aa4c3c421156eafda6656d6061c4`;
- overall decision: `BLOCKED_PATCH_PROSPECTIVE_INPUT_SEMANTICS_NOT_PROVEN`;
- DFF→FEDFUNDS: `43/43`, PASS;
- DEXCHUS→USDCNY: `43/43`, PASS;
- NASDAQCOM→NASDAQ monthly mean: `40/43`, three origin months not reconstructable from the frozen month-end ALFRED snapshot (`2023-10`, `2023-11`, `2023-12`), therefore hard gate FAIL despite materiality PASS on available months;
- Twelve London-hour metal proxy V1: overall FAIL/NOT_PROVEN; Gold had only `29` common observations and also failed return-correlation/gap gates; Silver/Platinum/Palladium ended `HTTP_RETRY_EXHAUSTED` and are not treated as semantic passes;
- raw vendor values logged: NO;
- database writes: NONE;
- forecast-ledger writes: NONE;
- Decision Store writes: NONE.

Required next sequence:

1. keep Patch architecture, frozen geometry and VW/3M/RW roles unchanged;
2. open a **versioned input-only V2 contract** before any new result is inspected;
3. fix only the failed macro availability semantic and daily-metal continuation semantic; do not relax V1 thresholds after seeing V1 results;
4. for any changed input construction, rerun the same locked Patch replay with geometry unchanged and issue a new explicit executable/input identity rather than silently overwriting V1;
5. only after the prospective input bridge passes, validate the generic monthly-reference → Emergency geometry bridge; never silently insert Patch into historical R4.1 `monthly_vw_forecast` identity;
6. before a real eligible month-end origin, persist immutable forecast input snapshot + forecast contract;
7. first forward evidence remains `PROSPECTIVE_SHADOW`; September 2026 may not be backdated.

Stage 5 remains closed as `PASS_PIYASA_SCREEN_CONTRACT`. Stage 6 remains blocked until a display-eligible stored Decision Store state exists. October 2026 at the end-September origin remains only a possible next prospective target if every Stage-4B gate closes before that origin.

Stage 3 is closed as:'''

s, n = re.subn(r'# 24\. IMMEDIATE NEXT WORK.*?Stage 3 is closed as:', new24, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit("IMMEDIATE_NEXT_REPLACE_FAILED")

new_blockers = r'''Confirmed active Stage-4B blockers after manifest v1.17 input-bridge audit:

1. `BLOCKED_PATCH_PROSPECTIVE_INPUT_SEMANTICS_NOT_PROVEN`
   - Patch historical replay is valid, but the exact prospective input continuation is not yet proven under the frozen V1 bridge;
2. `NASDAQCOM_MONTH_END_PIT_CONTINUATION_NOT_COMPLETE`
   - DFF and DEXCHUS monthly constructions passed 43/43, while NASDAQCOM had 3 missing month-end PIT reconstructions; no silent current-vintage fill is allowed;
3. `PATCH_DAILY_METALS_OPERATIONAL_CONTINUATION_NOT_PROVEN`
   - the frozen StakTrakr/LBMA historical artifact is not extended or relabelled; Twelve London-hour V1 did not pass the frozen compatibility/coverage gates;
4. `PATCH_R1_ARCHIVED_EXECUTABLE_IDENTITY_NOT_PROVEN`
   - the old archived Patch artifact remains historical evidence; the new reproducible implementation uses its own identity;
5. `VW_EXECUTABLE_IDENTITY_RECOVERY = BLOCKED_NOT_PROVEN`
   - VW remains audited shadow/reference;
6. `R4_2_MONTHLY_REFERENCE_BRIDGE_NOT_VALIDATED`;
7. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`;
8. `FORECAST_CONTRACT_NOT_ISSUED`.

Closed Stage-4B sub-gate:

- `PATCH_R1_REPRODUCIBLE_PRODUCTION_IMPLEMENTATION_NOT_YET_VALIDATED` → **closed for HISTORICAL_REPLAY only** by run `33600343405`, job `100152429384`; deterministic replay PASS, Patch beat RW on MAPE and MAE. This does not constitute a prospective issuer approval.

Useful data readiness retained from 2026-09-01:'''

s, n = re.subn(
    r'Confirmed active Stage-4B blockers after manifest v1\.16 path correction:.*?Useful data readiness retained from 2026-09-01:',
    new_blockers,
    s,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit("BLOCKERS_REPLACE_FAILED")

new_lane = r'''**Stage-4B H=1 forecast lane (fail-closed for prospective issuance):**

1. `CAUSAL_PATCH_R1_REPRO_V1` historical-replay validation is complete and may not be retuned on the locked 43-month window;
2. do not add Ridge/Huber/SVR/DOW/DMA/new Transformer variants or other model families to the production path merely because the prospective input bridge is difficult;
3. keep `VW_AUDITED_SHADOW_V2` as audited reference, `MOMENTUM_3M_R1` as direction context, and `RW_R1` as benchmark;
4. resolve only the failed prospective input semantics under a new versioned contract frozen before results;
5. any changed input construction must receive a new explicit Patch executable/input identity and rerun the same locked replay with geometry unchanged;
6. after the input bridge passes, validate the generic monthly-price-reference/Emergency bridge before building a complete EngineSnapshot;
7. before a real eligible month-end origin, persist immutable forecast input snapshot + forecast contract;
8. first forward forecast/decision evidence remains `PROSPECTIVE_SHADOW`, never retroactive and not `LIVE_PRODUCTION`.

No `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` **decision** row may be written while an active Stage-4B blocker prevents construction of the complete versioned EngineSnapshot. This does not block non-decision `Piyasa` monitoring.'''

s, n = re.subn(
    r'\*\*Stage-4B H=1 forecast lane \(fail-closed for prospective issuance\):\*\*.*?No `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` \*\*decision\*\* row may be written while an active Stage-4B blocker prevents construction of the complete versioned EngineSnapshot\. This does not block non-decision `Piyasa` monitoring\.',
    new_lane,
    s,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit("STAGE4B_LANE_REPLACE_FAILED")

marker = "### Manifest v1.16 forecast-path correction and retained data evidence"
if marker not in s:
    raise SystemExit("V116_MARKER_NOT_FOUND")
new_evidence = r'''### Manifest v1.17 Patch reproducibility and prospective-input evidence

New frozen evidence on 2026-09-02:

- Patch pre-2023 geometry selection run `33600168927`, job `100151896585`, SUCCESS: `L=252`, `P=21`, `D=32`; locked score window not used for selection;
- Patch locked replay run `33600343405`, job `100152429384`, SUCCESS: target reconciliation `43/43`, RW reconciliation `43/43`, deterministic max absolute difference `0`, Patch MAPE `3.108253722%`, RW MAPE `3.302322023%`, Patch MAE `101.660660440`, RW MAE `107.465116279`;
- historical-replay status: `PATCH_R1_REPRO_V1_HISTORICAL_REPLAY_ELIGIBLE`; forecast/decision writes NONE;
- prospective-input bridge V1 contract frozen before audit: `GOLD_CONTROL_CAUSAL_PATCH_R1_PROSPECTIVE_INPUT_BRIDGE_CONTRACT_V1.md`;
- bridge run `33602829565`, successful fail-closed attempt job `100161187043`, evidence commit `1a27dca699b6aa4c3c421156eafda6656d6061c4`;
- DFF→FEDFUNDS PASS `43/43`; DEXCHUS→USDCNY PASS `43/43`;
- NASDAQCOM hard gate FAIL `40/43` because origin months `2023-10`, `2023-11`, `2023-12` returned no valid month-end ALFRED reconstruction; available-month materiality was within the frozen threshold;
- metal continuation V1 overall FAIL/NOT_PROVEN: Gold coverage `29`, return correlation `0.776370092`, median return gap `83.777600 bps`, p95 `466.614818 bps`; Silver/Platinum/Palladium ended `HTTP_RETRY_EXHAUSTED` and are not semantic passes;
- overall bridge decision: `BLOCKED_PATCH_PROSPECTIVE_INPUT_SEMANTICS_NOT_PROVEN`;
- raw vendor values logged NO; DB, forecast-ledger and Decision Store writes NONE.

This evidence does **not** reopen model search and does **not** permit post-result threshold relaxation. The next work is versioned input-semantic correction only.

'''
s = s.replace(marker, new_evidence + marker, 1)

for required in [
    "**Manifest version:** 1.17",
    "BLOCKED_PATCH_PROSPECTIVE_INPUT_SEMANTICS_NOT_PROVEN",
    "33600343405",
    "33602829565",
    "1a27dca699b6aa4c3c421156eafda6656d6061c4",
    "NASDAQCOM_MONTH_END_PIT_CONTINUATION_NOT_COMPLETE",
    "PATCH_DAILY_METALS_OPERATIONAL_CONTINUATION_NOT_PROVEN",
    "RESOLVE CAUSAL_PATCH_R1 PROSPECTIVE INPUT SEMANTICS ONLY",
]:
    if required not in s:
        raise SystemExit(f"REQUIRED_V117_TEXT_MISSING:{required}")

# Stale status must be gone from active roadmap.
if "| 4B | `IN_PROGRESS_PATCH_R1_REPRODUCIBILITY`" in s:
    raise SystemExit("STALE_V116_STAGE4B_STATUS_REMAINS")

P.write_text(s, encoding="utf-8")
print("MANIFEST_V1_17_PATCH_INPUT_BRIDGE_RECONCILE_PASS")
