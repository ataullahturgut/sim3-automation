# HELIOS-H3 V3-GT — GAME-THEORETIC REVERSAL ARBITER RESULT

**Status:** **POSTHOC_STRENGTHENING_RESULT**  
**Binding design:** W8, rescue +1 / broken -1, five-policy Hedge market, threshold >0.50.  
**Probability:** mirror frozen AURORA probability only on routed events.  

## Period metrics

| Period | AURORA Acc | HELIOS V2 Acc | V3-GT Acc | Raw OPAL Acc | AURORA BA | V3-GT BA | AURORA Brier | V2 Brier | V3-GT Brier | Routed | Rescue | Broken | Net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 71.23% | 71.23% | 71.23% | 67.12% | 71.83% | 71.83% | 0.2118 | 0.2118 | 0.2118 | 0 | 0 | 0 | +0 |
| 2024 | 70.83% | 71.25% | 70.83% | 70.00% | 69.97% | 69.74% | 0.2006 | 0.1988 | 0.1988 | 4 | 2 | 2 | +0 |
| 2025 | 64.52% | 66.13% | 64.92% | 64.92% | 62.93% | 62.34% | 0.2276 | 0.2244 | 0.2280 | 13 | 7 | 6 | +1 |
| 2026 | 60.73% | 61.78% | 65.45% | 63.87% | 61.12% | 65.76% | 0.2477 | 0.2455 | 0.2370 | 17 | 13 | 4 | +9 |
| 2023-2024 | 71.02% | 71.24% | 71.02% | 68.63% | 71.24% | 71.16% | 0.2059 | 0.2050 | 0.2050 | 4 | 2 | 2 | +0 |
| 2025-2026 | 62.87% | 64.24% | 65.15% | 64.46% | 62.07% | 64.19% | 0.2363 | 0.2336 | 0.2319 | 30 | 20 | 10 | +10 |

## 2026 routed events

| Issue | COT vintage | Pos | Market share | AURORA | V3-GT | Actual | H3 return | Effect |
|---|---|---:|---:|---|---|---|---:|---|
| 2026-03-11 | 2026-03-03 | 1 | 96.8% | UP | DOWN | DOWN | -2.11% | RESCUED |
| 2026-06-05 | 2026-05-26 | 1 | 88.8% | UP | DOWN | DOWN | -3.85% | RESCUED |
| 2026-06-24 | 2026-06-16 | 1 | 98.4% | UP | DOWN | DOWN | -1.93% | RESCUED |
| 2026-07-29 | 2026-07-21 | 1 | 98.4% | DOWN | UP | UP | +0.57% | RESCUED |
| 2026-08-03 | 2026-07-21 | 2 | 94.2% | DOWN | UP | UP | +3.09% | RESCUED |
| 2026-08-04 | 2026-07-21 | 3 | 94.2% | DOWN | UP | UP | +4.98% | RESCUED |
| 2026-08-12 | 2026-08-04 | 1 | 99.5% | DOWN | UP | DOWN | -0.63% | BROKEN |
| 2026-08-13 | 2026-08-04 | 2 | 77.3% | UP | DOWN | DOWN | -0.06% | RESCUED |
| 2026-08-14 | 2026-08-04 | 3 | 77.3% | DOWN | UP | UP | +0.03% | RESCUED |
| 2026-08-21 | 2026-08-11 | 1 | 99.4% | UP | DOWN | UP | +3.18% | BROKEN |
| 2026-08-24 | 2026-08-11 | 2 | 91.6% | UP | DOWN | UP | +0.92% | BROKEN |
| 2026-08-25 | 2026-08-11 | 3 | 91.6% | UP | DOWN | DOWN | -0.91% | RESCUED |
| 2026-08-26 | 2026-08-18 | 1 | 92.7% | UP | DOWN | DOWN | -2.12% | RESCUED |
| 2026-08-28 | 2026-08-18 | 3 | 96.1% | DOWN | UP | DOWN | -4.95% | BROKEN |
| 2026-09-04 | 2026-08-25 | 1 | 51.5% | UP | DOWN | DOWN | -1.17% | RESCUED |
| 2026-09-10 | 2026-09-01 | 1 | 92.7% | UP | DOWN | DOWN | -2.03% | RESCUED |
| 2026-09-17 | 2026-09-08 | 1 | 97.9% | DOWN | UP | UP | +0.88% | RESCUED |

