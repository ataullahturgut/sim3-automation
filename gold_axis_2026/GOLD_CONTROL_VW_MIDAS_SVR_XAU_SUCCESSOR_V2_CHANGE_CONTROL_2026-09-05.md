# Gold Control — VW-MIDAS-SVR XAU Successor V2 Change Control

**Freeze date:** 2026-09-05  
**Identity:** `VW_MIDAS_SVR_XAU_SUCCESSOR_V2`  
**Status:** `PRE_REGISTERED_SOURCE_DRIVEN_RESEARCH_SUCCESSOR_V2`  
**Authority:** subordinate to `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.32, current production Neon state, `GOLD_CONTROL_UNRESOLVED_ENGINE_SUCCESSOR_ROADMAP_2026-09-04.md`, the archived V1 change-control/status, and the source evidence produced before any V2 model score.

## 1. Why V2 exists

`VW_MIDAS_SVR_XAU_SUCCESSOR_V1` remains terminally `SOURCE_BLOCKED_NO_MODEL_SCORE`.

V1 froze a direct historical monthly GPR website locator and a `2020-03` source window. Exhaustive source audit on 2026-09-05, before any V2 model score, established:

- required V1 GPR origins: `2020-09` through `2026-08` = 72;
- the frozen direct website URLs `data_gpr_export_YYYYMM.xls` are no longer retrievable for the required set;
- the authors' official GitHub archive history contains 58/72 required `.xls` vintage identities;
- 54/72 have an official Git archive addition timestamp no later than the corresponding 17:00 ET month-end origin;
- the continuous PIT-proven official-Git window is `2022-03` through `2026-08` = 54 origins;
- `2021-10` through `2022-01` exist in the official Git history but were added on 2022-03-01 and therefore are not treated as origin-time PIT proof;
- `2020-09` through `2021-09` and `2022-02` have no required `.xls` identity in the audited official Git history.

Therefore V2 is a **new source contract and source-driven window**, frozen before model scoring. V1 is not rewritten, re-scored or re-labelled.

## 2. Identity and non-equivalence

Archived `VW_MIDAS_MSVR` remains blocked and unchanged.

V2 remains:

- XAU only;
- single-output RBF SVR, not MSVR;
- `H1_MONTHLY_PRICE_RESEARCH_EXPERT` only;
- not an exact reproduction of Wang et al. (2026);
- not a replacement for the archived production/runtime VW row;
- ineligible for selector, ensemble, direction vote or position mapping.

## 3. Source contract change from V1

V2 historical GPR authority is:

`iacoviel/iacoviel.github.io` official Git repository, directory `gpr_archive_files`, vintage identity `data_gpr_export_YYYYMM.xls`.

For an origin at the end of month `p`:

1. the required vintage is `data_gpr_export_p.xls`;
2. official Git history must contain that exact file identity;
3. its earliest official archive-add commit timestamp must be no later than the 17:00 America/New_York cutoff on the last calendar day of `p`;
4. the workbook must parse successfully;
5. GPR observation `p-1` must exist in that exact vintage;
6. causal normalization uses only rows in that same vintage dated no later than `p-1`;
7. current/final-vintage GPR may not substitute for a missing historical vintage.

The official Git commit timestamp is used only as a **proven availability floor for the official archive**. It is not relabelled as a newspaper publication timestamp or as the system's historical retrieval time.

Historical reconstruction keeps:

- `retrieved_at` = true current reconstruction time;
- `first_seen_at` = true current reconstruction time;
- `provider_as_of` / `available_as_of` = official Git archive commit floor when PIT-proven;
- evidence class = `HISTORICAL_REPLAY_RECONSTRUCTION`;
- a distinct vintage-specific lineage and payload hash.

## 4. Source-driven research window

Because the first continuous PIT-proven official-Git GPR origin is `2022-03`, V2 freezes the following **before scoring**:

Source/input construction window:

`2022-03` through `2026-08`.

The V1 feature construction needs six completed monthly return lags, so the first feature-complete candidate origin is:

`2022-09`.

Minimum fit sample remains unchanged at 24 completed target months. Therefore the first outer origin eligible for an SVR fit is:

`2024-09`.

Untouched validation window:

`2024-09` through `2025-08` (12 monthly origins).

Locked diagnostic replay:

`2025-09` through `2026-07`.

Current reconstruction target:

`2026-09` from the completed `2026-08-31` information boundary, only if all V2 source, target-lineage bridge, deterministic and validation gates pass. Any such September output produced after the origin is historical reconstruction, never prospective issuance.

These dates are a deterministic consequence of the newly proven source start, the unchanged six-month feature requirement and the unchanged minimum fit sample of 24. They were fixed before V2 model performance was observed.

## 5. Features, weighting and model — unchanged from V1

Frozen feature vector remains exactly:

1. `MR_lag1`
2. `MR_lag2`
3. `MR_lag3`
4. `MR_abs_lag1`
5. `MR_MA_3`
6. `MR_MA_6`
7. `MR_sign_lag1`
8. `VW_DAILY_RETURN`
9. `GPR_norm_lagged`
10. `month_sin`
11. `month_cos`

Dynamic decay remains:

`lambda_p = 0.1 * exp(-10 * GPR_norm_p)`

`w_i = exp(-lambda_p * a_i) / sum_j exp(-lambda_p * a_j)`

`VW_DAILY_RETURN_p = sum_i w_i * r_i`

Model remains:

`sklearn.svm.SVR(kernel='rbf')`

Hyperparameter grid remains exactly:

- `C ∈ {0.25, 1.0, 4.0}`
- `gamma ∈ {0.05, 0.20, 0.80}`
- `epsilon ∈ {0.01, 0.05, 0.10}`

Inner selection remains the last up-to-12 eligible expanding one-step origins using only past-known outcomes, with tie-break lower C, then lower gamma, then lower epsilon.

Minimum fit sample remains 24.

## 6. Target/input lineage bridge remains mandatory

Historical XAU research lineage remains:

`XAU_MONTHLY_AVG_NY17_HOURLY_RESEARCH_V1`.

It is not identical to production `XAU_EOD_TWELVE_NY17`.

V2 may not receive prospective-shadow authority unless the previously frozen materiality bridge passes without threshold relaxation:

- level correlation >= 0.995;
- median absolute level gap <= 50 bps;
- p95 absolute level gap <= 100 bps;
- monthly return correlation >= 0.95;
- monthly return sign agreement >= 0.80.

A failed bridge blocks prospective promotion even if historical V2 validation passes.

## 7. Benchmark and validation gates

Mandatory benchmark remains:

`RW = origin-month XAU_MONTHLY_AVG_NY17_HOURLY_RESEARCH_V1`.

On the untouched 12-origin validation window `2024-09..2025-08`, V2 can be labelled at most `HISTORICAL_REPLAY_SPECIALIZED_SHADOW_ELIGIBLE` only if:

1. source/PIT gate PASS for every required V2 origin and every input row used by the model;
2. deterministic rerun PASS;
3. prefix/future-invariance PASS;
4. `Relative_MAE_vs_RW < 1.00`;
5. candidate MAPE <= RW MAPE;
6. candidate median absolute error <= RW median absolute error;
7. monthly win rate vs RW >= 0.50;
8. candidate MAE <= 1.50 × RW MAE separately in both source-determined validation calendar buckets `2024-09..2024-12` and `2025-01..2025-08`;
9. no unresolved leakage/source/availability exception remains.

The diagnostic window `2025-09..2026-07` cannot rescue a failed validation gate.

## 8. Hard governance locks

Frozen before V2 scoring:

- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`
- `NOT_PROVEN_EXPERT_SELECTION_RULE`
- `NOT_PROVEN_POSITION_MAPPING`
- direction vote = false
- no BUY/SELL/HOLD/EXIT/REDUCE mapping
- no decision-store write
- no forecast-contract production write
- no backdated prospective claim
- no archived VW status change
- no post-score feature/source/grid/window/gate change
- no current-final-vintage GPR substitution
- no use of locked diagnostic results to tune V2.

