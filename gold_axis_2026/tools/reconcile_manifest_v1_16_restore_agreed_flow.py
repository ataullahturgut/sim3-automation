from pathlib import Path
import re

P = Path(__file__).resolve().parents[1] / "GOLD_CONTROL_PROJECT_MANIFEST.md"
s = P.read_text(encoding="utf-8")

if "**Manifest version:** 1.15" not in s:
    raise SystemExit("EXPECTED_MANIFEST_V1_15_NOT_FOUND")
if "GOLD_CONTROL_H1_SUCCESSOR_VALIDATION_CONTRACT_R2.md" not in s:
    raise SystemExit("EXPECTED_R2_ACTIVE_REFERENCE_NOT_FOUND")

s = s.replace("**Manifest version:** 1.15", "**Manifest version:** 1.16", 1)
s = s.replace("**Freeze / issue date:** 2026-09-01", "**Freeze / issue date:** 2026-09-02", 1)

new7 = r'''# 7. H=1 FORECAST CONTRACT

Canonical target:

> **Next calendar month's average XAU/USD price**

Historical outcome/data-plane support:

- the locked CORE5 monthly gold target remains the canonical historical H=1 research target artifact;
- `XAU_MONTHLY_WB_PINKSHEET` is retained as a separately named World Bank historical data-plane lineage because the 127-month identity audit showed material equivalence to CORE5; it is not relabelled as CORE5 and does not redefine the forecast product;
- `XAU_EOD_TWELVE_NY17` remains the daily R4 decision-reference lineage; monthly forecast target and daily decision reference are intentionally different roles.

Canonical origin:

> **End of the previous completed calendar month**

Validation rules:

- random split forbidden,
- future target information forbidden,
- tuning only on past rolling/expanding origins,
- publication lag mandatory,
- vintage safety mandatory,
- benchmark comparison at the same horizon mandatory.

Common audited evaluation window:

`2023-01 → 2026-07`, `N=43`

Current archived/audited scorecard evidence:

| Model | MAPE % | Role / interpretation |
|---|---:|---|
| VW-MIDAS-MSVR audited | ~2.672 | audited analytical shadow/reference; exact original runner not recovered |
| Causal Patch R1 archived | ~3.03–3.08 depending exact closure artifact | historical Patch evidence; exact old training source/identity not fully recovered |
| 3M Momentum R1 | ~3.297 | reproducible direction challenger/context |
| Random Walk R1 | ~3.302 | mandatory naive benchmark |

## 7.1 H=1 role freeze — restored agreed architecture

The active H=1 development path is **not a broad model search**.

Frozen roles:

- **Intended production point-forecast path:** `CAUSAL_PATCH_R1_REPRO_V1` — a new deterministic, causal, reproducible implementation of the retained Patch architecture. It is not yet production-approved and may not claim exact archived executable identity unless separately proven;
- **Audited shadow/reference:** `VW_AUDITED_SHADOW_V2` — historical analytical reference; exact original executable runner remains `BLOCKED_NOT_PROVEN`;
- **Direction challenger/context:** `MOMENTUM_3M_R1`;
- **Mandatory naive benchmark:** `RW_R1`;
- **Auto selector:** `OFF`;
- **Auto ensemble primary:** `OFF`.

The simple monthly Ridge/Huber/SVR/Drift/Damped R2 successor lane introduced on 2026-09-01 is retired from the active production-development path. Its prior run remains recoverable in Git history as a negative historical experiment; it is not the next canonical model lane.

Binding correction record:

`gold_axis_2026/GOLD_CONTROL_FORECAST_PATH_CORRECTION_2026-09-02.md`

Active reproducibility contract:

`gold_axis_2026/GOLD_CONTROL_CAUSAL_PATCH_R1_REPRO_CONTRACT_V1.md`

The earlier successor R1/change-control documents are retained only as audit evidence of the failed exact legacy identity-recovery attempt. They do not override this v1.16 role freeze.

## 7.2 Current forecast-ledger state'''