## Dependence-aware inference

- V3GT_vs_AURORA / 2023-2024 / accuracy / block5: diff=+0.0000 pp; 95%=[-0.8715,+0.8715] pp; P(improve)=40.2%.
- V3GT_vs_AURORA / 2023-2024 / accuracy / block10: diff=+0.0000 pp; 95%=[-0.8715,+0.8715] pp; P(improve)=38.0%.
- V3GT_vs_AURORA / 2023-2024 / brier / block5: diff=-0.0009; 95%=[-0.0039,+0.0009]; P(improve)=66.9%.
- V3GT_vs_AURORA / 2023-2024 / brier / block10: diff=-0.0009; 95%=[-0.0037,+0.0008]; P(improve)=68.3%.
- V3GT_vs_AURORA / 2023-2024 / logloss / block5: diff=-0.0022; 95%=[-0.0087,+0.0017]; P(improve)=67.0%.
- V3GT_vs_AURORA / 2023-2024 / logloss / block10: diff=-0.0022; 95%=[-0.0087,+0.0015]; P(improve)=67.8%.
- V3GT_vs_AURORA / 2025-2026 / accuracy / block5: diff=+2.2779 pp; 95%=[+0.0000,+4.5558] pp; P(improve)=97.4%.
- V3GT_vs_AURORA / 2025-2026 / accuracy / block10: diff=+2.2779 pp; 95%=[+0.0000,+4.5558] pp; P(improve)=96.9%.
- V3GT_vs_AURORA / 2025-2026 / brier / block5: diff=-0.0044; 95%=[-0.0105,+0.0012]; P(improve)=93.6%.
- V3GT_vs_AURORA / 2025-2026 / brier / block10: diff=-0.0044; 95%=[-0.0104,+0.0012]; P(improve)=93.6%.
- V3GT_vs_AURORA / 2025-2026 / logloss / block5: diff=-0.0096; 95%=[-0.0228,+0.0027]; P(improve)=93.6%.
- V3GT_vs_AURORA / 2025-2026 / logloss / block10: diff=-0.0096; 95%=[-0.0229,+0.0024]; P(improve)=93.5%.
- V3GT_vs_AURORA / 2026 / accuracy / block5: diff=+4.7120 pp; 95%=[+1.0471,+8.9005] pp; P(improve)=99.2%.
- V3GT_vs_AURORA / 2026 / accuracy / block10: diff=+4.7120 pp; 95%=[+1.0471,+8.9005] pp; P(improve)=99.7%.
- V3GT_vs_AURORA / 2026 / brier / block5: diff=-0.0107; 95%=[-0.0216,-0.0007]; P(improve)=98.1%.
- V3GT_vs_AURORA / 2026 / brier / block10: diff=-0.0107; 95%=[-0.0214,-0.0020]; P(improve)=99.4%.
- V3GT_vs_AURORA / 2026 / logloss / block5: diff=-0.0227; 95%=[-0.0465,-0.0008]; P(improve)=97.9%.
- V3GT_vs_AURORA / 2026 / logloss / block10: diff=-0.0227; 95%=[-0.0458,-0.0038]; P(improve)=99.4%.
- V3GT_vs_HELIOS_V2 / 2023-2024 / accuracy / block5: diff=-0.2179 pp; 95%=[-0.6536,+0.0000] pp; P(improve)=0.0%.
- V3GT_vs_HELIOS_V2 / 2023-2024 / accuracy / block10: diff=-0.2179 pp; 95%=[-0.6536,+0.0000] pp; P(improve)=0.0%.
- V3GT_vs_HELIOS_V2 / 2023-2024 / brier / block5: diff=-0.0000; 95%=[-0.0008,+0.0007]; P(improve)=50.7%.
- V3GT_vs_HELIOS_V2 / 2023-2024 / brier / block10: diff=-0.0000; 95%=[-0.0009,+0.0007]; P(improve)=49.9%.
- V3GT_vs_HELIOS_V2 / 2023-2024 / logloss / block5: diff=-0.0001; 95%=[-0.0020,+0.0015]; P(improve)=53.5%.
- V3GT_vs_HELIOS_V2 / 2023-2024 / logloss / block10: diff=-0.0001; 95%=[-0.0021,+0.0015]; P(improve)=51.0%.
- V3GT_vs_HELIOS_V2 / 2025-2026 / accuracy / block5: diff=+0.9112 pp; 95%=[-0.9112,+2.7335] pp; P(improve)=80.2%.
- V3GT_vs_HELIOS_V2 / 2025-2026 / accuracy / block10: diff=+0.9112 pp; 95%=[-0.9112,+2.9613] pp; P(improve)=79.7%.
- V3GT_vs_HELIOS_V2 / 2025-2026 / brier / block5: diff=-0.0016; 95%=[-0.0080,+0.0043]; P(improve)=69.8%.
- V3GT_vs_HELIOS_V2 / 2025-2026 / brier / block10: diff=-0.0016; 95%=[-0.0083,+0.0039]; P(improve)=69.0%.
- V3GT_vs_HELIOS_V2 / 2025-2026 / logloss / block5: diff=-0.0040; 95%=[-0.0183,+0.0091]; P(improve)=71.4%.
- V3GT_vs_HELIOS_V2 / 2025-2026 / logloss / block10: diff=-0.0040; 95%=[-0.0186,+0.0082]; P(improve)=71.0%.
- V3GT_vs_HELIOS_V2 / 2026 / accuracy / block5: diff=+3.6649 pp; 95%=[+0.5236,+6.8063] pp; P(improve)=98.8%.
- V3GT_vs_HELIOS_V2 / 2026 / accuracy / block10: diff=+3.6649 pp; 95%=[+1.0471,+6.8063] pp; P(improve)=99.5%.
- V3GT_vs_HELIOS_V2 / 2026 / brier / block5: diff=-0.0085; 95%=[-0.0212,+0.0030]; P(improve)=92.2%.
- V3GT_vs_HELIOS_V2 / 2026 / brier / block10: diff=-0.0085; 95%=[-0.0215,+0.0014]; P(improve)=94.6%.
- V3GT_vs_HELIOS_V2 / 2026 / logloss / block5: diff=-0.0183; 95%=[-0.0468,+0.0070]; P(improve)=91.8%.
- V3GT_vs_HELIOS_V2 / 2026 / logloss / block10: diff=-0.0183; 95%=[-0.0472,+0.0043]; P(improve)=93.7%.
- V3GT_vs_OPAL_RAW / 2023-2024 / accuracy / block5: diff=+2.3965 pp; 95%=[-0.8715,+5.8824] pp; P(improve)=91.3%.
- V3GT_vs_OPAL_RAW / 2023-2024 / accuracy / block10: diff=+2.3965 pp; 95%=[-1.0893,+6.3181] pp; P(improve)=90.2%.
- V3GT_vs_OPAL_RAW / 2023-2024 / brier / block5: diff=-0.0131; 95%=[-0.0259,-0.0011]; P(improve)=98.4%.
- V3GT_vs_OPAL_RAW / 2023-2024 / brier / block10: diff=-0.0131; 95%=[-0.0274,-0.0006]; P(improve)=98.3%.
- V3GT_vs_OPAL_RAW / 2023-2024 / logloss / block5: diff=-0.0295; 95%=[-0.0590,-0.0035]; P(improve)=98.9%.
- V3GT_vs_OPAL_RAW / 2023-2024 / logloss / block10: diff=-0.0295; 95%=[-0.0602,-0.0020]; P(improve)=98.3%.
- V3GT_vs_OPAL_RAW / 2025-2026 / accuracy / block5: diff=+0.6834 pp; 95%=[-1.1390,+2.7335] pp; P(improve)=70.8%.
- V3GT_vs_OPAL_RAW / 2025-2026 / accuracy / block10: diff=+0.6834 pp; 95%=[-1.1390,+2.7335] pp; P(improve)=71.2%.
- V3GT_vs_OPAL_RAW / 2025-2026 / brier / block5: diff=-0.0064; 95%=[-0.0163,+0.0024]; P(improve)=91.0%.
- V3GT_vs_OPAL_RAW / 2025-2026 / brier / block10: diff=-0.0064; 95%=[-0.0168,+0.0023]; P(improve)=91.6%.
- V3GT_vs_OPAL_RAW / 2025-2026 / logloss / block5: diff=-0.0164; 95%=[-0.0401,+0.0039]; P(improve)=93.7%.
- V3GT_vs_OPAL_RAW / 2025-2026 / logloss / block10: diff=-0.0164; 95%=[-0.0409,+0.0037]; P(improve)=94.1%.
- V3GT_vs_OPAL_RAW / 2026 / accuracy / block5: diff=+1.5707 pp; 95%=[-1.5707,+4.7120] pp; P(improve)=79.6%.
- V3GT_vs_OPAL_RAW / 2026 / accuracy / block10: diff=+1.5707 pp; 95%=[-1.0471,+4.7120] pp; P(improve)=79.5%.
- V3GT_vs_OPAL_RAW / 2026 / brier / block5: diff=-0.0082; 95%=[-0.0262,+0.0064]; P(improve)=84.2%.
- V3GT_vs_OPAL_RAW / 2026 / brier / block10: diff=-0.0082; 95%=[-0.0276,+0.0061]; P(improve)=82.0%.
- V3GT_vs_OPAL_RAW / 2026 / logloss / block5: diff=-0.0214; 95%=[-0.0644,+0.0137]; P(improve)=86.1%.
- V3GT_vs_OPAL_RAW / 2026 / logloss / block10: diff=-0.0214; 95%=[-0.0671,+0.0118]; P(improve)=84.6%.
- V3GT_NET_RESCUE_CLUSTERED_BY_COT_VINTAGE / 2025-2026: net=+10; COT-vintage clusters=22; 95%=[+1,+19]; P(net>0)=97.5%.
- V3GT_NET_RESCUE_CLUSTERED_BY_COT_VINTAGE / 2026: net=+9; COT-vintage clusters=10; 95%=[+3,+15]; P(net>0)=99.8%.

