# GOLD SESSION — BOCPD V1 STAGE-2 FINAL AUTHORITY

**Date:** 2026-10-07  
**Status:** **COMPLETE / TWO SESSION HEADS DEVELOPMENT-ELIGIBLE / 2025 STILL CLOSED**

Binding preregistration:
- `GOLD_SESSION_BOCPD_V1_STAGE2_PREREG_2026-10-07.md`

Result authority:
- `GOLD_SESSION_BOCPD_V1_STAGE2_RESULT_2026-10-07.md`
- `GOLD_SESSION_BOCPD_V1_STAGE2_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_BOCPD_V1_STAGE2_GATE_2026-10-07.csv`
- `GOLD_SESSION_BOCPD_V1_STAGE2_SOURCE_SENSITIVITY_2026-10-07.csv`

## Frozen identity

Canonical model remains Handoff Competence BOCPD V1:
- Jeffreys Beta(0.5,0.5);
- expected run = 4 Handoff alarms;
- ACT when predictive P(RESCUE) >= 0.60 and P(theta>0.50) >= 0.80;
- no V4 hysteresis;
- no DPTC/SELLR/RTE-family input.

State is isolated by partition/window and only matured prior Handoff outcomes update the posterior.

## 2023–2024 development verdict

### Development-eligible for a later frozen 2025 transport

1. **SOBTI Asia Afternoon / S17_A1_SESSION**
   - eligible common N: 189
   - Handoff alarms: 16
   - BOCPD ACT: 5
   - rescue/broken/net: 3 / 2 / **+1**
   - action precision: 60.0%
   - BA: 52.18% -> **52.77%**
   - source-net panel: BASE +1, SI_n +1, NQ_n +1, ZN_v 0, CL_v +2, GC_n +2, NQ_c 0
   - verdict: **PASS_SOURCE_WEAK**

2. **SOBTI NY/London / STRUCTURAL_IRIS_1H**
   - eligible common N: 215
   - Handoff alarms: 17
   - BOCPD ACT: 5
   - rescue/broken/net: 3 / 2 / **+1**
   - action precision: 60.0%
   - BA: 53.26% -> **53.74%**
   - source-net panel: BASE +1, SI_n 0, NQ_n +1, ZN_v +1, CL_v +1, GC_n +1, NQ_c +1
   - verdict: **PASS_SOURCE_WEAK**

Both pass because no alternative roll mapping turns combined net negative, but each has at least one zero-net alternative; therefore neither may be labelled fully source-robust.

### Fail closed

- Sobti Asia Morning: BASE net +1 but multiple roll mappings turn negative; **SOURCE_SENSITIVE_FAIL**.
- Sobti Europe: BASE net -1 and all seven mappings net -1; **FAIL**.
- Sobti Late-US: zero ACTs; **DEVELOPMENT_GATE_FAIL**.
- WGC Asia: BASE net -1 and source-sensitive; **FAIL**.
- WGC Europe: BASE net -1; **FAIL**.
- WGC US: BASE net -1 and all seven mappings net -1; **FAIL**.

## Governance

- 2025 was not read in Stage-2.
- 2026 was not read.
- No BOCPD threshold, hazard, source mapping, base model, or Handoff threshold changed after results.
- Only the two development-eligible Sobti heads may be opened in a later, separate Stage-3 frozen 2025 transport.
- Stage-3 is **not executed by this authority**.

**Next project step:** BOCPD Stage-3 frozen 2025 transport for the two eligible heads, or—if the execution order intentionally closes BOCPD at development first—proceed only after an explicit next-step command.
