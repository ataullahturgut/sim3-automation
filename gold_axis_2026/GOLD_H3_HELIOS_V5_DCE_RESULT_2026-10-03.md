# HELIOS-H3 V5-DCE — DOMINANT-EXPERT CONTRADICTION EXCEPTION RESULT

**Status:** **POSTHOC_MECHANISM_RESULT**  
**Base:** V4-RGE, modified only at DCE exceptions.  
**Guardrails:** 2023 unchanged=True; 2024 unchanged=True.

## Metrics

| Period | AURORA | V2 | V3-GT | V4-RGE | V5-DCE | OPAL | V5 BA | V5 Brier | Exceptions | Rescue | Broken | Net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 71.23% | 71.23% | 71.23% | 71.23% | 71.23% | 67.12% | 71.83% | 0.2118 | 0 | 0 | 0 | +0 |
| 2024 | 70.83% | 71.25% | 70.83% | 71.25% | 71.25% | 70.00% | 70.22% | 0.1988 | 0 | 2 | 1 | +1 |
| 2025 | 64.52% | 66.13% | 64.92% | 66.13% | 66.53% | 64.92% | 64.59% | 0.2243 | 1 | 6 | 1 | +5 |
| 2026 | 60.73% | 61.78% | 65.45% | 64.40% | 65.45% | 63.87% | 65.76% | 0.2369 | 2 | 13 | 4 | +9 |
| 2023-2024 | 71.02% | 71.24% | 71.02% | 71.24% | 71.24% | 68.63% | 71.40% | 0.2050 | 0 | 2 | 1 | +1 |
| 2025-2026 | 62.87% | 64.24% | 65.15% | 65.38% | 66.06% | 64.46% | 65.25% | 0.2298 | 3 | 19 | 5 | +14 |

## DCE exceptions

| Issue | Year | PATH posterior | q_path | GT share | AURORA | V5 | Actual | H3 return | Effect |
|---|---:|---:|---:|---:|---|---|---|---:|---|
| 2025-10-15 | 2025 | 94.4% | 83.1% | 78.2% | DOWN | UP | UP | +4.59% | RESCUED |
| 2026-06-05 | 2026 | 77.5% | 61.5% | 88.8% | UP | DOWN | DOWN | -3.85% | RESCUED |
| 2026-06-24 | 2026 | 77.5% | 61.5% | 98.4% | UP | DOWN | DOWN | -1.93% | RESCUED |

## Dependence-aware inference

