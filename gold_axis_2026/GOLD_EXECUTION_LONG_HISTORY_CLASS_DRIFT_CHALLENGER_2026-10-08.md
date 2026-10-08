# Long-history class drift remedies — preregistered ablations

**Research:** SAME base LIT feature models; 2020+ unweighted vs 2020+ balanced class weights vs 2020+ 365-day sample half-life. 2025 never used to select mode. PRAMV V1 NOT rerun.

| LIT model | Year | Mode | N | BA | UP recall | DOWN recall | Brier | Δ BA vs long plain |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| LIT_DAY0_EXEC_0900 | 2023 | LONG_PLAIN | 253 | 50.73% | 96.00% | 5.47% | 0.2510 | +0.00pp |
| LIT_DAY0_EXEC_0900 | 2023 | LONG_CLASS_BALANCED | 253 | 49.78% | 48.00% | 51.56% | 0.2496 | -0.95pp |
| LIT_DAY0_EXEC_0900 | 2023 | LONG_HALFLIFE_365 | 253 | 51.03% | 88.00% | 14.06% | 0.2521 | +0.30pp |
| LIT_DAY0_EXEC_0900 | 2024 | LONG_PLAIN | 259 | 50.28% | 93.29% | 7.27% | 0.2478 | +0.00pp |
| LIT_DAY0_EXEC_0900 | 2024 | LONG_CLASS_BALANCED | 259 | 45.78% | 44.30% | 47.27% | 0.2511 | -4.50pp |
| LIT_DAY0_EXEC_0900 | 2024 | LONG_HALFLIFE_365 | 259 | 46.08% | 78.52% | 13.64% | 0.2493 | -4.20pp |
| LIT_DAY0_EXEC_0900 | 2025 | LONG_PLAIN | 238 | 53.26% | 96.99% | 9.52% | 0.2426 | +0.00pp |
| LIT_DAY0_EXEC_0900 | 2025 | LONG_CLASS_BALANCED | 238 | 56.44% | 62.41% | 50.48% | 0.2451 | +3.18pp |
| LIT_DAY0_EXEC_0900 | 2025 | LONG_HALFLIFE_365 | 238 | 50.48% | 100.00% | 0.95% | 0.2470 | -2.78pp |
| LIT_OVN0_1600_1630 | 2023 | LONG_PLAIN | 256 | 50.00% | 100.00% | 0.00% | 0.2506 | +0.00pp |
| LIT_OVN0_1600_1630 | 2023 | LONG_CLASS_BALANCED | 256 | 45.14% | 50.76% | 39.52% | 0.2504 | -4.86pp |
| LIT_OVN0_1600_1630 | 2023 | LONG_HALFLIFE_365 | 256 | 48.89% | 96.97% | 0.81% | 0.2507 | -1.11pp |
| LIT_OVN0_1600_1630 | 2024 | LONG_PLAIN | 259 | 50.00% | 100.00% | 0.00% | 0.2485 | +0.00pp |
| LIT_OVN0_1600_1630 | 2024 | LONG_CLASS_BALANCED | 259 | 50.53% | 51.06% | 50.00% | 0.2500 | +0.53pp |
| LIT_OVN0_1600_1630 | 2024 | LONG_HALFLIFE_365 | 259 | 50.34% | 92.20% | 8.47% | 0.2490 | +0.34pp |
| LIT_OVN0_1600_1630 | 2025 | LONG_PLAIN | 254 | 49.66% | 99.32% | 0.00% | 0.2465 | +0.00pp |
| LIT_OVN0_1600_1630 | 2025 | LONG_CLASS_BALANCED | 254 | 54.90% | 61.64% | 48.15% | 0.2499 | +5.24pp |
| LIT_OVN0_1600_1630 | 2025 | LONG_HALFLIFE_365 | 254 | 49.70% | 93.84% | 5.56% | 0.2467 | +0.04pp |
| LIT_OVN1_PAIR | 2023 | LONG_PLAIN | 255 | 47.46% | 90.08% | 4.84% | 0.2533 | +0.00pp |
| LIT_OVN1_PAIR | 2023 | LONG_CLASS_BALANCED | 255 | 47.86% | 47.33% | 48.39% | 0.2530 | +0.40pp |
| LIT_OVN1_PAIR | 2023 | LONG_HALFLIFE_365 | 255 | 45.97% | 85.50% | 6.45% | 0.2531 | -1.48pp |
| LIT_OVN1_PAIR | 2024 | LONG_PLAIN | 259 | 48.71% | 91.49% | 5.93% | 0.2475 | +0.00pp |
| LIT_OVN1_PAIR | 2024 | LONG_CLASS_BALANCED | 259 | 52.80% | 53.90% | 51.69% | 0.2489 | +4.09pp |
| LIT_OVN1_PAIR | 2024 | LONG_HALFLIFE_365 | 259 | 51.45% | 85.11% | 17.80% | 0.2494 | +2.74pp |
| LIT_OVN1_PAIR | 2025 | LONG_PLAIN | 253 | 50.50% | 88.97% | 12.04% | 0.2474 | +0.00pp |
| LIT_OVN1_PAIR | 2025 | LONG_CLASS_BALANCED | 253 | 50.06% | 48.28% | 51.85% | 0.2508 | -0.44pp |
| LIT_OVN1_PAIR | 2025 | LONG_HALFLIFE_365 | 253 | 52.86% | 75.17% | 30.56% | 0.2486 | +2.36pp |

Interpretation: avoid interpreting improved class balance as positive edge unless BA > 50% in both development years, calibration is sound, and 2025 retrospective transport is consistent. No prospective confirmation or bank P&L.
