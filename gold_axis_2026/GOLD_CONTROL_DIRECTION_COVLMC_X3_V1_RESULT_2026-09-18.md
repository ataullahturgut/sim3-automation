# GOLD CONTROL — DIRECTION_COVLMC_X3_V1_RESEARCH RESULT

**Date:** 2026-09-18  
**Identity:** `DIRECTION_COVLMC_X3_V1_RESEARCH`  
**Status:** `EVALUATED / NO_PROMOTION / PRE2025_COLLAPSE_TO_NEUTRAL / NOT_RUNTIME`

The direct exogenous-covariate VLMC extension was evaluated with:
- rolling 104-week Gold weekly sign history;
- DGS10 PIT, DEXCHUS PIT and GPR PIT covariates;
- origin cutoff fixed at New York 17:00;
- rolling-origin z-score scaling using only prior 104 weeks;
- R 4.4.1 + VLMCX 1.0;
- package-default alpha.level=0.05, max.depth=5, n.min=5.

Pre-2025 2024 result on the identical 44-week VLMC-104 support:
- COVLMC accuracy 0.5454545;
- balanced accuracy 0.5000000;
- 44 UP / 0 DOWN forecasts;
- P(UP)=0.5 at all 44 origins;
- DOWN sensitivity 0%;
- no fit warnings.

Parent VLMC-BS-104 on the same support:
- accuracy 0.5681818;
- balanced accuracy 0.5583333;
- DOWN sensitivity 0.45.

Thus the default reference COVLMC prunes/collapses to a neutral 0.5 prediction on this short sample and fails before 2025.

Post-diagnostic 2025 replay is retained only for completeness:
- 52 UP / 0 DOWN;
- raw accuracy 0.7115385 (exactly the always-UP baseline);
- balanced accuracy 0.50;
- DOWN sensitivity 0%.

No parameter rescue is authorized under this identity.
