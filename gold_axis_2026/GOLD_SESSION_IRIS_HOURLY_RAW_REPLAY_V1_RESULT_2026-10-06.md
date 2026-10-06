# IRIS SESSION RAW REPLAY V1 — HOURLY BRANCH

**Status:** IRIS hourly-only branch completed from raw sources.

- Historical derived IRIS files used as input: **NO**
- V5 targets independently reconstructed from raw 15m: **PASS**
- Hourly close availability leakage check: **PASS**
- Scoring: **2023-2024 only**
- 2025: **UNOPENED in this replay**

## Important limitation

The original full IRIS A1+PATH candidate needs a structural A1 logit. Rebuilding that logit against the new session targets requires sufficient earlier session-target history. The current governed V5 target history begins in 2023, so the full structural branch is not silently substituted with old H3 predictions.

## Metrics

| Partition | Window | Period | N | Accuracy | Balanced | UP recall | DOWN recall | Brier |
|---|---|---|---:|---:|---:|---:|---:|---:|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 2023 | 57 | 40.35% | 40.51% | 38.71% | 42.31% | 0.2973 |
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 2024 | 241 | 46.89% | 46.94% | 33.88% | 60.00% | 0.2743 |
| SOBTI_5_ET | ASIA_MORNING_LIT | 2023 | 57 | 56.14% | 55.85% | 39.29% | 72.41% | 0.2566 |
| SOBTI_5_ET | ASIA_MORNING_LIT | 2024 | 241 | 45.64% | 45.50% | 46.67% | 44.34% | 0.2785 |
| SOBTI_5_ET | EUROPE_LIT | 2023 | 69 | 40.58% | 40.53% | 39.39% | 41.67% | 0.2805 |
| SOBTI_5_ET | EUROPE_LIT | 2024 | 254 | 53.54% | 52.80% | 59.57% | 46.02% | 0.2668 |
| SOBTI_5_ET | NY_LONDON_LIT | 2023 | 67 | 56.72% | 56.64% | 51.52% | 61.76% | 0.2887 |
| SOBTI_5_ET | NY_LONDON_LIT | 2024 | 252 | 51.59% | 51.44% | 56.15% | 46.72% | 0.2656 |
| SOBTI_5_ET | US_LATE_LIT | 2023 | 16 | 68.75% | 55.45% | 90.91% | 20.00% | 0.2234 |
| SOBTI_5_ET | US_LATE_LIT | 2024 | 198 | 56.06% | 47.48% | 84.43% | 10.53% | 0.2508 |
| WGC_2026_NY3 | ASIA | 2023 | 72 | 45.83% | 42.86% | 58.14% | 27.59% | 0.3028 |
| WGC_2026_NY3 | ASIA | 2024 | 244 | 48.36% | 44.31% | 73.38% | 15.24% | 0.2703 |
| WGC_2026_NY3 | EUROPE | 2023 | 68 | 47.06% | 43.68% | 66.67% | 20.69% | 0.2733 |
| WGC_2026_NY3 | EUROPE | 2024 | 254 | 47.24% | 45.42% | 64.75% | 26.09% | 0.2707 |
| WGC_2026_NY3 | US | 2023 | 41 | 43.90% | 45.57% | 22.73% | 68.42% | 0.3117 |
| WGC_2026_NY3 | US | 2024 | 245 | 50.20% | 50.32% | 48.46% | 52.17% | 0.2656 |
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 2023-2024_SCORED | 298 | 45.64% | 45.86% | 34.87% | 56.85% | 0.2787 |
| SOBTI_5_ET | ASIA_MORNING_LIT | 2023-2024_SCORED | 298 | 47.65% | 47.88% | 45.40% | 50.37% | 0.2743 |
| SOBTI_5_ET | EUROPE_LIT | 2023-2024_SCORED | 323 | 50.77% | 50.36% | 55.75% | 44.97% | 0.2697 |
| SOBTI_5_ET | NY_LONDON_LIT | 2023-2024_SCORED | 319 | 52.66% | 52.61% | 55.21% | 50.00% | 0.2704 |
| SOBTI_5_ET | US_LATE_LIT | 2023-2024_SCORED | 214 | 57.01% | 48.04% | 84.96% | 11.11% | 0.2488 |
| WGC_2026_NY3 | ASIA | 2023-2024_SCORED | 316 | 47.78% | 43.85% | 69.78% | 17.91% | 0.2777 |
| WGC_2026_NY3 | EUROPE | 2023-2024_SCORED | 322 | 47.20% | 45.08% | 65.17% | 25.00% | 0.2713 |
| WGC_2026_NY3 | US | 2023-2024_SCORED | 286 | 49.30% | 49.61% | 44.74% | 54.48% | 0.2722 |
