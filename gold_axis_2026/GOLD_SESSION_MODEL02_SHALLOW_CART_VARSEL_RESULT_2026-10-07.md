# SESSION MODEL-02 — SHALLOW CART — VARIABLE-SELECTION RESULT

**Status:** variable analysis and frozen 2025 transport completed.

## Frozen per-session variables

| Partition | Window | DEV winner | Frozen variables |
|---|---|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | SELECTED_CART | palladium_r21, silver_r21, djia_r5 |
| SOBTI_5_ET | ASIA_MORNING_LIT | FULL_LEGACY_CART | gold_r1, gold_r5, gold_r21, sigma20, silver_r1, silver_r5, silver_r21, platinum_r1, platinum_r5, platinum_r21, palladium_r1, palladium_r5, palladium_r21, nasdaq_r1, nasdaq_r5, nasdaq_r21, sp500_r1, sp500_r5, sp500_r21, djia_r1, djia_r5, djia_r21 |
| SOBTI_5_ET | EUROPE_LIT | FULL_LEGACY_CART | gold_r1, gold_r5, gold_r21, sigma20, silver_r1, silver_r5, silver_r21, platinum_r1, platinum_r5, platinum_r21, palladium_r1, palladium_r5, palladium_r21, nasdaq_r1, nasdaq_r5, nasdaq_r21, sp500_r1, sp500_r5, sp500_r21, djia_r1, djia_r5, djia_r21 |
| SOBTI_5_ET | NY_LONDON_LIT | SELECTED_CART | palladium_r21, sigma20, sp500_r21, gold_r1 |
| SOBTI_5_ET | US_LATE_LIT | FULL_LEGACY_CART | gold_r1, gold_r5, gold_r21, sigma20, silver_r1, silver_r5, silver_r21, platinum_r1, platinum_r5, platinum_r21, palladium_r1, palladium_r5, palladium_r21, nasdaq_r1, nasdaq_r5, nasdaq_r21, sp500_r1, sp500_r5, sp500_r21, djia_r1, djia_r5, djia_r21 |
| WGC_2026_NY3 | ASIA | SELECTED_CART | nasdaq_r5, gold_r5, platinum_r5, sp500_r5 |
| WGC_2026_NY3 | EUROPE | GOLD_ONLY_CART | gold_r1, gold_r5, gold_r21, sigma20 |
| WGC_2026_NY3 | US | GOLD_ONLY_CART | gold_r1, gold_r5, gold_r21, sigma20 |

## 2025 frozen-specification transport

| Partition | Window | N | Accuracy | BA | UP recall | DOWN recall | Brier |
|---|---|---:|---:|---:|---:|---:|---:|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 240 | 42.92% | 43.35% | 60.68% | 26.02% | 0.2569 |
| SOBTI_5_ET | ASIA_MORNING_LIT | 239 | 49.79% | 49.55% | 68.60% | 30.51% | 0.2621 |
| SOBTI_5_ET | EUROPE_LIT | 247 | 44.94% | 43.27% | 53.85% | 32.69% | 0.2639 |
| SOBTI_5_ET | NY_LONDON_LIT | 245 | 51.43% | 48.07% | 74.64% | 21.50% | 0.2522 |
| SOBTI_5_ET | US_LATE_LIT | 195 | 55.38% | 49.57% | 70.97% | 28.17% | 0.2534 |
| WGC_2026_NY3 | ASIA | 253 | 51.78% | 48.59% | 74.65% | 22.52% | 0.2552 |
| WGC_2026_NY3 | EUROPE | 247 | 52.63% | 48.50% | 76.06% | 20.95% | 0.2522 |
| WGC_2026_NY3 | US | 239 | 48.12% | 49.88% | 36.30% | 63.46% | 0.2557 |

Feature selection used only 2022 warm-up and 2023-2024 matured development history. 2025 was opened only after the per-session representation was frozen; 2026 was not used.
