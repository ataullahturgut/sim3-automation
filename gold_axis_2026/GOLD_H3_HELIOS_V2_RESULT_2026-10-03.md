# HELIOS-H3 V2 — POSTERIOR-CALIBRATED REGIME ROUTER RESULT

**Status:** **POSTHOC_STRENGTHENING_RESULT**  
**Binding routing:** identical to HELIOS V1; only routed probability calibration changes.  

## Metrics

| Period | AURORA Acc | V1 Soft | V1 Hard | V2 Acc | Raw OPAL | AURORA Brier | V1 Soft Brier | V1 Hard Brier | V2 Brier |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 71.23% | 71.23% | 71.23% | 71.23% | 67.12% | 0.2118 | 0.2118 | 0.2118 | 0.2118 |
| 2024 | 70.83% | 71.25% | 71.25% | 71.25% | 70.00% | 0.2006 | 0.1989 | 0.1984 | 0.1988 |
| 2025 | 64.52% | 66.13% | 66.13% | 66.13% | 64.92% | 0.2276 | 0.2253 | 0.2246 | 0.2244 |
| 2026 | 60.73% | 61.78% | 61.78% | 61.78% | 63.87% | 0.2477 | 0.2460 | 0.2455 | 0.2455 |
| 2023-2024 | 71.02% | 71.24% | 71.24% | 71.24% | 68.63% | 0.2059 | 0.2050 | 0.2048 | 0.2050 |
| 2025-2026 | 62.87% | 64.24% | 64.24% | 64.24% | 64.46% | 0.2363 | 0.2343 | 0.2337 | 0.2336 |

## Gate sensitivity

| Config | Period | Acc | BA | Brier | Logloss | Active share | Switches |
|---|---|---:|---:|---:|---:|---:|---|
| W6_4_2 | 2023-2024 | 71.24% | 71.40% | 0.2050 | 0.5970 | 24.8% | 2024-07-16 |
| W6_4_2 | 2025 | 66.13% | 64.26% | 0.2239 | 0.6506 | 100.0% | 2024-07-16 |
| W6_4_2 | 2026 | 61.78% | 62.21% | 0.2451 | 0.7020 | 100.0% | 2024-07-16 |
| W6_4_2 | 2025-2026 | 64.24% | 63.31% | 0.2331 | 0.6729 | 100.0% | 2024-07-16 |
| W8_5_3_BINDING | 2023-2024 | 71.24% | 71.40% | 0.2050 | 0.5970 | 24.8% | 2024-07-16 |
| W8_5_3_BINDING | 2025 | 66.13% | 64.26% | 0.2244 | 0.6520 | 100.0% | 2024-07-16 |
| W8_5_3_BINDING | 2026 | 61.78% | 62.21% | 0.2455 | 0.7028 | 100.0% | 2024-07-16 |
| W8_5_3_BINDING | 2025-2026 | 64.24% | 63.31% | 0.2336 | 0.6741 | 100.0% | 2024-07-16 |
| W10_6_4 | 2023-2024 | 71.24% | 71.44% | 0.2057 | 0.5987 | 12.9% | 2024-10-03 |
| W10_6_4 | 2025 | 66.13% | 64.26% | 0.2243 | 0.6515 | 100.0% | 2024-10-03 |
| W10_6_4 | 2026 | 61.78% | 62.21% | 0.2458 | 0.7041 | 100.0% | 2024-10-03 |
| W10_6_4 | 2025-2026 | 64.24% | 63.31% | 0.2337 | 0.6744 | 100.0% | 2024-10-03 |

## Dependence-aware bootstrap