- V5DCE_vs_AURORA / 2025-2026 / accuracy / block5: diff=+3.1891 pp; 95%=[+1.1390,+5.2392] pp; P(improve)=99.9%.
- V5DCE_vs_AURORA / 2025-2026 / accuracy / block10: diff=+3.1891 pp; 95%=[+1.1390,+5.4670] pp; P(improve)=100.0%.
- V5DCE_vs_AURORA / 2025-2026 / brier / block5: diff=-0.0065; 95%=[-0.0127,-0.0006]; P(improve)=98.5%.
- V5DCE_vs_AURORA / 2025-2026 / brier / block10: diff=-0.0065; 95%=[-0.0127,-0.0007]; P(improve)=98.7%.
- V5DCE_vs_AURORA / 2025-2026 / logloss / block5: diff=-0.0137; 95%=[-0.0272,-0.0005]; P(improve)=97.9%.
- V5DCE_vs_AURORA / 2025-2026 / logloss / block10: diff=-0.0137; 95%=[-0.0274,-0.0011]; P(improve)=98.4%.
- V5DCE_vs_AURORA / 2026 / accuracy / block5: diff=+4.7120 pp; 95%=[+1.0471,+8.9005] pp; P(improve)=99.4%.
- V5DCE_vs_AURORA / 2026 / accuracy / block10: diff=+4.7120 pp; 95%=[+1.0471,+8.9005] pp; P(improve)=99.7%.
- V5DCE_vs_AURORA / 2026 / brier / block5: diff=-0.0107; 95%=[-0.0223,+0.0005]; P(improve)=96.9%.
- V5DCE_vs_AURORA / 2026 / brier / block10: diff=-0.0107; 95%=[-0.0227,-0.0003]; P(improve)=97.8%.
- V5DCE_vs_AURORA / 2026 / logloss / block5: diff=-0.0227; 95%=[-0.0481,+0.0014]; P(improve)=96.8%.
- V5DCE_vs_AURORA / 2026 / logloss / block10: diff=-0.0227; 95%=[-0.0489,+0.0003]; P(improve)=97.4%.
- V5DCE_vs_HELIOS_V2 / 2025-2026 / accuracy / block5: diff=+1.8223 pp; 95%=[+0.4556,+3.4169] pp; P(improve)=99.2%.
- V5DCE_vs_HELIOS_V2 / 2025-2026 / accuracy / block10: diff=+1.8223 pp; 95%=[+0.4556,+3.4169] pp; P(improve)=99.7%.
- V5DCE_vs_HELIOS_V2 / 2025-2026 / brier / block5: diff=-0.0038; 95%=[-0.0085,+0.0005]; P(improve)=95.8%.
- V5DCE_vs_HELIOS_V2 / 2025-2026 / brier / block10: diff=-0.0038; 95%=[-0.0086,-0.0002]; P(improve)=98.3%.
- V5DCE_vs_HELIOS_V2 / 2025-2026 / logloss / block5: diff=-0.0081; 95%=[-0.0186,+0.0009]; P(improve)=95.8%.
- V5DCE_vs_HELIOS_V2 / 2025-2026 / logloss / block10: diff=-0.0081; 95%=[-0.0186,-0.0002]; P(improve)=98.1%.
- V5DCE_vs_HELIOS_V2 / 2026 / accuracy / block5: diff=+3.6649 pp; 95%=[+0.5236,+6.8063] pp; P(improve)=98.5%.
- V5DCE_vs_HELIOS_V2 / 2026 / accuracy / block10: diff=+3.6649 pp; 95%=[+1.0471,+6.8063] pp; P(improve)=99.6%.
- V5DCE_vs_HELIOS_V2 / 2026 / brier / block5: diff=-0.0085; 95%=[-0.0193,+0.0011]; P(improve)=95.9%.
- V5DCE_vs_HELIOS_V2 / 2026 / brier / block10: diff=-0.0085; 95%=[-0.0192,-0.0004]; P(improve)=98.2%.
- V5DCE_vs_HELIOS_V2 / 2026 / logloss / block5: diff=-0.0184; 95%=[-0.0411,+0.0024]; P(improve)=95.7%.
- V5DCE_vs_HELIOS_V2 / 2026 / logloss / block10: diff=-0.0184; 95%=[-0.0424,-0.0006]; P(improve)=98.0%.
- V5DCE_vs_HELIOS_V3_GT / 2025-2026 / accuracy / block5: diff=+0.9112 pp; 95%=[-0.2278,+2.0501] pp; P(improve)=92.9%.
- V5DCE_vs_HELIOS_V3_GT / 2025-2026 / accuracy / block10: diff=+0.9112 pp; 95%=[-0.2278,+2.0501] pp; P(improve)=91.9%.
- V5DCE_vs_HELIOS_V3_GT / 2025-2026 / brier / block5: diff=-0.0021; 95%=[-0.0060,+0.0016]; P(improve)=86.8%.
- V5DCE_vs_HELIOS_V3_GT / 2025-2026 / brier / block10: diff=-0.0021; 95%=[-0.0061,+0.0015]; P(improve)=87.0%.
- V5DCE_vs_HELIOS_V3_GT / 2025-2026 / logloss / block5: diff=-0.0041; 95%=[-0.0126,+0.0044]; P(improve)=82.3%.
- V5DCE_vs_HELIOS_V3_GT / 2025-2026 / logloss / block10: diff=-0.0041; 95%=[-0.0128,+0.0041]; P(improve)=84.0%.
- V5DCE_vs_HELIOS_V3_GT / 2026 / accuracy / block5: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- V5DCE_vs_HELIOS_V3_GT / 2026 / accuracy / block10: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- V5DCE_vs_HELIOS_V3_GT / 2026 / brier / block5: diff=-0.0001; 95%=[-0.0054,+0.0055]; P(improve)=53.8%.
- V5DCE_vs_HELIOS_V3_GT / 2026 / brier / block10: diff=-0.0001; 95%=[-0.0054,+0.0055]; P(improve)=52.6%.
- V5DCE_vs_HELIOS_V3_GT / 2026 / logloss / block5: diff=-0.0000; 95%=[-0.0115,+0.0131]; P(improve)=53.4%.
- V5DCE_vs_HELIOS_V3_GT / 2026 / logloss / block10: diff=-0.0000; 95%=[-0.0124,+0.0131]; P(improve)=52.7%.
- V5DCE_vs_HELIOS_V4_RGE / 2025-2026 / accuracy / block5: diff=+0.6834 pp; 95%=[+0.0000,+1.5945] pp; P(improve)=95.6%.
- V5DCE_vs_HELIOS_V4_RGE / 2025-2026 / accuracy / block10: diff=+0.6834 pp; 95%=[+0.0000,+1.5945] pp; P(improve)=95.5%.
- V5DCE_vs_HELIOS_V4_RGE / 2025-2026 / brier / block5: diff=-0.0008; 95%=[-0.0022,+0.0000]; P(improve)=95.4%.
- V5DCE_vs_HELIOS_V4_RGE / 2025-2026 / brier / block10: diff=-0.0008; 95%=[-0.0021,+0.0000]; P(improve)=95.1%.
- V5DCE_vs_HELIOS_V4_RGE / 2025-2026 / logloss / block5: diff=-0.0017; 95%=[-0.0044,+0.0000]; P(improve)=95.1%.
- V5DCE_vs_HELIOS_V4_RGE / 2025-2026 / logloss / block10: diff=-0.0017; 95%=[-0.0043,+0.0000]; P(improve)=95.9%.
- V5DCE_vs_HELIOS_V4_RGE / 2026 / accuracy / block5: diff=+1.0471 pp; 95%=[+0.0000,+2.6178] pp; P(improve)=87.4%.
- V5DCE_vs_HELIOS_V4_RGE / 2026 / accuracy / block10: diff=+1.0471 pp; 95%=[+0.0000,+2.6178] pp; P(improve)=87.8%.
- V5DCE_vs_HELIOS_V4_RGE / 2026 / brier / block5: diff=-0.0018; 95%=[-0.0048,+0.0000]; P(improve)=87.5%.
- V5DCE_vs_HELIOS_V4_RGE / 2026 / brier / block10: diff=-0.0018; 95%=[-0.0048,+0.0000]; P(improve)=87.6%.
- V5DCE_vs_HELIOS_V4_RGE / 2026 / logloss / block5: diff=-0.0036; 95%=[-0.0097,+0.0000]; P(improve)=87.6%.
- V5DCE_vs_HELIOS_V4_RGE / 2026 / logloss / block10: diff=-0.0036; 95%=[-0.0097,+0.0000]; P(improve)=87.7%.
- COT-vintage cluster / 2025-2026: net=+14, clusters=17, 95%=[+7,+21], P(net>0)=100.0%.
- COT-vintage cluster / 2026: net=+9, clusters=10, 95%=[+3,+15], P(net>0)=99.8%.

