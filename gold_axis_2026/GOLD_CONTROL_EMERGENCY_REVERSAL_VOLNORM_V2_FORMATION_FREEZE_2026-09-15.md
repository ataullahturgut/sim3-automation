# GOLD CONTROL — EMERGENCY REVERSAL VOLNORM V2 FORMATION FREEZE

**Freeze date:** 2026-09-15  
**Identity:** `EMERGENCY_REVERSAL_VOLNORM_SUCCESSOR_V2`  
**Status:** `FORMATION_PASS_FROZEN_BEFORE_2025_REPLAY`  
**Formation workflow run:** `35022661725`  
**2025 observations consumed during formation:** `0`

## Frozen executable/configuration identity

- configuration SHA-256: `0419bd741d08f92c755e7ae8e26ebd6c1caf2619ed7518fda72b555bc7bdebdc`
- implementation SHA-256: `a35aeeed794ecd72e41036ce51178c38e8d29bc4ea1833e7dbfe3c0f03330a4e`
- formation timeline SHA-256: `1600b810e4ea724f6f863ca11505d30e49c3288271476dd8be0f0b7ac14aff69`

Frozen parameters/source:

- source: `XAU_TWELVE_1H_SELECT_14_00_NY_RESEARCH_V2`;
- provider: Twelve Data `XAU/USD` 1h, `America/New_York`;
- exact selected hourly open time: `14:00:00`;
- volatility window: 20 prior observed returns;
- leg threshold: 2.0 path-vol units;
- reversal threshold: 2.0 path-vol units;
- extreme annotation threshold: 3.0 path-vol units;
- annual source coverage gate: >=95%;
- monthly forecast dependency: NONE;
- raw fixed-percent threshold: NONE.

## Formation evidence

Formation interval: calendar 2022–2024 only.

Source coverage:

- 2022: 257/260 = 98.85%;
- 2023: 256/260 = 98.46%;
- 2024: 258/262 = 98.47%.

Detector accounting:

- selected closes: 771;
- eligible post-warmup rows: 750;
- reversal alerts: 11;
- UP alerts: 5;
- DOWN alerts: 6;
- EXTREME alerts: 1;
- alert rate: 1.4667%.

All targeted tests passed (8/8), including strictly prior-only volatility, transition-only alerts, prefix invariance, exact determinism, no monthly forecast dependency and V2 source-contract identity.

## Challenge lock

From this freeze onward, the 2025 retrospective challenge may execute only if runtime recomputation of the configuration and implementation hashes exactly matches the values above.

The challenge must be two-stage:

1. **engine stage:** run the frozen detector over the complete source history required to initialize state and generate every eligible 2025 output, then save and hash the complete 2025 timeline without loading the 19-event volatility inventory;
2. **overlay stage:** read the already-frozen 2025 engine timeline and only then overlay the independent frozen 19-event volatility inventory.

No source, threshold, volatility window, state transition or alert rule may change after the 2025 engine output is observed under this identity.
