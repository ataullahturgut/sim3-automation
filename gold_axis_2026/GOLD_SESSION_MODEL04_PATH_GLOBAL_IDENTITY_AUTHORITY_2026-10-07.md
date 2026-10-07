# SESSION MODEL-04 — IRIS HOURLY_ONLY / PATH_GLOBAL — IDENTITY AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / BASELINE IDENTITY ACCEPTED / NO DUPLICATE BASELINE RERUN REQUIRED

## Baseline identity

Accepted existing authority:
- `GOLD_SESSION_IRIS_HOURLY_RAW_REPLAY_V1_SUMMARY_2026-10-06.json`
- `GOLD_SESSION_IRIS_HOURLY_RAW_REPLAY_V1_RESULT_2026-10-06.md`
- corrected 2025 transport in `GOLD_SESSION_STAGE1_GLOBAL_CONTROLS_2025_V2_CONTINUOUS_SUMMARY_2026-10-07.json`

Model:
- original IRIS `HOURLY_ONLY_ALL / PATH_GLOBAL`
- StandardScaler + LogisticRegression(L2, C=1.0)
- threshold 0.50
- five-row causal replay
- minimum 180 matured same-window training rows

Feature block:
- h_ret_1, h_ret_3, h_ret_6, h_ret_12, h_ret_24, h_ret_48
- h_lag2
- h_session_ret
- h_rv_6, h_rv_12, h_rv_24, h_rv_48
- h_up_semivol_24, h_down_semivol_24, h_down_up_semivol_ratio_24
- h_jump_concentration_24
- h_range_24
- h_upfrac_24
- h_slope_6, h_slope_24
- h_max_drawdown_24
- h_recovery_24
- h_close_location_24
- h_age_max_pos_24, h_age_max_neg_24

## Raw-source identity

Hourly source:
- Neon series `XAU_USD_TWELVE_1H_RESEARCH_V1`
- 17,644 raw hourly rows
- observed span used in initial replay: 2022-01-02 23:00 UTC -> 2024-12-31 21:00 UTC

Target:
- V5 session targets independently reconstructed from raw 15-minute XAU
- target reproduction: PASS

Historical derived IRIS predictions/states are not used as model inputs.

## Clock / availability rule

The Twelve hourly timestamp is the **bar-open time**, while the stored value is the **bar-close value**.

Therefore:
- a bar opened at T becomes known at T+1h;
- PATH_GLOBAL uses the latest completed hourly close with `available_at <= session_start`;
- equality is valid because the hourly bar has completed exactly when the target window begins;
- no hourly close occurring after target start may be used.

This hourly rule is intentionally different from the 15-minute target-start-bar rule. A 15-minute target bar opening at the session start is target-window information and is not used as a predictor.

## Development evidence

2023–2024 combined PATH_GLOBAL results:

| Window | N | Accuracy | BA | UP recall | DOWN recall | Brier |
|---|---:|---:|---:|---:|---:|---:|
| Sobti Asia Afternoon | 298 | 45.64% | 45.86% | 34.87% | 56.85% | 0.2787 |
| Sobti Asia Morning | 298 | 47.65% | 47.88% | 45.40% | 50.37% | 0.2743 |
| Sobti Europe | 323 | 50.77% | 50.36% | 55.75% | 44.97% | 0.2697 |
| Sobti NY/London | 319 | 52.66% | 52.61% | 55.21% | 50.00% | 0.2704 |
| Sobti Late-US | 214 | 57.01% | 48.04% | 84.96% | 11.11% | 0.2488 |
| WGC Asia | 316 | 47.78% | 43.85% | 69.78% | 17.91% | 0.2777 |
| WGC Europe | 322 | 47.20% | 45.08% | 65.17% | 25.00% | 0.2713 |
| WGC US | 286 | 49.30% | 49.61% | 44.74% | 54.48% | 0.2722 |

Baseline development conclusion: no universal robust session edge; Late-US apparent accuracy is one-sided and fails the class-recall floor.

## Corrected 2025 transport identity

Independent identity audit:
- PATH_GLOBAL matched rows: **284**
- maximum absolute probability difference: **0.0**

Thus the corrected 2025 implementation is exactly identity-consistent with the frozen PATH_GLOBAL specification.

2025 corrected full-head transport metrics from the global-control authority:

| Window | N | Accuracy | BA | UP recall | DOWN recall | Brier |
|---|---:|---:|---:|---:|---:|---:|
| Sobti Asia Afternoon | 137 | 50.36% | 50.35% | 48.53% | 52.17% | 0.2705 |
| Sobti Asia Morning | 140 | 53.57% | 53.52% | 52.24% | 54.79% | 0.2656 |
| Sobti Europe | 144 | 54.17% | 51.12% | 71.08% | 31.15% | 0.2627 |
| Sobti NY/London | 144 | 41.67% | 42.68% | 34.57% | 50.79% | 0.2740 |
| Sobti Late-US | 107 | 59.81% | 53.30% | 79.10% | 27.50% | 0.2559 |
| WGC Asia | 105 | 60.00% | 58.14% | 75.86% | 40.43% | 0.2608 |
| WGC Europe | 145 | 53.10% | 51.59% | 66.25% | 36.92% | 0.2676 |
| WGC US | 140 | 47.14% | 49.38% | 37.35% | 61.40% | 0.2825 |

## Binding decision

1. SESSION Model-04 PATH_GLOBAL baseline identity is accepted.
2. No duplicate baseline rerun is required.
3. Baseline remains a heterogeneous/window-specific candidate, not a universal model.
4. A model-specific feature-selection challenger may now be tested, but only within the original 25 hourly PATH/VOL/SHAPE variables.
5. Adding 15-minute or cross-metal variables would create a different lineage and is not part of Model-04B.
6. Feature selection must use 2023–2024 only; 2025 is transport only; 2026 remains unopened.
