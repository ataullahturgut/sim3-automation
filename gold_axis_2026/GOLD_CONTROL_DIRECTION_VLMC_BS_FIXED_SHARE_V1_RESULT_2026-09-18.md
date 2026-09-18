# GOLD CONTROL — DIRECTION_VLMC_BS_FIXED_SHARE_V1_RESEARCH RESULT

**Date:** 2026-09-18  
**Identity:** `DIRECTION_VLMC_BS_FIXED_SHARE_V1_RESEARCH`  
**Status:** `EVALUATED / NO_PROMOTION / 2025_DEGRADATION / NOT_RUNTIME`

Fixed-Share was tested as a literature-grounded response to the instability of the best VLMC-BS rolling window across regimes.

Frozen pre-2025 selection:
- experts: corrected VLMC-BS-26 and VLMC-BS-52;
- expert loss: zero-one direction loss;
- eta = 1.0;
- alpha = 0.05;
- selected on 2023 common development only;
- 2024 validation not used for tuning;
- 2025 not used for tuning.

Results:
- 2023 development: accuracy 0.6046512, balanced accuracy 0.6184211;
- 2024 validation: accuracy 0.6792453, balanced accuracy 0.6780627, DOWN sensitivity 0.6153846;
- locked 2025 replay: accuracy 0.4807692, balanced accuracy 0.3972973, DOWN sensitivity 0.2000000, 3/15 DOWN weeks captured.

Conclusion:
the online expert-tracking layer does not solve the 2025 generalization failure. It materially degrades the corrected standalone VLMC-BS family in 2025 and is not promoted. No further Fixed-Share tuning is authorized under this identity.
