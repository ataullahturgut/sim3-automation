# HELIOS-H3 V4-RGE — REGRET-GATED EXPANSION RESULT

**Status:** **POSTHOC_STRENGTHENING_RESULT**  
**Base:** HELIOS V2 preserved; broader OPAL only after positive non-consensus regret.  

## Expansion switches

- **2026-06-29 -> ACTIVE**; recent 10: 1000110111, 6W/4L, regret +2.

## Metrics

| Period | AURORA | V2 | V3-GT | V4-RGE | OPAL | V4 BA | V4 Brier | Base routes | Expansion | Rescue | Broken | Net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 71.23% | 71.23% | 71.23% | 71.23% | 67.12% | 71.83% | 0.2118 | 0 | 0 | 0 | 0 | +0 |
| 2024 | 70.83% | 71.25% | 70.83% | 71.25% | 70.00% | 70.22% | 0.1988 | 3 | 0 | 2 | 1 | +1 |
| 2025 | 64.52% | 66.13% | 64.92% | 66.13% | 64.92% | 64.26% | 0.2244 | 6 | 0 | 5 | 1 | +4 |
| 2026 | 60.73% | 61.78% | 65.45% | 64.40% | 63.87% | 64.76% | 0.2387 | 4 | 11 | 11 | 4 | +7 |
| 2023-2024 | 71.02% | 71.24% | 71.02% | 71.24% | 68.63% | 71.40% | 0.2050 | 3 | 0 | 2 | 1 | +1 |
| 2025-2026 | 62.87% | 64.24% | 65.15% | 65.38% | 64.46% | 64.54% | 0.2306 | 10 | 11 | 16 | 5 | +11 |

## Dependence-aware inference

