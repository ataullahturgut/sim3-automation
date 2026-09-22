# GOLD CONTROL — SELECTIVE TRIAGE V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `DOWNSIDE_SELECTIVE_TRIAGE_V1_RESEARCH`  
**Status class:** EXPLORATORY / POST-RESULT-DESIGNED / NOT CONFIRMATORY  
**Manifest update:** FORBIDDEN  
**Runtime / production authority:** NONE

## Goal

Do not force every primary SQRT-HAR-DR alarm into a binary DOWN / NOT-DOWN verdict.

Reuse the two frozen heterogeneous verifiers:
- path-morphology CBR-DTW probability `p_path`;
- SP500 cross-market context probability `p_sp`.

Three-way triage:
- **CONFIRM_DOWN** if `p_path>=0.50 AND p_sp>=0.50`;
- **VETO_SUSPECT** if `p_path<0.50 AND p_sp<0.50`;
- **UNCERTAIN** otherwise.

No threshold tuning.

Report for each year:
- group counts and coverage;
- actual next-day DOWN rate within each group;
- CONFIRM precision;
- VETO false-negative rate;
- UNCERTAIN DOWN rate;
- separation `DOWN_rate(CONFIRM)-DOWN_rate(VETO)`.

This identity is descriptive/exploratory because it was designed after seeing the two component verifier results.