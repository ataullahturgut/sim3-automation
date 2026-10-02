# HERA-H3 V1 — HIERARCHICAL EXHAUSTION-REVERSAL ADAPTER RESULT

**Status:** **MECHANISM_PASS**  
**Evidence class:** retrospective mechanism validation; architecture was motivated after historical OPAL regime dependence was observed.  
**Rule:** AURORA STRUCTURAL_IRIS -> AURORA; AURORA PATH_GLOBAL -> OPAL.

## Period metrics

| Model | Period | N | Accuracy | Balanced acc | Brier | UP recall | DOWN recall | PATH share |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| AURORA | 2022_H2 | 33 | 57.58% | 58.27% | 0.2567 | 55.00% | 61.54% | 0.0% |
| OPAL | 2022_H2 | 33 | 57.58% | 62.31% | 0.2707 | 40.00% | 84.62% | 0.0% |
| HERA | 2022_H2 | 33 | 57.58% | 58.27% | 0.2567 | 55.00% | 61.54% | 0.0% |
| AURORA | 2023 | 219 | 71.23% | 71.83% | 0.2118 | 60.00% | 83.65% | 0.0% |
| OPAL | 2023 | 219 | 67.12% | 67.41% | 0.2303 | 61.74% | 73.08% | 0.0% |
| HERA | 2023 | 219 | 71.23% | 71.83% | 0.2118 | 60.00% | 83.65% | 0.0% |
| AURORA | 2024 | 240 | 70.83% | 69.97% | 0.2006 | 76.47% | 63.46% | 0.0% |
| OPAL | 2024 | 240 | 70.00% | 67.99% | 0.2070 | 83.09% | 52.88% | 0.0% |
| HERA | 2024 | 240 | 70.83% | 69.97% | 0.2006 | 76.47% | 63.46% | 0.0% |
| AURORA | 2025 | 248 | 64.52% | 62.93% | 0.2276 | 70.20% | 55.67% | 29.4% |
| OPAL | 2025 | 248 | 64.92% | 61.42% | 0.2330 | 77.48% | 45.36% | 29.4% |
| HERA | 2025 | 248 | 65.73% | 63.74% | 0.2248 | 72.85% | 54.64% | 29.4% |
| AURORA | 2026 | 191 | 60.73% | 61.12% | 0.2477 | 69.23% | 53.00% | 100.0% |
| OPAL | 2026 | 191 | 63.87% | 64.21% | 0.2452 | 71.43% | 57.00% | 100.0% |
| HERA | 2026 | 191 | 63.87% | 64.21% | 0.2452 | 71.43% | 57.00% | 100.0% |
| AURORA | 2025-2026 | 439 | 62.87% | 62.07% | 0.2363 | 69.83% | 54.31% | 60.1% |
| OPAL | 2025-2026 | 439 | 64.46% | 63.24% | 0.2383 | 75.21% | 51.27% | 60.1% |
| HERA | 2025-2026 | 439 | 64.92% | 64.08% | 0.2337 | 72.31% | 55.84% | 60.1% |

## Changed calls

- 2025: 5 changed; 4 rescued / 1 broken.
- 2026: 24 changed; 15 rescued / 9 broken.

## Dependence-aware bootstrap

