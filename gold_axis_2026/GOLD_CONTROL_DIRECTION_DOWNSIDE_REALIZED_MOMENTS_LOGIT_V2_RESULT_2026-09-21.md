# GOLD CONTROL — DOWNSIDE REALIZED-MOMENTS LOGIT V2 RESULT

**Identity:** `DIRECTION_DOWNSIDE_REALIZED_MOMENTS_LOGIT_V2_RESEARCH`  
**Parent observation:** `DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_SPOT_XAU_V1_RESEARCH`  
**Evidence:** preregistered cross-model realized-moment feature confirmation; research-only.  

## Main model metrics

| period | model | acc | BA | UP sens | DOWN sens | DOWN forecasts | Brier | freq Brier |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2023 | AR1_LOGIT | 0.4926 | 0.4949 | 0.9505 | 0.0392 | 9 | 0.2527 | 0.2509 |
| 2023 | RV_LOGIT | 0.5665 | 0.5671 | 0.6832 | 0.4510 | 78 | 0.2486 | 0.2509 |
| 2023 | RSK_LOGIT | 0.4680 | 0.4696 | 0.8020 | 0.1373 | 34 | 0.2529 | 0.2509 |
| 2023 | RM_LOGIT | 0.5468 | 0.5469 | 0.5743 | 0.5196 | 96 | 0.2508 | 0.2509 |
| 2023 | AR1_RM_LOGIT | 0.5271 | 0.5271 | 0.5347 | 0.5196 | 100 | 0.2518 | 0.2509 |
| 2024 | AR1_LOGIT | 0.5659 | 0.4938 | 0.9412 | 0.0465 | 11 | 0.2469 | 0.2470 |
| 2024 | RV_LOGIT | 0.5463 | 0.4948 | 0.8151 | 0.1744 | 37 | 0.2496 | 0.2470 |
| 2024 | RSK_LOGIT | 0.5463 | 0.4819 | 0.8824 | 0.0814 | 21 | 0.2465 | 0.2470 |
| 2024 | RM_LOGIT | 0.5122 | 0.4750 | 0.7059 | 0.2442 | 56 | 0.2491 | 0.2470 |
| 2024 | AR1_RM_LOGIT | 0.5317 | 0.4935 | 0.7311 | 0.2558 | 54 | 0.2493 | 0.2470 |
| 2025 | AR1_LOGIT | 0.5992 | 0.5135 | 0.9857 | 0.0412 | 6 | 0.2444 | 0.2449 |
| 2025 | RV_LOGIT | 0.5907 | 0.5000 | 1.0000 | 0.0000 | 0 | 0.2465 | 0.2449 |
| 2025 | RSK_LOGIT | 0.5865 | 0.5043 | 0.9571 | 0.0515 | 11 | 0.2438 | 0.2449 |
| 2025 | RM_LOGIT | 0.5823 | 0.4976 | 0.9643 | 0.0309 | 8 | 0.2457 | 0.2449 |
| 2025 | AR1_RM_LOGIT | 0.5823 | 0.4992 | 0.9571 | 0.0412 | 10 | 0.2458 | 0.2449 |

## Primary AR1+RM versus AR1 comparison

| period | delta DOWN | delta BA | delta Brier (RM-AR1) | RM-only DOWN correct | AR1-only DOWN correct | sign-test p |
|---|---:|---:|---:|---:|---:|---:|
| 2023 | +0.4804 | +0.0323 | -0.0010 | 49 | 0 | 0.0000 |
| 2024 | +0.2093 | -0.0004 | +0.0024 | 19 | 1 | 0.0000 |
| 2025 | +0.0000 | -0.0143 | +0.0014 | 3 | 3 | 1.0000 |

## Frozen decisions

- Pre-2025 feature-contribution gate: **FAIL**.
- Strong standalone direction gate: **FAIL**.
- 2025 is challenge evidence only and cannot change either pre-2025 decision.
- No runtime, production or trading authority is created by this experiment.
