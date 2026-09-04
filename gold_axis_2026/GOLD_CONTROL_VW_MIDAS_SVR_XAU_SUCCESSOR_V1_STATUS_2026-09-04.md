# Gold Control — VW MIDAS SVR XAU Successor V1 Status

**Date:** 2026-09-04  
**Identity:** `VW_MIDAS_SVR_XAU_SUCCESSOR_V1`  
**Frozen contract:** `V1_2026-09-04`  
**Evidence class:** source-readiness / engineering; **no model score produced**.

## Result

`BLOCKED_GPR_VINTAGE_PIT_NOT_PROVEN:202009:HTTP_404`

GitHub Actions evidence:

- workflow: `Gold Control VW MIDAS SVR XAU Successor V1`
- run: `33908054366`
- tested SHA: `0e2e8ad0ef372c743c2e184fe9b2c9f4aa71b534`
- governance assertions: PASS
- deterministic/PIT unit tests: PASS (`8 passed`)
- historical source gate: BLOCKED
- first failing GPR vintage: `data_gpr_export_202009.xls` -> HTTP 404
- model validation score: `NOT_RUN`
- locked diagnostic score: `NOT_RUN`
- Sep-2026 model reconstruction: `NOT_RUN`
- raw vendor market values logged: NO
- database writes: NONE
- prospective claim: FALSE

## Interpretation

This is not a model-performance failure. The pre-registered V1 contract required every origin to use the historical GPR vintage that would have been available at that origin. The first required vintage (`202009`) is not available at the frozen official URL. The engine therefore stopped before validation, exactly as specified by the frozen source gate.

The official Caldara–Iacoviello GPR site states that monthly data are updated at the beginning of each month, provides an older-vintage archive, names monthly vintage files as `data_gpr_export_YYYYMM.xls`, and warns that recent/history values may be revised. Those facts make silent substitution of the current final vintage for a missing historical vintage methodologically invalid for a PIT claim.

Authority page: `https://www.matteoiacoviello.com/gpr.htm`  
Citation: Caldara & Iacoviello (2022), *American Economic Review*, 112(4), 1194–1225.

## Binding consequence

V1 is closed as:

`SOURCE_BLOCKED_NO_MODEL_SCORE`

The V1 window, feature set and thresholds are not amended after observing this blocker.

A source-readiness-only archive probe is authorized next. If it identifies a continuous historical-vintage interval, any model using a different start date/window must be pre-registered under a **new successor version** before model scoring. If no adequate vintage interval exists, a final-vintage historical research variant may be studied only under an explicitly weaker evidence identity; it may not be called PIT/prospective-grade.

Archived production/runtime `VW_MIDAS_MSVR` remains:

`BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN`
