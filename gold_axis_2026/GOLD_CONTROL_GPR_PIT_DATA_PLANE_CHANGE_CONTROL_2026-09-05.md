# Gold Control — GPR PIT Data Plane Change Control

**Freeze date:** 2026-09-05  
**Change identity:** `GPR_PIT_DATA_PLANE_V2`  
**Status before canonical merge:** `PRE_REGISTERED_SOURCE_INGESTION_CHANGE`  
**Required manifest authority:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.33 or later explicitly containing token `MANIFEST_V1_33_GPR_PIT_DATA_PLANE`.

## 1. Purpose

Populate the existing Gold Data R2.7 / production Neon data plane with a separate, audit-safe historical GPR vintage reconstruction series needed by `VW_MIDAS_SVR_XAU_SUCCESSOR_V2` research.

This is **source ingestion only**. It is not model promotion, forecast issuance, decision issuance or an archived-engine status change.

## 2. Separate series identity

New data-plane series:

`GPR_OFFICIAL_GIT_PIT`

It is intentionally distinct from:

`GPR_OFFICIAL`

`GPR_OFFICIAL` remains the current/final-vintage official workbook retrieval lane. `GPR_OFFICIAL_GIT_PIT` is a historical replay/reconstruction lane based on exact monthly files in the authors' official Git archive history.

No consumer may silently substitute one for the other.

## 3. Proven source window

Exhaustive pre-result audit of V1's 72 required origins established:

- required origins `2020-09..2026-08`: 72;
- exact historical `.xls` identities ever present in official Git history: 58;
- PIT-proven by exact official Git add timestamp no later than the corresponding month-end 17:00 ET origin: 54;
- continuous PIT-proven window: `2022-03..2026-08`, exactly 54 origins;
- V1 direct frozen historical URLs currently retrievable: 0/72;
- therefore V1 remains `SOURCE_BLOCKED_NO_MODEL_SCORE`.

The V2 data plane may ingest **only** the clean continuous `2022-03..2026-08` window. The 18 unproven V1 origins are not persisted under the new PIT series.

## 4. Vintage semantics

For each origin month `p` in `2022-03..2026-08`:

- exact source file: `gpr_archive_files/data_gpr_export_YYYYMM.xls` where `YYYYMM=p`;
- official source repository: `iacoviel/iacoviel.github.io`;
- exact file must have an official Git archive-add commit timestamp `<=` the last-calendar-day 17:00 America/New_York origin cutoff;
- exact workbook must parse;
- GPR observation `p-1` must exist;
- all stored rows for that vintage are bounded to observations `<=p-1`;
- current/final-vintage substitution is forbidden.

Timestamp semantics:

- `retrieved_at` = true current reconstruction retrieval time;
- `first_seen_at` = true current reconstruction retrieval time on first insert;
- `provider_as_of` = earliest official Git archive-add commit timestamp for the exact vintage;
- `available_as_of` = same proven official archive availability floor;
- the Git timestamp is not described as the newspaper publication timestamp or as historical Gold Control retrieval time.

Evidence class:

`HISTORICAL_REPLAY_RECONSTRUCTION`

## 5. Existing Neon tables only

No new schema/table is authorized.

Permitted writes are restricted to existing source-data/audit tables:

- `source_registry`
- `retrieval_runs`
- `observations`
- `source_vintages`
- `quality_events` only if a governed persistence run records a source-data quality event.

The implementation must use vintage-specific lineage IDs and payload SHA-256 hashes.

## 6. Explicitly prohibited writes

This change must not insert/update/delete:

- `monthly_forecast_contracts`
- `decision_signal_snapshots`
- `decision_runs`
- `decision_events`
- engine runtime authority rows
- model validation status
- selector/ensemble state
- BUY/SELL/HOLD/EXIT/REDUCE mapping.

The production ingestion job must verify the four decision/forecast authority table counts immediately before and after persistence and fail if they change.

## 7. Production write gate

Production persistence is allowed only after all of the following are true:

1. this change-control exists on canonical `gold-r4-direction-engine`;
2. canonical manifest is v1.33 or later and explicitly authorizes `MANIFEST_V1_33_GPR_PIT_DATA_PLANE`;
3. exact canonical workflow SHA is checked out;
4. 72-origin source audit is rebuilt from the official Git repository;
5. V2 window builder proves `54/54` required vintages;
6. `quality_errors=0` inside the 54-origin V2 window;
7. all 54 exact vintages parse and contain required `p-1` GPR;
8. no current/final-vintage substitution occurs;
9. production Neon decision/forecast authority stores are unchanged by the source ingestion.

If any gate fails, no production source persistence is authorized.

## 8. Model consequence

Successful ingestion removes only the **GPR V2 historical data-plane blocker**.

It does not by itself make VW V2 acceptable. VW V2 must still pass:

- its frozen XAU research/production lineage bridge;
- deterministic and prefix-invariance tests;
- untouched validation against Random Walk;
- all frozen V2 validation gates.

Maximum historical model status remains research/shadow eligibility until separate prospective evidence exists.
