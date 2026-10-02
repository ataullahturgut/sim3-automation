# AIM-H3 V1 — ADAPTIVE INTRADAY MIXTURE RESULT

**Status:** **NOT_PROMOTED_CONFIRM_FAIL**  
**Selected half-life:** **126** matured forecasts  
**Selected eta:** **10**  
**2023 + 2024 frozen confirmation:** **False**

## Selection grid — 2022 H2

| Half-life | Eta | Eligible | Δ accuracy | Δ balanced | Δ Brier |
|---:|---:|---|---:|---:|---:|
| 21 | 10 | True | +0.89 pp | +0.83 pp | -0.0006 |
| 21 | 20 | True | +0.89 pp | +0.83 pp | -0.0004 |
| 21 | 40 | False | +0.89 pp | +0.83 pp | +0.0000 |
| 63 | 10 | True | +0.89 pp | +0.83 pp | -0.0006 |
| 63 | 20 | True | +0.00 pp | +0.00 pp | -0.0004 |
| 63 | 40 | True | +0.00 pp | +0.00 pp | -0.0000 |
| 126 | 10 | True | +0.89 pp | +0.96 pp | -0.0006 |
| 126 | 20 | True | +0.89 pp | +0.96 pp | -0.0004 |
| 126 | 40 | True | +0.89 pp | +0.96 pp | -0.0000 |

## Period metrics

| Model | Period | N | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |
|---|---|---:|---:|---:|---:|---:|---:|
| STRUCTURAL_IRIS | SELECT_2022_H2 | 112 | 62.50% | 62.05% | 0.2317 | 55.77% | 68.33% |
| PATH_GLOBAL | SELECT_2022_H2 | 112 | 60.71% | 60.26% | 0.2323 | 53.85% | 66.67% |
| PATH_RECENT126 | SELECT_2022_H2 | 112 | 59.82% | 59.29% | 0.2352 | 51.92% | 66.67% |
| AIM | SELECT_2022_H2 | 112 | 63.39% | 63.01% | 0.2311 | 57.69% | 68.33% |
| STRUCTURAL_IRIS | 2023 | 219 | 71.23% | 71.83% | 0.2118 | 60.00% | 83.65% |
| PATH_GLOBAL | 2023 | 219 | 67.58% | 67.89% | 0.2145 | 61.74% | 74.04% |
| PATH_RECENT126 | 2023 | 219 | 63.47% | 63.42% | 0.2292 | 64.35% | 62.50% |
| AIM | 2023 | 219 | 68.49% | 68.80% | 0.2158 | 62.61% | 75.00% |
| STRUCTURAL_IRIS | 2024 | 240 | 70.83% | 69.97% | 0.2006 | 76.47% | 63.46% |
| PATH_GLOBAL | 2024 | 240 | 65.00% | 64.25% | 0.2073 | 69.85% | 58.65% |
| PATH_RECENT126 | 2024 | 240 | 63.33% | 62.90% | 0.2187 | 66.18% | 59.62% |
| AIM | 2024 | 240 | 66.67% | 65.95% | 0.2045 | 71.32% | 60.58% |
| STRUCTURAL_IRIS | 2025 | 248 | 63.71% | 62.27% | 0.2294 | 68.87% | 55.67% |
| PATH_GLOBAL | 2025 | 248 | 64.92% | 62.53% | 0.2269 | 73.51% | 51.55% |
| PATH_RECENT126 | 2025 | 248 | 59.68% | 60.07% | 0.2462 | 58.28% | 61.86% |
| AIM | 2025 | 248 | 63.71% | 62.27% | 0.2279 | 68.87% | 55.67% |
| STRUCTURAL_IRIS | 2026 | 191 | 58.64% | 59.12% | 0.2556 | 69.23% | 49.00% |
| PATH_GLOBAL | 2026 | 191 | 60.73% | 61.12% | 0.2477 | 69.23% | 53.00% |
| PATH_RECENT126 | 2026 | 191 | 58.64% | 58.82% | 0.2570 | 62.64% | 55.00% |
| AIM | 2026 | 191 | 57.07% | 57.42% | 0.2500 | 64.84% | 50.00% |
| STRUCTURAL_IRIS | 2025-2026 | 439 | 61.50% | 60.65% | 0.2408 | 69.01% | 52.28% |
| PATH_GLOBAL | 2025-2026 | 439 | 63.10% | 62.09% | 0.2360 | 71.90% | 52.28% |
| PATH_RECENT126 | 2025-2026 | 439 | 59.23% | 59.15% | 0.2509 | 59.92% | 58.38% |
| AIM | 2025-2026 | 439 | 60.82% | 60.07% | 0.2375 | 67.36% | 52.79% |

## Mean adaptive weights

| Year | Structural | Path global | Path recent126 |
|---:|---:|---:|---:|
| 2022 | 32.3% | 33.2% | 34.5% |
| 2023 | 33.6% | 34.1% | 32.3% |
| 2024 | 36.3% | 34.3% | 29.3% |
| 2025 | 35.2% | 33.9% | 30.9% |
| 2026 | 34.4% | 35.8% | 29.8% |

## 2026 rescue

- structural accuracy: **58.64%**
- AIM accuracy: **57.07%**
- rescued calls: **4**
- broken calls: **7**
- net rescue: **-3**

## Governance

AIM half-life and eta were selected only on Jul-Dec 2022. 2023 and 2024 were frozen confirmations; 2025/2026 were transport/stress. Weights at each origin used only already-matured earlier expert losses.
