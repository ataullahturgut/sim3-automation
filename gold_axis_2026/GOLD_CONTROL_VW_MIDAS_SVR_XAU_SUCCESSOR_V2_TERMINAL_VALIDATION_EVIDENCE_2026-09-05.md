# Gold Control — VW-MIDAS-SVR XAU Successor V2 Terminal Validation Evidence

**Evidence date:** 2026-09-05  
**Identity:** `VW_MIDAS_SVR_XAU_SUCCESSOR_V2`  
**Binding terminal result:** `REJECT_ALL_VW_SUCCESSOR_V2_CANDIDATES`  
**Validation workflow:** `Gold Control VW MIDAS SVR XAU Successor V2 Validation`  
**Workflow run:** `33967027740`  
**Tested commit:** `561b488f766fa836dd50e26497c004dac16a2195`

## 1. Pre-score source and eligibility gates

The dedicated source preflight completed SUCCESS before the V2 model score:

- workflow run `33966777073`;
- XAU hourly research source months = `54/54` (`2022-03..2026-08`);
- minimum valid daily research references in any required month = `15`;
- GPR historical PIT origins = `54/54` (`GPR_OFFICIAL_GIT_PIT`);
- model scoring during source preflight = `NO`;
- database writes during source preflight = `NONE`.

A deterministic contract-consistency correction was frozen before scoring:

- first feature-complete origin = `2022-09`;
- `2024-09` has 24 prior model rows but no eligible inner origin with 24 prior fit rows;
- first fully tunable outer origin = `2024-10`;
- untouched validation origins = `2024-10..2025-09` = 12;
- locked diagnostic origins = `2025-10..2026-07`.

No feature, source identity, SVR grid, minimum-fit rule, benchmark, or validation threshold was changed.

## 2. Determinism and leakage controls

Validation execution reported:

- deterministic rerun = `PASS`;
- prefix/future invariance = `PASS`;
- source gate = `PASS`;
- raw vendor market values logged = `NO`;
- database writes = `NONE`;
- production authority = `FALSE`;
- prospective claim = `FALSE`.

## 3. Untouched validation result

Validation origins:

`2024-10..2025-09` (12 origins)

Corresponding targets:

`2024-11..2025-10`

Candidate versus mandatory Random-Walk benchmark:

| Metric | VW V2 | RW | Gate consequence |
|---|---:|---:|---|
| MAE | 107.907463 | 125.475645 | candidate better |
| MAPE | 3.260387% | 3.706419% | PASS |
| Median absolute error | 75.061714 | 67.491510 | **FAIL** |
| Relative MAE vs RW | 0.859987 | 1.000000 | PASS (`<1`) |
| Monthly win rate vs RW | 0.583333 | — | PASS (`>=0.50`) |
| Directional accuracy | 0.666667 | — | diagnostic |

Source-determined validation bucket MAE ratios versus RW:

- `2024-10..2024-12` = **1.631148** -> **FAIL** (`>1.50`);
- `2025-01..2025-09` = `0.791347` -> PASS.

Therefore two frozen validation gates fail:

1. `median_ae_not_worse_than_rw`;
2. `all_origin_bucket_mae_ratios_lte_1_5`.

The fact that aggregate MAE/MAPE and monthly win rate are better than RW does not override these preregistered failure conditions.

## 4. Locked diagnostic result

Locked diagnostic origins:

`2025-10..2026-07` (10 origins)

Diagnostic-only Relative MAE vs RW:

`1.044906`

Diagnostic MAE:

- VW V2 = `233.627181`;
- RW = `223.586782`.

Diagnostic MAPE:

- VW V2 = `5.163342%`;
- RW = `4.938043%`.

The locked diagnostic is worse than RW and, under the frozen contract, could not rescue a failed validation result in any event.

## 5. XAU production-lineage bridge status

The V2 exact-1m entitlement probe (run `33967189721`) was source-only and computed no model score or bridge metric.

Frozen probe dates:

- `2024-12-16`: exact `16:59` 1-minute bar not returned;
- `2025-06-16`: PASS;
- `2026-08-28`: PASS.

Probe result:

`BLOCKED_HISTORICAL_EXACT_1MIN_BRIDGE_SOURCE_NOT_PROVEN`

A separate source-driven 12-month bridge execution window (`2025-07..2026-06`) was frozen before its bridge metrics. Its outcome cannot change the V2 rejection because the untouched validation gate has already failed.

## 6. Binding disposition

V2 must stop as:

`REJECT_ALL_VW_SUCCESSOR_V2_CANDIDATES`

Consequences:

- no September 2026 V2 reconstruction is issued;
- no V2 prospective/shadow promotion;
- no selector or ensemble entry;
- no production forecast-contract write;
- no Decision Store write;
- no archived `VW_MIDAS_MSVR` status change;
- no post-result feature/grid/window/gate retuning.

`VW_MIDAS_SVR_XAU_SUCCESSOR_V1` remains `SOURCE_BLOCKED_NO_MODEL_SCORE`.

Archived `VW_MIDAS_MSVR` remains `BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN`.

The successfully governed `GPR_OFFICIAL_GIT_PIT` data plane remains valid independently of this model rejection and may be reused only by separately pre-registered future research identities.
