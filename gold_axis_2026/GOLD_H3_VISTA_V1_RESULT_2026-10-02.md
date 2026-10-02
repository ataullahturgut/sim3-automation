# VISTA-H3 V1 — VOLATILITY-INFORMED STATE-TRANSITION RESULT

**Status:** **MECHANISM_PASS**  
**Dynamic hazard:** 0.05 * exp(k*(shock-0.5)), clipped [0.02, 0.125]  
**2023 + 2024 confirmation:** **True**

## Period metrics

| Model | Period | N | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |
|---|---|---:|---:|---:|---:|---:|---:|
| STRUCTURAL_IRIS | 2022_H2 | 112 | 62.50% | 62.05% | 0.2317 | 55.77% | 68.33% |
| SENTRY | 2022_H2 | 112 | 62.50% | 62.05% | 0.2317 | 55.77% | 68.33% |
| DART | 2022_H2 | 112 | 62.50% | 62.05% | 0.2317 | 55.77% | 68.33% |
| VISTA | 2022_H2 | 112 | 62.50% | 62.05% | 0.2317 | 55.77% | 68.33% |
| STRUCTURAL_IRIS | 2023 | 219 | 71.23% | 71.83% | 0.2118 | 60.00% | 83.65% |
| SENTRY | 2023 | 219 | 71.23% | 71.83% | 0.2118 | 60.00% | 83.65% |
| DART | 2023 | 219 | 71.23% | 71.83% | 0.2118 | 60.00% | 83.65% |
| VISTA | 2023 | 219 | 71.23% | 71.83% | 0.2118 | 60.00% | 83.65% |
| STRUCTURAL_IRIS | 2024 | 240 | 70.83% | 69.97% | 0.2006 | 76.47% | 63.46% |
| SENTRY | 2024 | 240 | 70.83% | 69.97% | 0.2006 | 76.47% | 63.46% |
| DART | 2024 | 240 | 70.83% | 69.97% | 0.2006 | 76.47% | 63.46% |
| VISTA | 2024 | 240 | 70.83% | 69.97% | 0.2006 | 76.47% | 63.46% |
| STRUCTURAL_IRIS | 2025 | 248 | 63.71% | 62.27% | 0.2294 | 68.87% | 55.67% |
| SENTRY | 2025 | 248 | 64.52% | 62.93% | 0.2276 | 70.20% | 55.67% |
| DART | 2025 | 248 | 64.11% | 62.60% | 0.2303 | 69.54% | 55.67% |
| VISTA | 2025 | 248 | 64.11% | 62.60% | 0.2303 | 69.54% | 55.67% |
| STRUCTURAL_IRIS | 2026 | 191 | 58.64% | 59.12% | 0.2556 | 69.23% | 49.00% |
| SENTRY | 2026 | 191 | 60.21% | 60.71% | 0.2513 | 71.43% | 50.00% |
| DART | 2026 | 191 | 60.73% | 61.12% | 0.2477 | 69.23% | 53.00% |
| VISTA | 2026 | 191 | 60.73% | 61.12% | 0.2477 | 69.23% | 53.00% |
| STRUCTURAL_IRIS | 2025-2026 | 439 | 61.50% | 60.65% | 0.2408 | 69.01% | 52.28% |
| SENTRY | 2025-2026 | 439 | 62.64% | 61.73% | 0.2379 | 70.66% | 52.79% |
| DART | 2025-2026 | 439 | 62.64% | 61.87% | 0.2378 | 69.42% | 54.31% |
| VISTA | 2025-2026 | 439 | 62.64% | 61.87% | 0.2378 | 69.42% | 54.31% |

## Annual state / hazard

| Year | PATH share | Mean shock | Mean hazard | P90 hazard | Mean Pr(PATH superior) |
|---:|---:|---:|---:|---:|---:|
| 2022 | 0.0% | 0.504 | 0.0560 | 0.1025 | 0.583 |
| 2023 | 0.0% | 0.437 | 0.0493 | 0.0852 | 0.211 |
| 2024 | 0.0% | 0.528 | 0.0567 | 0.0905 | 0.178 |
| 2025 | 22.2% | 0.576 | 0.0614 | 0.0954 | 0.307 |
| 2026 | 100.0% | 0.678 | 0.0710 | 0.0972 | 0.819 |

## State switches

- 2025-10-14: STRUCTURAL_IRIS -> PATH_GLOBAL; shock=0.915; hazard=0.1026; q_path=0.823; Pr(PATH superior)=0.932

## 2026 rescue

- Structural accuracy: **58.64%**
- VISTA accuracy: **60.73%**
- rescued: **7**
- broken: **3**
- net rescue: **+4**
- PATH origins: **191 / 191**

## Dependence-aware bootstrap highlights

- 2026 VISTA_vs_DART accuracy (block10): diff=+0.0000 pp; 95%=[+0.0000, +0.0000] pp; P(improve)=0.0%.
- 2026 VISTA_vs_DART brier (block10): diff=+0.0000; 95%=[+0.0000, +0.0000]; P(improve)=0.0%.
- 2026 VISTA_vs_SENTRY accuracy (block10): diff=+0.5236 pp; 95%=[-1.5707, +2.6178] pp; P(improve)=59.2%.
- 2026 VISTA_vs_SENTRY brier (block10): diff=-0.0036; 95%=[-0.0077, -0.0006]; P(improve)=99.4%.
- 2026 VISTA_vs_STRUCTURAL accuracy (block10): diff=+2.0942 pp; 95%=[-1.5707, +5.7592] pp; P(improve)=84.2%.
- 2026 VISTA_vs_STRUCTURAL brier (block10): diff=-0.0079; 95%=[-0.0137, -0.0028]; P(improve)=100.0%.
- 2025-2026 VISTA_vs_DART accuracy (block10): diff=+0.0000 pp; 95%=[+0.0000, +0.0000] pp; P(improve)=0.0%.
- 2025-2026 VISTA_vs_DART brier (block10): diff=+0.0000; 95%=[+0.0000, +0.0000]; P(improve)=0.0%.
- 2025-2026 VISTA_vs_SENTRY accuracy (block10): diff=+0.0000 pp; 95%=[-1.1390, +1.1390] pp; P(improve)=42.0%.
- 2025-2026 VISTA_vs_SENTRY brier (block10): diff=-0.0001; 95%=[-0.0027, +0.0029]; P(improve)=55.5%.
- 2025-2026 VISTA_vs_STRUCTURAL accuracy (block10): diff=+1.1390 pp; 95%=[-0.6834, +3.1891] pp; P(improve)=85.5%.
- 2025-2026 VISTA_vs_STRUCTURAL brier (block10): diff=-0.0029; 95%=[-0.0065, +0.0008]; P(improve)=94.0%.

## Governance

VISTA changes only the BOCPD hazard prior. Expert probabilities, disagreement outcomes, and DART state thresholds are frozen. Shock percentiles use only prior 16:00 anchors. 2025/2026 did not tune V1.
