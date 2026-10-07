# GOLD SESSION — CANONICAL INCREMENTAL / DISAGREEMENT AUDIT

**Scope:** 2023–2024 development only. No 2025/2026 outcomes read.

## Balanced base selected per session

| Partition | Window | Base | N | BA | UP | DOWN | Brier |
|---|---|---|---:|---:|---:|---:|---:|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | S17_A1_SESSION | 191 | 52.21% | 53.85% | 50.57% | 0.2688 |
| SOBTI_5_ET | ASIA_MORNING_LIT | CORE3_A0 | 358 | 53.88% | 57.14% | 50.62% | 0.2603 |
| SOBTI_5_ET | EUROPE_LIT | CORE3_A0 | 383 | 51.12% | 54.81% | 47.43% | 0.2655 |
| SOBTI_5_ET | NY_LONDON_LIT | STRUCTURAL_IRIS_1H | 215 | 53.26% | 46.15% | 60.36% | 0.2796 |
| SOBTI_5_ET | US_LATE_LIT | S17_A1_SESSION | 89 | 50.23% | 68.75% | 31.71% | 0.2667 |
| WGC_2026_NY3 | ASIA | S15_SESSION_ONLY | 152 | 56.21% | 67.33% | 45.10% | 0.2497 |
| WGC_2026_NY3 | EUROPE | STRUCTURAL_IRIS_1H | 210 | 52.28% | 68.60% | 35.96% | 0.2681 |
| WGC_2026_NY3 | US | S18_A1_PATH_SESSION | 177 | 50.89% | 32.56% | 69.23% | 0.3041 |

## Highest positive incremental candidates on exact-common rows

| Partition | Window | Base | Candidate | Common N | Disagree N | Rescue | Break | Net | Cand win on disagreement | ΔUP | ΔDOWN | Agreement | Corr |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | S17_A1_SESSION | STRUCTURAL_IRIS_1H | 190 | 70 | 34 | 36 | -2 | 48.57% | -1.94 pp | +0.00 pp | 63.16% | 0.331 |
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | S17_A1_SESSION | S18_A1_PATH_SESSION | 191 | 56 | 24 | 32 | -8 | 42.86% | -3.85 pp | -4.60 pp | 70.68% | 0.603 |
| SOBTI_5_ET | ASIA_MORNING_LIT | CORE3_A0 | NOVA_A1_ARCR | 223 | 11 | 5 | 6 | -1 | 45.45% | -0.78 pp | +0.00 pp | 95.07% | 0.993 |
| SOBTI_5_ET | ASIA_MORNING_LIT | CORE3_A0 | S17_A1_SESSION | 184 | 83 | 39 | 44 | -5 | 46.99% | -9.43 pp | +6.41 pp | 54.89% | 0.158 |
| SOBTI_5_ET | EUROPE_LIT | CORE3_A0 | PATH_GLOBAL_1H | 323 | 153 | 76 | 77 | -1 | 49.67% | +0.00 pp | -0.67 pp | 52.63% | 0.123 |
| SOBTI_5_ET | EUROPE_LIT | CORE3_A0 | S15_SESSION_ONLY | 225 | 105 | 52 | 53 | -1 | 49.52% | +23.02 pp | -30.30 pp | 53.33% | -0.112 |
| SOBTI_5_ET | NY_LONDON_LIT | STRUCTURAL_IRIS_1H | S16_PATH_SESSION | 215 | 84 | 41 | 43 | -2 | 48.81% | +7.69 pp | -9.01 pp | 60.93% | 0.431 |
| SOBTI_5_ET | NY_LONDON_LIT | STRUCTURAL_IRIS_1H | PATH_GLOBAL_1H | 190 | 59 | 28 | 31 | -3 | 47.46% | +7.22 pp | -10.75 pp | 68.95% | 0.632 |
| SOBTI_5_ET | US_LATE_LIT | S17_A1_SESSION | NOVA_A1_ARCR | 68 | 25 | 14 | 11 | +3 | 56.00% | +14.71 pp | -5.88 pp | 63.24% | 0.079 |
| SOBTI_5_ET | US_LATE_LIT | S17_A1_SESSION | CORE3_A0 | 89 | 33 | 18 | 15 | +3 | 54.55% | +14.58 pp | -9.76 pp | 62.92% | 0.050 |
| WGC_2026_NY3 | ASIA | S15_SESSION_ONLY | S18_A1_PATH_SESSION | 102 | 30 | 17 | 13 | +4 | 56.67% | +14.49 pp | -18.18 pp | 70.59% | 0.428 |
| WGC_2026_NY3 | ASIA | S15_SESSION_ONLY | STRUCTURAL_IRIS_1H | 102 | 35 | 19 | 16 | +3 | 54.29% | +14.49 pp | -21.21 pp | 65.69% | 0.183 |
| WGC_2026_NY3 | ASIA | S15_SESSION_ONLY | S17_A1_SESSION | 102 | 30 | 16 | 14 | +2 | 53.33% | +10.14 pp | -15.15 pp | 70.59% | 0.657 |
| WGC_2026_NY3 | EUROPE | STRUCTURAL_IRIS_1H | NOVA_A1_ARCR | 145 | 37 | 19 | 18 | +1 | 51.35% | -7.06 pp | +11.67 pp | 74.48% | 0.424 |
| WGC_2026_NY3 | EUROPE | STRUCTURAL_IRIS_1H | CORE3_A0 | 210 | 59 | 30 | 29 | +1 | 50.85% | -2.48 pp | +4.49 pp | 71.90% | 0.359 |
| WGC_2026_NY3 | US | S18_A1_PATH_SESSION | S17_A1_SESSION | 177 | 56 | 28 | 28 | +0 | 50.00% | -9.30 pp | +8.79 pp | 68.36% | 0.459 |
| WGC_2026_NY3 | US | S18_A1_PATH_SESSION | STRUCTURAL_IRIS_1H | 177 | 25 | 12 | 13 | -1 | 48.00% | -2.33 pp | +1.10 pp | 85.88% | 0.827 |

## Interpretation guardrail

Positive net rescue is evidence of incremental directional information on the common development rows, not automatic consensus membership. Selected-feature variants and correction specialists require their own second-stage audit before the role matrix can be fully frozen.
