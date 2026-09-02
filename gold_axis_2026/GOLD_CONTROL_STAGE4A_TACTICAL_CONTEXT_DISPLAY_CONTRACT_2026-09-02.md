# Gold Control Stage 4A Tactical Shadow-Context Display Contract

**Status:** `FROZEN_BEFORE_TACTICAL_CONTEXT_ISSUANCE`  
**Date:** 2026-09-02  
**Manifest authority:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.22  
**Scope:** Stage 4A current-state substrate / UI context only

## Purpose

Expose already-governed R4.1 directional components to the `Görünüm` screen without fabricating a complete forward Decision Store snapshot.

This contract does **not** create a canonical decision, forecast, action, position, selector, ensemble, or prospective H=1 claim.

## Frozen input contract

- series: `XAU_EOD_TWELVE_NY17`
- quality: `APPROVED_CANONICAL_TWELVE_NY17`
- source: Twelve Data
- late-bootstrap target context: `2026-09`
- selected observations: approved PIT rows with `observation_ts < 2026-09-02T00:00:00Z`
- every selected row must satisfy `available_as_of <= calculation_ts` and `retrieved_at <= calculation_ts`
- one lineage only; no provider mixing

## Frozen tactical logic

No signal formula is changed.

- FAST: frozen R4.1 `fast_state(closes)`
  - trace contract: `SMA20_2_MARKET_DAY_PERSISTENCE`
- SLOW: frozen R4.1 `completed_weekly_closes(...)` then `slow_state(...)`
  - trace contract: `COMPLETED_WEEKLY_SMA4_2_WEEK_PERSISTENCE`

## Persistence contract

Outputs are separate immutable derived features:

- `FAST_STATE` / `R4_1_SMA20_2_MARKET_DAY_PERSISTENCE_V1`
- `SLOW_STATE` / `R4_1_COMPLETED_WEEKLY_SMA4_2_WEEK_PERSISTENCE_V1`

Both rows:

- persist only to `derived_feature_snapshots`;
- use evidence/quality `LATE_BOOTSTRAP_SHADOW_CONTEXT`;
- bind the exact selected observation IDs, timestamps, lineage and input fingerprint;
- are append-only and require the existing immutable mutation-rejection trigger;
- log no raw market prices;
- carry `prospective_h1_claim=false`;
- carry `decision_store_write=NONE` and `canonical_forecast_write=NONE`.

Idempotence is by feature identity + target context + exact input fingerprint. A conflicting pre-existing row fails closed.

## UI authority

The final mobile UI may render `MONTHLY_DIRECTION_3M`, `FAST_STATE`, and `SLOW_STATE` as **SHADOW CONTEXT** directional arrows when their immutable context rows exist.

It must simultaneously preserve:

- `KANONİK KARAR YOK` until a display-eligible complete Decision Store state exists;
- Stage 6 = `BLOCKED_NO_DISPLAY_ELIGIBLE_DECISION_SNAPSHOT`;
- `NOT_PROVEN_POSITION_MAPPING`;
- no BUY / SELL / HOLD / exposure language.

`SHADOW CONTEXT` must never be relabelled `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION`.

## Forecast separation

This contract does not alter H=1 forecast issuance. September 2026 remains non-backfillable. The first possible Patch `MONTH_END_EXPERT` target remains October 2026 at the eligible end-September origin under its own frozen issuer contract.
