# SILVER SHORT-HORIZON V1 — TARGET / BASELINE RESULT

**Identity:** `GLOBAL_XAG_PUBLIC_STAKTRAKR_V1`  
**Pinned source:** `54fdf1c8d39b7b6c7b874d0f30f784296e886044`  
**Common-metal coverage:** 2010-01-04 .. 2026-09-28 (n=4232)

## DEV 2022-2024

| H | Block | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| H1 | SILVER_ONLY | 755 | 50.60% | 51.04% | 0.2510 | 0.6952 | 36.50% | 65.57% |
| H1 | CORE3 | 755 | 51.39% | 51.79% | 0.2510 | 0.6952 | 38.82% | 64.75% |
| H1 | CORE4 | 755 | 51.26% | 51.58% | 0.2514 | 0.6960 | 40.87% | 62.30% |
| H3 | SILVER_ONLY | 755 | 50.73% | 50.16% | 0.2493 | 0.6918 | 65.05% | 35.26% |
| H3 | CORE3 | 755 | 50.33% | 49.86% | 0.2506 | 0.6944 | 62.24% | 37.47% |
| H3 | CORE4 | 755 | 50.73% | 50.23% | 0.2507 | 0.6946 | 63.27% | 37.19% |
| H5 | SILVER_ONLY | 755 | 53.91% | 53.91% | 0.2481 | 0.6893 | 55.29% | 52.52% |
| H5 | CORE3 | 755 | 51.79% | 51.78% | 0.2490 | 0.6911 | 55.56% | 48.01% |
| H5 | CORE4 | 755 | 50.73% | 50.72% | 0.2501 | 0.6933 | 55.29% | 46.15% |

## Frozen DEV selection

- Horizon: **H5**
- Feature block: **SILVER_ONLY**
- DEV accuracy: **53.91%**
- DEV balanced accuracy: **53.91%**
- DEV Brier: **0.2481**

## 2025 / 2026 transport opened only after DEV selection

| Mode | Year | N | Accuracy | Balanced acc | Brier | Log loss |
|---|---:|---:|---:|---:|---:|---:|
| STATIC_PRE2025 | 2025 | 253 | 43.08% | 51.78% | 0.2574 | 0.7081 |
| ADAPTIVE_ORIGIN_SAFE | 2025 | 253 | 49.41% | 55.17% | 0.2527 | 0.6986 |
| STATIC_PRE2025 | 2026 | 189 | 43.39% | 44.11% | 0.2808 | 0.7650 |
| ADAPTIVE_ORIGIN_SAFE | 2026 | 189 | 42.33% | 43.33% | 0.2758 | 0.7515 |

## Governance

The horizon/block winner is selected from 2022-2024 only. 2025/2026 results are report-only transport evidence and may not change V1 configuration.