- V4RGE_vs_AURORA / 2023-2024 / accuracy / block5: diff=+0.2179 pp; 95%=[-0.4357,+1.0893] pp; P(improve)=60.4%.
- V4RGE_vs_AURORA / 2023-2024 / accuracy / block10: diff=+0.2179 pp; 95%=[-0.4357,+0.8715] pp; P(improve)=61.2%.
- V4RGE_vs_AURORA / 2023-2024 / brier / block5: diff=-0.0009; 95%=[-0.0034,+0.0007]; P(improve)=74.9%.
- V4RGE_vs_AURORA / 2023-2024 / brier / block10: diff=-0.0009; 95%=[-0.0032,+0.0007]; P(improve)=77.6%.
- V4RGE_vs_AURORA / 2023-2024 / logloss / block5: diff=-0.0021; 95%=[-0.0078,+0.0014]; P(improve)=76.3%.
- V4RGE_vs_AURORA / 2023-2024 / logloss / block10: diff=-0.0021; 95%=[-0.0071,+0.0014]; P(improve)=79.4%.
- V4RGE_vs_AURORA / 2025-2026 / accuracy / block5: diff=+2.5057 pp; 95%=[+0.6834,+4.5558] pp; P(improve)=99.5%.
- V4RGE_vs_AURORA / 2025-2026 / accuracy / block10: diff=+2.5057 pp; 95%=[+0.6834,+4.5558] pp; P(improve)=99.7%.
- V4RGE_vs_AURORA / 2025-2026 / brier / block5: diff=-0.0057; 95%=[-0.0119,+0.0000]; P(improve)=97.4%.
- V4RGE_vs_AURORA / 2025-2026 / brier / block10: diff=-0.0057; 95%=[-0.0118,+0.0000]; P(improve)=97.5%.
- V4RGE_vs_AURORA / 2025-2026 / logloss / block5: diff=-0.0120; 95%=[-0.0258,+0.0006]; P(improve)=96.7%.
- V4RGE_vs_AURORA / 2025-2026 / logloss / block10: diff=-0.0120; 95%=[-0.0255,+0.0006]; P(improve)=96.8%.
- V4RGE_vs_AURORA / 2026 / accuracy / block5: diff=+3.6649 pp; 95%=[+0.0000,+7.8534] pp; P(improve)=97.4%.
- V4RGE_vs_AURORA / 2026 / accuracy / block10: diff=+3.6649 pp; 95%=[+0.5236,+7.8534] pp; P(improve)=98.0%.
- V4RGE_vs_AURORA / 2026 / brier / block5: diff=-0.0090; 95%=[-0.0209,+0.0017]; P(improve)=94.8%.
- V4RGE_vs_AURORA / 2026 / brier / block10: diff=-0.0090; 95%=[-0.0211,+0.0016]; P(improve)=95.2%.
- V4RGE_vs_AURORA / 2026 / logloss / block5: diff=-0.0192; 95%=[-0.0444,+0.0046]; P(improve)=94.2%.
- V4RGE_vs_AURORA / 2026 / logloss / block10: diff=-0.0192; 95%=[-0.0455,+0.0039]; P(improve)=94.7%.
- V4RGE_vs_HELIOS_V2 / 2023-2024 / accuracy / block5: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- V4RGE_vs_HELIOS_V2 / 2023-2024 / accuracy / block10: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- V4RGE_vs_HELIOS_V2 / 2023-2024 / brier / block5: diff=+0.0000; 95%=[+0.0000,+0.0000]; P(improve)=0.0%.
- V4RGE_vs_HELIOS_V2 / 2023-2024 / brier / block10: diff=+0.0000; 95%=[+0.0000,+0.0000]; P(improve)=0.0%.
- V4RGE_vs_HELIOS_V2 / 2023-2024 / logloss / block5: diff=+0.0000; 95%=[+0.0000,+0.0000]; P(improve)=0.0%.
- V4RGE_vs_HELIOS_V2 / 2023-2024 / logloss / block10: diff=+0.0000; 95%=[+0.0000,+0.0000]; P(improve)=0.0%.
- V4RGE_vs_HELIOS_V2 / 2025-2026 / accuracy / block5: diff=+1.1390 pp; 95%=[+0.0000,+2.5057] pp; P(improve)=95.0%.
- V4RGE_vs_HELIOS_V2 / 2025-2026 / accuracy / block10: diff=+1.1390 pp; 95%=[+0.0000,+2.5057] pp; P(improve)=96.3%.
- V4RGE_vs_HELIOS_V2 / 2025-2026 / brier / block5: diff=-0.0029; 95%=[-0.0074,+0.0011]; P(improve)=91.6%.
- V4RGE_vs_HELIOS_V2 / 2025-2026 / brier / block10: diff=-0.0029; 95%=[-0.0078,+0.0004]; P(improve)=93.2%.
- V4RGE_vs_HELIOS_V2 / 2025-2026 / logloss / block5: diff=-0.0064; 95%=[-0.0167,+0.0024]; P(improve)=91.7%.
- V4RGE_vs_HELIOS_V2 / 2025-2026 / logloss / block10: diff=-0.0064; 95%=[-0.0172,+0.0010]; P(improve)=93.4%.
- V4RGE_vs_HELIOS_V2 / 2026 / accuracy / block5: diff=+2.6178 pp; 95%=[+0.0000,+5.7592] pp; P(improve)=95.2%.
- V4RGE_vs_HELIOS_V2 / 2026 / accuracy / block10: diff=+2.6178 pp; 95%=[+0.0000,+5.7592] pp; P(improve)=96.9%.
- V4RGE_vs_HELIOS_V2 / 2026 / brier / block5: diff=-0.0068; 95%=[-0.0170,+0.0024]; P(improve)=92.7%.
- V4RGE_vs_HELIOS_V2 / 2026 / brier / block10: diff=-0.0068; 95%=[-0.0176,+0.0010]; P(improve)=94.1%.
- V4RGE_vs_HELIOS_V2 / 2026 / logloss / block5: diff=-0.0148; 95%=[-0.0377,+0.0057]; P(improve)=91.6%.
- V4RGE_vs_HELIOS_V2 / 2026 / logloss / block10: diff=-0.0148; 95%=[-0.0389,+0.0024]; P(improve)=93.5%.
- V4RGE_vs_HELIOS_V3_GT / 2023-2024 / accuracy / block5: diff=+0.2179 pp; 95%=[+0.0000,+0.6536] pp; P(improve)=63.2%.
- V4RGE_vs_HELIOS_V3_GT / 2023-2024 / accuracy / block10: diff=+0.2179 pp; 95%=[+0.0000,+0.6536] pp; P(improve)=63.2%.
- V4RGE_vs_HELIOS_V3_GT / 2023-2024 / brier / block5: diff=+0.0000; 95%=[-0.0007,+0.0008]; P(improve)=48.3%.
- V4RGE_vs_HELIOS_V3_GT / 2023-2024 / brier / block10: diff=+0.0000; 95%=[-0.0007,+0.0009]; P(improve)=47.7%.
- V4RGE_vs_HELIOS_V3_GT / 2023-2024 / logloss / block5: diff=+0.0001; 95%=[-0.0015,+0.0019]; P(improve)=44.8%.
- V4RGE_vs_HELIOS_V3_GT / 2023-2024 / logloss / block10: diff=+0.0001; 95%=[-0.0015,+0.0021]; P(improve)=45.4%.
- V4RGE_vs_HELIOS_V3_GT / 2025-2026 / accuracy / block5: diff=+0.2278 pp; 95%=[-1.1390,+1.5945] pp; P(improve)=54.3%.
- V4RGE_vs_HELIOS_V3_GT / 2025-2026 / accuracy / block10: diff=+0.2278 pp; 95%=[-1.1390,+1.8223] pp; P(improve)=55.0%.
- V4RGE_vs_HELIOS_V3_GT / 2025-2026 / brier / block5: diff=-0.0013; 95%=[-0.0055,+0.0026]; P(improve)=74.2%.
- V4RGE_vs_HELIOS_V3_GT / 2025-2026 / brier / block10: diff=-0.0013; 95%=[-0.0053,+0.0026]; P(improve)=73.6%.
- V4RGE_vs_HELIOS_V3_GT / 2025-2026 / logloss / block5: diff=-0.0024; 95%=[-0.0116,+0.0066]; P(improve)=71.1%.
- V4RGE_vs_HELIOS_V3_GT / 2025-2026 / logloss / block10: diff=-0.0024; 95%=[-0.0110,+0.0061]; P(improve)=71.2%.
- V4RGE_vs_HELIOS_V3_GT / 2026 / accuracy / block5: diff=-1.0471 pp; 95%=[-2.6178,+0.0000] pp; P(improve)=0.0%.
- V4RGE_vs_HELIOS_V3_GT / 2026 / accuracy / block10: diff=-1.0471 pp; 95%=[-2.6178,+0.0000] pp; P(improve)=0.0%.
- V4RGE_vs_HELIOS_V3_GT / 2026 / brier / block5: diff=+0.0017; 95%=[-0.0038,+0.0076]; P(improve)=27.2%.
- V4RGE_vs_HELIOS_V3_GT / 2026 / brier / block10: diff=+0.0017; 95%=[-0.0040,+0.0075]; P(improve)=27.8%.
- V4RGE_vs_HELIOS_V3_GT / 2026 / logloss / block5: diff=+0.0036; 95%=[-0.0091,+0.0167]; P(improve)=28.8%.
- V4RGE_vs_HELIOS_V3_GT / 2026 / logloss / block10: diff=+0.0036; 95%=[-0.0091,+0.0166]; P(improve)=28.7%.
- V4RGE_vs_OPAL_RAW / 2023-2024 / accuracy / block5: diff=+2.6144 pp; 95%=[-0.6536,+6.1002] pp; P(improve)=92.3%.
- V4RGE_vs_OPAL_RAW / 2023-2024 / accuracy / block10: diff=+2.6144 pp; 95%=[-0.8715,+6.5359] pp; P(improve)=92.2%.
- V4RGE_vs_OPAL_RAW / 2023-2024 / brier / block5: diff=-0.0131; 95%=[-0.0266,-0.0010]; P(improve)=98.1%.
- V4RGE_vs_OPAL_RAW / 2023-2024 / brier / block10: diff=-0.0131; 95%=[-0.0274,-0.0007]; P(improve)=98.0%.
- V4RGE_vs_OPAL_RAW / 2023-2024 / logloss / block5: diff=-0.0294; 95%=[-0.0595,-0.0033]; P(improve)=98.6%.
- V4RGE_vs_OPAL_RAW / 2023-2024 / logloss / block10: diff=-0.0294; 95%=[-0.0611,-0.0018]; P(improve)=98.2%.
- V4RGE_vs_OPAL_RAW / 2025-2026 / accuracy / block5: diff=+0.9112 pp; 95%=[-1.3667,+3.1891] pp; P(improve)=75.1%.
- V4RGE_vs_OPAL_RAW / 2025-2026 / accuracy / block10: diff=+0.9112 pp; 95%=[-1.1446,+3.1891] pp; P(improve)=75.7%.
- V4RGE_vs_OPAL_RAW / 2025-2026 / brier / block5: diff=-0.0077; 95%=[-0.0170,+0.0009]; P(improve)=95.7%.
- V4RGE_vs_OPAL_RAW / 2025-2026 / brier / block10: diff=-0.0077; 95%=[-0.0172,+0.0008]; P(improve)=95.9%.
- V4RGE_vs_OPAL_RAW / 2025-2026 / logloss / block5: diff=-0.0188; 95%=[-0.0405,+0.0008]; P(improve)=96.9%.
- V4RGE_vs_OPAL_RAW / 2025-2026 / logloss / block10: diff=-0.0188; 95%=[-0.0406,+0.0001]; P(improve)=97.4%.
- V4RGE_vs_OPAL_RAW / 2026 / accuracy / block5: diff=+0.5236 pp; 95%=[-2.6178,+4.1885] pp; P(improve)=55.5%.
- V4RGE_vs_OPAL_RAW / 2026 / accuracy / block10: diff=+0.5236 pp; 95%=[-2.6178,+4.1885] pp; P(improve)=54.1%.
- V4RGE_vs_OPAL_RAW / 2026 / brier / block5: diff=-0.0065; 95%=[-0.0221,+0.0067]; P(improve)=81.3%.
- V4RGE_vs_OPAL_RAW / 2026 / brier / block10: diff=-0.0065; 95%=[-0.0220,+0.0062]; P(improve)=79.9%.
- V4RGE_vs_OPAL_RAW / 2026 / logloss / block5: diff=-0.0178; 95%=[-0.0546,+0.0134]; P(improve)=85.0%.
- V4RGE_vs_OPAL_RAW / 2026 / logloss / block10: diff=-0.0178; 95%=[-0.0560,+0.0111]; P(improve)=85.3%.
- COT-vintage cluster / 2025-2026: net=+11, clusters=14, 95%=[+4,+18], P(net>0)=99.8%.
- COT-vintage cluster / 2026: net=+7, clusters=8, 95%=[+1,+13], P(net>0)=98.7%.

## Robustness

- W8_REGRET+2_-2: Acc 65.15%, BA 64.28%, Brier 0.2308, rescue/broken 15/5, net +10, switches 2026-06-29;2026-09-10;2026-09-17.
- W10_REGRET+2_-2: Acc 65.38%, BA 64.54%, Brier 0.2306, rescue/broken 16/5, net +11, switches 2026-06-29.
- W12_REGRET+2_-2: Acc 65.38%, BA 64.54%, Brier 0.2306, rescue/broken 16/5, net +11, switches 2026-06-29.

## Governance

V4-RGE is second-order post-hoc strengthening research. It preserves the frozen AURORA champion governance. No historical result may be treated as prospective confirmation; any operational use requires a separate future-origin freeze.
