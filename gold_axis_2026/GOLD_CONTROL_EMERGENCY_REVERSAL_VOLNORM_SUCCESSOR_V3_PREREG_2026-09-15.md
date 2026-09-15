# GOLD CONTROL — EMERGENCY REVERSAL VOLNORM SUCCESSOR V3 PREREGISTRATION

**Date frozen:** 2026-09-15  
**Identity:** `EMERGENCY_REVERSAL_VOLNORM_SUCCESSOR_V3`  
**Status:** `FROZEN_CORRECTIVE_SUCCESSOR_BEFORE_VALID_2025_REPLAY`  
**Parent V2:** `INVALID_SOURCE_GOVERNANCE_BUG_DO_NOT_SCORE`  
**Production authority:** NONE  
**Database writes:** NONE

## 1. Corrective-only scope

V3 exists solely to enforce the weekday source semantics that V2 intended but failed to implement.

The invalid V2 challenge exposed the defect because 270 selected 2025 dates exceeded the 261 Monday-Friday calendar days. All V2 2025 performance outputs are withdrawn.

V3 changes **no detector-performance parameter** in response to that invalid result:

- fixed source hour remains 14:00 ET;
- volatility window remains 20 prior observed returns;
- leg threshold remains 2.0 path-vol units;
- reversal threshold remains 2.0 path-vol units;
- EXTREME threshold remains 3.0 path-vol units;
- peak/trough state logic remains unchanged;
- monthly forecast input remains absent.

The only source correction is an explicit Monday-Friday gate before a provider bar may enter the daily path, plus an invariant forbidding yearly selected counts above the number of calendar weekdays.

## 2. Pre-2025 verification of the source correction

A corrected source probe used only 2022–2024 and explicitly discarded Saturday/Sunday bars before coverage accounting.

For 14:00 ET:

- 2022: 257/260 = 98.85%;
- 2023: 256/260 = 98.46%;
- 2024: 258/262 = 98.47%;
- weekend bars encountered at this hour in 2022–2024: 0;
- overlap with weekday 16:00 source: 707 dates;
- level correlation: 0.9999335;
- median absolute level gap: 6.79 bp;
- p95 absolute level gap: 31.23 bp.

Thus the 14:00 pre-2025 source choice remains supported without using any 2025 performance outcome.

## 3. Frozen V3 source contract

- provider: Twelve Data;
- symbol: `XAU/USD`;
- interval: `1h`;
- timezone: `America/New_York`;
- selected bar open time: exact `14:00:00`;
- selected value: positive finite `close`;
- eligible calendar dates: Monday through Friday only (`dayofweek < 5`);
- Saturday/Sunday bars: explicitly rejected from the governed path;
- no fallback hour;
- no interpolation;
- no forward fill;
- no provider substitution;
- annual coverage gate: selected weekday dates / calendar Monday-Friday dates >= 0.95;
- invariant: selected weekday dates <= calendar Monday-Friday dates;
- evidence class: `HISTORICAL_RESEARCH_RECONSTRUCTION`.

## 4. Frozen detector mathematics

Unchanged from V1/V2:

`r_t = ln(P_t/P_{t-1})`

`sigma20_t = sample_std(r_{t-20},...,r_{t-1})`

with the current return excluded.

For a running extreme `e` and current observed date `t`:

`path_sigma(e,t) = sqrt(sum_{j=e+1..t} sigma20_j^2)`.

Initial directional leg requires absolute path score >=2.0. A reversal alert requires an opposite path score >=2.0 from the current running peak/trough. Absolute reversal score >=3.0 is annotated EXTREME.

One alert is emitted only on a state transition.

## 5. Formation revalidation

V3 must rerun 2022–2024 formation with the corrected weekday guard before 2025 may be replayed.

Required gates:

- coverage >=95% in each formation year;
- no selected weekend date;
- selected count never exceeds calendar weekdays;
- exact determinism;
- prefix invariance;
- current observation excluded from its own volatility scale;
- no monthly forecast input;
- no 2025 observation read;
- >=3 formation reversal alerts;
- formation alert rate <20%;
- no production/database write.

After PASS, V3 configuration and implementation hashes must be frozen before a valid corrected 2025 replay.

## 6. Corrected 2025 replay protocol

The replay remains two-stage and engine-first:

1. run V3 across the full historical path required for state initialization and all eligible 2025 Monday-Friday origins **without loading the 19-event volatility inventory**;
2. assert 2025 selected count <=261 and annual coverage >=95%;
3. save/hash/freeze the complete 2025 engine timeline;
4. only then run a separate overlay process containing the frozen 19-event inventory.

The corrected replay is retrospective diagnostic evidence. Because an invalid V2 2025 output was already observed, V3 must not be described as human-blind prospective/OOS evidence. No V3 parameter may be changed using the invalid V2 result.
