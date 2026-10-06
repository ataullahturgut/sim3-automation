# SESSION IRIS15 — NESTED VARIABLE / LAG SELECTION V2 BALANCED

**Status:** SESSION_IRIS15_NESTED_SELECTION_V2_BALANCED_COMPLETE

- 2023–2024 development chronology only; 2025/2026 unopened.
- Every outer test block selects variables using only earlier training data.
- Class-balanced L1 selects variables/lags; selected set is refit with class-balanced L2 C=0.30.
- Silver/Platinum are optional candidates, never forced.

## 2024 outer-replay metrics

| Model | Partition | Window | N | Acc | BA | Brier |
|---|---|---|---:|---:|---:|---:|
| FULL_XAU15_L2_C1 | SOBTI_5_ET | ASIA_AFTERNOON_LIT | 93 | 52.69% | 52.43% | 0.2999 |
| FULL_XAU15_L2_C1 | SOBTI_5_ET | ASIA_MORNING_LIT | 90 | 54.44% | 55.20% | 0.2991 |
| FULL_XAU15_L2_C1 | SOBTI_5_ET | EUROPE_LIT | 113 | 47.79% | 45.50% | 0.3093 |
| FULL_XAU15_L2_C1 | SOBTI_5_ET | NY_LONDON_LIT | 116 | 55.17% | 55.13% | 0.2891 |
| FULL_XAU15_L2_C1 | SOBTI_5_ET | US_LATE_LIT | 15 | 66.67% | 69.44% | 0.2188 |
| FULL_XAU15_L2_C1 | WGC_2026_NY3 | ASIA | 3 | 66.67% | 66.67% | 0.1396 |
| FULL_XAU15_L2_C1 | WGC_2026_NY3 | EUROPE | 114 | 50.00% | 48.62% | 0.2845 |
| FULL_XAU15_L2_C1 | WGC_2026_NY3 | US | 83 | 50.60% | 50.41% | 0.2796 |
| SELECT_ALL15_BAL | SOBTI_5_ET | ASIA_AFTERNOON_LIT | 93 | 51.61% | 51.67% | 0.2932 |
| SELECT_ALL15_BAL | SOBTI_5_ET | ASIA_MORNING_LIT | 90 | 53.33% | 49.77% | 0.2695 |
| SELECT_ALL15_BAL | SOBTI_5_ET | EUROPE_LIT | 113 | 51.33% | 46.70% | 0.2781 |
| SELECT_ALL15_BAL | SOBTI_5_ET | NY_LONDON_LIT | 116 | 50.86% | 50.92% | 0.2908 |
| SELECT_ALL15_BAL | SOBTI_5_ET | US_LATE_LIT | 15 | 66.67% | 66.67% | 0.1734 |
| SELECT_ALL15_BAL | WGC_2026_NY3 | ASIA | 3 | 100.00% | 100.00% | 0.0846 |
| SELECT_ALL15_BAL | WGC_2026_NY3 | EUROPE | 114 | 46.49% | 47.30% | 0.2673 |
| SELECT_ALL15_BAL | WGC_2026_NY3 | US | 83 | 53.01% | 52.61% | 0.2537 |
| SELECT_XAU15_BAL | SOBTI_5_ET | ASIA_AFTERNOON_LIT | 93 | 55.91% | 55.83% | 0.2699 |
| SELECT_XAU15_BAL | SOBTI_5_ET | ASIA_MORNING_LIT | 90 | 53.33% | 53.03% | 0.2824 |
| SELECT_XAU15_BAL | SOBTI_5_ET | EUROPE_LIT | 113 | 53.98% | 48.66% | 0.2574 |
| SELECT_XAU15_BAL | SOBTI_5_ET | NY_LONDON_LIT | 116 | 54.31% | 54.28% | 0.2750 |
| SELECT_XAU15_BAL | SOBTI_5_ET | US_LATE_LIT | 15 | 60.00% | 63.89% | 0.1923 |
| SELECT_XAU15_BAL | WGC_2026_NY3 | ASIA | 3 | 66.67% | 66.67% | 0.2438 |
| SELECT_XAU15_BAL | WGC_2026_NY3 | EUROPE | 114 | 50.00% | 49.87% | 0.2684 |
| SELECT_XAU15_BAL | WGC_2026_NY3 | US | 83 | 46.99% | 46.72% | 0.2670 |

## Cross-metal selection rates

| Partition | Window | Blocks | Silver selected | Platinum selected | Both |
|---|---|---:|---:|---:|---:|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 19 | 100.0% | 100.0% | 100.0% |
| SOBTI_5_ET | ASIA_MORNING_LIT | 18 | 55.6% | 55.6% | 55.6% |
| SOBTI_5_ET | EUROPE_LIT | 23 | 56.5% | 39.1% | 39.1% |
| SOBTI_5_ET | NY_LONDON_LIT | 24 | 83.3% | 95.8% | 83.3% |
| SOBTI_5_ET | US_LATE_LIT | 3 | 100.0% | 100.0% | 100.0% |
| WGC_2026_NY3 | ASIA | 1 | 100.0% | 100.0% | 100.0% |
| WGC_2026_NY3 | EUROPE | 23 | 95.7% | 39.1% | 39.1% |
| WGC_2026_NY3 | US | 17 | 41.2% | 41.2% | 41.2% |