s, n = re.subn(r'# 7\. H=1 FORECAST CONTRACT.*?## 7\.2 Current forecast-ledger state', new7, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit("SECTION7_REPLACE_FAILED")

new231 = r'''## 23.1 Current roadmap status — 2026-09-02

| Stage | Current status | Evidence / blocker |
|---|---|---|
| 0 | `PASS` | Manifest read-first contract active |
| 1 | `PASS_AUDIT_COMPLETE_WITH_OPERATIONAL_BLOCKERS` | Data inventory/lineage audited; useful 2026-09-01 historical/PIT backfill retained |
| 2 | `PASS_CONTRACT_CANONICALIZED; FORECAST_NOT_ISSUED` | H=1 target/origin and restored Patch/VW/3M/RW role registry frozen; no prospective H=1 row exists |
| 3 | `PASS_DECISION_STORE_AND_READ_PATH` | Production append-only store/read path active; no fabricated current decision |
| 4A | `PASS_CURRENT_STATE_SUBSTRATE_FOR_SHADOW_CONTEXT` | NY17 backfill SUCCESS; monthly direction bootstrap issued; Fast/Slow rehearsal SUCCESS; forecast-state append-only guards 3/3 |
| 4B | `IN_PROGRESS_PATCH_R1_REPRODUCIBILITY` | Broad R2 model-search lane retired; Causal Patch reproducibility contract frozen before locked score; VW remains audited reference; forecast snapshot/contract not issued |
| 5 | `PASS_PIYASA_SCREEN_CONTRACT` | Canonical Piyasa implementation + deterministic/live Streamlit smoke PASS |
| 6 | `BLOCKED_NO_DISPLAY_ELIGIBLE_DECISION_SNAPSHOT` | No complete forward stored decision row may be fabricated |
| 7 | `BLOCKED_FORECAST_NOT_ISSUED` | Canonical H=1 forecast ledger has no issued row |
| 8–12 | `NOT_STARTED / NOT_COMPLETE` | Their own dependency gates are not satisfied |

The architecture remains the agreed six-layer system: data plane → H=1 forecast/monthly context → Fast/Slow tactical → BOCPD break → Emergency → GVZ risk/Decision State. The R2 detour did not alter those layers.

---

# 24. IMMEDIATE NEXT WORK'''

s, n = re.subn(r'## 23\.1 Current roadmap status — 2026-09-01.*?---\n\n# 24\. IMMEDIATE NEXT WORK', new231, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit("ROADMAP_STATUS_REPLACE_FAILED")

new24 = r'''# 24. IMMEDIATE NEXT WORK

The immediate canonical task is now:

## `STAGE 4B — BUILD AND VALIDATE CAUSAL_PATCH_R1_REPRO_V1; KEEP VW AS AUDITED REFERENCE; DO NOT REOPEN A BROAD MODEL SEARCH`

Required sequence:

1. use the locked CORE5 monthly artifact and the exact pinned daily precious-metals source commit;
2. apply the conservative origin-safe GPR lag and causal daily decomposition rules frozen in `GOLD_CONTROL_CAUSAL_PATCH_R1_REPRO_CONTRACT_V1.md`;
3. select Patch geometry only on pre-2023 development data;
4. run the locked 43-month `2023-01→2026-07` replay twice and prove deterministic equality;
5. compare the candidate with RW on the same 43 months and report archived Patch/VW only as references;
6. if the Patch reproducibility/performance gates pass, freeze its new executable identity before any future issuance;
7. if it fails, keep work inside the Patch reproducibility problem unless a new explicit change-control authorizes a different model family;
8. before the first eligible future origin, write immutable forecast input snapshot + forecast contract; no September backdating.

Stage 5 remains closed as `PASS_PIYASA_SCREEN_CONTRACT`. Stage 6 remains blocked until a display-eligible stored Decision Store state exists. The first still-eligible contract-compliant prospective H=1 target remains October 2026 at the end-September origin, subject to completion of Stage 4B.

Stage 3 is closed as:'''

s, n = re.subn(r'# 24\. IMMEDIATE NEXT WORK.*?Stage 3 is closed as:', new24, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit("IMMEDIATE_NEXT_REPLACE_FAILED")

newblock = r'''Confirmed active Stage-4B blockers after manifest v1.16 path correction:

1. `PATCH_R1_REPRODUCIBLE_PRODUCTION_IMPLEMENTATION_NOT_YET_VALIDATED`
   - the agreed primary architecture is restored, but the new deterministic causal implementation has not yet passed its locked replay gates;
2. `PATCH_R1_ARCHIVED_EXECUTABLE_IDENTITY_NOT_PROVEN`
   - the old archived Patch artifact remains historical evidence; the new reproducible implementation must use a new explicit identity unless exact equivalence is proven;
3. `VW_EXECUTABLE_IDENTITY_RECOVERY = BLOCKED_NOT_PROVEN`
   - VW remains audited shadow/reference and does not need to be silently reconstructed or substituted into a new executable identity;
4. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`;
5. `FORECAST_CONTRACT_NOT_ISSUED`.

Useful data readiness retained from 2026-09-01:

- CORE5 ↔ World Bank target identity audit PASS over 127/127 months;
- governed Neon historical/PIT backfill wrote 639 source-labelled observations and did not create a forecast contract;
- ALFRED DGS10/DFF/DEXCHUS/NASDAQ100 PIT reconstructions remain data-plane assets, but they do not force those variables into the Patch model beyond the frozen Patch contract.

Retired-model-path note:

- the simple R2 Ridge/Huber/SVR/Drift/Damped replay is no longer an active production-development lane;
- its Git history is retained for audit, but active R2 contract/runner/score artifacts were removed from the canonical tree on 2026-09-02.

Legacy executable-identity audit evidence remains valid: the old VW/Patch exact executable identities were not recovered. This is a provenance fact, not a mandate to abandon the agreed Patch/VW role architecture.

Closed current-state/context gates:'''

s, n = re.subn(r'Confirmed active Stage-4B successor blockers after manifest v1\.14 change-control:.*?Closed current-state/context gates:', newblock, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit("BLOCKERS_REPLACE_FAILED")

newlane = r'''**Stage-4B H=1 forecast lane (fail-closed for prospective issuance):**

1. execute `GOLD_CONTROL_CAUSAL_PATCH_R1_REPRO_CONTRACT_V1.md`;
2. do not add Ridge/Huber/SVR/DOW/DMA/Transformer variants or other model families to the production path merely because they are available or interesting;
3. keep `VW_AUDITED_SHADOW_V2` as audited reference, `MOMENTUM_3M_R1` as direction context, and `RW_R1` as benchmark;
4. if `CAUSAL_PATCH_R1_REPRO_V1` passes its frozen replay gates, freeze its executable version and input contract;
5. revalidate the monthly-reference/Emergency bridge before inserting a new executable forecast into the complete EngineSnapshot;
6. before a real eligible month-end origin, persist immutable forecast input snapshot + forecast contract;
7. first forward forecast/decision evidence remains `PROSPECTIVE_SHADOW`, never retroactive and not `LIVE_PRODUCTION`.

No `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` **decision** row may be written while an active Stage-4B blocker prevents construction of the complete versioned EngineSnapshot. This does not block non-decision `Piyasa` monitoring.'''

s, n = re.subn(r'\*\*Stage-4B successor lane \(continues fail-closed for prospective issuance\):\*\*.*?No `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` \*\*decision\*\* row may be written while an active Stage-4B successor blocker prevents construction of the complete versioned EngineSnapshot\. This does not block non-decision `Piyasa` monitoring\.', newlane, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit("STAGE4B_LANE_REPLACE_FAILED")

newv = r'''### Manifest v1.16 forecast-path correction and retained data evidence

The approved architecture was restored on 2026-09-02 after the simple R2 successor model-search detour was identified as inconsistent with the previously agreed H=1 role freeze.

Preserved evidence:

- CORE5 ↔ World Bank monthly target identity audit: run `33535312896`, job `99948062874`, `SUCCESS`; 127/127 common months, 123/127 exact, all within USD 0.50;
- governed Neon historical/PIT backfill: run `33538748716`, job `99959440836`, `SUCCESS`; 639/639 observations written, revisions 0, no forecast issuance;
- forecast-state counts after the write remained `forecast_input_snapshots=0`, `derived_feature_snapshots=1`, `monthly_forecast_contracts=0`;
- Decision Store, NY17, Fast/Slow, BOCPD, Emergency, GVZ and Piyasa contracts remain unchanged.

Rolled back from active path:

- R2 validation contract;
- R2 replay runner/workflow;
- active R2 score/prediction/evidence files;
- manifest instruction to continue Ridge/Huber/SVR/Drift/Damped as the next canonical forecast lane.

Binding replacement:

- `GOLD_CONTROL_FORECAST_PATH_CORRECTION_2026-09-02.md`;
- `GOLD_CONTROL_CAUSAL_PATCH_R1_REPRO_CONTRACT_V1.md`.

### Manifest v1.8 forecast/monthly-context dependency audit'''

s, n = re.subn(r'### Manifest v1\.15 successor target/input reconciliation.*?### Manifest v1\.8 forecast/monthly-context dependency audit', newv, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit("V115_EVIDENCE_REPLACE_FAILED")

for bad in [
    "GOLD_CONTROL_H1_SUCCESSOR_VALIDATION_CONTRACT_R2.md",
    "RUN THE FROZEN SUCCESSOR R2 HISTORICAL REPLAY",
    "IN_PROGRESS_SUCCESSOR_R2_HISTORICAL_REPLAY_AUTHORIZED",
    "GOLD_H1_SUCCESSOR_R2_NOT_VALIDATED",
]:
    if bad in s:
        raise SystemExit(f"STALE_ACTIVE_R2_REFERENCE:{bad}")

for required in [
    "**Manifest version:** 1.16",
    "CAUSAL_PATCH_R1_REPRO_V1",
    "VW_AUDITED_SHADOW_V2",
    "**Auto selector:** `OFF`",
    "GOLD_CONTROL_FORECAST_PATH_CORRECTION_2026-09-02.md",
    "GOLD_CONTROL_CAUSAL_PATCH_R1_REPRO_CONTRACT_V1.md",
    "IN_PROGRESS_PATCH_R1_REPRODUCIBILITY",
]:
    if required not in s:
        raise SystemExit(f"REQUIRED_V116_TEXT_MISSING:{required}")

P.write_text(s, encoding="utf-8")
print("MANIFEST_V1_16_RESTORE_AGREED_FLOW_PASS")
