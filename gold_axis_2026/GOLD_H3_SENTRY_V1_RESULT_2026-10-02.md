# SENTRY-H3 V1 — CAUSAL EXPERT FAILOVER RESULT

**Status:** **MECHANISM_PASS**  
**Rule:** last 63 matured calls; enter PATH at net rescue >= +3; return STRUCTURAL at <= 0.  
**2023 + 2024 confirmation:** **True**

## Period metrics

| Model | Period | N | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |
|---|---|---:|---:|---:|---:|---:|---:|
| STRUCTURAL_IRIS | 2022_H2 | 112 | 62.50% | 62.05% | 0.2317 | 55.77% | 68.33% |
| PATH_GLOBAL | 2022_H2 | 112 | 60.71% | 60.26% | 0.2323 | 53.85% | 66.67% |
| SENTRY | 2022_H2 | 112 | 62.50% | 62.05% | 0.2317 | 55.77% | 68.33% |
| STRUCTURAL_IRIS | 2023 | 219 | 71.23% | 71.83% | 0.2118 | 60.00% | 83.65% |
| PATH_GLOBAL | 2023 | 219 | 67.58% | 67.89% | 0.2145 | 61.74% | 74.04% |
| SENTRY | 2023 | 219 | 71.23% | 71.83% | 0.2118 | 60.00% | 83.65% |
| STRUCTURAL_IRIS | 2024 | 240 | 70.83% | 69.97% | 0.2006 | 76.47% | 63.46% |
| PATH_GLOBAL | 2024 | 240 | 65.00% | 64.25% | 0.2073 | 69.85% | 58.65% |
| SENTRY | 2024 | 240 | 70.83% | 69.97% | 0.2006 | 76.47% | 63.46% |
| STRUCTURAL_IRIS | 2025 | 248 | 63.71% | 62.27% | 0.2294 | 68.87% | 55.67% |
| PATH_GLOBAL | 2025 | 248 | 64.92% | 62.53% | 0.2269 | 73.51% | 51.55% |
| SENTRY | 2025 | 248 | 64.52% | 62.93% | 0.2276 | 70.20% | 55.67% |
| STRUCTURAL_IRIS | 2026 | 191 | 58.64% | 59.12% | 0.2556 | 69.23% | 49.00% |
| PATH_GLOBAL | 2026 | 191 | 60.73% | 61.12% | 0.2477 | 69.23% | 53.00% |
| SENTRY | 2026 | 191 | 60.21% | 60.71% | 0.2513 | 71.43% | 50.00% |
| STRUCTURAL_IRIS | 2025-2026 | 439 | 61.50% | 60.65% | 0.2408 | 69.01% | 52.28% |
| PATH_GLOBAL | 2025-2026 | 439 | 63.10% | 62.09% | 0.2360 | 71.90% | 52.28% |
| SENTRY | 2025-2026 | 439 | 62.64% | 61.73% | 0.2379 | 70.66% | 52.79% |

## PATH state share

| Year | PATH share | Mean net rescue63 | Median net rescue63 |
|---:|---:|---:|---:|
| 2022 | 0.0% | +0.15 | +1.0 |
| 2023 | 0.0% | -2.24 | -2.0 |
| 2024 | 0.0% | -3.30 | -3.0 |
| 2025 | 29.4% | -0.47 | -1.0 |
| 2026 | 41.9% | +1.71 | +1.0 |

## State switches

- 2025-09-18: STRUCTURAL_IRIS -> PATH_GLOBAL; net_rescue63=+3
- 2026-04-24: PATH_GLOBAL -> STRUCTURAL_IRIS; net_rescue63=+0

## 2026 rescue

- structural accuracy: **58.64%**
- SENTRY accuracy: **60.21%**
- rescued calls: **4**
- broken calls: **1**
- net rescue: **+3**
- PATH-active origins: **80 / 191**

## Governance

The failover rule was fixed before this run and was not optimized on 2023-2026 outcomes. All switches use only already-matured paired historical H3 correctness.
