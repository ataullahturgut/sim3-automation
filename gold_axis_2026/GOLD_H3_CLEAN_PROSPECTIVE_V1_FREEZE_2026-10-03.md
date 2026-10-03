# CLEAN H3 PROSPECTIVE V1 — FREEZE AUTHORITY

**Freeze date:** 2026-10-03  
**Freeze timestamp:** 2026-10-03T11:33:49Z  
**Umbrella identity:** `CLEAN_H3_PROSPECTIVE_V1`  
**Baseline:** `CLEAN_AURORA_H3_V1_PROSPECTIVE`  
**Shadow challenger:** `CLEAN_V5_DCE_H3_V1_PROSPECTIVE_SHADOW`  
**First eligible feature cutoff:** **2026-10-05**

## Purpose
Forward-only H3 experiment from corrected clean history. Legacy AURORA and HERA prospective ledgers remain immutable.

## Clean historical freeze
Corrected 2026-02-27 values: Gold **5183.80**, Silver **88.14**, Platinum **2369.25**, Palladium **1789.96**.
Frozen inputs: clean daily prices, clean AURORA expert matrix, and clean RIFT/VEGA/OPAL training panels.
Bootstrap evidence: `73d1240cdc4dcac6f3671d53640094fcc61e2083`.
Reproduction max errors: AURORA <5e-16; RIFT 1.11e-16; TURN 8.33e-17; VEGA 5.55e-17; OPAL 8.33e-17; all override decisions exact.

## Clean AURORA
Rules unchanged: A1 0.75/0.25, recent252, five-issued-origin blocks, Logistic L2 STRUCTURAL/PATH, monthly expert refit, SENTRY 63/42/+3, DART hazard 0.05, PATH exit >=8 disagreements with Pr(PATH superior)<=0.10 and q_path<=0.40.

## Clean V5-DCE shadow
Frozen rules: RIFT/VEGA/OPAL thresholds 0.70; CFTC +7d; TURN frozen tail rule; HELIOS consensus latest8 enter5 exit3; V3-GT >0.50; V4-RGE W10 regret +2/-2; V5-DCE PATH posterior >0.50 and GT share >0.50. Diagnostic GT 0.60/0.70 is NOT used.

## Causal updating
Only matured H3 outcomes may enter training/competence. Pending outcomes are unavailable. Reversal monthly models use frozen clean history plus matured prospective rows. Policy/regret states replay chronologically.

## Integrity gate
`GOLD_H3_DATA_INTEGRITY_GATE_V1` is mandatory before feature generation, issuance or settlement.

## Issuance / no backfill
First eligible feature cutoff **2026-10-05**. Clean AURORA and V5 shadow share the next-weekday 08:00 America/New_York deadline. Misses are never outcome-aware backfilled.

## Governance
Any threshold, feature, model-class, game-policy, RGE/DCE, integrity or lag change requires a new version. Legacy prospective experiments remain untouched.
