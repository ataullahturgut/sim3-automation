# GOLD MONTHLY — ChHHO F4 FX Legacy Native Result

**Date:** 2026-09-29  
**Status:** COMPLETE / VALID FOR LEGACY ENDPOINT REPRESENTATION ONLY / SUPERSEDED FOR FAMILY DECISION  
**Decision:** DO NOT INTERPRET AS FAMILY-WIDE FX REJECTION

## Authority
- run: **36552598677**
- head commit: **1174b455471f895814b42bbd3d2a4aa7ab06c51b**
- summary artifact: **11026195076**
- digest: `sha256:db389252b953b252a3a0b33fefbbc00c8e2df757ef53f25c64fcf254442d1a56`
- Neon reads: **0**
- 2025/2026 selection use: **NONE**
- random split: **NONE**

## Baseline parity
- canonical BASE: **1413.029779 / 23/33**
- observed BASE: **1413.029779 / 23/33**
- parity: **PASS**

## Legacy routed FX result
- routed ΣAE: **1811.986846**
- routed direction: **18/33**
- ΔΣAE vs BASE: **-398.957067**
- percent improvement: **-28.23%**
- months improved / tied / worsened: **8 / 10 / 15**
- year ΔΣAE:
  - 2022: **-31.3106**
  - 2023: **-150.9376**
  - 2024: **-216.7089**
- promotion gate under old charter: **FAIL**

Router usage:
- BASE 10
- FX_BREADTH_DISP 7
- FX_BROAD 5
- FX_BROAD_CNY 5
- FX_BROAD_SAFE 3
- FX_SAFEHAVEN 2
- FX_CNY 1

## Why this is superseded for family inference

The run is numerically valid for the exact implementation tested, but the later F4 reset found three methodological defects in the external-native design:

1. daily FX was mainly collapsed into endpoint-to-endpoint monthly changes rather than CURRENT8-style MR1 + GPR-conditioned VW;
2. intramonth daily path information was therefore under-used;
3. ChHHO population/search density was not increased as antecedent dimension rose from 80 to 90/100.

The pathological CNY/safe-haven static candidates are therefore treated as **architecture/optimizer stability diagnostics**, not as literal evidence that those economic channels contain no signal.

## Binding status

- Old FX native design: **REJECTED**
- FX family itself: **REOPENED UNDER F4 RESET**
- Redesigned FX must use:
  - daily quote normalization;
  - monthly-average MR1 analogue;
  - GPR-conditioned daily VW analogue;
  - dimension-adjusted optimizer population;
  - hard BASE parity gate.

Current authority:
`GOLD_MONTHLY_F4_RESET_PROCESSING_PARITY_AUDIT_2026-09-29.md`.

## Kontrol ve Uyum Özeti
- BASE parity: PASS
- legacy endpoint FX implementation: FAIL
- family-wide rejection: SUPERSEDED
- daily-path redesign required: YES
- optimizer-dimension parity required: YES
- 2025 tuning: NONE
- Neon: 0
