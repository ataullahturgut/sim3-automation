# GOLD CONTROL — LIVE MARKET / ROADMAP CHANGE CONTROL

**Date:** 2026-09-01  
**Target manifest:** v1.10  
**Canonical branch:** `gold-r4-direction-engine`

## Problem

Manifest v1.9 correctly separates `Piyasa`, `Görünüm`, `Tahmin`, and `Geçmiş`, but the roadmap applies a globally linear Stage-4-before-Stage-5 gate. That over-couples the live market-monitoring product surface to unresolved H=1 forecast/VW issuance even though the `Piyasa` contract explicitly uses indicative live market data and must not derive or fabricate a decision from it.

## Authority / methodology evidence

1. CME Group documents EBS Market Spot FX & Precious Metals trade-date roll at 17:00 ET. This supports a distinct completed-session/EOD decision-reference semantic rather than treating a live quote as the model close.
2. Twelve Data documents real-time XAU/USD access through REST/WebSocket, but its 2026 terms make external/public display dependent on subscription/redistribution rights. Therefore Twelve remains approved for the private/internal canonical NY17 model-data path and is not silently promoted to a public raw-price UI source.
3. Gold API documents a free unauthenticated `GET /price/XAU` current-price endpoint, asks consumers to cache for 30 seconds, and explicitly supports website use. Its provider-managed upstream fallback is opaque, so it is suitable only for Tier-C indicative display/monitoring and is prohibited from EOD, benchmark, forecast, or decision-reference use.
4. NIST AI RMF / AIRC guidance treats production monitoring of system functionality/components as a continuous operational activity and recommends monitoring/documenting production behavior independently of pre-deployment/model evaluation. This supports decoupling market/data monitoring from forecast-model readiness while preserving separate decision claims.

## Runtime evidence

Gold API live-source probe:

- workflow: `Gold Control Live Gold API Probe`
- run: `33518757788`
- job: `99892357951`
- result: `SUCCESS`
- verified without logging raw price: HTTP 200, `symbol=XAU`, `currency=USD`, positive finite price field, parseable `updatedAt`, freshness <600 seconds
- database writes: none

Forecast/context reconcile audit:

- workflow: `Gold Control v1.10 State Reconcile Audit`
- run: `33518909613`
- job: `99892866821`
- result: `SUCCESS`
- `forecast_input_snapshots=0`
- `derived_feature_snapshots=1`
- `monthly_forecast_contracts=0`
- latest derived feature: `MONTHLY_DIRECTION_3M`, quality `LATE_BOOTSTRAP_SHADOW_CONTEXT`
- append-only trigger coverage: 3/3

Existing Stage-4 evidence also remains binding:

- canonical NY17 history backfill run `33515654716`: `SUCCESS`
- monthly-direction rehearsal run `33516364318`: `SUCCESS`
- late-bootstrap monthly-direction issuance run `33516396253`: `SUCCESS`
- Fast/Slow tactical rehearsal run `33516790212`: `SUCCESS` (`ROBUST_UP` / `ROBUST_UP`), read-only and not a prospective H=1 claim
- forecast-state append-only production migration run `33516015898`: `SUCCESS`

## Decision

### 1. Separate data/display semantics from decision semantics

- `XAU_SPOT_GOLDAPI` becomes the primary **indicative live display/monitoring** series for the `Piyasa` surface.
- `XAU_EOD_TWELVE_NY17` remains the canonical R4.1 completed-session internal decision reference.
- `XAU_SPOT_XAUS` remains a separate legacy/secondary indicative lineage and is not silently merged with Gold API.
- No live spot source may supply `monthly_vw_forecast`, H=1 forecast, EOD close, benchmark, or final decision state.

### 2. Correct roadmap gating

The roadmap becomes **dependency-gated rather than globally linear**:

- Stage 4A — current-state data/context substrate: canonical NY17 history, monthly direction context, Fast/Slow calculability, immutable state infrastructure.
- Stage 4B — forecast-dependent final R4.1 issuer: current H=1 executable issuer, VW monthly reference, immutable forecast input snapshot, forecast contract, complete `EngineSnapshot`, first `PROSPECTIVE_SHADOW` decision.
- Stage 5 `Piyasa` may progress after its own live/history/source/freshness contract is proven even while Stage 4B remains blocked.
- Stage 5 must show `KANONİK KARAR YOK` when no display-eligible Decision Store row exists and must state `Canlı spot ≠ son EOD karar`.
- Stage 6 `Görünüm` cannot be marked complete until a display-eligible stored decision snapshot exists; component rehearsals may be shown only on technical/shadow surfaces with explicit evidence labels.
- Stage 7 `Tahmin` cannot be marked complete until a canonical issued H=1 forecast exists.
- Stage 8 `Geçmiş` must continue separating `HISTORICAL_REPLAY`, `PROSPECTIVE_SHADOW`, and `LIVE_PRODUCTION`.

This change does **not** alter R4.1 formulas, thresholds, forecast target, forecast origin, model roles, position mapping, or prospective evidence rules.

## Active forecast blockers after this change

1. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`
2. `FORECAST_CONTRACT_NOT_ISSUED`
3. `PATCH_R1_CURRENT_ISSUER_NOT_PROVEN`
4. `VW_CURRENT_MONTHLY_REFERENCE_NOT_ISSUED` / `VW_EXECUTABLE_REPRODUCTION_BLOCKED_NOT_PROVEN`

`SEPTEMBER_2026_H1_PROSPECTIVE_ORIGIN_MISSED` remains a temporal evidence boundary. The first fully contract-compliant H=1 prospective target remains October 2026 with end-September origin, provided the active forecast blockers are closed before issuance.

## Immediate product step

Activate and smoke-test the `XAU_SPOT_GOLDAPI` live adapter in the transitional app with explicit source/freshness metadata. Do not change final decision logic, forecast values, or action mapping during this step.
