# GOLD CONTROL — IMPORTANCE-WEIGHTED HISTORICAL SOURCE ADAPTATION V1

**Status:** `IMPORTANCE_WEIGHTED_SIGNAL_SAMPLE_LIMITED_NOT_CERTIFIED`

Source: n=98 (UP=46, DOWN=52).  
2022 target covariate calls: n=7.  
Importance-weight ESS=46.09; gate >= 20.0; passed=True.

| Model | 2023-24 true retained | 2025 false removed | 2025 true retained | 2025 precision before | 2025 precision after |
|---|---:|---:|---:|---:|---:|
| UNWEIGHTED_SOURCE | 2/4 | 6/12 | 10/13 | 52.0% | 62.5% |
| IMPORTANCE_WEIGHTED_SOURCE | 3/4 | 6/12 | 11/13 | 52.0% | 64.7% |

The 2022 call covariates were used for density-ratio estimation, but their outcome labels were not used to train either failure detector.
No source row is treated as an actual historical UP2 call.
Research-only; no veto is promoted.
