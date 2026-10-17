# E1 monthly known-segment baseline — actual-data retrospective audit (2026-10-12)

**Scope:** monthly H=1 average XAU/USD price. This is a diagnostic audit conducted **after** Claude's PR #85 and after results were discussed, **not** a new preregistered or untouched OOS test. The incumbent ChHHO model and monthly manifest remain unchanged.

## Source and time contract
- Frozen ChHHO **33 exact per-target price predictions**: GitHub Actions artifact **11049132605**, `GOLD_MONTHLY_CROSS_MODEL_ERROR_OVERLAP_V1_2026-09-29.json`, `month_analysis` keys `target, actual, chhho_forecast`. Checksum: the 33 abs errors sum to 1413.0297794084559 USD, matching the canonical manifest.
- Target actual: Neon `observations`, `CORE5_GOLD_USD_OZ_RESEARCH_R1` monthly average; verify all 33 exact target values against the artifact. Later opened years use only source retrospective baselines, not ChHHO fabricated forecasts.
- Origin baseline: latest historically archived daily `XAU_STAKTRAKR_RESEARCH_DAILY_R1` observation **within the completed origin month**; monthly Stak mean and CORE5 prior mean as controls.
- Provenance restriction: these series were ingested on 2026-09-05; historical daily *first-print/availability* and actual bank executable quotes are NOT established. Last observation is an origin-safe **retrospective price proxy**, not a certified live trading price.
- Comparable actual target is World Bank-derived monthly mean, not next-month close or trade P&L. All scores paired by the exact 33 2022-04..2024-12 target months. No training, no parameter or candidate search.

## Result (real stored gold data, 33 months)
| Predictor | DEV total absolute error (USD) | MAE (USD) |
|---|---:|---:|
| Frozen ChHHO | **1413.03** | **42.82** |
| STAK origin last daily price (no fit) | 1513.32 | 45.86 |
| STAK origin monthly average (no fit) | 1767.05 | 53.55 |
| WB prior monthly average (publication timing unproven) | 1758.00 | 53.27 |

Compared with the much harder **last-daily-price** baseline, frozen ChHHO reduces aggregate absolute error by **100.29 USD (6.63%)**, with monthly error wins **19 / 33**. Three-month moving-block bootstrap (20,000 draws, seed 20261012) for mean paired error reduction is **[-3.27, +10.89] USD per month (95% CI)**, spanning zero. This improvement is **not** statistically established.

Direction under the WB prior-month-average anchor: **ChHHO 23/32**, last-price sign **21/32**; **one flat outcome (2023-10) is excluded**. The canonical monthly manifest states 23/33 on its own scoring convention; do not silently change that canonical number. Monthly average price error is the main measure.

2025/2026 price-only baselines can be recomputed from the 52-row ledger; they are repeatedly inspected historical periods and have no matched frozen ChHHO rows in this artifact.

**Interpretation:** Claude's claim that the monthly ChHHO gain is wholly averaging-induced is **not demonstrated**. ChHHO does beat this stronger retrospective last-price baseline numerically, but by an uncertain margin. Conversely the older large margin versus previous-month mean overstates incremental skill. Neither monthly forecasting nor short-horizon transfer is promoted/rejected on this diagnostic alone.

## Required before authority change
1. Obtain verified origin-time WB/Stak publication vintages; if missing, report archival limitation.
2. Retrieve per-month **frozen DE-ABC** forecasts and match exact 33 target prices; do not infer from aggregate 1415.84.
3. Validate same-origin and same-target source/units for ChHHO and candidate controls.
4. Keep a prospective untouched timestamped lockbox; do not use these opened results for model tuning.
5. Evaluate incremental calibration versus same-sample no-fit trend, and explicit paired uncertainty.

## Reproduce
`python3 gold_axis_2026/tools/gold_e1_20261012_monthly_known_segment_audit.py`

Data: `GOLD_E1_20261012_MONTHLY_KNOWN_SEGMENT_INPUT_ROWS.csv`. Output: `GOLD_E1_20261012_MONTHLY_KNOWN_SEGMENT_RECALC.json`.

Do not edit monthly canonical manifest or existing forecasts. This PR is a diagnostic research-only supplement.
