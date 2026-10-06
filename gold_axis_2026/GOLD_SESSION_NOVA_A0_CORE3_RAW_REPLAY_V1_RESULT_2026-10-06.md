# NOVA A0 / CORE3 — RAW SESSION REPLAY V1

**Status:** completed from raw daily metals + raw 15m targets.

- model role: Stage-1 primary direction engine
- 2023–2024 only; 2025 unopened
- same-day daily metal values: prohibited
- V5 raw target reproduction: PASS

## Metrics

| Partition | Window | Period | N | Accuracy | Balanced | UP recall | DOWN recall | Brier |
|---|---|---|---:|---:|---:|---:|---:|---:|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 2023 | 117 | 44.44% | 44.67% | 39.34% | 50.00% | 0.2684 |
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 2024 | 241 | 49.38% | 49.42% | 39.67% | 59.17% | 0.2592 |
| SOBTI_5_ET | ASIA_MORNING_LIT | 2023 | 117 | 52.14% | 51.83% | 59.02% | 44.64% | 0.2506 |
| SOBTI_5_ET | ASIA_MORNING_LIT | 2024 | 241 | 55.19% | 55.03% | 56.30% | 53.77% | 0.2649 |
| SOBTI_5_ET | EUROPE_LIT | 2023 | 129 | 51.16% | 51.18% | 50.75% | 51.61% | 0.2744 |
| SOBTI_5_ET | EUROPE_LIT | 2024 | 254 | 51.57% | 50.94% | 56.74% | 45.13% | 0.2609 |
| SOBTI_5_ET | NY_LONDON_LIT | 2023 | 127 | 55.12% | 52.26% | 30.91% | 73.61% | 0.2610 |
| SOBTI_5_ET | NY_LONDON_LIT | 2024 | 252 | 48.02% | 47.77% | 55.38% | 40.16% | 0.2683 |
| SOBTI_5_ET | US_LATE_LIT | 2023 | 76 | 51.32% | 44.13% | 74.47% | 13.79% | 0.2571 |
| SOBTI_5_ET | US_LATE_LIT | 2024 | 198 | 59.09% | 52.17% | 81.97% | 22.37% | 0.2425 |
| WGC_2026_NY3 | ASIA | 2023 | 132 | 55.30% | 53.64% | 63.64% | 43.64% | 0.2479 |
| WGC_2026_NY3 | ASIA | 2024 | 244 | 52.87% | 49.78% | 71.94% | 27.62% | 0.2590 |
| WGC_2026_NY3 | EUROPE | 2023 | 128 | 50.78% | 49.14% | 58.67% | 39.62% | 0.2651 |
| WGC_2026_NY3 | EUROPE | 2024 | 254 | 51.18% | 49.92% | 63.31% | 36.52% | 0.2542 |
| WGC_2026_NY3 | US | 2023 | 101 | 53.47% | 50.29% | 35.00% | 65.57% | 0.2645 |
| WGC_2026_NY3 | US | 2024 | 245 | 45.31% | 45.60% | 40.77% | 50.43% | 0.2718 |
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 2023-2024_SCORED | 358 | 47.77% | 47.91% | 39.56% | 56.25% | 0.2622 |
| SOBTI_5_ET | ASIA_MORNING_LIT | 2023-2024_SCORED | 358 | 54.19% | 53.88% | 57.14% | 50.62% | 0.2603 |
| SOBTI_5_ET | EUROPE_LIT | 2023-2024_SCORED | 383 | 51.44% | 51.12% | 54.81% | 47.43% | 0.2655 |
| SOBTI_5_ET | NY_LONDON_LIT | 2023-2024_SCORED | 379 | 50.40% | 50.34% | 48.11% | 52.58% | 0.2659 |
| SOBTI_5_ET | US_LATE_LIT | 2023-2024_SCORED | 274 | 56.93% | 49.94% | 79.88% | 20.00% | 0.2466 |
| WGC_2026_NY3 | ASIA | 2023-2024_SCORED | 376 | 53.72% | 51.05% | 68.98% | 33.12% | 0.2551 |
| WGC_2026_NY3 | EUROPE | 2023-2024_SCORED | 382 | 51.05% | 49.59% | 61.68% | 37.50% | 0.2578 |
| WGC_2026_NY3 | US | 2023-2024_SCORED | 346 | 47.69% | 47.55% | 39.41% | 55.68% | 0.2697 |
