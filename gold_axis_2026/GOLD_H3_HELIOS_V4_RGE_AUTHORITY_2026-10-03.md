# HELIOS-H3 V4-RGE — REGRET-GATED EXPANSION AUTHORITY

**Date:** 2026-10-03  
**Identity:** `HELIOS_H3_V4_RGE_RESEARCH`  
**Parents:** `HELIOS_H3_V2_RESEARCH` + `HELIOS_H3_V3_GT_RESEARCH`  
**Status:** POST-DIAGNOSTIC / POST-HOC STRENGTHENING RESEARCH

## Purpose

V2 is the high-precision protected reversal router but under-captures the 2026 expansion in useful OPAL reversals.
V3-GT recovers many 2026 rescues but gives back V2 gains in 2024-2025.

V4-RGE is designed to preserve V2 by default and permit V3-style broader OPAL routing only after causal evidence shows that non-consensus OPAL has developed positive regret versus KEEP.

## Frozen base

- AURORA remains the base champion.
- HELIOS V1/V2 macro gate is unchanged.
- Every V2 consensus route is retained exactly.
- V2 probability calibration is retained on all base consensus routes.

## Regret-gated expansion

Expansion candidates:
- OPAL override = true;
- HELIOS consensus candidate = false;
- HELIOS macro gate = ACTIVE.

The expansion competence ledger observes every matured non-consensus OPAL outcome, whether or not it was acted on.

Binding recent window:
- latest **10 matured non-consensus OPAL events**.

Event utility relative to KEEP:
- rescue = +1;
- broken = -1.

Recent regret:
`R_t = sum utility over latest 10 matured non-consensus OPAL events`.

Hysteretic expansion gate:
- initial INACTIVE;
- enter ACTIVE when `R_t >= +2` (at least 6/10 rescues);
- exit ACTIVE when `R_t <= -2` (at most 4/10 rescues);
- otherwise retain state.

All outcomes must be target-matured before entering the ledger.

## V3 policy-market confirmation

Even while the expansion gate is ACTIVE, a non-consensus event is routed only if the frozen V3-GT five-policy market has weighted flip share > 0.50.

The V3 policy market remains:
- KEEP
- HELIOS_CONSENSUS
- COT_FRESH
- FRESH_OR_CONSENSUS
- OPAL_ALL

with latest-8 matured OPAL utility and rescue +1 / broken -1.

## Probability

Start from HELIOS V2 probability.

- no expansion: `p_V4 = p_V2`
- expansion route: `p_V4 = 1 - p_AURORA`

No new fitted probability calibration is allowed.

## Evaluation

Report 2023, 2024, 2025, 2026, 2023-2024, 2025-2026.

Compare:
- AURORA
- HELIOS V2
- HELIOS V3-GT
- HELIOS V4-RGE
- raw OPAL.

Primary:
- net rescue
- accuracy
- preservation of V2 in pre-expansion regimes.

Supporting:
- balanced accuracy
- Brier
- logloss
- base routes vs expansion routes.

Inference:
- block-5 and block-10 paired moving-block bootstrap;
- COT-vintage clustered net-rescue bootstrap.

Sensitivity diagnostics only:
- expansion windows 8 and 12 using the same +/-2 regret hysteresis concept.
They may not replace the binding W10 design based on retrospective performance.

## Governance

This is second-order post-hoc strengthening research. The design was created after observing HELIOS V2 and V3-GT historical behavior.
It cannot be called prospective confirmation and cannot replace frozen AURORA without a new future-origin freeze.