## Sensitivity

- path_posterior: path>0.40, GT>0.50: Acc 65.83%, BA 65.00%, Brier 0.2298, exceptions 4, net +13.
- path_posterior: path>0.50, GT>0.50: Acc 66.06%, BA 65.25%, Brier 0.2298, exceptions 3, net +14.
- path_posterior: path>0.60, GT>0.50: Acc 66.06%, BA 65.25%, Brier 0.2298, exceptions 3, net +14.
- path_posterior: path>0.70, GT>0.50: Acc 66.06%, BA 65.25%, Brier 0.2298, exceptions 3, net +14.
- path_posterior: path>0.75, GT>0.50: Acc 66.06%, BA 65.25%, Brier 0.2298, exceptions 3, net +14.
- path_posterior: path>0.80, GT>0.50: Acc 65.60%, BA 64.74%, Brier 0.2306, exceptions 1, net +12.
- gt_share: path>0.50, GT>0.50: Acc 66.06%, BA 65.25%, Brier 0.2298, exceptions 3, net +14.
- gt_share: path>0.50, GT>0.60: Acc 66.06%, BA 65.25%, Brier 0.2298, exceptions 3, net +14.
- gt_share: path>0.50, GT>0.70: Acc 66.06%, BA 65.25%, Brier 0.2298, exceptions 3, net +14.
- gt_share: path>0.50, GT>0.80: Acc 65.83%, BA 65.04%, Brier 0.2299, exceptions 2, net +13.

## Governance

V5-DCE is post-hoc mechanism research. The three historical exceptions were discovered after retrospective error anatomy. The result is therefore hypothesis-generating/strengthening evidence, not pristine confirmation. AURORA remains the frozen prospective champion until a separately frozen future-origin challenger accumulates evidence.
