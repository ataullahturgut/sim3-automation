# GOLD CONTROL — DISCRETE-BURR LACD-POT EXTREME-DOWN HAZARD XAU V1R2 PREREGISTRATION

**Date:** 2026-09-21  
**Identity:** `DOWNSIDE_DISCRETE_BURR_LACDPOT_HAZARD_XAU_V1R2_RESEARCH`  
**Reason for new identity:** post-run authority audit found the R1 long daily StakTrakr return axis had only 0.3396 return correlation and 60.12% sign agreement with the governed NY17 research axis over 2024–2025. R1 is therefore not accepted as the authoritative Gold Control test of the ACD-POT hypothesis.  
**Change from R1:** input source only. Model equations, threshold quantile, chronology, estimation, alert rule and gates are unchanged.  
**Primary data provider:** Twelve Data `XAU/USD`, interval `1day`, requested timezone `America/New_York`.  
**Manifest update:** DEFERRED UNTIL USER REVIEWS RESULTS.  
**Production writes:** NONE.

## Frozen contract

- daily close from true provider daily bars; no synthesized OHLC/close;
- requested history: 2010-01-01 through required evaluation end;
- Monday-Friday only;
- loss `L_t=-log(C_t/C_(t-1))`;
- formation through 2023-12-31;
- extreme threshold = formation nearest-rank 95th percentile of negated returns;
- discrete-Burr LACD duration hazard exactly as frozen in R1;
- formation hazard nearest-rank 95th percentile = fixed alert threshold;
- 2024 fixed validation;
- unchanged 2025 locked challenge;
- no threshold, distribution, optimizer, parameter-bound, or gate changes from R1.

The same R1 research gates apply.

R2 exists solely to correct the input authority/clock problem; it is not a post-result parameter rescue.
