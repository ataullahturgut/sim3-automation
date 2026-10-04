# OPA-H3 V2 — MOMENTUM-OPPOSED OPTIONS POSITIONING TRANSITION PREREGISTRATION

**Date:** 2026-10-04  
**Identity:** `OPA_H3_V2_TRANSITION`  
**Parent:** OPA-H3 V1 DEV failure  
**Binding champion:** `SAGE_H3_V2_EXCEPTION_ONLY`

## Rationale

OPA V1 showed that a generic linear mixture of aggregate Gold CALL/PUT OI and volume features is not selective enough.

V2 tests a narrower mechanism: a rapid option-positioning transition *against the currently prevailing XAU momentum direction*.

For momentum sign `m = +1` for UP and `m = -1` for DOWN:

- `oi_opp = -m * Δlog(call_OI / put_OI)`
- `vol_opp = -m * Δlog(call_volume / put_volume)`
- `level_opp = -m * log(call_OI / put_OI)`

Positive values mean the options-positioning state moves against the current momentum direction.

## Frozen rule family

DEV 2023-2024 only.

Quantile grid for `oi_opp`: `[0.70, 0.80, 0.85, 0.90, 0.95]`.

Four mechanism rules are evaluated:

A. `OI_EXTREME`: oi_opp >= DEV quantile  
B. `OI_EXTREME_VOL_CONFIRM`: oi_opp >= quantile AND vol_opp > 0  
C. `OI_EXTREME_LEVEL_CONFIRM`: oi_opp >= quantile AND level_opp > 0  
D. `OI_EXTREME_DUAL_CONFIRM`: oi_opp >= quantile AND vol_opp > 0 AND level_opp > 0

No other features or thresholds may be searched.

## Eligibility and selection

Universe:
- HELIOS V5 follows frozen momentum.

Target:
- V5 rescue target = 1 if V5 direction is wrong.

A DEV rule is eligible only if:
- actions >= 8
- action rate <= 20%
- precision >= 55%
- net rescue >= +2

Selection:
1. highest net rescue
2. highest precision
3. highest rescue count
4. lower action rate
5. higher quantile
6. rule order D, B, C, A

No eligible rule => `OPA_V2_DEV_FAIL`.

## 2025 untouched confirmation

Frozen selected rule passes only if, excluding existing SAGE V2 OCS overlaps:
- >= 2 rescues
- net rescue > 0
- precision >= 50%
- SAGE V2+OPA accuracy >= SAGE V2 on identical covered origins

Only then may 2026 be opened.

## 2026

Because the official CME FTP preliminary-OI schema currently has validated historical coverage only through 2026-03-19, any 2026 result is explicitly a **covered partial holdout**, not a full-year 2026 claim.

No 2026 outcome may alter V2.
