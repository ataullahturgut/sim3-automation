# GOLD CONTROL — HISTORICAL RECONSTRUCTION ARTIFACT LANES V1.45

**Date:** 2026-09-09  
**Status:** `FROZEN_IMPLEMENTATION_OF_V145_HISTORICAL_RECONSTRUCTION_STORAGE_OPTION`  
**Parent manifest:** `gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md` v1.45  
**Parent readiness contract:** `gold_axis_2026/GOLD_CONTROL_HISTORICAL_PILOT_READINESS_CONTRACT_V145_2026-09-08.md`  
**Scope:** historical-pilot reconstruction storage and lineage only; no model/threshold/feature/source-provider/evaluation-rule change; no production authority write.

---

## 1. Decision

For `GOLD_PILOT_V1`, historical NY17 and historical GVZ gap completion will use **immutable GitHub artifact lanes** rather than inserting reconstructed historical rows into the live/current production source series.

This implements the already-frozen V1.45 rule that historical reconstruction may be stored append-only **or** as immutable artifacts with truthful retrieval, source, quality, lineage and fingerprint metadata.

This choice does not change the governed provider or source semantic consumed by any engine. It changes only where retrospective reconstruction evidence is stored for the historical pilot.

No artifact created under this contract may be relabelled `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION`.

---

## 2. Why production canonical rows are not rewritten

Historical observations retrieved after their historical observation dates were not held prospectively by Gold Control at those dates. Inserting them into the live canonical series without a distinct evidence lane could obscure that distinction.

Therefore:

- live/current `XAU_EOD_TWELVE_NY17` rows remain untouched;
- live/current `GVZ_CBOE` rows remain untouched by this historical-pilot gap completion;
- authority stores remain untouched;
- historical replay consumes only explicitly identified artifact-lane records;
- current/live readiness continues to use V1.43/V1.44 production surfaces and is not promoted by historical artifact completion.

---

## 3. NY17 historical artifact lane

### 3.1 Lane identity

Artifact lane ID:

`XAU_EOD_TWELVE_NY17_HISTORICAL_REPLAY_V145`

Governed source semantic remains:

`XAU_EOD_TWELVE_NY17`

Provider/source contract remains exactly:

- provider: `Twelve Data`;
- symbol: `XAU/USD`;
- interval: `1min`;
- timezone: `America/New_York`;
- accepted source bar: unique exact `16:59:00` bar;
- accepted value: `close` only after positive/finiteness/OHLC-range validation;
- observation semantic: corresponding `17:00 ET` session boundary, converted to UTC;
- fallback: none;
- interpolation: forbidden;
- forward-fill: forbidden;
- synthetic bar: forbidden;
- alternate provider: forbidden.

### 3.2 Mandatory per-date adjudication

Each required date must end in one of:

- `VALID_EXACT_BAR`;
- `PROVIDER_NO_BAR`;
- explicit fail-closed blocker such as `ENTITLEMENT_BLOCKED`, `AUTHENTICATION_ERROR`, `INVALID_REQUEST`, `SERVER_ERROR`, `MALFORMED_BAR`, `REQUEST_ERROR`.

A historical month/cell cannot be promoted to complete while any required date remains under a fail-closed blocker.

`PROVIDER_NO_BAR` is an adjudicated non-observation, not an imputed value.

### 3.3 Mandatory lineage

Every `VALID_EXACT_BAR` artifact row must retain at minimum:

- trade date;
- source bar datetime;
- OHLC values;
- accepted close;
- actual `retrieved_at`;
- provider response payload SHA-256;
- provider/symbol/interval/timezone;
- accepted source time and stored semantic;
- `evidence_class=HISTORICAL_REPLAY_RECONSTRUCTION`;
- `prospective_claim=false`;
- impacted readiness cells.

No historical availability timestamp may be fabricated.

---

## 4. GVZ historical artifact lane

Artifact lane ID:

`GVZ_CBOE_HISTORICAL_REPLAY_V145`

Governed source identity remains:

`GVZ_CBOE`

Source remains the official Cboe historical GVZ CSV linked by Cboe's Historical Data page.

The frozen exact gap artifact is:

`gold_axis_2026/data_pipeline/audits/historical_gvz_gap_inventory_v145.csv`

The source payload fingerprint used to build that inventory must remain recorded. Historical rows retain:

- observation date;
- official Cboe value;
- source URL/payload SHA-256;
- actual retrieval timestamp from the source evidence;
- `evidence_class=HISTORICAL_REPLAY_RECONSTRUCTION`;
- `prospective_claim=false`;
- impacted readiness cell(s).

No missing Cboe date is interpolated or forward-filled.

---

## 5. Artifact authority and reproducibility

The historical reconstruction bundle must record SHA-256 fingerprints for all input and output artifacts. A deterministic rerun over identical inputs must produce identical normalized data rows and identical content fingerprints except for explicitly excluded wrapper timestamps.

The bundle builder must contain **no database write path** and must not import/use production persistence helpers.

Required output classes:

1. NY17 exact-bar reconstruction rows;
2. NY17 provider-no-bar adjudication rows;
3. GVZ historical reconstruction rows;
4. machine-readable bundle manifest containing source/input/output hashes and blocker counts.

If any NY17 required date remains unresolved/blocked, bundle status is `BLOCKED_DATA` and the historical NY17 lane is not declared complete.

---

## 6. Historical readiness interpretation

After artifact completion, the V1.45 historical readiness audit/replay layer may treat the artifact lane as an explicitly governed historical reconstruction of the **same frozen source/bar identity** for historical-pilot purposes only.

This does not make the reconstructed rows prospective and does not make current/live production data ready.

The five NY17-dependent engines remain:

- `MONTHLY_DIRECTION_3M`
- `FAST`
- `SLOW`
- `EMERGENCY_LEVEL`
- `EMERGENCY_REVERSAL`

GVZ remains:

- `GVZ_RISK`

Each engine still requires its role-specific chronological/prehistory/reference rules from the V1.45 readiness contract. Data completion alone cannot create `READY_PROVEN`; at most it removes the data blocker and permits deterministic replay/verification.

---

## 7. Production safety boundary

This artifact-lane implementation authorizes **zero** production database writes.

Specifically it must not write:

- `observations`;
- `source_registry`;
- `retrieval_runs`;
- `monthly_forecast_contracts`;
- `decision_signal_snapshots`;
- `decision_runs`;
- `decision_events`;
- current runtime/context tables;
- selector/ensemble state.

If a later decision is made to mirror historical artifacts into Neon, that requires a separate explicit production-write approval and must preserve the artifact evidence class and truthful retrieval timestamps.

---

## 8. Stop condition

Artifact-lane gap completion is complete only when:

1. all required NY17 dates have final exact-provider adjudications;
2. every accepted NY17 row passes the frozen exact 16:59/OHLC contract;
3. all 295 currently identified GVZ historical gap rows are present in the frozen Cboe reconstruction artifact unless a later read-only production reconciliation proves some are already present;
4. bundle fingerprints and deterministic build tests pass;
5. no production database write occurred;
6. readiness is re-audited before any model-performance scoring.

Until then:

`GOLD_PILOT_V1_HISTORICAL_READINESS = NOT_YET_PROVEN`.
