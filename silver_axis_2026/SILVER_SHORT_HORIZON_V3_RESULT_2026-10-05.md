# SILVER SHORT-HORIZON V3 — MACRO/RISK RESULT

**DEV selection uses 2022-2024 only. 2025/2026 transport is opened only after the V3 winner is frozen.**

| Block | Model | Accuracy | BA | Brier | Log loss |
|---|---|---:|---:|---:|---:|
| RATES | LOGIT_L2 | 53.25% | 53.25% | 0.2472 | 0.6876 |
| BASE | LOGIT_L2 | 53.91% | 53.91% | 0.2481 | 0.6893 |
| MACRO_RISK | LOGIT_L2 | 52.58% | 52.58% | 0.2483 | 0.6897 |
| FX | LOGIT_L2 | 52.72% | 52.71% | 0.2490 | 0.6912 |
| RISK | LOGIT_L2 | 51.26% | 51.25% | 0.2495 | 0.6922 |
| BASE | HGB | 54.70% | 54.70% | 0.2519 | 0.6977 |
| MACRO_RISK | HGB | 54.70% | 54.70% | 0.2522 | 0.6983 |
| FX | HGB | 51.13% | 51.12% | 0.2546 | 0.7039 |
| RATES | HGB | 51.66% | 51.65% | 0.2556 | 0.7055 |
| RISK | HGB | 49.54% | 49.53% | 0.2562 | 0.7070 |

## Frozen V3 champion

- **BASE / LOGIT_L2**
- DEV accuracy **53.91%**
- DEV BA **53.91%**
- DEV Brier **0.2481**
- annual stability **True**, years BA<50% = 0

## Transport

| Mode | Year | N | Accuracy | BA | Brier | Log loss |
|---|---:|---:|---:|---:|---:|---:|
| STATIC_PRE2025 | 2025 | 253 | 43.08% | 51.78% | 0.2574 | 0.7081 |
| ADAPTIVE_ORIGIN_SAFE | 2025 | 253 | 49.41% | 55.17% | 0.2527 | 0.6986 |
| STATIC_PRE2025 | 2026 | 189 | 43.39% | 44.11% | 0.2808 | 0.7650 |
| ADAPTIVE_ORIGIN_SAFE | 2026 | 189 | 42.33% | 43.33% | 0.2758 | 0.7515 |