- V2_vs_AURORA / 2023-2024 / accuracy / block5: diff=+0.2179 pp; 95%=[-0.4357,+0.8769] pp; P(improve)=61.0%.
- V2_vs_AURORA / 2023-2024 / accuracy / block10: diff=+0.2179 pp; 95%=[-0.4357,+0.8715] pp; P(improve)=61.0%.
- V2_vs_AURORA / 2023-2024 / brier / block5: diff=-0.0009; 95%=[-0.0034,+0.0007]; P(improve)=74.9%.
- V2_vs_AURORA / 2023-2024 / brier / block10: diff=-0.0009; 95%=[-0.0032,+0.0007]; P(improve)=77.5%.
- V2_vs_AURORA / 2023-2024 / logloss / block5: diff=-0.0021; 95%=[-0.0074,+0.0016]; P(improve)=75.8%.
- V2_vs_AURORA / 2023-2024 / logloss / block10: diff=-0.0021; 95%=[-0.0072,+0.0014]; P(improve)=78.7%.
- V2_vs_AURORA / 2025-2026 / accuracy / block5: diff=+1.3667 pp; 95%=[+0.0000,+2.9613] pp; P(improve)=95.7%.
- V2_vs_AURORA / 2025-2026 / accuracy / block10: diff=+1.3667 pp; 95%=[+0.0000,+2.9613] pp; P(improve)=95.9%.
- V2_vs_AURORA / 2025-2026 / brier / block5: diff=-0.0028; 95%=[-0.0074,+0.0018]; P(improve)=88.1%.
- V2_vs_AURORA / 2025-2026 / brier / block10: diff=-0.0028; 95%=[-0.0074,+0.0019]; P(improve)=87.8%.
- V2_vs_AURORA / 2025-2026 / logloss / block5: diff=-0.0056; 95%=[-0.0160,+0.0046]; P(improve)=85.6%.
- V2_vs_AURORA / 2025-2026 / logloss / block10: diff=-0.0056; 95%=[-0.0160,+0.0044]; P(improve)=86.2%.
- V2_vs_AURORA / 2026 / accuracy / block5: diff=+1.0471 pp; 95%=[-1.0471,+3.6649] pp; P(improve)=72.6%.
- V2_vs_AURORA / 2026 / accuracy / block10: diff=+1.0471 pp; 95%=[-1.0471,+3.6649] pp; P(improve)=73.2%.
- V2_vs_AURORA / 2026 / brier / block5: diff=-0.0022; 95%=[-0.0102,+0.0048]; P(improve)=71.6%.
- V2_vs_AURORA / 2026 / brier / block10: diff=-0.0022; 95%=[-0.0097,+0.0048]; P(improve)=71.2%.
- V2_vs_AURORA / 2026 / logloss / block5: diff=-0.0044; 95%=[-0.0212,+0.0109]; P(improve)=68.0%.
- V2_vs_AURORA / 2026 / logloss / block10: diff=-0.0044; 95%=[-0.0212,+0.0117]; P(improve)=68.7%.
- V2_vs_HELIOS_V1_SOFT / 2023-2024 / accuracy / block5: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- V2_vs_HELIOS_V1_SOFT / 2023-2024 / accuracy / block10: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- V2_vs_HELIOS_V1_SOFT / 2023-2024 / brier / block5: diff=-0.0000; 95%=[-0.0006,+0.0006]; P(improve)=55.1%.
- V2_vs_HELIOS_V1_SOFT / 2023-2024 / brier / block10: diff=-0.0000; 95%=[-0.0006,+0.0005]; P(improve)=54.1%.
- V2_vs_HELIOS_V1_SOFT / 2023-2024 / logloss / block5: diff=-0.0001; 95%=[-0.0013,+0.0012]; P(improve)=55.2%.
- V2_vs_HELIOS_V1_SOFT / 2023-2024 / logloss / block10: diff=-0.0001; 95%=[-0.0012,+0.0011]; P(improve)=54.0%.
- V2_vs_HELIOS_V1_SOFT / 2025-2026 / accuracy / block5: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- V2_vs_HELIOS_V1_SOFT / 2025-2026 / accuracy / block10: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- V2_vs_HELIOS_V1_SOFT / 2025-2026 / brier / block5: diff=-0.0007; 95%=[-0.0037,+0.0024]; P(improve)=69.0%.
- V2_vs_HELIOS_V1_SOFT / 2025-2026 / brier / block10: diff=-0.0007; 95%=[-0.0037,+0.0025]; P(improve)=68.9%.
- V2_vs_HELIOS_V1_SOFT / 2025-2026 / logloss / block5: diff=-0.0013; 95%=[-0.0080,+0.0063]; P(improve)=64.6%.
- V2_vs_HELIOS_V1_SOFT / 2025-2026 / logloss / block10: diff=-0.0013; 95%=[-0.0080,+0.0062]; P(improve)=64.1%.
- V2_vs_HELIOS_V1_SOFT / 2026 / accuracy / block5: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- V2_vs_HELIOS_V1_SOFT / 2026 / accuracy / block10: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- V2_vs_HELIOS_V1_SOFT / 2026 / brier / block5: diff=-0.0005; 95%=[-0.0059,+0.0053]; P(improve)=55.5%.
- V2_vs_HELIOS_V1_SOFT / 2026 / brier / block10: diff=-0.0005; 95%=[-0.0061,+0.0053]; P(improve)=55.1%.
- V2_vs_HELIOS_V1_SOFT / 2026 / logloss / block5: diff=-0.0010; 95%=[-0.0133,+0.0127]; P(improve)=55.9%.
- V2_vs_HELIOS_V1_SOFT / 2026 / logloss / block10: diff=-0.0010; 95%=[-0.0136,+0.0127]; P(improve)=55.8%.
- V2_vs_HELIOS_V1_HARD / 2023-2024 / accuracy / block5: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- V2_vs_HELIOS_V1_HARD / 2023-2024 / accuracy / block10: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- V2_vs_HELIOS_V1_HARD / 2023-2024 / brier / block5: diff=+0.0002; 95%=[-0.0003,+0.0009]; P(improve)=22.9%.
- V2_vs_HELIOS_V1_HARD / 2023-2024 / brier / block10: diff=+0.0002; 95%=[-0.0003,+0.0010]; P(improve)=25.7%.
- V2_vs_HELIOS_V1_HARD / 2023-2024 / logloss / block5: diff=+0.0006; 95%=[-0.0006,+0.0021]; P(improve)=21.7%.
- V2_vs_HELIOS_V1_HARD / 2023-2024 / logloss / block10: diff=+0.0006; 95%=[-0.0006,+0.0023]; P(improve)=23.4%.
- V2_vs_HELIOS_V1_HARD / 2025-2026 / accuracy / block5: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- V2_vs_HELIOS_V1_HARD / 2025-2026 / accuracy / block10: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- V2_vs_HELIOS_V1_HARD / 2025-2026 / brier / block5: diff=-0.0002; 95%=[-0.0029,+0.0028]; P(improve)=55.9%.
- V2_vs_HELIOS_V1_HARD / 2025-2026 / brier / block10: diff=-0.0002; 95%=[-0.0029,+0.0028]; P(improve)=54.4%.
- V2_vs_HELIOS_V1_HARD / 2025-2026 / logloss / block5: diff=-0.0000; 95%=[-0.0062,+0.0070]; P(improve)=51.9%.
- V2_vs_HELIOS_V1_HARD / 2025-2026 / logloss / block10: diff=-0.0000; 95%=[-0.0064,+0.0071]; P(improve)=51.0%.
- V2_vs_HELIOS_V1_HARD / 2026 / accuracy / block5: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- V2_vs_HELIOS_V1_HARD / 2026 / accuracy / block10: diff=+0.0000 pp; 95%=[+0.0000,+0.0000] pp; P(improve)=0.0%.
- V2_vs_HELIOS_V1_HARD / 2026 / brier / block5: diff=-0.0001; 95%=[-0.0051,+0.0055]; P(improve)=53.1%.
- V2_vs_HELIOS_V1_HARD / 2026 / brier / block10: diff=-0.0001; 95%=[-0.0054,+0.0055]; P(improve)=53.1%.
- V2_vs_HELIOS_V1_HARD / 2026 / logloss / block5: diff=-0.0000; 95%=[-0.0120,+0.0131]; P(improve)=53.3%.
- V2_vs_HELIOS_V1_HARD / 2026 / logloss / block10: diff=-0.0000; 95%=[-0.0124,+0.0131]; P(improve)=53.1%.
- V2_vs_OPAL_RAW / 2023-2024 / accuracy / block5: diff=+2.6144 pp; 95%=[-0.6536,+6.1002] pp; P(improve)=93.0%.
- V2_vs_OPAL_RAW / 2023-2024 / accuracy / block10: diff=+2.6144 pp; 95%=[-0.8715,+6.5359] pp; P(improve)=91.6%.
- V2_vs_OPAL_RAW / 2023-2024 / brier / block5: diff=-0.0131; 95%=[-0.0262,-0.0010]; P(improve)=98.4%.
- V2_vs_OPAL_RAW / 2023-2024 / brier / block10: diff=-0.0131; 95%=[-0.0278,-0.0007]; P(improve)=98.3%.
- V2_vs_OPAL_RAW / 2023-2024 / logloss / block5: diff=-0.0294; 95%=[-0.0603,-0.0027]; P(improve)=98.5%.
- V2_vs_OPAL_RAW / 2023-2024 / logloss / block10: diff=-0.0294; 95%=[-0.0627,-0.0020]; P(improve)=98.2%.
- V2_vs_OPAL_RAW / 2025-2026 / accuracy / block5: diff=-0.2278 pp; 95%=[-2.7335,+2.2779] pp; P(improve)=38.9%.
- V2_vs_OPAL_RAW / 2025-2026 / accuracy / block10: diff=-0.2278 pp; 95%=[-2.5057,+2.0501] pp; P(improve)=37.4%.
- V2_vs_OPAL_RAW / 2025-2026 / brier / block5: diff=-0.0047; 95%=[-0.0142,+0.0039]; P(improve)=84.7%.
- V2_vs_OPAL_RAW / 2025-2026 / brier / block10: diff=-0.0047; 95%=[-0.0138,+0.0034]; P(improve)=86.1%.
- V2_vs_OPAL_RAW / 2025-2026 / logloss / block5: diff=-0.0124; 95%=[-0.0339,+0.0072]; P(improve)=88.5%.
- V2_vs_OPAL_RAW / 2025-2026 / logloss / block10: diff=-0.0124; 95%=[-0.0327,+0.0059]; P(improve)=89.6%.
- V2_vs_OPAL_RAW / 2026 / accuracy / block5: diff=-2.0942 pp; 95%=[-6.2827,+1.5707] pp; P(improve)=11.5%.
- V2_vs_OPAL_RAW / 2026 / accuracy / block10: diff=-2.0942 pp; 95%=[-5.2356,+1.0471] pp; P(improve)=7.5%.
- V2_vs_OPAL_RAW / 2026 / brier / block5: diff=+0.0002; 95%=[-0.0148,+0.0139]; P(improve)=48.1%.
- V2_vs_OPAL_RAW / 2026 / brier / block10: diff=+0.0002; 95%=[-0.0137,+0.0119]; P(improve)=45.3%.
- V2_vs_OPAL_RAW / 2026 / logloss / block5: diff=-0.0030; 95%=[-0.0370,+0.0284]; P(improve)=55.5%.
- V2_vs_OPAL_RAW / 2026 / logloss / block10: diff=-0.0030; 95%=[-0.0356,+0.0240]; P(improve)=54.6%.

## Governance

V2 is a post-hoc strengthening study. Historical results cannot replace prospective proof. The frozen AURORA prospective champion remains unchanged until HELIOS is separately frozen and accumulates future origins.
