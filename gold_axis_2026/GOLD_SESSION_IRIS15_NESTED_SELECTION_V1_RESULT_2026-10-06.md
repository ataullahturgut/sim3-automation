# SESSION IRIS15 — NESTED VARIABLE / LAG SELECTION V1

**Status:** SESSION_IRIS15_NESTED_SELECTION_V1_COMPLETE

- 2023–2024 development chronology only; 2025/2026 unopened.
- Every outer test block selects variables using only earlier training data.
- L1 selects variables/lags; selected set is refit with L2 C=0.30.
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
| SELECT_ALL15 | SOBTI_5_ET | ASIA_AFTERNOON_LIT | 93 | 53.76% | 53.54% | 0.2798 |
| SELECT_ALL15 | SOBTI_5_ET | ASIA_MORNING_LIT | 90 | 56.67% | 52.60% | 0.2674 |
| SELECT_ALL15 | SOBTI_5_ET | EUROPE_LIT | 113 | 53.98% | 48.66% | 0.2757 |
| SELECT_ALL15 | SOBTI_5_ET | NY_LONDON_LIT | 116 | 51.72% | 51.83% | 0.2840 |
| SELECT_ALL15 | SOBTI_5_ET | US_LATE_LIT | 15 | 60.00% | 63.89% | 0.1970 |
| SELECT_ALL15 | WGC_2026_NY3 | ASIA | 3 | 100.00% | 100.00% | 0.0450 |
| SELECT_ALL15 | WGC_2026_NY3 | EUROPE | 114 | 52.63% | 49.92% | 0.2621 |
| SELECT_ALL15 | WGC_2026_NY3 | US | 83 | 54.22% | 53.69% | 0.2466 |
| SELECT_XAU15 | SOBTI_5_ET | ASIA_AFTERNOON_LIT | 93 | 51.61% | 51.53% | 0.2838 |
| SELECT_XAU15 | SOBTI_5_ET | ASIA_MORNING_LIT | 90 | 55.56% | 54.11% | 0.2730 |
| SELECT_XAU15 | SOBTI_5_ET | EUROPE_LIT | 113 | 55.75% | 50.48% | 0.2609 |
| SELECT_XAU15 | SOBTI_5_ET | NY_LONDON_LIT | 116 | 53.45% | 53.46% | 0.2749 |
| SELECT_XAU15 | SOBTI_5_ET | US_LATE_LIT | 15 | 40.00% | 50.00% | 0.2758 |
| SELECT_XAU15 | WGC_2026_NY3 | ASIA | 3 | 66.67% | 66.67% | 0.1840 |
| SELECT_XAU15 | WGC_2026_NY3 | EUROPE | 114 | 53.51% | 51.95% | 0.2727 |
| SELECT_XAU15 | WGC_2026_NY3 | US | 83 | 46.99% | 46.43% | 0.2680 |

## Cross-metal selection rates

| Partition | Window | Blocks | Silver selected | Platinum selected | Both |
|---|---|---:|---:|---:|---:|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 19 | 94.7% | 94.7% | 94.7% |
| SOBTI_5_ET | ASIA_MORNING_LIT | 18 | 50.0% | 50.0% | 50.0% |
| SOBTI_5_ET | EUROPE_LIT | 23 | 56.5% | 39.1% | 39.1% |
| SOBTI_5_ET | NY_LONDON_LIT | 24 | 87.5% | 87.5% | 87.5% |
| SOBTI_5_ET | US_LATE_LIT | 3 | 66.7% | 66.7% | 66.7% |
| WGC_2026_NY3 | ASIA | 1 | 100.0% | 100.0% | 100.0% |
| WGC_2026_NY3 | EUROPE | 23 | 69.6% | 43.5% | 43.5% |
| WGC_2026_NY3 | US | 17 | 29.4% | 29.4% | 29.4% |
