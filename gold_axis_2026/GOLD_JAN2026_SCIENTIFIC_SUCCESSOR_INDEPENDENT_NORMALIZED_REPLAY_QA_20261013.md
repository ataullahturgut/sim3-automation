# Independent normalized replay check — 2026-10-13
Research only. This QA used the normalized daily return/open-quote factors in
`GOLD_JAN2026_SCIENTIFIC_SUCCESSOR_DERIVED_DAILY_FEATURE_INPUT_20261013.csv` and independently recomputed the portfolio NAV with a second in-memory JavaScript routine; it did **NOT** rerun the committed Python reproducer. Compared all four annual study cohorts and the original B0 vs Stage-B-selected S4 policy in the frozen saved JSON results. All eight pass, including the exact number of executed paid actions. Maximum absolute difference in percentage-point return: **7.11e-13**, attributable to floating-point accumulation.

| Cohort | B0 recomputed net % | B0 action count | S4 recomputed net % | S4 action count |
|---|---:|---:|---:|---:|
| 2023 DEV | -3.640160535053 | 17 | 5.995765867721 | 3 |
| 2024 DEV | -12.465533076495 | 26 | 15.091487510421 | 4 |
| 2025 exploratory validation | 2.090780224671 | 30 | 41.172499333438 | 5 |
| Jan2026 prior-exposed | 7.026135139468 | 1 | 10.151439903974 | 1 |

This recheck establishes **portfolio arithmetic consistency for B0 and S4 from the committed session-factor input**. It does not validate upstream external spot-vendor labels, bank executable ASK/BID, contemporaneous price provenance, original 2026 news firstprint clocks, or causal inference. Stage A/C combination outputs have not been independently rerun by the QA routine; their JSONs remain exploratory. The stdlib Python code is stored for user/local reproduction, but has not been executed as part of this particular QA.