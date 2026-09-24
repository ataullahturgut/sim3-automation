# GOLD CONTROL — DIRECTION ENGINE MEMORY POLICY COMPARISON V1

**Date:** 2026-09-24  
**Identity:** `DIRECTION_ENGINE_MEMORY_POLICY_COMPARISON_V1`  
**Parent evidence:** `DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1R2`  
**Scope:** SQRT-HAR-DR, pre-2025 only

## Decision rule

Primary criteria are MSE and QLIKE. High-risk AUC, alarm coverage/stability, and cross-origin consistency are mandatory guards. A single best W is not selected from the surface; the previously identified contiguous rolling band 475–550 is treated as one policy candidate.

## Policy comparison

| Policy | Mean MSE | Mean QLIKE | Mean AUC | Mean precision | Mean recall | Mean coverage |
|---|---:|---:|---:|---:|---:|---:|
| Expanding | 6.82941e-10 | 0.153923 | 0.728278 | 0.4938 | 0.2725 | 0.0960 |
| Rolling W=500 (band representative only) | 6.70263e-10 | 0.148784 | 0.726494 | 0.5316 | 0.2730 | 0.0748 |
| Break-conditioned | 6.91777e-10 | 0.148158 | 0.724286 | 0.7333 | 0.1788 | 0.0342 |

The full rolling band 475/500/525/550 improves both MSE and QLIKE versus expanding in **all three** 2022–2024 origins. W=500 is shown only as a reporting representative; this comparison does not freeze a single W.

Relative to expanding, representative W=500 changes mean MSE by **-1.86%**, QLIKE by **-3.34%**, mean AUC by **-0.0018**, precision by **+3.78 pp**, recall by approximately **+0.05 pp**, and coverage by **-2.12 pp**.

Break-conditioned history repeatedly identifies 2020-03-20, and improves mean QLIKE by about **3.75%**, but mean MSE is about **1.29% worse** than expanding. More importantly, alert counts are 10 / 1 / 10 for 2022 / 2023 / 2024. That collapse in 2023 means the very high average precision is not sufficient evidence for using it as the primary risk-memory policy.

## Frozen A3 decision

**Status: `ROBUST_ROLLING_POLICY_ADVANCES_TO_FREEZE_STAGE`**

- Advance **ROLLING BAND 475–550** to the policy-freeze stage.
- Keep **EXPANDING** as the mandatory comparator.
- Keep **BREAK-CONDITIONED** as a structural-break diagnostic / challenger, not the primary SQRT memory policy.
- Do **not** interpret W=500 as frozen yet; it is only the center/reporting representative of the robust band.
- 2025 and 2026 remain unopened for selection.

## Governance

No random split. No 2025/2026 selection. No production writes. No runtime promotion. SQRT formula/features are unchanged.
