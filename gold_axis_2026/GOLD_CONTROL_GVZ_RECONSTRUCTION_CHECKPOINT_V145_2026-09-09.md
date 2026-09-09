# Gold Control V1.45 — GVZ Reconstruction Checkpoint

**Status:** `PASS`  
**Previous canonical HEAD:** `3d9c24efc43e5d91e470d71d7840714a20786be0`  
**Production database writes:** `NONE`

The frozen official-Cboe gap was reverified against production and completed in the governed immutable historical-replay artifact lane.

- lane: `GVZ_CBOE_HISTORICAL_REPLAY_V145`
- rows: `295`
- range: `2025-01-02..2026-03-09`
- official payload SHA-256: `7a2acc2e858d48fc02b7e4925f88df0716fba0a69e7d64c7d94039ed49771fd3`
- normalized output SHA-256: `8c11a86cf43dc66faf8658d37c444a4650b0175c639daa511af1e5330d941059`
- evidence class: `HISTORICAL_REPLAY_RECONSTRUCTION`
- prospective claim: `false`

The combined reconstruction bundle also contains 442 valid NY17 exact bars and 242 explicit provider-no-bar adjudications. Two builds over identical inputs produced byte-identical SHA-256 lists.

Workflow identity:

- run: `34349389199`
- artifact ID: `10103029670`
- artifact digest: `sha256:79bd7a0fa4024e5fbc3ebe8b4f912468d010c86437a8ed6360fd64206eed8430`

No live/current production observation or authority table was changed. The frozen artifact-lane contract makes this bundle the historical-pilot evidence authority; it does not create prospective evidence.
