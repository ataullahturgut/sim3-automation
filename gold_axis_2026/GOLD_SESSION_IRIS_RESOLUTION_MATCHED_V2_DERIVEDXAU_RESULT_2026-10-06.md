# SESSION IRIS — MATCHED 15m vs DERIVED-1h RESOLUTION TEST

**Status:** SESSION_IRIS_RESOLUTION_MATCHED_V2_DERIVEDXAU_COMPLETE

- Same target rows, same CORE3, same model, same feature families.
- XAU 1h is derived from the same governed XAU 15m archive; native 1h vendor bars are excluded from this binding comparison.
- Difference under test: 15m vs 1h intraday sampling / pre-target freshness.
- 2025/2026 unopened.

## Paired comparison

| Family | Partition | Window | N | 15m Acc | 1h Acc | ΔAcc pp | 15m BA | 1h BA | ΔBA pp | 15m Brier | 1h Brier | 15m-only correct | 1h-only correct |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| XAU_ONLY | SOBTI_5_ET | ASIA_AFTERNOON_LIT | 93 | 52.69% | 47.31% | +5.38 | 52.43% | 47.43% | +5.00 | 0.2999 | 0.2975 | 18 | 13 |
| XAU_ONLY | SOBTI_5_ET | ASIA_MORNING_LIT | 88 | 54.55% | 52.27% | +2.27 | 55.13% | 51.07% | +4.06 | 0.3010 | 0.3000 | 12 | 10 |
| XAU_ONLY | SOBTI_5_ET | EUROPE_LIT | 112 | 46.43% | 47.32% | -0.89 | 43.68% | 44.76% | -1.09 | 0.3131 | 0.3087 | 16 | 17 |
| XAU_ONLY | SOBTI_5_ET | NY_LONDON_LIT | 114 | 56.14% | 52.63% | +3.51 | 56.16% | 52.56% | +3.60 | 0.2983 | 0.2917 | 14 | 10 |
| XAU_ONLY | SOBTI_5_ET | US_LATE_LIT | 15 | 66.67% | 60.00% | +6.67 | 69.44% | 61.11% | +8.33 | 0.2188 | 0.2389 | 3 | 2 |
| XAU_ONLY | WGC_2026_NY3 | ASIA | 2 | 50.00% | 50.00% | +0.00 | 50.00% | 50.00% | +0.00 | 0.1807 | 0.2796 | 1 | 1 |
| XAU_ONLY | WGC_2026_NY3 | EUROPE | 109 | 52.29% | 51.38% | +0.92 | 50.60% | 49.54% | +1.06 | 0.2863 | 0.2867 | 13 | 12 |
| XAU_ONLY | WGC_2026_NY3 | US | 82 | 53.66% | 47.56% | +6.10 | 53.27% | 47.14% | +6.13 | 0.2798 | 0.2762 | 12 | 7 |
| XAU_SI | SOBTI_5_ET | ASIA_AFTERNOON_LIT | 93 | 50.54% | 53.76% | -3.23 | 50.21% | 53.82% | -3.61 | 0.3093 | 0.3127 | 11 | 14 |
| XAU_SI | SOBTI_5_ET | ASIA_MORNING_LIT | 88 | 50.00% | 51.14% | -1.14 | 49.57% | 49.25% | +0.32 | 0.3217 | 0.3115 | 13 | 14 |
| XAU_SI | SOBTI_5_ET | EUROPE_LIT | 112 | 47.32% | 45.54% | +1.79 | 44.43% | 43.91% | +0.53 | 0.3320 | 0.3329 | 21 | 19 |
| XAU_SI | SOBTI_5_ET | NY_LONDON_LIT | 114 | 50.88% | 47.37% | +3.51 | 50.92% | 47.29% | +3.63 | 0.3200 | 0.3191 | 14 | 10 |
| XAU_SI | SOBTI_5_ET | US_LATE_LIT | 15 | 66.67% | 73.33% | -6.67 | 66.67% | 77.78% | -11.11 | 0.2184 | 0.2086 | 2 | 3 |
| XAU_SI | WGC_2026_NY3 | ASIA | 2 | 100.00% | 100.00% | +0.00 | 100.00% | 100.00% | +0.00 | 0.0286 | 0.0132 | 0 | 0 |
| XAU_SI | WGC_2026_NY3 | EUROPE | 109 | 48.62% | 48.62% | +0.00 | 46.35% | 48.15% | -1.80 | 0.3125 | 0.3166 | 16 | 16 |
| XAU_SI | WGC_2026_NY3 | US | 82 | 53.66% | 54.88% | -1.22 | 53.33% | 54.58% | -1.25 | 0.2998 | 0.3011 | 9 | 10 |
| XAU_SI_PL | SOBTI_5_ET | ASIA_AFTERNOON_LIT | 93 | 53.76% | 49.46% | +4.30 | 53.47% | 49.44% | +4.03 | 0.3129 | 0.3323 | 14 | 10 |
| XAU_SI_PL | SOBTI_5_ET | ASIA_MORNING_LIT | 88 | 51.14% | 53.41% | -2.27 | 49.68% | 51.18% | -1.50 | 0.3404 | 0.3318 | 16 | 18 |
| XAU_SI_PL | SOBTI_5_ET | EUROPE_LIT | 112 | 50.00% | 47.32% | +2.68 | 48.35% | 46.08% | +2.27 | 0.3494 | 0.3483 | 18 | 15 |
| XAU_SI_PL | SOBTI_5_ET | NY_LONDON_LIT | 114 | 53.51% | 56.14% | -2.63 | 53.54% | 56.13% | -2.59 | 0.3429 | 0.3267 | 11 | 14 |
| XAU_SI_PL | SOBTI_5_ET | US_LATE_LIT | 15 | 73.33% | 80.00% | -6.67 | 75.00% | 83.33% | -8.33 | 0.1818 | 0.1909 | 1 | 2 |
| XAU_SI_PL | WGC_2026_NY3 | ASIA | 2 | 100.00% | 100.00% | +0.00 | 100.00% | 100.00% | +0.00 | 0.0210 | 0.0079 | 0 | 0 |
| XAU_SI_PL | WGC_2026_NY3 | EUROPE | 109 | 51.38% | 45.87% | +5.50 | 49.02% | 45.21% | +3.81 | 0.3171 | 0.3563 | 21 | 15 |
| XAU_SI_PL | WGC_2026_NY3 | US | 82 | 53.66% | 62.20% | -8.54 | 53.21% | 62.02% | -8.81 | 0.2861 | 0.2865 | 9 | 16 |
