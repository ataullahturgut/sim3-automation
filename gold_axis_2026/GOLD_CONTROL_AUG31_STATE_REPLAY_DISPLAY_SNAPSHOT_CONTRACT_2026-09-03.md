# Gold Control — Aug31 State Replay Deployment Snapshot Contract

**Status:** `FROZEN_AUG31_STATE_REPLAY_DISPLAY_SNAPSHOT_V1`  
**Evidence authority:** production Neon historical replay rows  
**Purpose:** read-only deployment fallback only

This artifact exists because the public/mobile hosting instance may not have `NEON_DATABASE_URL`. It is a fingerprint-validated replica of the seven `AUG31_REPLAY_*` derived feature rows already persisted in production Neon.

It is not a calculation or model authority and may not create or modify an output. Neon remains the authoritative dynamic evidence plane.

The snapshot must contain exactly these seven replay feature identities:

- `AUG31_REPLAY_MONTHLY_DIRECTION_3M`
- `AUG31_REPLAY_FAST_STATE`
- `AUG31_REPLAY_SLOW_STATE`
- `AUG31_REPLAY_GVZ_VALUE`
- `AUG31_REPLAY_GVZ_CAP`
- `AUG31_REPLAY_GVZ_PANIC`
- `AUG31_REPLAY_GVZ_REGIME`

Every row must retain `HISTORICAL_REPLAY`, `prospective_h1_claim=false`, `current_runtime_authority=false`, `canonical_authority=false`, target context `2026-09` and state boundary `2026-08-31T21:00:00+00:00`.

The artifact also carries the exact blocked-component map from `FROZEN_AUG31_EOD_STATE_REPLAY_V1`. It may not contain a selector result, canonical forecast, Decision Store state, classification, action mapping, credentials, raw XAU price history, or a BUY/SELL/HOLD/EXIT/REDUCE instruction.

A deterministic SHA-256 payload fingerprint is mandatory. Invalid cardinality, identity, evidence class, authority flags, boundary, target, blocker map, or fingerprint must fail closed.