- 2025 HERA_vs_AURORA accuracy block5: diff=+1.2097 pp; 95%=[+0.0000,+2.8226] pp; P(improve)=93.7%.
- 2025 HERA_vs_AURORA accuracy block10: diff=+1.2097 pp; 95%=[+0.0000,+2.8226] pp; P(improve)=93.8%.
- 2025 HERA_vs_AURORA brier block5: diff=-0.0028; 95%=[-0.0068,+0.0002]; P(improve)=94.4%.
- 2025 HERA_vs_AURORA brier block10: diff=-0.0028; 95%=[-0.0069,+0.0002]; P(improve)=94.0%.
- 2025 HERA_vs_AURORA logloss block5: diff=-0.0060; 95%=[-0.0145,+0.0005]; P(improve)=93.5%.
- 2025 HERA_vs_AURORA logloss block10: diff=-0.0060; 95%=[-0.0145,+0.0003]; P(improve)=94.2%.
- 2025 HERA_vs_OPAL accuracy block5: diff=+0.8065 pp; 95%=[-2.4194,+4.0323] pp; P(improve)=63.8%.
- 2025 HERA_vs_OPAL accuracy block10: diff=+0.8065 pp; 95%=[-2.0161,+3.6290] pp; P(improve)=64.5%.
- 2025 HERA_vs_OPAL brier block5: diff=-0.0081; 95%=[-0.0214,+0.0034]; P(improve)=90.5%.
- 2025 HERA_vs_OPAL brier block10: diff=-0.0081; 95%=[-0.0212,+0.0033]; P(improve)=90.5%.
- 2025 HERA_vs_OPAL logloss block5: diff=-0.0191; 95%=[-0.0483,+0.0077]; P(improve)=91.3%.
- 2025 HERA_vs_OPAL logloss block10: diff=-0.0191; 95%=[-0.0492,+0.0069]; P(improve)=91.5%.
- 2026 HERA_vs_AURORA accuracy block5: diff=+3.1414 pp; 95%=[-1.5707,+7.8534] pp; P(improve)=87.8%.
- 2026 HERA_vs_AURORA accuracy block10: diff=+3.1414 pp; 95%=[-1.5707,+7.8534] pp; P(improve)=88.8%.
- 2026 HERA_vs_AURORA brier block5: diff=-0.0024; 95%=[-0.0194,+0.0159]; P(improve)=63.5%.
- 2026 HERA_vs_AURORA brier block10: diff=-0.0024; 95%=[-0.0180,+0.0164]; P(improve)=64.5%.
- 2026 HERA_vs_AURORA logloss block5: diff=-0.0014; 95%=[-0.0399,+0.0413]; P(improve)=54.6%.
- 2026 HERA_vs_AURORA logloss block10: diff=-0.0014; 95%=[-0.0368,+0.0424]; P(improve)=55.8%.
- 2026 HERA_vs_OPAL accuracy block5: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- 2026 HERA_vs_OPAL accuracy block10: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- 2026 HERA_vs_OPAL brier block5: diff=+0.0000; 95%=[+0.0000,+0.0000]; P(improve)=0.0%.
- 2026 HERA_vs_OPAL brier block10: diff=+0.0000; 95%=[+0.0000,+0.0000]; P(improve)=0.0%.
- 2026 HERA_vs_OPAL logloss block5: diff=+0.0000; 95%=[+0.0000,+0.0000]; P(improve)=0.0%.
- 2026 HERA_vs_OPAL logloss block10: diff=+0.0000; 95%=[+0.0000,+0.0000]; P(improve)=0.0%.
- 2025-2026 HERA_vs_AURORA accuracy block5: diff=+2.0501 pp; 95%=[-0.2278,+4.3280] pp; P(improve)=95.5%.
- 2025-2026 HERA_vs_AURORA accuracy block10: diff=+2.0501 pp; 95%=[-0.2278,+4.3280] pp; P(improve)=96.1%.
- 2025-2026 HERA_vs_AURORA brier block5: diff=-0.0027; 95%=[-0.0100,+0.0055]; P(improve)=76.0%.
- 2025-2026 HERA_vs_AURORA brier block10: diff=-0.0027; 95%=[-0.0097,+0.0057]; P(improve)=76.0%.
- 2025-2026 HERA_vs_AURORA logloss block5: diff=-0.0040; 95%=[-0.0209,+0.0152]; P(improve)=68.6%.
- 2025-2026 HERA_vs_AURORA logloss block10: diff=-0.0040; 95%=[-0.0201,+0.0156]; P(improve)=68.6%.
- 2025-2026 HERA_vs_OPAL accuracy block5: diff=+0.4556 pp; 95%=[-1.3667,+2.2779] pp; P(improve)=64.5%.
- 2025-2026 HERA_vs_OPAL accuracy block10: diff=+0.4556 pp; 95%=[-1.1390,+2.2779] pp; P(improve)=65.2%.
- 2025-2026 HERA_vs_OPAL brier block5: diff=-0.0046; 95%=[-0.0123,+0.0020]; P(improve)=90.9%.
- 2025-2026 HERA_vs_OPAL brier block10: diff=-0.0046; 95%=[-0.0123,+0.0020]; P(improve)=90.1%.
- 2025-2026 HERA_vs_OPAL logloss block5: diff=-0.0108; 95%=[-0.0278,+0.0045]; P(improve)=91.5%.
- 2025-2026 HERA_vs_OPAL logloss block10: diff=-0.0108; 95%=[-0.0286,+0.0044]; P(improve)=90.8%.

## Governance

HERA introduces no new numerical threshold or fitted parameter. It composes two frozen parent mechanisms using AURORA's already-causal active-expert state. Because HERA was conceived after observing OPAL's historical regime dependence, 2022-2026 results remain retrospective mechanism evidence. Existing AURORA prospective validation is unchanged.
