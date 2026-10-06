# S1.4 STRUCTURAL_IRIS — FRESH A1 + PATH

**Status:** S1_4_STRUCTURAL_IRIS_FRESH_COMPLETE

- Fresh A1 regenerated from raw daily metals in-process.
- Canonical head: A1 logit + same-source-derived 1h XAU full IRIS PATH.
- Challengers: A1 + 15m full PATH and A1 + 15m frozen-selection-mode PATH.
- No archived A1/IRIS predictions used.
- 2025/2026 unopened.

## Paired metrics on exact scored rows

| Partition | Window | Model | N | Acc | BA | UP | DOWN | Brier | ΔBA vs A1 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | A1_DIRECT_MATCHED | 50 | 44.00% | 44.23% | 38.46% | 50.00% | 0.2631 | +0.00 pp |
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | S14_A1_PLUS_1H_FULL | 50 | 52.00% | 51.44% | 65.38% | 37.50% | 0.2714 | +7.21 pp |
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | S14_A1_PLUS_15M_FULL | 50 | 50.00% | 50.16% | 46.15% | 54.17% | 0.2756 | +5.93 pp |
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | S14_A1_PLUS_15M_BLUEPRINT | 50 | 48.00% | 47.76% | 53.85% | 41.67% | 0.2622 | +3.53 pp |
| SOBTI_5_ET | ASIA_MORNING_LIT | A1_DIRECT_MATCHED | 46 | 65.22% | 64.96% | 65.62% | 64.29% | 0.2561 | +0.00 pp |
| SOBTI_5_ET | ASIA_MORNING_LIT | S14_A1_PLUS_1H_FULL | 46 | 52.17% | 43.53% | 65.62% | 21.43% | 0.3019 | -21.43 pp |
| SOBTI_5_ET | ASIA_MORNING_LIT | S14_A1_PLUS_15M_FULL | 46 | 54.35% | 45.09% | 68.75% | 21.43% | 0.2805 | -19.87 pp |
| SOBTI_5_ET | ASIA_MORNING_LIT | S14_A1_PLUS_15M_BLUEPRINT | 46 | 54.35% | 45.09% | 68.75% | 21.43% | 0.2805 | -19.87 pp |
| SOBTI_5_ET | EUROPE_LIT | A1_DIRECT_MATCHED | 66 | 48.48% | 48.21% | 50.00% | 46.43% | 0.2644 | +0.00 pp |
| SOBTI_5_ET | EUROPE_LIT | S14_A1_PLUS_1H_FULL | 66 | 51.52% | 47.09% | 76.32% | 17.86% | 0.3015 | -1.13 pp |
| SOBTI_5_ET | EUROPE_LIT | S14_A1_PLUS_15M_FULL | 66 | 53.03% | 49.34% | 73.68% | 25.00% | 0.3011 | +1.13 pp |
| SOBTI_5_ET | EUROPE_LIT | S14_A1_PLUS_15M_BLUEPRINT | 66 | 53.03% | 49.34% | 73.68% | 25.00% | 0.3011 | +1.13 pp |
| SOBTI_5_ET | NY_LONDON_LIT | A1_DIRECT_MATCHED | 66 | 48.48% | 48.53% | 50.00% | 47.06% | 0.2621 | +0.00 pp |
| SOBTI_5_ET | NY_LONDON_LIT | S14_A1_PLUS_1H_FULL | 66 | 54.55% | 54.69% | 59.38% | 50.00% | 0.2942 | +6.16 pp |
| SOBTI_5_ET | NY_LONDON_LIT | S14_A1_PLUS_15M_FULL | 66 | 48.48% | 48.71% | 56.25% | 41.18% | 0.3084 | +0.18 pp |
| SOBTI_5_ET | NY_LONDON_LIT | S14_A1_PLUS_15M_BLUEPRINT | 66 | 48.48% | 48.71% | 56.25% | 41.18% | 0.3084 | +0.18 pp |
| WGC_2026_NY3 | ASIA | A1_DIRECT_MATCHED | 11 | 54.55% | 48.21% | 71.43% | 25.00% | 0.2318 | +0.00 pp |
| WGC_2026_NY3 | ASIA | S14_A1_PLUS_1H_FULL | 11 | 54.55% | 48.21% | 71.43% | 25.00% | 0.2963 | +0.00 pp |
| WGC_2026_NY3 | ASIA | S14_A1_PLUS_15M_FULL | 11 | 54.55% | 48.21% | 71.43% | 25.00% | 0.2892 | +0.00 pp |
| WGC_2026_NY3 | ASIA | S14_A1_PLUS_15M_BLUEPRINT | 11 | 54.55% | 48.21% | 71.43% | 25.00% | 0.2892 | +0.00 pp |
| WGC_2026_NY3 | EUROPE | A1_DIRECT_MATCHED | 65 | 44.62% | 40.00% | 60.00% | 20.00% | 0.2603 | +0.00 pp |
| WGC_2026_NY3 | EUROPE | S14_A1_PLUS_1H_FULL | 65 | 63.08% | 59.50% | 75.00% | 44.00% | 0.2368 | +19.50 pp |
| WGC_2026_NY3 | EUROPE | S14_A1_PLUS_15M_FULL | 65 | 55.38% | 51.00% | 70.00% | 32.00% | 0.2903 | +11.00 pp |
| WGC_2026_NY3 | EUROPE | S14_A1_PLUS_15M_BLUEPRINT | 65 | 60.00% | 56.25% | 72.50% | 40.00% | 0.2703 | +16.25 pp |
| WGC_2026_NY3 | US | A1_DIRECT_MATCHED | 44 | 43.18% | 43.68% | 47.37% | 40.00% | 0.2598 | +0.00 pp |
| WGC_2026_NY3 | US | S14_A1_PLUS_1H_FULL | 44 | 56.82% | 56.95% | 57.89% | 56.00% | 0.2910 | +13.26 pp |
| WGC_2026_NY3 | US | S14_A1_PLUS_15M_FULL | 44 | 47.73% | 48.95% | 57.89% | 40.00% | 0.3358 | +5.26 pp |
| WGC_2026_NY3 | US | S14_A1_PLUS_15M_BLUEPRINT | 44 | 47.73% | 48.95% | 57.89% | 40.00% | 0.3358 | +5.26 pp |
