# AURORA-H3 V1 — ASYMMETRIC UNIFIED REGIME ONLINE ROUTING RESULT

**Status:** **MECHANISM_PASS**  
**Entry:** SENTRY fast evidence (net rescue63 >= +3)  
**Exit:** DART slow Bayesian reversal evidence  
**2023 + 2024 confirmation:** **True**

## Period metrics

| Model | Period | N | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |
|---|---|---:|---:|---:|---:|---:|---:|
| STRUCTURAL_IRIS | 2022_H2 | 112 | 62.50% | 62.05% | 0.2317 | 55.77% | 68.33% |
| SENTRY | 2022_H2 | 112 | 62.50% | 62.05% | 0.2317 | 55.77% | 68.33% |
| DART | 2022_H2 | 112 | 62.50% | 62.05% | 0.2317 | 55.77% | 68.33% |
| AURORA | 2022_H2 | 112 | 62.50% | 62.05% | 0.2317 | 55.77% | 68.33% |
| STRUCTURAL_IRIS | 2023 | 219 | 71.23% | 71.83% | 0.2118 | 60.00% | 83.65% |
| SENTRY | 2023 | 219 | 71.23% | 71.83% | 0.2118 | 60.00% | 83.65% |
| DART | 2023 | 219 | 71.23% | 71.83% | 0.2118 | 60.00% | 83.65% |
| AURORA | 2023 | 219 | 71.23% | 71.83% | 0.2118 | 60.00% | 83.65% |
| STRUCTURAL_IRIS | 2024 | 240 | 70.83% | 69.97% | 0.2006 | 76.47% | 63.46% |
| SENTRY | 2024 | 240 | 70.83% | 69.97% | 0.2006 | 76.47% | 63.46% |
| DART | 2024 | 240 | 70.83% | 69.97% | 0.2006 | 76.47% | 63.46% |
| AURORA | 2024 | 240 | 70.83% | 69.97% | 0.2006 | 76.47% | 63.46% |
| STRUCTURAL_IRIS | 2025 | 248 | 63.71% | 62.27% | 0.2294 | 68.87% | 55.67% |
| SENTRY | 2025 | 248 | 64.52% | 62.93% | 0.2276 | 70.20% | 55.67% |
| DART | 2025 | 248 | 64.11% | 62.60% | 0.2303 | 69.54% | 55.67% |
| AURORA | 2025 | 248 | 64.52% | 62.93% | 0.2276 | 70.20% | 55.67% |
| STRUCTURAL_IRIS | 2026 | 191 | 58.64% | 59.12% | 0.2556 | 69.23% | 49.00% |
| SENTRY | 2026 | 191 | 60.21% | 60.71% | 0.2513 | 71.43% | 50.00% |
| DART | 2026 | 191 | 60.73% | 61.12% | 0.2477 | 69.23% | 53.00% |
| AURORA | 2026 | 191 | 60.73% | 61.12% | 0.2477 | 69.23% | 53.00% |
| STRUCTURAL_IRIS | 2025-2026 | 439 | 61.50% | 60.65% | 0.2408 | 69.01% | 52.28% |
| SENTRY | 2025-2026 | 439 | 62.64% | 61.73% | 0.2379 | 70.66% | 52.79% |
| DART | 2025-2026 | 439 | 62.64% | 61.87% | 0.2378 | 69.42% | 54.31% |
| AURORA | 2025-2026 | 439 | 62.87% | 62.07% | 0.2363 | 69.83% | 54.31% |

## Annual state

| Year | PATH share | Mean net rescue63 | Mean q_path | Mean Pr(PATH superior) |
|---:|---:|---:|---:|---:|
| 2022 | 0.0% | +0.15 | 0.540 | 0.568 |
| 2023 | 0.0% | -2.24 | 0.390 | 0.213 |
| 2024 | 0.0% | -3.30 | 0.361 | 0.182 |
| 2025 | 29.4% | -0.47 | 0.436 | 0.319 |
| 2026 | 100.0% | +1.71 | 0.681 | 0.856 |

## State switches

- 2025-09-18: STRUCTURAL_IRIS -> PATH_GLOBAL; net_rescue63=+3; q_path=0.794; Pr(PATH superior)=0.899

## 2026 rescue

- Structural accuracy: **58.64%**
- AURORA accuracy: **60.73%**
- rescued: **7**
- broken: **3**
- net rescue: **+4**
- PATH origins: **191 / 191**

## Dependence-aware bootstrap highlights

- 2026 AURORA_vs_DART accuracy (block10): diff=+0.0000 pp; 95%=[+0.0000, +0.0000] pp; P(improve)=0.0%.
- 2026 AURORA_vs_DART brier (block10): diff=+0.0000; 95%=[+0.0000, +0.0000]; P(improve)=0.0%.
- 2026 AURORA_vs_SENTRY accuracy (block10): diff=+0.5236 pp; 95%=[-1.5707, +2.6178] pp; P(improve)=59.2%.
- 2026 AURORA_vs_SENTRY brier (block10): diff=-0.0036; 95%=[-0.0077, -0.0006]; P(improve)=99.4%.
- 2026 AURORA_vs_STRUCTURAL accuracy (block10): diff=+2.0942 pp; 95%=[-1.5707, +5.7592] pp; P(improve)=84.2%.
- 2026 AURORA_vs_STRUCTURAL brier (block10): diff=-0.0079; 95%=[-0.0137, -0.0028]; P(improve)=100.0%.
- 2025-2026 AURORA_vs_DART accuracy (block10): diff=+0.2278 pp; 95%=[+0.0000, +0.6834] pp; P(improve)=63.9%.
- 2025-2026 AURORA_vs_DART brier (block10): diff=-0.0015; 95%=[-0.0041, +0.0000]; P(improve)=93.6%.
- 2025-2026 AURORA_vs_SENTRY accuracy (block10): diff=+0.2278 pp; 95%=[-0.6834, +1.1390] pp; P(improve)=58.3%.
- 2025-2026 AURORA_vs_SENTRY brier (block10): diff=-0.0016; 95%=[-0.0035, -0.0002]; P(improve)=99.2%.
- 2025-2026 AURORA_vs_STRUCTURAL accuracy (block10): diff=+1.3667 pp; 95%=[-0.6834, +3.4169] pp; P(improve)=89.7%.
- 2025-2026 AURORA_vs_STRUCTURAL brier (block10): diff=-0.0044; 95%=[-0.0087, -0.0001]; P(improve)=97.8%.

## Governance

AURORA introduces no new fitted threshold. Entry is the frozen SENTRY rule; exit is the frozen DART reversal rule. All evidence fields are causal and based only on matured prior H3 outcomes.
