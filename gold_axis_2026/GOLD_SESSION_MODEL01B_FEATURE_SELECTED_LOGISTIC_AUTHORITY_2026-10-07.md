# SESSION MODEL-01B — FEATURE-SELECTED CLASSICAL LOGISTIC — AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / DIAGNOSTIC CHALLENGER / DOES NOT REPLACE MODEL-01

## Question

Can the Classical CORE3 Logistic session baseline be materially improved by selecting variables separately for each session and adding only clock-safe pre-session XAU15 state features?

## Data / clock gate

PASS.

- V5 session targets are used.
- Daily CORE3 inputs use only a strictly earlier America/New_York calendar date.
- XAU15 state uses only completed 15-minute observations with `available_at < target_start`.
- A bar becoming available exactly at target start is rejected.
- No target-window information is used.
- WGC Asia uses only the already-governed NY 17:00–18:00 maintenance as-of exception; no synthetic OHLC bar is fabricated.
- 2025 is not used for feature selection.
- 2026 is unopened.

## Fair comparison

2025 CORE3 and Model-01B are compared on the **exact same common rows and identical causal five-row block chronology**.

| Session | CORE3 BA | Model-01B BA | Delta | CORE3 Brier | Model-01B Brier | Verdict |
|---|---:|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 55.98% | 59.09% | +3.11 pp | 0.2447 | 0.2528 | BA improves, calibration worsens |
| Sobti Asia Morning | 48.63% | 46.53% | -2.10 pp | 0.2599 | 0.2769 | worse |
| Sobti Europe | 46.83% | 46.43% | -0.40 pp | 0.2589 | 0.2570 | no directional gain |
| Sobti NY/London | 51.68% | 46.18% | -5.50 pp | 0.2610 | 0.2679 | materially worse |
| Sobti Late-US | 51.47% | 48.75% | -2.72 pp | 0.2538 | 0.2589 | worse |
| WGC Asia | 51.67% | 52.53% | +0.86 pp | 0.2671 | 0.2589 | joint BA + calibration improvement, modest |
| WGC Europe | 49.73% | 50.98% | +1.25 pp | 0.2606 | 0.2650 | BA improves, calibration worsens |
| WGC US | 44.99% | 44.80% | -0.19 pp | 0.2735 | 0.2710 | no directional gain |

## Frozen feature sets

- Sobti Asia Afternoon: gold_r3, g_rv_48, g_jump_concentration_24, g_down_semivol_24, g_down_up_semivol_ratio_24, g_recovery_24, sigma20, g_age_max_pos_24
- Sobti Asia Morning: gold_r1, g_ret_3h, g_age_max_neg_24, g_down_up_semivol_ratio_24, gold_r5, g_ret_1h, platinum_r5, g_jump_concentration_24
- Sobti Europe: gold_r3, gold_r1, gold_r5, g_slope_6, platinum_r21, g_age_max_pos_24, g_max_drawdown_24, silver_r1
- Sobti NY/London: gold_r5, gold_r3, gold_r1, g_ret_1h, g_slope_6, g_range_24, sigma20, g_lag2
- Sobti Late-US: g_slope_6, g_jump_concentration_24, g_lag2, g_rv_48, g_upfrac_24, sigma20, platinum_r21, g_age_max_neg_24
- WGC Asia: g_max_drawdown_24, g_ret_3h, g_rv_48, gold_r1, g_upfrac_24, gold_r10, gold_r21, g_ret_1h
- WGC Europe: platinum_r21, gold_r5, g_lag2, gold_r3, silver_r1, gold_r1, g_max_drawdown_24, g_ret_48h
- WGC US: g_slope_6, sigma20, gold_r5, gold_r3, g_range_24, gold_r1, g_ret_1h, platinum_r21

## Binding decision

1. **Do not replace SESSION Model-01 CORE3 with Model-01B globally.**
2. The feature-selection hypothesis is not generally validated across sessions.
3. The useful result is session specificity:
   - WGC Asia has the cleanest joint 2025 improvement, but the gain is modest and does not justify a new primary model by itself.
   - Sobti Asia Afternoon and WGC Europe gain BA but lose probability calibration.
4. Preserve the selected feature sets as diagnostics/candidate information for later models; do not force them onto NOVA/A1, IRIS, or other architectures.
5. Every later model must perform model-specific feature contribution analysis under the same pre-session availability rule where variable selection is part of that model.
6. SESSION Model-03 remains NOVA / A1-ARCR.

## Evidence

- `GOLD_SESSION_MODEL01B_FEATURE_SELECTED_LOGISTIC_PREREG_2026-10-07.md`
- `GOLD_SESSION_MODEL01B_FEATURE_SELECTED_LOGISTIC_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_MODEL01B_FEATURE_SELECTED_LOGISTIC_2025_METRICS_2026-10-07.csv`
- `GOLD_SESSION_MODEL01B_FEATURE_SELECTED_LOGISTIC_FROZEN_FEATURES_2026-10-07.json`
