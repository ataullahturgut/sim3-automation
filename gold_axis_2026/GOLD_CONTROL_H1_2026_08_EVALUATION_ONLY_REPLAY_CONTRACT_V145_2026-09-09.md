# Gold Control — H=1 2026-08 Evaluation-only Replay Contract V1.45

**Status:** `FROZEN_BEFORE_2026_08_REPLAY_OUTPUT_EXECUTION_OR_INSPECTION`  
**Frozen at:** 2026-09-09  
**Scope:** Component Verification C9 for the four frozen H=1 engines; historical replay only.

## Purpose

The existing immutable H=1 evidence ends at target month `2026-07`. This contract adds exactly one technical replay target, `2026-08`, without changing any model identity, source identity, feature, threshold, geometry, hyperparameter grid, seed, selection rule, or evaluation rule.

The replay origin is the governed prior month end. No August 2026 observation or realized August target may enter feature construction, training, inner configuration selection, or technical PASS/FAIL.

## Frozen engine rules

### CAUSAL_PATCH

- identity: `CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE`;
- geometry: `L=252`, `P=21`, `D=32`;
- seeds, optimizer, loss, validation split and median-of-three procedure remain exactly as implemented by V7;
- daily feature history is strictly before the existing V7 origin-date cutoff;
- the July 2026 price anchor is reconstructed only from the same Twelve Data `XAU/USD`, `1h`, `America/New_York`, unique `16:00:00` source-bar semantic used by V6/V7;
- no August observation is permitted.

### VW_MIDAS_MSVR_SUCCESSOR_V1

- frozen four-metal daily source identities and GPR PIT origin-vintage rule remain unchanged;
- the existing configuration grid and prior-only nested ranking rule remain unchanged;
- the `2026-08` feature vector uses completed July/June inputs only;
- target-month metal values may not be required or read merely to construct the feature vector;
- the price anchor remains the frozen prior-month `CORE5_GOLD_USD_OZ_RESEARCH_R1` value;
- realized August target is excluded from Component Verification.

### MOMENTUM_3M / RANDOM_WALK

- identities remain `MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND` and `RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND`;
- source remains `SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2` only;
- the July 2026 monthly mean may be reconstructed only from the same Twelve Data `XAU/USD`, `1h`, `America/New_York`, unique `16:00:00` source-bar semantic and minimum-observation rule;
- Random Walk equals the July governed mean;
- Momentum uses the frozen four-positive-level / three simple-return formula over April–July 2026;
- August observations are forbidden.

## Gates

A technical C9 PASS requires exact source identity, positive finite inputs, zero duplicate selected dates, the frozen minimum observation count, origin compliance, two identical rerun outputs, `prospective_claim=false`, and zero production/authority writes.

Performance values are not inputs to this gate. A missing governed source yields `BLOCKED_DATA`; an implementation/contract mismatch yields `IMPLEMENTATION_FAIL`. Provider substitution, interpolation, forward-fill and post-result tuning are prohibited.

