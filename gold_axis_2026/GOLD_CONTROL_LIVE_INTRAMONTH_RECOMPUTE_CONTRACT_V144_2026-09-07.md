# GOLD CONTROL · LIVE INTRAMONTH RECOMPUTE CONTRACT V1.44

Date: 2026-09-07

## Purpose

This contract closes the governed gap between successful raw-data ingestion and stale derived intramonth context. It is intentionally narrower than forecast or decision authority.

The writer is **append-only** and may write only:

- current tactical/risk derived features (`FAST_STATE`, `SLOW_STATE`, `GVZ_VALUE`, `GVZ_CAP`, `GVZ_PANIC`, `GVZ_REGIME`); and
- current runtime/context rows for `FAST`, `SLOW`, `GVZ_RISK`, `EMERGENCY_LEVEL`, `EMERGENCY_REVERSAL`.

It may not write or mutate monthly H=1 forecasts, selector/ensemble state, decision runs, decision events, decision signal snapshots, or position instructions.

## Authority basis

The engineering design follows these authority benchmarks:

1. Federal Reserve SR 26-2 / Revised Guidance on Model Risk Management: ongoing monitoring should verify implementation, source-data accuracy/completeness/consistency, system integration, change control and model-use limitations. This is used as an engineering benchmark, not as a claim that banking regulation legally applies to Gold Control.
2. NIST AI RMF / post-deployment monitoring guidance: deployed components and changing real-world inputs should be monitored rather than assuming pre-deployment behavior remains valid.
3. W3C PROV: derived outputs should preserve explicit provenance from source entity through transformation/activity to output evidence.
4. Hyndman & Athanasopoulos rolling-origin time-series evaluation: future observations must not enter a past forecast origin. Therefore this writer updates only intramonth contexts; it never refreshes September H=1 monthly forecasts with September observations.

## Source and timing rules

### FAST

- source: `XAU_EOD_TWELVE_NY17` only;
- algorithm: frozen R4.1 SMA20 + two completed-trade-date persistence rule;
- input: latest completed canonical NY17 observations;
- no forward-fill, interpolation or provider substitution.

### SLOW

- underlying source: `XAU_EOD_TWELVE_NY17` only;
- algorithm: frozen R4.1 weekly-close/SMA4 + two completed-week persistence rule;
- incomplete current week is excluded;
- the runner may execute daily but the SLOW fingerprint changes only when relevant completed-week inputs change.

### GVZ_RISK

- source: `GVZ_CBOE` only;
- thresholds remain frozen in `r4_1/src/gold_r4/gvz.py`;
- current regime mapping: cap 1.0 = NORMAL, cap 0.5 = ELEVATED, cap 0.25 = PANIC.

### Emergency

- XAU source: accepted target-month `XAU_EOD_TWELVE_NY17` rows;
- state is replayed chronologically from the start of the target month on every refresh so peak/trough reversal memory is deterministic and recoverable;
- monthly reference is explicit and immutable for the target month;
- for September 2026 the current Causal Patch reference is historical-replay evidence. The writer may therefore produce a **fresh-input historical-reference context**, but it must not relabel that output as a prospective September forecast or prospective Emergency reference;
- when a later target month has an eligible `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` monthly reference, the reference evidence may support prospective context issuance under the same append-only writer.

## Fail-closed source gate

Before any intramonth persistence:

- canonical XAU must have enough history for the frozen FAST rule;
- canonical XAU must not trail the accepted independent `XAU_DAILY_XAUS` trade date;
- XAU quality must be `APPROVED_CANONICAL_TWELVE_NY17`;
- GVZ must have an approved observation;
- the current target context must be unique;
- required current runtime identities must exist;
- the Emergency monthly reference must have positive value, correct target month, explicit evidence class and no unexpected canonical-authority promotion.

Failure of any gate causes **zero writes**.

## Idempotency and provenance

Each logical output receives an SHA-256 input fingerprint over the exact governed inputs and this contract version.

A new append-only row is inserted only when that component's latest fingerprint for the target context changes. Re-running the same inputs therefore produces zero duplicate context rows.

Every persisted output records or carries:

- source series identity;
- source observation timestamp(s);
- source availability cutoff;
- selected observation IDs/lineage where applicable;
- input fingerprint;
- feature/model version;
- Git commit;
- target context;
- context issuance mode;
- `prospective_h1_claim=false`;
- `canonical_forecast_authority=false`;
- `AUTO_SELECTOR=OFF`;
- `AUTO_ENSEMBLE=OFF`;
- `decision_store_write=NONE`.

## Catch-up versus prospective-shadow operation

Two execution modes are frozen:

- `catchup`: used when repairing context after the relevant source observations were already available before deployment of this writer; persisted runtime evidence remains `HISTORICAL_REPLAY`.
- `prospective-shadow`: used for later observations first consumed by the deployed scheduled writer. FAST/SLOW/GVZ may be issued as `PROSPECTIVE_SHADOW` context. Emergency remains limited by the evidence class of its frozen monthly reference.

No catch-up row may be relabelled as prospective.

## Scheduler dependency

The production scheduler must run intramonth recomputation **after successful source ingestion**, not merely on an unrelated wall-clock timer:

1. canonical NY17 reconciliation succeeds;
2. intramonth recompute runs;
3. post-write readiness audit runs;
4. snapshot/UI refresh consumes the new state.

A second recompute should follow the daily authority ingest/retry path so newly released GVZ context is also consumed.

## September acceptance target

After canonical XAU catches the latest accepted completed trade date, the first V1.44 catch-up is expected to replace stale FAST/SLOW/GVZ contexts and replace the Emergency month-open `NO_SEPTEMBER_EOD_OBSERVATION` placeholder with a chronologically recomputed September context, while leaving all September H=1 monthly forecast references unchanged.
