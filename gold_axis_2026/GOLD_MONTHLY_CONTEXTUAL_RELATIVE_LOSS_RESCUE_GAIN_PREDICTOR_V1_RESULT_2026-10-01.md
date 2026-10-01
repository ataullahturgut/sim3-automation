# GOLD MONTHLY — Contextual Relative-Loss / Rescue-Gain Predictor V1 Result

**Date:** 2026-10-01  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS / ROBUSTNESS=WEAK / DEV-ONLY / NO PRODUCTION SWITCH

## Authority and execution

Authority:
- `GOLD_MONTHLY_CONTEXTUAL_RELATIVE_LOSS_RESCUE_GAIN_PREDICTOR_V1_AUTHORITY_2026-10-01.md`
- authority commit: `10638e7a0849449fb1bb3655ea678e63450cd601`

Corrected Stage-1 source:
- run: **36847468918**
- artifact: **11154006919**
- commit: `cd0f24fb79deeadc0ffc34bd27b7a723a314f4a8`
- correction: semantic regime confidence was added to the Stage-1 output schema; Stage-1 numerical rescue checkpoints remained unchanged.

Predictor execution:
- run: **36847543031**
- artifact: **11154625268**
- head commit: `42f7c38719dc46a2c3f5d45f9a8352584a7e5e09`
- conclusion: **SUCCESS**

## Chronological DEV evaluation

Frozen protocol:
- first **8 DEV targets** = warm-up;
- chronological evaluation: **2022-12..2024-12**;
- evaluated frozen Specialist Hedge warning months: **14**;
- 2025/2026 not used for feature, alpha, model, or policy selection.

DEV research leader:
- predictor: **RIDGE_CORE_A10**
- policy: **DIRECT_SWITCH**
- KEEP MAIN ΣAE: **782.7432 USD**
- selector ΣAE: **778.0388 USD**
- gain versus KEEP: **+4.7044 USD**
- actions: **13 SWITCH / 1 KEEP**
- beneficial non-KEEP actions: **5**
- harmful non-KEEP actions: **8**
- worst incremental harm: **31.6639 USD**

Same-window best fixed challenger was still worse than KEEP:
- CNN-LSTM LB6 gain versus KEEP: approximately **-1.26 USD**.

## Interpretation

The formal pre-registered gate is positive because chronological selector ΣAE is lower than KEEP MAIN. However, the margin is only **4.70 USD**, harmful switches outnumber beneficial switches, and the selector switches on almost every warning.

Therefore this is a **WEAK research pass**, not evidence for an operational automatic switch.

No production rule is authorized.
