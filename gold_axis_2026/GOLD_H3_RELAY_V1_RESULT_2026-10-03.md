# RELAY-H3 V1 — REGIME-ADAPTIVE OPTIONS-RESCUE TRUST ROUTER RESULT

**Status:** **MECHANISM_PASS**  
**Evidence class:** retrospective mechanism validation; architecture was motivated after OPAL historical behavior was observed.  
**Trust BOCPD:** hazard 1/20; enter Pr>=0.90 & q>=0.60; exit Pr<=0.10 & q<=0.40.

## Period metrics

| Model | Period | N | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |
|---|---|---:|---:|---:|---:|---:|---:|
| AURORA | 2022_H2 | 33 | 57.58% | 58.27% | 0.2567 | 55.00% | 61.54% |
| OPAL | 2022_H2 | 33 | 57.58% | 62.31% | 0.2707 | 40.00% | 84.62% |
| RELAY | 2022_H2 | 33 | 57.58% | 58.27% | 0.2567 | 55.00% | 61.54% |
| AURORA | 2023 | 219 | 71.23% | 71.83% | 0.2118 | 60.00% | 83.65% |
| OPAL | 2023 | 219 | 67.12% | 67.41% | 0.2303 | 61.74% | 73.08% |
| RELAY | 2023 | 219 | 71.23% | 71.83% | 0.2118 | 60.00% | 83.65% |
| AURORA | 2024 | 240 | 70.83% | 69.97% | 0.2006 | 76.47% | 63.46% |
| OPAL | 2024 | 240 | 70.00% | 67.99% | 0.2070 | 83.09% | 52.88% |
| RELAY | 2024 | 240 | 70.83% | 69.97% | 0.2006 | 76.47% | 63.46% |
| AURORA | 2025 | 248 | 64.52% | 62.93% | 0.2276 | 70.20% | 55.67% |
| OPAL | 2025 | 248 | 64.92% | 61.42% | 0.2330 | 77.48% | 45.36% |
| RELAY | 2025 | 248 | 64.52% | 62.93% | 0.2276 | 70.20% | 55.67% |
| AURORA | 2026 | 191 | 60.73% | 61.12% | 0.2477 | 69.23% | 53.00% |
| OPAL | 2026 | 191 | 63.87% | 64.21% | 0.2452 | 71.43% | 57.00% |
| RELAY | 2026 | 191 | 61.26% | 61.66% | 0.2522 | 70.33% | 53.00% |
| AURORA | 2025-2026 | 439 | 62.87% | 62.07% | 0.2363 | 69.83% | 54.31% |
| OPAL | 2025-2026 | 439 | 64.46% | 63.24% | 0.2383 | 75.21% | 51.27% |
| RELAY | 2025-2026 | 439 | 63.10% | 62.28% | 0.2383 | 70.25% | 54.31% |

## Trust state by year

| Year | OPAL-trusted share | Mean q(OPAL win) | Mean Pr(OPAL superior) | Matured override events |
|---:|---:|---:|---:|---:|
| 2022 | 0.0% | 0.392 | 0.328 | 7 |
| 2023 | 0.0% | 0.366 | 0.205 | 35 |
| 2024 | 0.0% | 0.413 | 0.221 | 54 |
| 2025 | 0.0% | 0.484 | 0.403 | 78 |
| 2026 | 20.9% | 0.619 | 0.700 | 102 |

## Trust-state switches

- 2026-08-03: AURORA_ONLY -> OPAL_TRUSTED; q=0.762; Pr=0.922; events=83

## 2026 rescue

- AURORA accuracy: **60.73%**
- RELAY accuracy: **61.26%**
- rescued: **10**
- broken: **9**
- net rescue: **+1**
- OPAL-trusted origins: **40 / 191**

## Dependence-aware bootstrap

- 2023-2024 accuracy block5: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- 2023-2024 accuracy block10: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- 2023-2024 brier block5: diff=+0.0000; 95%=[+0.0000,+0.0000]; P(improve)=0.0%.
- 2023-2024 brier block10: diff=+0.0000; 95%=[+0.0000,+0.0000]; P(improve)=0.0%.
- 2023-2024 logloss block5: diff=+0.0000; 95%=[+0.0000,+0.0000]; P(improve)=0.0%.
- 2023-2024 logloss block10: diff=+0.0000; 95%=[+0.0000,+0.0000]; P(improve)=0.0%.
- 2025-2026 accuracy block5: diff=+0.2278 pp; 95%=[-1.5945,+2.0501] pp; P(improve)=54.6%.
- 2025-2026 accuracy block10: diff=+0.2278 pp; 95%=[-1.5945,+1.8223] pp; P(improve)=55.7%.
- 2025-2026 brier block5: diff=+0.0020; 95%=[-0.0045,+0.0092]; P(improve)=29.5%.
- 2025-2026 brier block10: diff=+0.0020; 95%=[-0.0037,+0.0094]; P(improve)=29.5%.
- 2025-2026 logloss block5: diff=+0.0058; 95%=[-0.0090,+0.0233]; P(improve)=24.6%.
- 2025-2026 logloss block10: diff=+0.0058; 95%=[-0.0073,+0.0233]; P(improve)=24.5%.
- 2026 accuracy block5: diff=+0.5236 pp; 95%=[-3.6649,+4.7120] pp; P(improve)=55.2%.
- 2026 accuracy block10: diff=+0.5236 pp; 95%=[-3.1414,+4.1885] pp; P(improve)=55.7%.
- 2026 brier block5: diff=+0.0046; 95%=[-0.0107,+0.0214]; P(improve)=30.2%.
- 2026 brier block10: diff=+0.0046; 95%=[-0.0086,+0.0212]; P(improve)=29.4%.
- 2026 logloss block5: diff=+0.0133; 95%=[-0.0224,+0.0527]; P(improve)=24.7%.
- 2026 logloss block10: diff=+0.0133; 95%=[-0.0173,+0.0535]; P(improve)=24.9%.

## Governance

RELAY introduces no new tuned detector parameter; it reuses DART's frozen BOCPD hazard and symmetric trust thresholds. Only matured OPAL-vs-AURORA direction-changing events update trust. Existing frozen AURORA prospective validation is unchanged.