## 9. Data-plane rule

Gold Data R2.7 / Neon remains the canonical data architecture. No new database architecture is introduced.

Historical official-Git GPR vintages must be represented through the existing data-plane semantics:

- `source_vintages` for immutable vintage payload identity/hash;
- `observations` for vintage-specific rows;
- truthful `provider_as_of`, `available_as_of`, `first_seen_at`, `retrieved_at`;
- vintage-specific `lineage_id`;
- `payload_hash`;
- quality/evidence metadata.

The feature-branch builder is dry-run/evidence-only. Production persistence is prohibited until this source contract and ingestion path receive canonical governance acceptance.

## 10. Stop states

If any of the 54 required V2 official-Git vintages fails parse, lacks `p-1`, violates the archive-commit cutoff, or changes the continuous source window, stop as:

`BLOCKED_GPR_V2_PIT_DATA_PLANE_NOT_READY`

If 54/54 source/PIT rows build but the XAU lineage/coverage bridge fails, stop as:

`BLOCKED_XAU_RESEARCH_TO_PRODUCTION_LINEAGE_BRIDGE_NOT_PROVEN`

If source/bridge pass but historical validation gates fail, stop as:

`REJECT_ALL_VW_SUCCESSOR_V2_CANDIDATES`

If historical validation passes, maximum status remains:

`HISTORICAL_REPLAY_SPECIALIZED_SHADOW_ELIGIBLE`

Prospective issuance still requires a separate prospective-shadow contract and genuinely future origins.
