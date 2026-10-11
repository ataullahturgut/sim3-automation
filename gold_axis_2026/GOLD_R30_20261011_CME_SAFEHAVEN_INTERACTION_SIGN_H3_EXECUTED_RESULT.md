# R30 — executed preissue NQ-ZN safehaven / Gold disagreement interaction, 11 Oct 2026 TRT
Pre-outcome prereg: GOLD_R30_CROSSMARKET_RISKOFF_DISAGREEMENT_GOLD_H3_20261011_PREREG.md (commit c8f0daf28c9407b284c0601c1ac8ec679b2fbc8f). Actually ran read-only Neon SQL and in-tool JS numerical Newton logistic + price CBR, no invented backtest. No DB write. Frozen score2024 train2023 matured n202, score2025 AND2026 train2023+2024 matured n407, L2=30 intercept unpenalized Newton16, train-only standardization, cutoff0.5. Preissue 08:45TR Gold BID M15 04:45–08:30, CME NQ/ZN/CL 01–04 UTC 1h bars complete by05UTC; entry09TR, exact third next weekday09TR, BIDASK sign parity. Price PATH uses41NN 8 cum halfhours normalized by 16-bar sqrt squared logreturns, 5 pseudo prior, training 2020 onward with label maturity. SAFE adds binary NQ4<0/ZN4>0 plus linear redundant safehaven; DISAGREE adds Gold4 z*(ZN4 z-NQ4 z); BOTH binary+interaction. Same cohort across models within year.

| Year | N / UP / DOWN | Model | BA% | UP recall% | DOWN recall% | Brier |
|---|---|---|---:|---:|---:|---:|
|2024|205/122/83|PATH|51.44|63.11|39.76|.25576|
|2024|205/122/83|BASE R28 four features|52.95|54.10|51.81|.25035|
|2024|205/122/83|SAFE|49.51|50.82|48.19|.25405|
|2024|205/122/83|DISAGREE|49.58|37.70|61.45|.25502|
|2024|205/122/83|BOTH|50.64|43.44|57.83|.25770|
|2025|201/127/74|PATH|54.06|81.10|27.03|.24460|
|2025|201/127/74|BASE|53.78|91.34|16.22|.24293|
|2025|201/127/74|SAFE|53.44|86.61|20.27|.24509|
|2025|201/127/74|DISAGREE|53.78|91.34|16.22|.24299|
|2025|201/127/74|BOTH|53.84|87.40|20.27|.24515|
|2026|99/46/53|PATH|46.10|69.57|22.64|.26678|
|2026|99/46/53|BASE|51.54|80.43|22.64|.25561|
|2026|99/46/53|SAFE|52.19|76.09|28.30|.25403|
|2026|99/46/53|DISAGREE|52.48|80.43|24.53|.25580|
|2026|99/46/53|BOTH|53.14|76.09|30.19|.25422|

Paired rescued/broken vs PATH: BASE 2024 40/41,2025 27/22,2026 19/14; BOTH 2024 41/50,2025 27/24,2026 21/14. All models share exact annual date cohort. **NO PROMOTION**: 2026 BOTH BA53.14 with DOWN30.19 remains inadequate; 2024 falls 52.95 BASE to50.64 BOTH and 2025 PATH54.06 exceeds BOTH53.84. A 2026-selected winner is retrospective selection, not repeatable edge. Brier also worse 2024/25 for BOTH vs BASE.

RECONCILIATION OPEN: Fresh SQL source 1696 complete Gold origin days and 1655 valid gold H3 labels, macro 709 (2023 204,2024 205,2025 201,2026 99); earlier R28 reported 1654/708 with 2026 98 (UP45/DOWN53). 2024 and2025 BASE BA and recall exactly reproduce R28; 2026 cohort includes ONE additional UP origin vs R28 and therefore its n99 BA must not be compared directly to R28 n98. No source rows mutated. Need exact date-set diff against archived R28 daily predictions to resolve, which are not in its summary. Do not silently relabel, exclude or select that row. 2025/26 already repeatedly inspected; 2027 independent lockbox required; historical CME continuous roll firstprint and bank fills not certified.