## Robustness summary

- window / W6_C1.00: Acc 65.15%, routed 30, rescue/broken 20/10, net +10, Brier 0.2323.
- window / W8_C1.00: Acc 65.15%, routed 30, rescue/broken 20/10, net +10, Brier 0.2319.
- window / W10_C1.00: Acc 64.69%, routed 26, rescue/broken 17/9, net +8, Brier 0.2331.
- window / W12_C1.00: Acc 64.92%, routed 27, rescue/broken 18/9, net +9, Brier 0.2332.
- broken_cost / W8_C1.25: Acc 65.60%, routed 24, rescue/broken 18/6, net +12, Brier 0.2309.
- broken_cost / W8_C1.50: Acc 65.38%, routed 23, rescue/broken 17/6, net +11, Brier 0.2313.
- policy_ablation / NO_UNION: Acc 64.69%, routed 26, rescue/broken 17/9, net +8, Brier 0.2328.
- policy_ablation / NO_FRESH: Acc 64.92%, routed 27, rescue/broken 18/9, net +9, Brier 0.2328.
- policy_ablation / NO_OPAL_ALL: Acc 64.92%, routed 19, rescue/broken 14/5, net +9, Brier 0.2323.
- policy_ablation / CORE3: Acc 64.92%, routed 19, rescue/broken 14/5, net +9, Brier 0.2329.

## Governance

V3-GT is retrospective strengthening research. Its architecture was developed after historical error anatomy and therefore cannot be called prospective confirmation. The frozen AURORA prospective champion remains unchanged. Any operational promotion requires a separate future-origin V3-GT freeze with no retrospective retuning.
