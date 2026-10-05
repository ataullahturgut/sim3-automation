# SILVER SHORT-HORIZON V2 — RELATIVE-VALUE RESULT

**Evidence:** DEV selection 2022-2024 only; 2025/2026 opened after frozen V2 selection.

## DEV candidates

| H | Block | Model | Accuracy | BA | Brier | Log loss |
|---|---|---|---:|---:|---:|---:|
| H5 | SILVER_PATH | LOGIT_L2 | 53.91% | 53.91% | 0.2481 | 0.6893 |
| H3 | SILVER_PATH | LOGIT_L2 | 50.73% | 50.16% | 0.2493 | 0.6918 |
| H3 | RELATIVE_VALUE | LOGIT_L2 | 50.46% | 50.07% | 0.2508 | 0.6948 |
| H5 | RELATIVE_VALUE | LOGIT_L2 | 49.93% | 49.94% | 0.2508 | 0.6949 |
| H1 | SILVER_PATH | LOGIT_L2 | 50.60% | 51.04% | 0.2510 | 0.6952 |
| H1 | RELATIVE_VALUE | LOGIT_L2 | 49.40% | 49.77% | 0.2514 | 0.6960 |
| H1 | SILVER_PATH | HGB | 49.80% | 49.72% | 0.2516 | 0.6965 |
| H5 | METAL_STATE | LOGIT_L2 | 51.66% | 51.65% | 0.2518 | 0.6972 |
| H5 | SILVER_PATH | HGB | 54.70% | 54.70% | 0.2519 | 0.6977 |
| H1 | METAL_STATE | LOGIT_L2 | 49.67% | 49.95% | 0.2525 | 0.6983 |
| H3 | METAL_STATE | LOGIT_L2 | 49.67% | 49.41% | 0.2537 | 0.7008 |
| H1 | RELATIVE_VALUE | HGB | 50.20% | 50.19% | 0.2558 | 0.7052 |
| H1 | METAL_STATE | HGB | 52.32% | 52.32% | 0.2562 | 0.7064 |
| H3 | SILVER_PATH | HGB | 51.26% | 50.78% | 0.2575 | 0.7092 |
| H5 | RELATIVE_VALUE | HGB | 50.20% | 50.19% | 0.2579 | 0.7098 |
| H5 | METAL_STATE | HGB | 50.46% | 50.45% | 0.2584 | 0.7108 |
| H3 | RELATIVE_VALUE | HGB | 47.15% | 46.70% | 0.2633 | 0.7210 |
| H3 | METAL_STATE | HGB | 46.49% | 45.84% | 0.2651 | 0.7248 |

## Frozen champion

- **H5 / SILVER_PATH / LOGIT_L2**
- DEV accuracy **53.91%**
- DEV BA **53.91%**
- DEV Brier **0.2481**
- annual stability flag **True**; DEV years BA<50% = 0

## Transport

| Mode | Year | N | Accuracy | BA | Brier | Log loss |
|---|---:|---:|---:|---:|---:|---:|
| STATIC_PRE2025 | 2025 | 253 | 43.08% | 51.78% | 0.2574 | 0.7081 |
| ADAPTIVE_ORIGIN_SAFE | 2025 | 253 | 49.41% | 55.17% | 0.2527 | 0.6986 |
| STATIC_PRE2025 | 2026 | 189 | 43.39% | 44.11% | 0.2808 | 0.7650 |
| ADAPTIVE_ORIGIN_SAFE | 2026 | 189 | 42.33% | 43.33% | 0.2758 | 0.7515 |
