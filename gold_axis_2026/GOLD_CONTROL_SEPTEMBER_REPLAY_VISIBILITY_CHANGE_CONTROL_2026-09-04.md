# GOLD CONTROL — SEPTEMBER 2026 REPLAY VISIBILITY / MOTOR ACTIVATION CHANGE CONTROL

**Date:** 2026-09-04  
**Manifest authority:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.30  
**Canonical branch:** `gold-r4-direction-engine`  
**Scope:** presentation/observability only; no new forecast, selector, ensemble, position mapping, or decision authority.

## 1. Purpose

The September 2026 H=1 rows already persisted in production Neon are historical replay evidence and must be visible to the user during September without being misrepresented as a prospective/canonical forecast.

The governed engine inventory must also distinguish engines that are already active, engines waiting for the next eligible month-end origin, and engines that are technically blocked with no date-based automatic activation.

## 2. September H=1 replay display contract

Production historical-replay expert rows:

- `MOMENTUM_3M` = `4345.814584037808 USD/oz`
- `RANDOM_WALK` = `4397.305673870967 USD/oz`
- target month = `2026-09`
- forecast origin = `2026-08-31T21:00:00Z`
- evidence class = `HISTORICAL_REPLAY`
- canonical authority = `false`
- selector = `NOT_PROVEN_EXPERT_SELECTION_RULE`
- auto selector = `OFF`
- auto ensemble = `OFF`

Presentation requirements:

- The first visible Forecast/Tahmin hero may show the two replay expert values when no governed canonical forecast exists.
- The hero must say `EYLÜL 2026 H=1 REPLAY` and `REPLAY · PROSPECTIVE DEĞİL`.
- Replay origin must be labelled `REPLAY ORIGIN`, never `CANONICAL ORIGIN`.
- The values remain separate expert outputs; no average, winner, selector, ensemble, or synthetic canonical forecast may be invented.
- Official prospective September state remains `NOT_ISSUED_MISSED_2026_08_31_ORIGIN`.

## 3. Governed motor inventory and activation gates

Current production runtime authority remains `latest_engine_runtime_state` with 12 governed motors:

- ACTIVE = 4
- WAITING = 3
- BLOCKED = 5
- direction-vote permitted = 3

### ACTIVE now

- `MONTHLY_DIRECTION_3M` — strategic direction context; direction vote permitted.
- `FAST` — tactical direction context; direction vote permitted.
- `SLOW` — tactical direction context; direction vote permitted.
- `GVZ_RISK` — risk-only context; direction vote not permitted.

### WAITING for an eligible month-end origin

- `CAUSAL_PATCH`
- `MOMENTUM_3M`
- `RANDOM_WALK`

These are not missing-data failures. Their runtime status is `WAITING_ELIGIBLE_MONTH_END_ORIGIN`.

Under the frozen v1.30 H=1 contract, the first currently possible legitimate forward target is **October 2026**, using the **completed September month-end origin**, and only if all issuer, availability, publication-lag, vintage/PIT, snapshot, and persistence gates close at that origin. No September prospective row may be backfilled.

### BLOCKED — not date-triggered

- `VW_MIDAS_MSVR` — `BLOCKED_NOT_PROVEN_EXECUTABLE`; requires exact executable runner/provenance proof.
- `MACRO_EVENT` — `BLOCKED_NOT_FULLY_RECOVERED`; requires full frozen event-rule/implementation recovery and validation.
- `EMERGENCY_LEVEL` — `BLOCKED_NO_PERSISTED_MONTHLY_PRICE_REFERENCE`; requires authorized persisted monthly price reference.
- `EMERGENCY_REVERSAL` — same persisted monthly price-reference blocker.
- `BOCPD` — `BLOCKED_EXACT_FORWARD_BOCPD_RULE_NOT_RECOVERED`; requires exact forward rule recovery, freeze, and tests.

No calendar date is promised for the five blocked motors. They become eligible only after their exact blocker is closed under change control. Numbers must not be fabricated meanwhile.

## 4. Non-negotiable locks

This change does not alter:

- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`
- `NOT_PROVEN_EXPERT_SELECTION_RULE`
- `NOT_PROVEN_POSITION_MAPPING`
- no BUY/SELL/HOLD/EXIT/REDUCE output
- historical replay and prospective/live evidence remain separate
- Neon remains mutable production-state authority; GitHub remains code/contract authority

## 5. Acceptance proof required

Before canonical promotion:

1. deterministic app tests PASS;
2. production read-only audit proves exact September replay values and 4/3/5 runtime distribution;
3. 390×844 DB-backed Forecast screen visibly shows both replay values at the top with replay-only labels;
4. 390×844 engine-inventory view shows activation timing/blocker explanations;
5. no action/selector/ensemble/canonical authority is introduced;
6. canonical and deployment/UI branches are fast-forwarded only after the exact candidate head passes.
